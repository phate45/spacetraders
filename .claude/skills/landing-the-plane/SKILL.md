---
name: landing-the-plane
description: Complete session-end protocol for agents. Use when ending a work session, when Mark says "land the plane", or before signing off.
---

# Landing the Plane

Session completion protocol. Work is NOT complete until `git push` succeeds.

## Mandatory Checklist

Execute ALL steps. Do not skip any.

### 1. File Issues for Discovered Work

Create draft issues for anything that needs follow-up. Draft status ensures tasks are refined before becoming available work.

```bash
bd create "Remaining work title" -t task -p 2 -d "Description" --json
bd update <id> --status draft
```

Use [discovering-issues](../discovering-issues/SKILL.md) skill for proper issue discovery patterns.

### 2. Run Quality Gates (If Code Changed)

**Only if source code was modified.**

Delegate to the quality-gate agent to preserve CT context:

```
Task tool:
  subagent_type: quality-gate
  model: haiku
  prompt: "Verify project state."
```

**Expected responses:**
- Pass: `"✓ All quality gates passed"`
- Fail: `"✗ Quality gate failed: logged in spacetraders-<id>"` (P1 draft task created)

**Skip if:** Only modified documentation, config files, vault notes, or beads metadata.

### 3. Update Issue Status

**Completed work with worktrees:**
```bash
end-work <id>  # Handles merge, cleanup, close in one step
```

**Research tasks (no worktree):**
```bash
bd close <id> -r "Summary of findings"
```

**In-progress work — add handoff context via comment (preserves agent notes):**
```bash
bd comment <id> "SESSION HANDOFF

COMPLETED: [Specific deliverables done]
IN_PROGRESS: [Current state]
NEXT: [Concrete next step]
BLOCKERS: [If any]" --author control-tower --json
```

Comments survive context compaction. The notes field belongs to the executing agent; CT adds context through comments.

### 4. Sync and Push (MANDATORY)

Run the session-end script to handle sync/pull/push in one call:

```bash
python3 scripts/session-end.py
```

**Exit codes:**
- `0` - Success: synced, pulled, pushed, verified
- `2` - Conflicts: resolve manually, then run again
- `3` - Dirty: uncommitted non-beads changes, commit first

The script handles `bd sync`, `git pull --rebase`, `git push`, and verification automatically.

### 5. Clean Up (if needed)

The script reports stashes in `post_state.stashes`. If any exist:
- Review: are they still needed?
- Drop if stale: `git stash drop stash@{N}`
- Prune remote branches if needed

### 6. Write Work Log

Synthesize the session into a work log entry in the vault:

```
/writing-work-logs
```

This creates a narrative summary of what was accomplished, not just a list of closed tasks.

### 7. Hand Off

Provide context for next session:
- What was completed
- What's in progress
- Any blockers or decisions needed

Task comments (step 3) are the **CT handoff mechanism**. The notes field belongs to agents; CT adds context through comments which preserve agent state. Conversation history disappears at session end; comments persist.

For comprehensive notes patterns and resumability guidelines, see the [beads skill](../beads/SKILL.md).

## Anti-Patterns

**NEVER do these:**

| Anti-Pattern | Why It's Wrong |
|--------------|----------------|
| Skip `session-end.py` | Sync/push are mandatory, not optional |
| Ignore non-zero exit codes | Conflicts (2) and dirty (3) require action |
| Say "ready to push when you are" | YOU must run the script, not Mark |
| Stop before script succeeds | Work stranded locally, causes rebase conflicts |

**Mark coordinates multiple agents.** Unpushed work causes severe rebase conflicts when other agents push changes.

## Conflict Resolution

If `git pull --rebase` causes conflicts in `.beads/issues.jsonl`:

```bash
git checkout --theirs .beads/issues.jsonl
bd import -i .beads/issues.jsonl
bd sync
git push
```

See [resolving-jsonl-conflicts](../resolving-jsonl-conflicts/SKILL.md) for detailed guidance.

## Quick Reference

```bash
# Minimal landing sequence
bd close <ids> -r "Done"
python3 scripts/session-end.py
```
