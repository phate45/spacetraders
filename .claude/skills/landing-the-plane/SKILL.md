---
name: landing-the-plane
description: Complete session-end protocol for agents. Use when ending a work session, when Mark says "land the plane", or before signing off.
---

# Landing the Plane

Session completion protocol. Work is NOT complete until `git push` succeeds.

## Mandatory Checklist

Execute ALL steps. Do not skip any.

### 1. File Issues for Remaining Work

Create beads issues for anything that needs follow-up:

```bash
bd create "Remaining work title" -t task -p 2 -d "Description" --json
```

Use [creating-tasks](../creating-tasks/SKILL.md) or [discovering-issues](../discovering-issues/SKILL.md) skills for proper issue creation.

### 2. Run Quality Gates (If Code Changed)

**Only if source code was modified.**

Use the `host-executor` MCP server to run cargo commands:

```
mcp__host-executor__execute_command
tool: cargo
args: ["check"]
```

Then `cargo test` and `cargo clippy`.

**Skip if:** Only modified documentation, config files, vault notes, or beads metadata.

### 3. Update Issue Status

```bash
bd close <id1> <id2> ... -r "Completed"  # Batch close finished work
bd update <id> --status in_progress      # Update work still active
```

**For in-progress work, update notes for session handoff:**

```bash
bd update <id> --notes "COMPLETED: [Specific deliverables done]

IN_PROGRESS: [Current state, what's partially done]

NEXT: [Concrete next step - not vague]

BLOCKERS: [What's preventing progress, if any]

KEY_DECISIONS: [Important user guidance or choices made]"
```

Notes survive context compaction. Write as if explaining to a future agent with zero conversation history.

### 4. Sync and Push (MANDATORY)

Run the session-end script to handle sync/pull/push in one call:

```bash
python3 scripts/session-end.py --pretty
```

**Exit codes:**
- `0` - Success: synced, pulled, pushed, verified
- `2` - Conflicts: resolve manually, then run again
- `3` - Dirty: uncommitted non-beads changes, commit first

The script handles `bd sync`, `git pull --rebase`, `git push`, and verification automatically.

### 5. Clean Up (if needed)

- Clear stashes: `git stash list` then `git stash drop` if appropriate
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

The notes field (step 3) is the **primary handoff mechanism**. Conversation history disappears at session end; notes persist. Write notes as the canonical source of truth for session resumption.

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
python3 scripts/session-end.py --pretty
```
