---
name: resolving-jsonl-conflicts
description: Resolve git conflicts in beads JSONL files. Use when git pull/merge/rebase fails with conflicts in .beads/ directory.
---

# Resolving JSONL Conflicts

When `git pull --rebase` or `git merge` results in conflicts in `.beads/issues.jsonl`, use this resolution procedure.

## When This Happens

- Multiple agents pushed changes to the same repository
- You rebased onto a branch with different beads state
- Manual edits to JSONL files conflicted

## Resolution Procedure

```bash
# 1. Accept remote version (theirs)
git checkout --theirs .beads/issues.jsonl

# 2. Import the remote state into local database
bd import -i .beads/issues.jsonl

# 3. Sync to reconcile any local changes
bd sync

# 4. Complete the rebase/merge
git add .beads/issues.jsonl
git rebase --continue  # or git merge --continue

# 5. Push
git push
```

## Why Accept Theirs

The JSONL file is an export format, not the source of truth. The beads database is the source of truth. By accepting the remote JSONL and importing it:

1. Local database receives all remote changes
2. `bd sync` re-exports with merged state
3. No manual conflict resolution needed in JSONL format

## Verification

After resolution:

```bash
bd list --status open  # Should show all expected issues
bd doctor              # Check for sync problems
git status             # Should be clean
```

## Prevention

Git hooks reduce conflict likelihood:

```bash
bd hooks install
```

Hooks auto-sync before commits and after merges, keeping JSONL in sync with database state.

## If Import Fails

If `bd import` reports errors:

```bash
# Check JSONL validity
cat .beads/issues.jsonl | head -5

# If corrupted, pull fresh from remote
git checkout origin/master -- .beads/issues.jsonl
bd import -i .beads/issues.jsonl
```
