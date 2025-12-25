---
name: checkpointing
description: Checkpoint session state before context compaction. Use when context is filling up and conversation will continue after compaction. Creates CONTEXT.md and updates work log.
---

# Checkpointing

Mid-session checkpoint protocol for context compaction. Unlike `/landing-the-plane`, the session continues—no push required.

## When to Use

- Context window filling up, compaction imminent
- Mark says "checkpoint", "prepare for compaction", or similar
- You sense conversation needs to be summarized for continuity

## Mandatory Steps

### 1. Sync Beads State

```bash
bd sync --json
```

Ensures all task updates are persisted before context compaction.

### 2. Write Work Log

**Invoke writing-work-logs skill FIRST:**

```
/writing-work-logs
```

Then write to today's log file at `/home/phate/Documents/second-brain/01_Projects/spacetraders/logs/YYYY-MM-DD.md`

This captures what was accomplished so far. If the log already exists from earlier in the session, append a new `## [Topic]` section.

### 3. Create CONTEXT.md

Write `/home/phate/BigProjects/spacetraders/CONTEXT.md` with session state:

```markdown
# Session Context — [Date] ([Time])

## What Happened This Session

[Narrative summary of work completed]

### Completed Work

[Task IDs and brief descriptions]

### In-Progress Work

[Any work still active]

## Current Task Queue

| ID | Title | Priority | Type |
|----|-------|----------|------|
| `spacetraders-xxx` | Title | P2 | task |

## Key Files Changed

```
Created:
- file1.md
- file2.md

Modified:
- file3.md
```

## Key Decisions This Session

1. **Decision Name** — Explanation
2. **Another Decision** — Why it matters

## Session Protocol Notes

- [ ] All changes committed
- [ ] `bd sync` completed
- [ ] Any blockers or pending questions

## Quick Reference

```bash
bd ready --json    # See available work
bd show <id> --json | jq '.[0]'  # Task details
```
```

### 4. Verify State

```bash
git status
bd ready --json
```

Confirm:
- No uncommitted beads changes (bd sync handled this)
- Code changes are either committed or explicitly in-progress

## What This Skill Does NOT Do

Unlike `/landing-the-plane`:
- Does NOT require `git push` (session continues)
- Does NOT close tasks (work may be ongoing)
- Does NOT clean up stashes or worktrees
- Does NOT provide final handoff

This is a **checkpoint**, not a **landing**.

## Anti-Patterns

| Anti-Pattern | Why It's Wrong |
|--------------|----------------|
| Skip work log | Session narrative lost; CONTEXT.md alone is insufficient |
| Skip bd sync | Beads state not persisted; risks data loss on crash |
| Write CONTEXT.md without reading current state | Stale or inaccurate context for resumption |
| Copy entire conversation | CONTEXT.md should be synthesized, not transcribed |

## Quick Reference

```bash
# Minimal checkpoint sequence
bd sync --json
# Invoke /writing-work-logs, write to vault
# Create CONTEXT.md with session state
git status  # Verify no critical uncommitted changes
```
