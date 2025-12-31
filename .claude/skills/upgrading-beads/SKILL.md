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

**For JSON output**, filter to show only non-ok checks (preserves top-level fields):
```bash
bd doctor --json 2>/dev/null | jq '.checks = [.checks[] | select(.status != "ok")]'
```

**Fallback:** If the `!=` operator causes escaping issues in certain execution contexts, use positive matching instead:
```bash
bd doctor --json 2>/dev/null | jq '.checks | map(select(.status == "warning" or .status == "error" or .status == "fail"))'
```

**Ignore these warnings** (local divergence from author's expectations):
- `Claude Plugin: beads plugin not installed`
- `Claude Integration: Not configured`
- `Issues Tracking: issues.jsonl is ignored by git` — expected with sync-branch workflow
- `DB-JSONL Sync: Count mismatch` — transient; resolves after `bd sync`

**Surface to Mark** any other warnings or failures. If the changelog review (step 2 or 4) has relevant context for the issue, include it.

**Do NOT run `bd doctor --fix`** — it's interactive and requires Mark's input.

### 7. Apply Config Updates

New beads versions may require updates to `.beads/.gitignore` or `.beads/config.yaml`.

**Check for missing gitignore patterns:**
```bash
# Doctor will report "Outdated .beads/.gitignore" if patterns are missing
# Common additions: redirect (v0.42.0+)
```

**Verify sync-branch config:**
```bash
bd config get sync-branch --json
# Should return: "value": "beads-sync"
```

If config changes are needed, apply them and **commit before running `bd sync`**:

```bash
# Example: add redirect pattern
echo "redirect" >> .beads/.gitignore

# Example: set sync-branch (use hyphen, not dot)
bd config set sync.branch beads-sync

# CRITICAL: Commit before sync
git add .beads/.gitignore .beads/config.yaml
git commit -m "chore(beads): post-upgrade config updates"

# Now safe to sync
bd sync
```

> **⚠️ Warning:** Local changes to `.beads/` files get overwritten by `bd sync` if not committed first. The sync-branch workflow pulls from beads-sync, which can clobber uncommitted local changes.

### 8. Conclude

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

## Troubleshooting

> **Note:** Troubleshooting steps that modify `issues.jsonl` require Mark's approval. Surface the diagnosis to Mark and let him execute the fix.

### DB-JSONL Count Mismatch

`bd doctor` reports database and JSONL have different issue counts.

**Diagnose:** Identify specific missing entries:
```bash
diff <(bd export | jq -r '.id' | sort) <(cat .beads/issues.jsonl | jq -r '.id' | sort)
```

**Common causes:**
1. **Missing issue in JSONL:** Append from export, commit before `bd sync` can overwrite
2. **Tombstones:** Use `bd compact --prune` to remove soft-deleted entries
3. **Sync branch divergence:** See "Sync Branch Circular Conflict" below

**Escalate to Mark** with the diff output and let him decide the resolution.

### Custom Status Validation Failure

Fresh DB import fails with `invalid status: draft` (or other custom status).

**Cause:** Custom statuses stored in DB config, not `config.yaml`. Fresh DB lacks setting.

**Fix:**
```bash
bd config set status.custom "draft,review"
bd import -i .beads/issues.jsonl
```

**Finding custom statuses from old DB:**
```bash
bd --db /tmp/old-beads.db config list --json | jq 'to_entries[] | select(.key | contains("status"))'
```

### Sync Branch Circular Conflict

`bd sync` keeps pulling stale data from beads-sync branch, reintroducing mismatches after every fix attempt.

**Cause:** beads-sync branch diverged from master. Content-level merge produces inconsistent results.

**Nuclear fix (Mark only):** Directly update the sync worktree, bypassing merge:
```bash
# Export clean state
bd export > .beads/issues.jsonl

# Copy to sync worktree (location: .git/beads-worktrees/beads-sync/.beads/)
cp .beads/issues.jsonl .git/beads-worktrees/beads-sync/.beads/issues.jsonl

# Commit and push from worktree
cd .git/beads-worktrees/beads-sync
git add .beads/issues.jsonl && git commit -m "fix: sync JSONL with master" && git push

# Return to main project
cd /home/phate/BigProjects/spacetraders
bd sync
```

**Warning:** After `cd` into worktree, beads commands operate on wrong project. Always run `pwd` before beads commands.

**Escalate to Mark** if you detect this pattern — do not attempt the nuclear fix autonomously.

### Sync Restoring Stale Data from Master

`bd sync` overwrites good local JSONL with stale data. Working copy keeps reverting to fewer issues than the database has.

**Symptoms:**
- After sync, JSONL has fewer lines than before
- `bd doctor` shows DB-JSONL count mismatch immediately after sync
- Sync worktree has correct data, but main JSONL doesn't update

**Cause:** `issues.jsonl` was historically committed to master. When sync pulls, git restores the stale committed version over uncommitted changes.

**Root cause fix:** Remove `issues.jsonl` from master's history entirely, making beads-sync the sole owner.

**High-level procedure:**
1. Update `.beads/.gitignore` to ignore `issues.jsonl` and `interactions.jsonl`
2. Commit the gitignore change
3. Run `git filter-repo --path .beads/issues.jsonl --path .beads/interactions.jsonl --invert-paths --force`
4. Re-add origin remote (filter-repo removes it)
5. Create backup branches from origin refs
6. Commit existing worktree files to beads-sync
7. Re-init database with custom statuses
8. Verify with `bd sync` and `bd doctor`

**Full details:** See vault work log:
`/home/phate/Documents/second-brain/01_Projects/spacetraders/logs/2025-12-30.md`
Section: "Beads Upgrade and History Cleanup"

### AGENTS.md Created During Troubleshooting

`bd init` creates an `AGENTS.md` file in the project root with landing-the-plane instructions.

**If this appears during troubleshooting:** Delete it — we have our own agent workflow documentation.

```bash
rm AGENTS.md
```

### Full Troubleshooting Reference

For detailed walkthrough with context, see vault work logs:
- `logs/2025-12-27.md` — "Beads Upgrade and DB-JSONL Sync Troubleshooting"
- `logs/2025-12-30.md` — "Beads Upgrade and History Cleanup" (filter-repo procedure)

## CLI Notes

- `bd sync` does **not** have `--json` output
- `bd doctor --fix` is interactive — do not run without Mark

## Hands-Off Rules

**Do NOT proactively run commands that overwrite `issues.jsonl`:**
- `bd export > .beads/issues.jsonl` — potentially destructive
- Direct file manipulation of `.beads/issues.jsonl`

These commands can cause data loss if the DB and JSONL have diverged. Surface the issue to Mark and let him decide how to resolve.

**Safe commands:**
- `bd sync` — handles export/import with conflict detection
- `bd doctor` (without `--fix`) — read-only diagnostics

## Quick Reference

```bash
# Check only
python3 scripts/install_beads.py --check

# Full upgrade
python3 scripts/install_beads.py

# Force reinstall
python3 scripts/install_beads.py --force
```
