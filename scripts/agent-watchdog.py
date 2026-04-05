#!/usr/bin/env python3
"""
Agent watchdog runner for long-running CLI agents.

Goal: never treat "command submitted" as "agent successfully started".
This wrapper adds:
- binary preflight
- startup timeout (no first output)
- idle timeout (no fresh logs/artifacts)
- wall timeout
- bounded retries
- machine-readable status.json summary

Typical usage:
  python3 scripts/agent-watchdog.py \
    --label writer \
    --binary claude \
    --command "claude --permission-mode bypassPermissions --print 'write an article'" \
    --cwd /path/to/project \
    --startup-timeout 30 \
    --idle-timeout 300 \
    --wall-timeout 1800 \
    --retries 1
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

TRANSIENT_PATTERNS = [
    r"server_error",
    r"internal server error",
    r"\b429\b",
    r"\b502\b",
    r"\b503\b",
    r"\b504\b",
    r"timed? out",
    r"timeout",
    r"connection reset",
    r"econnreset",
    r"overloaded",
    r"try again",
    r"temporar(?:y|ily)",
]

COMMAND_MISSING_PATTERNS = [
    r"command not found",
    r"No such file or directory",
    r"not recognized as an internal or external command",
]


def iso_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


@dataclass
class AttemptResult:
    attempt: int
    started_at: str
    finished_at: str
    duration_seconds: float
    outcome: str
    exit_code: Optional[int]
    retryable: bool
    log_path: str
    matched_pattern: Optional[str]
    artifact_matches: List[str]
    summary: str


class WatchdogError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run a CLI agent with watchdog, retries, and status output.")
    p.add_argument("--label", required=True, help="Human-readable task label")
    p.add_argument("--command", required=True, help="Shell command to execute")
    p.add_argument("--binary", help="Binary to preflight-check (recommended for complex shell commands)")
    p.add_argument("--cwd", default=os.getcwd(), help="Working directory")
    p.add_argument("--runs-dir", default=".runs/agent-watchdog", help="Base directory for run logs/status")
    p.add_argument("--startup-timeout", type=int, default=30, help="Seconds allowed before first output appears")
    p.add_argument("--idle-timeout", type=int, default=300, help="Seconds allowed without fresh logs/artifacts")
    p.add_argument("--wall-timeout", type=int, default=1800, help="Maximum seconds for one attempt")
    p.add_argument("--retries", type=int, default=1, help="Number of retries after the first attempt")
    p.add_argument("--poll-interval", type=int, default=5, help="Monitor poll interval in seconds")
    p.add_argument("--expect-file", action="append", default=[], help="Glob pattern for expected artifacts (repeatable)")
    p.add_argument("--retry-on-regex", action="append", default=[], help="Additional retry regex patterns (repeatable)")
    p.add_argument("--shell", default="/bin/bash", help="Shell used to run the command")
    return p.parse_args()


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "run"


def read_tail(path: Path, max_bytes: int = 6000) -> str:
    if not path.exists():
        return ""
    data = path.read_bytes()
    return data[-max_bytes:].decode("utf-8", errors="replace")


def match_first(patterns: List[str], text: str) -> Optional[str]:
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
            return pattern
    return None


def ensure_binary(binary: Optional[str], command: str) -> str:
    if binary:
        target = binary
    else:
        try:
            target = shlex.split(command)[0]
        except Exception:
            raise WatchdogError("Unable to infer binary from command. Pass --binary explicitly.")
    if not shutil.which(target):
        raise WatchdogError(f"Preflight failed: binary '{target}' is not on PATH")
    return target


def collect_artifacts(cwd: Path, patterns: List[str]) -> List[str]:
    matches: List[str] = []
    for pattern in patterns:
        base = cwd if not os.path.isabs(pattern) else Path("/")
        for path in base.glob(pattern if not os.path.isabs(pattern) else pattern.lstrip("/")):
            try:
                rel = path.relative_to(cwd)
                matches.append(str(rel))
            except Exception:
                matches.append(str(path))
    return sorted(set(matches))


def terminate_process_tree(proc: subprocess.Popen, grace_seconds: int = 8) -> None:
    if proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    deadline = time.time() + grace_seconds
    while time.time() < deadline:
        if proc.poll() is not None:
            return
        time.sleep(0.3)
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        return


def write_status(status_path: Path, payload: dict) -> None:
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def monitor_attempt(args: argparse.Namespace, run_dir: Path, attempt_num: int, retry_patterns: List[str]) -> AttemptResult:
    cwd = Path(args.cwd).resolve()
    attempt_dir = run_dir / f"attempt-{attempt_num:02d}"
    attempt_dir.mkdir(parents=True, exist_ok=True)
    log_path = attempt_dir / "agent.log"
    meta_path = attempt_dir / "meta.json"

    started_at = iso_now()
    start_ts = time.time()

    with log_path.open("wb") as log_file:
        proc = subprocess.Popen(
            args.command,
            shell=True,
            cwd=str(cwd),
            executable=args.shell,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid,
        )

    write_status(
        meta_path,
        {
            "attempt": attempt_num,
            "started_at": started_at,
            "pid": proc.pid,
            "cwd": str(cwd),
            "command": args.command,
            "binary": args.binary,
        },
    )

    first_output_seen = False
    last_progress_ts = start_ts
    last_log_signature = (0, 0.0)
    known_artifacts: List[str] = []
    outcome = "unknown"
    matched_pattern: Optional[str] = None
    retryable = False
    exit_code: Optional[int] = None
    summary = ""

    while True:
        time.sleep(max(1, args.poll_interval))
        now = time.time()

        if log_path.exists():
            stat = log_path.stat()
            current_signature = (stat.st_size, stat.st_mtime)
            if stat.st_size > 0 and not first_output_seen:
                first_output_seen = True
                last_progress_ts = now
            if current_signature != last_log_signature:
                last_progress_ts = now
                last_log_signature = current_signature

        current_artifacts = collect_artifacts(cwd, args.expect_file)
        if current_artifacts != known_artifacts:
            known_artifacts = current_artifacts
            last_progress_ts = now

        elapsed = now - start_ts
        idle_for = now - last_progress_ts
        exit_code = proc.poll()

        if exit_code is not None:
            tail = read_tail(log_path)
            if exit_code == 0:
                outcome = "success"
                retryable = False
                summary = "Attempt completed successfully."
            else:
                missing_match = match_first(COMMAND_MISSING_PATTERNS, tail)
                transient_match = match_first(retry_patterns, tail)
                if exit_code == 127 or missing_match:
                    outcome = "command_missing_or_not_executable"
                    retryable = False
                    matched_pattern = missing_match
                    summary = "Process exited before real work started; command/binary is missing or not executable."
                elif transient_match:
                    outcome = "transient_process_error"
                    retryable = True
                    matched_pattern = transient_match
                    summary = "Process exited with a transient-looking error; safe to retry."
                else:
                    outcome = "process_exit_nonzero"
                    retryable = False
                    summary = "Process exited non-zero without matching a retryable pattern."
            break

        if not first_output_seen and elapsed > args.startup_timeout:
            terminate_process_tree(proc)
            tail = read_tail(log_path)
            missing_match = match_first(COMMAND_MISSING_PATTERNS, tail)
            outcome = "startup_timeout"
            retryable = not bool(missing_match)
            matched_pattern = missing_match
            summary = "No output appeared before startup timeout."
            if missing_match:
                outcome = "command_missing_or_not_executable"
                retryable = False
                summary = "Startup produced a command-missing style error."
            break

        if elapsed > args.wall_timeout:
            terminate_process_tree(proc)
            outcome = "wall_timeout"
            retryable = True
            summary = "Attempt exceeded wall timeout."
            break

        if idle_for > args.idle_timeout:
            terminate_process_tree(proc)
            outcome = "idle_timeout"
            retryable = True
            summary = "Attempt produced no fresh logs/artifacts for too long."
            break

    finished_at = iso_now()
    duration = round(time.time() - start_ts, 2)
    result = AttemptResult(
        attempt=attempt_num,
        started_at=started_at,
        finished_at=finished_at,
        duration_seconds=duration,
        outcome=outcome,
        exit_code=exit_code,
        retryable=retryable,
        log_path=str(log_path),
        matched_pattern=matched_pattern,
        artifact_matches=known_artifacts,
        summary=summary,
    )
    write_status(attempt_dir / "result.json", asdict(result))
    print(
        json.dumps(
            {
                "event": "attempt_finished",
                "attempt": attempt_num,
                "outcome": outcome,
                "retryable": retryable,
                "exit_code": exit_code,
                "summary": summary,
                "log_path": str(log_path),
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    return result


def main() -> int:
    args = parse_args()
    retry_patterns = TRANSIENT_PATTERNS + args.retry_on_regex
    started_at = iso_now()

    try:
        ensured_binary = ensure_binary(args.binary, args.command)
    except WatchdogError as exc:
        run_slug = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{slugify(args.label)}"
        run_dir = (Path(args.cwd) / args.runs_dir / run_slug).resolve()
        run_dir.mkdir(parents=True, exist_ok=True)
        status = {
            "label": args.label,
            "started_at": started_at,
            "finished_at": iso_now(),
            "cwd": str(Path(args.cwd).resolve()),
            "command": args.command,
            "binary": args.binary,
            "final_outcome": "preflight_failed",
            "final_exit_code": 2,
            "summary": str(exc),
            "attempts": [],
        }
        write_status(run_dir / "status.json", status)
        print(json.dumps({"event": "preflight_failed", "summary": str(exc), "status_path": str(run_dir / 'status.json')}, ensure_ascii=False), flush=True)
        return 2

    args.binary = ensured_binary
    run_slug = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{slugify(args.label)}"
    run_dir = (Path(args.cwd) / args.runs_dir / run_slug).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)

    print(
        json.dumps(
            {
                "event": "run_started",
                "label": args.label,
                "cwd": str(Path(args.cwd).resolve()),
                "binary": args.binary,
                "run_dir": str(run_dir),
                "retries": args.retries,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )

    attempts: List[AttemptResult] = []
    max_attempts = args.retries + 1
    final_exit = 1
    final_outcome = "unknown"
    final_summary = ""

    for attempt_num in range(1, max_attempts + 1):
        result = monitor_attempt(args, run_dir, attempt_num, retry_patterns)
        attempts.append(result)
        if result.outcome == "success":
            final_outcome = "success"
            final_exit = 0
            final_summary = result.summary
            break
        if not result.retryable or attempt_num >= max_attempts:
            final_outcome = result.outcome
            final_exit = result.exit_code if result.exit_code is not None else 1
            final_summary = result.summary
            break
        print(
            json.dumps(
                {
                    "event": "retry_scheduled",
                    "next_attempt": attempt_num + 1,
                    "reason": result.outcome,
                },
                ensure_ascii=False,
            ),
            flush=True,
        )

    payload = {
        "label": args.label,
        "started_at": started_at,
        "finished_at": iso_now(),
        "cwd": str(Path(args.cwd).resolve()),
        "command": args.command,
        "binary": args.binary,
        "final_outcome": final_outcome,
        "final_exit_code": final_exit,
        "summary": final_summary,
        "attempts": [asdict(x) for x in attempts],
    }
    write_status(run_dir / "status.json", payload)
    print(json.dumps({"event": "run_finished", "final_outcome": final_outcome, "final_exit_code": final_exit, "status_path": str(run_dir / 'status.json')}, ensure_ascii=False), flush=True)
    return final_exit


if __name__ == "__main__":
    sys.exit(main())
