# Beads Task Notes Field Format

Shared reference for the `notes` field structure in beads tasks.

## Standard Format

```
COMPLETED: Specific deliverables (what was built/done)
IN_PROGRESS: Current state + what's partially done
NEXT: Immediate next step (concrete, not vague)
BLOCKERS: What's preventing progress
KEY_DECISIONS: Important context or user guidance
CRITERIA: Acceptance criteria status (which are done, which remain)
VAULT_DOCS: Documentation created (file paths, if any)
```

All sections are optional. Include what's relevant.

**CRITERIA section:** Track acceptance criteria progress here instead of using `bd update --acceptance`. List completed criteria and remaining ones. This avoids permission issues with the acceptance field while preserving progress tracking.

## Quality Criteria

**"Future-me test"** — Could you resume in 2 weeks with zero conversation history?
- [ ] What was completed? (Specific deliverables, not "made progress")
- [ ] What's in progress? (Current state + immediate next step)
- [ ] What's blocked? (Specific blockers with context)
- [ ] What decisions were made? (Why, not just what)

**"Stranger test"** — Could another developer understand without asking?
- [ ] Technical choices explained (not just stated)
- [ ] Trade-offs documented (why this approach vs alternatives)
- [ ] User input captured (decisions from discussion)

## Examples

### Good

```
COMPLETED: JWT auth with RS256 (1hr access, 7d refresh tokens)
KEY_DECISIONS: RS256 over HS256 per security review - enables key rotation
IN_PROGRESS: Password reset flow - email service working, need rate limiting
BLOCKERS: Waiting on user decision: reset token expiry (15min vs 1hr trade-off)
NEXT: Implement rate limiting (5 attempts/15min) once expiry decided
```

### Bad

```
Working on auth. Made some progress. More to do.
```

### Checkpoint (blocked, awaiting resume)

```
COMPLETED: API client skeleton with auth flow
IN_PROGRESS: Rate limiting implementation
BLOCKERS: MCP host-executor returning permission denied on cargo test
NEXT: Need CT to verify MCP server config, then resume
KEY_DECISIONS: Using token bucket algorithm per Mark's guidance
```

## Key Rules

**⚠️ CRITICAL: `bd update --notes` REPLACES the entire field.**

The notes field is not append-only. When you run:
```bash
bd update <id> --notes "NEW_CONTENT"
```
The previous notes are completely replaced with `NEW_CONTENT`. If you don't synthesize previous state into your update, that context is **lost**.

**Correct pattern:**
1. Read current notes (provided by `begin-work` or `bd show`)
2. Understand previous state
3. Write COMPLETE current state (synthesizing what matters from previous)
4. Overwrite with your comprehensive update

- **Current state only** — Overwrite previous notes, don't append history
- **Specific accomplishments** — Not vague progress statements
- **Concrete next step** — Not "continue working"
- **Written for zero context** — Survives compaction events

## When to Update Notes

- After completing significant work chunks
- Before decisions that need user input
- When hitting blockers
- Before checkpointing (if yielding for CT resolution)
- At session end (if Control Tower)

## Related Documentation

- `/agent-working` skill — Full workflow including notes updates
- `/beads` skill — Task lifecycle and field usage
- `/landing-the-plane` skill — Session-end notes protocol
