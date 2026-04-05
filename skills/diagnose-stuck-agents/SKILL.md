---
name: diagnose-stuck-agents
description: Diagnose frozen, silent, slow, or fake-start local agent tasks and watchdog runs. Use when a local CLI agent, detached background task, watchdog job, or multi-agent workflow seems stuck, produces no output, exits silently, times out, or when the parent agent is unsure whether the child is truly running.
---

# Diagnose Stuck Agents

Use this skill when progress is unclear or suspicious.

## Workflow

1. Check whether the task actually started.
   - verify the backend binary exists
   - inspect launcher log / watchdog `status.json`
   - distinguish preflight failure from runtime failure

2. Inspect live process state.
   - list parent/child processes
   - inspect CPU, RSS, elapsed time, process state
   - check whether the child is gone while the parent still waits

3. Inspect task-specific evidence.
   - `.runs/agent-watchdog/.../status.json`
   - attempt logs
   - expected artifacts
   - detached launcher logs

4. Classify the failure:
   - fake start
   - startup timeout
   - idle timeout
   - wall timeout
   - transient external failure
   - buffering/observability problem
   - process killed by outer session lifecycle

5. Recommend the next action:
   - retry with same config
   - retry with detached launcher
   - switch backend
   - widen startup threshold
   - tighten artifact checks
   - human intervention required

## Rules

- Never report "still running" based only on a PID.
- Prefer status files and artifacts over raw process existence.
- Treat missing first output with caution: it may be buffering, not a dead task.
- If the outer tool session killed the parent, call that out explicitly.

## Useful local paths

Read `references/local-debug-checklist.md` when you need command snippets and local conventions.