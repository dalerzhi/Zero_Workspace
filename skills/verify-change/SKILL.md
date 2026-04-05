---
name: verify-change
description: Verify that a code or workflow change actually works in practice, not just that it looks plausible. Use when a feature, fix, refactor, UI change, automation, or integration has been implemented and needs real validation through tests, runtime checks, browser checks, logs, screenshots, or end-to-end flow verification.
---

# Verify Change

Use this skill after implementation and before claiming success.

## Workflow

1. Define what "working" means for this change.
   - command succeeds?
   - tests pass?
   - UI renders correctly?
   - API returns expected data?
   - file/artifact is generated?

2. Choose the strongest available verification path:
   - existing automated tests
   - focused manual runtime check
   - browser-based verification for UI flows
   - API/CLI verification for integrations
   - artifact inspection for generated outputs

3. Run verification in increasing cost order:
   - lint/type/unit first
   - then integration/e2e/manual flow

4. Record evidence, not vibes:
   - command output
   - screenshot path
   - generated file path
   - before/after behavior
   - failing step if verification breaks

5. Report one of 3 outcomes:
   - **verified**
   - **partially verified**
   - **not verified**

## Rules

- "Code looks correct" is not verification.
- If you cannot run a full verification path, say exactly what is missing.
- Prefer reproducing the user-visible behavior over only checking internal code paths.
- If verification fails, switch into diagnosis instead of pretending the task is done.

## Final report

Use this structure:
- verification path used
- evidence collected
- remaining uncertainty