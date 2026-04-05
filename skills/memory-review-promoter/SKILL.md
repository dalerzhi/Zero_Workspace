---
name: memory-review-promoter
description: Review recent notes, working memory, and long-term memory for duplicates, stale guidance, and items worth promotion into durable memory. Use when cleaning up memory files, reconciling daily notes with MEMORY.md, promoting repeated lessons, or checking whether temporary working notes should become long-term instructions.
---

# Memory Review Promoter

Use this skill for memory maintenance, not for answering a normal memory question.

## Workflow

1. Read the relevant memory layers.
   - today's / recent `memory/YYYY-MM-DD.md`
   - `MEMORY.md`
   - if relevant, `.learnings/`

2. Classify findings:
   - promote to long-term memory
   - keep as short-term/daily note
   - deduplicate
   - mark stale/outdated
   - ambiguous: needs user confirmation

3. Look for conflicts:
   - recent note contradicts long-term memory
   - duplicated rules in multiple places
   - stale instructions still shaping behavior

4. Propose specific edits.
   - what to add
   - what to remove
   - what to rewrite
   - why

5. Only apply changes when confidence is high or the user explicitly asked for cleanup.

## Rules

- Prefer concise durable rules in `MEMORY.md`.
- Keep raw session detail in daily notes unless it will matter again.
- Promote repeated mistakes and repeated preferences aggressively.
- If uncertain whether something is temporary or durable, ask or mark it ambiguous.
