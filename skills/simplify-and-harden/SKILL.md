---
name: simplify-and-harden
description: Review and improve changed code for reuse, simplicity, clarity, and efficiency after implementation. Use when code has just been written or refactored and needs a cleanup/review pass, especially for repetitive logic, hacky patches, copy-paste, redundant state, stringly typed code, hot-path bloat, or missed reuse opportunities.
---

# Simplify and Harden

Use this skill after a code change exists. Do not use it for initial implementation.

## Workflow

1. Inspect the current change set.
   - Prefer `git diff` / `git diff --stat`.
   - If git is unavailable, inspect the files edited in this task.

2. Review the change through 3 lenses:
   - **Reuse**: Is newly written logic duplicating an existing helper/utility/pattern?
   - **Quality**: Any copy-paste drift, leaky abstractions, redundant state, over-parameterization, or unnecessary comments?
   - **Efficiency**: Any duplicated work, missed concurrency, hot-path overhead, or unconditional updates?

3. Fix issues directly when the fix is low-risk and clearly improves the code.

4. If a finding is debatable, note it briefly instead of over-editing.

5. End with a terse report:
   - what was simplified
   - what was hardened
   - what was intentionally left unchanged

## Rules

- Prefer deleting code to adding abstractions unless reuse is clearly justified.
- Prefer existing utilities over hand-rolled helpers.
- Do not preserve comments that merely narrate obvious code.
- Be suspicious of:
  - redundant caches/state
  - repeated string/path/env handling
  - wide fan-out parameter additions
  - no-op updates in polling/event loops
  - broad reads when narrow reads would do

## Output style

Keep the final report short and concrete. No essay.