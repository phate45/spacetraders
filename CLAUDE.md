# spacetraders

@CLAUDE.local.md

## Project Overview

A SpaceTraders API client and automation project. SpaceTraders is a programmable fleet-management game accessed entirely through REST APIs.

**Tech Stack:**
- **Rust** - Core business logic, CLI client, API interactions
- **Python (uv)** - Scripting, automation, build orchestration
- **TypeScript (bun)** - Future frontend visualizations (deferred)

## Command Execution

**Unsure about working directory?** Run `pwd` first.

Do NOT use defensive patterns like `git -C /path` or `cd /path && git ...`—these break permission matching and trigger unnecessary approval prompts. Every time.

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
- **Lifecycle:** Created by `begin-work` script, removed after merge

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
