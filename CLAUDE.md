# spacetraders

@CLAUDE.local.md

## Project Overview

A SpaceTraders API client and automation project. SpaceTraders is a programmable fleet-management game accessed entirely through REST APIs.

**Tech Stack:**
- **Rust** - Core business logic, CLI client, API interactions
- **Python (uv)** - Scripting, automation, build orchestration
- **TypeScript (bun)** - Future frontend visualizations (deferred)

## API Reference

SpaceTraders API schemas are available locally:
- **Full reference:** `DOCS-REFERENCE.md` — endpoint listing, model descriptions
- **JSON schemas:** `api-docs/models/*.json` — 76 model definitions (Waypoint.json, Contract.json, etc.)
- **OpenAPI spec:** `api-docs/reference/SpaceTraders.json` — complete API definition

When implementing API endpoints, check these local schemas first before making test API calls.

## Command Execution

**Unsure about working directory?** Run `pwd` first.

**When filesystem commands behave unexpectedly** (directory should exist but `cd` returns "not found", file operations fail mysteriously): STOP. Run `pwd` and reorient yourself immediately. You may have drifted into an unexpected directory.

Do NOT use defensive patterns like `git -C /path` or `cd /path && git ...`—these break permission matching and trigger unnecessary approval prompts. Every time.

Do NOT chain commands with `&&` when the first command changes directory or state. Run them as separate Bash invocations instead.

**Scripts restriction:** Do NOT execute scripts in `scripts/` without explicit direction from Mark or a skill. These are project utilities that require intentional invocation.

```bash
# ✅ Correct - verify first, then run
pwd
git status

# ❌ Wrong - defensive patterns cause permission friction
git -C /home/phate/BigProjects/spacetraders status
cd /home/phate/BigProjects/spacetraders && git status
```

## Task Management with Beads

This project uses **bd (beads)** for task tracking. Do NOT use markdown TODOs or other tracking.

**IMPORTANT:** Always use `--json` at the end of each `bd` cli call for agent-friendly output.
Good: `bd ready --json`, `bd blocked --json`
Bad: `bd stats`, `bd list`

**Working directory:** `bd` finds the `.beads/` root automatically—run it directly without `cd`:
```bash
# ✅ Correct - bd works from anywhere
bd update spacetraders-935 --status review --json

# ❌ Wrong - unnecessary cd breaks permission matching
cd /path/to/worktree && bd update spacetraders-935 --status review --json
```

This differs from `git`, which requires the correct working directory.

### Quick Reference

```bash
bd ready                    # See available work (unblocked)
bd list --status in_progress  # Check active work
bd show <id>                # View issue details
bd comments <id>            # View issue comments
bd update <id> --status in_progress  # Claim work
bd close <id> -r "Reason"   # Complete work
bd sync                     # Sync with git
```

### Discovering Work

If you find bugs, TODOs, or follow-up work while implementing, use:
- `/discovering-issues` - Creates draft tasks for later refinement

## Worktrees

Agent work happens in isolated git worktrees:
- **Location:** `./worktrees/<task-id>` (e.g., `./worktrees/q4x`)
- **Branch naming:** `<type>/<id>` (e.g., `task/q4x`, `feature/abc`)

**Worktree path ↔ branch name correspondence:** The worktree directory name matches the task ID, which matches the branch name suffix. If you're looking for `worktrees/4dl.6`, the branch is `feature/4dl.6`. This redundancy helps verify you're in the right place.

**If worktree navigation fails:**
1. Run `ls /home/phate/BigProjects/spacetraders/worktrees/` to see what actually exists
2. Run `git worktree list` to see registered worktrees with their paths
3. Compare against expected task ID—typos happen (e.g., `4dl` vs `4dl.6`)

## Host Executor MCP

The `host-executor` MCP server is **ONLY** for `cargo` and `bun` commands. All other commands will be denied.

```
mcp__host-executor__execute_command
tool: cargo
args: "check"
worktree: "q4x"  # Optional: run in worktree
```

**Do NOT use host-executor for:**
- Shell commands (git, rg, fd, etc.) → Use Bash tool
- Python scripts → Use Bash tool
- `begin-work` → Use Bash tool

## Agent Workflow

If you are an agent working on a task:

1. **Invoke `/agent-working` skill FIRST** — This is your workflow entry point
2. All file writes MUST be within your assigned worktree
3. Use `bd update <id> --status review` when work is complete
