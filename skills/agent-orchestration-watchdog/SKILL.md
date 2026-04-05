---
name: agent-orchestration-watchdog
description: Orchestrate long-running local CLI agents and multi-agent workflows with startup checks, timeouts, retries, detached background execution, and status-based progress reporting. Use when spawning writing/research/coding agents, fan-out/fan-in workflows, or any child-agent task where "started" vs "really running" matters, especially after hangs, silent failures, fake starts, or missing-output problems.
---

# Agent Orchestration Watchdog

Use this skill when running long local agent tasks that must be supervised instead of blindly awaited.

## Default workflow

1. For standard tasks, start with:
   - `python3 scripts/run-agent-task.py --kind writing|research|coding ...`
2. For complex tasks, use:
   - `python3 scripts/agent-watchdog.py ...`
3. Treat progress as real only when supported by one of:
   - first valid startup signal
   - fresh logs
   - fresh artifacts
   - `status.json` state change
4. On failure, distinguish:
   - preflight failure
   - startup timeout
   - idle timeout
   - wall timeout
   - transient process error
   - non-retryable process error

## Rules

- Never treat "command submitted" as "agent successfully started".
- Always preflight-check the backend binary.
- Prefer status-file driven reporting over guessing from process existence.
- For long detached jobs, do not rely only on OpenClaw tool-session lifetime.
- If a task has expected deliverables, monitor artifacts explicitly.
- Use bounded retries; do not loop forever.

## Recommended entrypoints

### Writing / research / coding
Use `scripts/run-agent-task.py` first.

### Special cases
Use `scripts/agent-watchdog.py` directly when you need custom shell commands, retry regexes, or custom artifact monitoring.

## What to read next

- For Zero's local rules and thresholds, read `references/zero-watchdog-rules.md`.
- For design lessons learned from Claude Code source, read `references/claude-code-lessons.md`.
