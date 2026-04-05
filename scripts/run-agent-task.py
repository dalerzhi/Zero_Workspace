#!/usr/bin/env python3
"""
High-level launcher for long-running CLI agent tasks.

This is the human-friendly entrypoint on top of scripts/agent-watchdog.py.
It chooses sane watchdog defaults for different task classes and currently
uses Claude Code as the default available local agent.
"""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path("/Users/a123456/.openclaw/workspace")
WATCHDOG = WORKSPACE / "scripts" / "agent-watchdog.py"
CLAUDE_BIN = "/opt/homebrew/bin/claude"

PRESETS = {
    "writing": {"startup": 30, "idle": 300, "wall": 1800, "retries": 1},
    "research": {"startup": 30, "idle": 300, "wall": 1800, "retries": 1},
    "coding": {"startup": 45, "idle": 600, "wall": 3600, "retries": 1},
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Launch an agent task through the watchdog with preset timeouts.")
    p.add_argument("--kind", choices=sorted(PRESETS.keys()), required=True, help="Task kind preset")
    p.add_argument("--label", required=True, help="Run label")
    p.add_argument("--task", help="Task prompt text")
    p.add_argument("--task-file", help="Read task prompt from file")
    p.add_argument("--cwd", default=str(WORKSPACE), help="Working directory for the task")
    p.add_argument("--agent", default="claude", choices=["claude"], help="Local agent backend (currently claude only)")
    p.add_argument("--model", help="Optional model override for claude")
    p.add_argument("--effort", choices=["low", "medium", "high", "max"], help="Optional effort override for claude")
    p.add_argument("--expect-file", action="append", default=[], help="Expected artifact glob (repeatable)")
    p.add_argument("--startup-timeout", type=int, help="Override startup timeout")
    p.add_argument("--idle-timeout", type=int, help="Override idle timeout")
    p.add_argument("--wall-timeout", type=int, help="Override wall timeout")
    p.add_argument("--retries", type=int, help="Override retry count")
    p.add_argument("--dry-run", action="store_true", help="Print the final watchdog command without executing it")
    return p.parse_args()


def load_task(args: argparse.Namespace) -> str:
    if bool(args.task) == bool(args.task_file):
        raise SystemExit("Pass exactly one of --task or --task-file")
    if args.task_file:
        return Path(args.task_file).read_text(encoding="utf-8")
    return args.task


def build_agent_command(args: argparse.Namespace, task: str) -> tuple[str, str]:
    if args.agent != "claude":
        raise SystemExit(f"Unsupported agent backend: {args.agent}")
    parts = [CLAUDE_BIN, "--permission-mode", "bypassPermissions", "--print"]
    if args.model:
        parts += ["--model", args.model]
    if args.effort:
        parts += ["--effort", args.effort]
    parts.append(task)
    return "claude", shlex.join(parts)


def main() -> int:
    args = parse_args()
    task = load_task(args)
    binary, agent_command = build_agent_command(args, task)
    preset = PRESETS[args.kind]

    startup = args.startup_timeout or preset["startup"]
    idle = args.idle_timeout or preset["idle"]
    wall = args.wall_timeout or preset["wall"]
    retries = args.retries if args.retries is not None else preset["retries"]

    cmd = [
        sys.executable,
        str(WATCHDOG),
        "--label",
        args.label,
        "--binary",
        binary,
        "--command",
        agent_command,
        "--cwd",
        args.cwd,
        "--startup-timeout",
        str(startup),
        "--idle-timeout",
        str(idle),
        "--wall-timeout",
        str(wall),
        "--retries",
        str(retries),
    ]
    for pattern in args.expect_file:
        cmd += ["--expect-file", pattern]

    if args.dry_run:
        print(shlex.join(cmd))
        return 0

    os.execvp(cmd[0], cmd)


if __name__ == "__main__":
    raise SystemExit(main())
