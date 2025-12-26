---
name: upgrading-beads
description: Full beads CLI upgrade workflow. Use when checking for updates, performing upgrades, or when beads behavior seems off.
---

# Upgrading Beads

Complete workflow for checking and upgrading the beads CLI tool.

## Upgrade Workflow

### 1. Check for Updates

```bash
python3 scripts/install_beads.py --check
```

Shows installed version, latest version, and whether update is available.

If no update available, stop here. Otherwise note the version range for changelog review.

### 2. Review Changelog (If /tmp/beads Exists)

Check if local beads repo exists:

```bash
test -d /tmp/beads && echo "exists" || echo "missing"
```

**If exists:** Pull latest and dispatch Explore agent for changelog analysis:

```bash
git -C /tmp/beads pull
```

Then dispatch Explore agent with prompt:
```
Check the beads changelog for versions <current> through <latest>.
Use `rg "^#+" /tmp/beads/CHANGELOG.md` to get section line offsets.
Read only the relevant version sections (file is 3k+ lines).
Report: breaking changes, new features, deprecations.
```

**If missing:** Stop and report to Mark. Wait for him to reacquire the repo before continuing.

### 3. Run Upgrade

```bash
python3 scripts/install_beads.py
```

### 4. Check What Changed

```bash
bd info --whats-new --json | jq '.recent_changes[:5]'
```

Review recent changes for breaking changes or new features.

### 5. Update Git Hooks

```bash
bd hooks install
```

Hooks provide automatic sync between database and JSONL:

| Hook | Purpose |
|------|---------|
| `pre-commit` | Flushes pending changes before commit |
| `post-merge` | Imports updated JSONL after pull/merge |
| `pre-push` | Exports database to JSONL before push |
| `post-checkout` | Imports JSONL after branch checkout |

**Why hooks matter**: Without hooks, you can commit database changes locally but push stale JSONL to remote, causing sync issues.

### 6. Verify Installation

```bash
bd doctor
```

Checks for common issues (sync problems, missing hooks).

**Ignore these warnings** (local divergence from author's expectations):
- `Sync Branch Config: sync-branch not configured`
- `Claude Plugin: beads plugin not installed`
- `Claude Integration: Not configured`

**Surface to Mark** any other warnings or failures. If the changelog review (step 2 or 4) has relevant context for the issue, include it.

### 7. Conclude

Provide synthesis of:
1. Version jump (from → to)
2. Breaking changes affecting our usage
3. New features of interest
4. Any doctor issues that required resolution

## When to Use This Skill

- Periodic upgrade checks
- When beads commands behave unexpectedly
- When hooks seem to not fire
- After manual beads binary update

## Quick Reference

```bash
# Check only
python3 scripts/install_beads.py --check

# Full upgrade
python3 scripts/install_beads.py

# Force reinstall
python3 scripts/install_beads.py --force
```
