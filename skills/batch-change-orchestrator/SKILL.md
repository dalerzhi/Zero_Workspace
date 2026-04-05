---
name: batch-change-orchestrator
description: Plan and execute a large, mostly mechanical change across many independent units with explicit decomposition, parallel workers, progress tracking, and fan-in reporting. Use when a migration, refactor, bulk rename, repetitive cleanup, or multi-file mechanical edit can be sliced into parallel work units and should not be done as one giant undifferentiated task.
---

# Batch Change Orchestrator

Use this skill for large but decomposable changes.

## Workflow

1. Research the scope first.
   - identify files, patterns, and conventions
   - confirm the change is mostly mechanical and parallelizable

2. Decompose into independent work units.
   - each unit should be self-contained
   - avoid hidden dependency chains between sibling units
   - split by directory, module, feature area, or pattern family

3. Define verification for each unit.
   - unit tests, smoke checks, screenshots, or artifact checks
   - do not let workers invent success criteria late

4. Launch workers in parallel only after the decomposition is solid.
   - use watchdog-backed launchers
   - require clear labels and expected artifacts where possible

5. Track fan-out / fan-in explicitly.
   - maintain a status table
   - mark running / done / failed / blocked
   - collect only final outputs that matter

6. Merge and summarize.
   - unify repeated lessons
   - call out failures and skipped units clearly

## Rules

- Do not parallelize tightly coupled edits.
- Do not start workers before defining unit boundaries.
- Require each worker to report concrete deliverables, not just narrative progress.
- If one worker reveals a bad decomposition, stop and re-plan instead of brute-forcing.

## Read next

Read `references/planning-checklist.md` before using this skill on a real migration.