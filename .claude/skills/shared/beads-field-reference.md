# Beads Field Reference

Task context flows through beads fields. Understanding each field's purpose prevents misuse.

## Field Overview

| Field | Purpose | Mutability | Contains |
|-------|---------|------------|----------|
| `description` | Problem statement | Immutable | WHY and WHAT (what problem we're solving) |
| `design` | Implementation approach | Can evolve | HOW to build it (technical approach) |
| `acceptance_criteria` | Definition of done | Mostly stable | WHAT success looks like (verifiable outcomes) |
| `notes` | Session handoff | Frequent updates | Current state (checkpoint/resume context) |
| `comments` | External feedback | Append-only | Review findings, CT notes (via `bd comment`) |

## Reading Priority

**For implementers (resuming work):**
1. `notes` — Start here. Contains handoff from previous session.
2. `comments` — Check if status was `review` (feedback to address).
3. `acceptance_criteria` — What's done, what remains.
4. `design` — Implementation approach.
5. `description` — Problem context if needed.

**For reviewers:**
1. `acceptance_criteria` — Your verification checklist.
2. `notes` — Agent's claimed completion state (verify, don't trust).
3. `design` — Intended approach (did they follow it?).
4. `comments` — Prior review feedback if any.

## Critical Distinctions

**design vs acceptance_criteria:**
- `design` = HOW (implementation details, technical choices)
- `acceptance_criteria` = WHAT (verifiable outcomes, definition of done)

Design can evolve as implementation reveals better approaches. Acceptance criteria remain stable once defined.

**notes vs comments:**
- `notes` = Agent's work record (owned by implementer)
- `comments` = External feedback (owned by reviewers, CT)

Reviewers write to `comments` via `bd comment`. Never overwrite agent's `notes` with review feedback.

## Notes Field Warning

`bd update --notes "X"` **REPLACES** the entire field. Previous content is destroyed.

**Correct pattern:**
```bash
# 1. Read existing notes
existing=$(bd show <id> --json | jq -r '.[0].notes // ""')

# 2. Synthesize new state (don't append history—write current state)
bd update <id> --notes "COMPLETED: [current deliverables]

IN_PROGRESS: [current work]

NEXT: [concrete next step]" --json
```

See `shared/notes-format.md` for full format and examples.

## Comments Field

Comments are append-only. Use for:
- Review findings (`bd comment <id> "REVIEW: ..." -a "reviewer-name"`)
- CT guidance or notes
- External feedback that shouldn't overwrite agent state

```bash
bd comment <id> "REVIEW:
VERDICT: REQUEST_CHANGES
REASON: Criterion 2 not met - missing error handling" -a "task-reviewer" --json
```

Agent can read comments on resume to see feedback.
