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

### 4. Push to Remote (MANDATORY)

```bash
git pull --rebase
bd sync
git push
git status  # MUST show "up to date with origin"
```

If push fails, resolve and retry until it succeeds.

### 5. Clean Up

- Clear stashes: `git stash list` then `git stash drop` if appropriate
- Prune remote branches if needed

### 6. Verify

All changes must be:
- Committed locally
- Pushed to remote
- Visible in `git status` as "up to date"

### 7. Write Work Log

Synthesize the session into a work log entry in the vault:

```
/writing-work-logs
```

This creates a narrative summary of what was accomplished, not just a list of closed tasks.

### 8. Hand Off

Provide context for next session:
- What was completed
- What's in progress
- Any blockers or decisions needed

## Anti-Patterns

**NEVER do these:**

| Anti-Pattern | Why It's Wrong |
|--------------|----------------|
| Stop before `git push` completes | Work stranded locally, causes rebase conflicts |
| Say "ready to push when you are" | YOU must push, not Mark |
| Batch the push for later | Push NOW, not later |
| Assume push will succeed | Verify with `git status` |
| Skip `bd sync` | Beads changes won't reach remote |

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
git pull --rebase && bd sync && git push
git status  # Verify "up to date"
```
