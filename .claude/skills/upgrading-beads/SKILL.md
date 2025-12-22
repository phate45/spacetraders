---
name: upgrading-beads
description: Post-upgrade tasks after updating beads CLI. Use after running install_beads.py or when beads behavior seems off.
---

# Upgrading Beads

After upgrading the beads CLI tool, perform these steps to ensure proper operation.

## Post-Upgrade Checklist

### 1. Check What Changed

```bash
bd info --whats-new
```

Review release notes for breaking changes or new features.

### 2. Restart Daemons

```bash
bd daemons killall
```

Old daemon processes may have stale code. Killing them forces restart with new version.

### 3. Update Git Hooks

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

### 4. Verify Installation

```bash
bd doctor
```

Checks for common issues (sync problems, missing hooks, daemon status).

## When to Use This Skill

- After running `python scripts/install_beads.py`
- After manual beads binary update
- When beads commands behave unexpectedly
- When hooks seem to not fire

## Upgrade Script

This project includes an upgrade helper:

```bash
python scripts/install_beads.py          # Install or upgrade
python scripts/install_beads.py --check  # Check if update available
python scripts/install_beads.py --force  # Force reinstall
```
