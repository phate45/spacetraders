# spacetraders

@CLAUDE.local.md

## Project Overview

A SpaceTraders API client and automation project. SpaceTraders is a programmable fleet-management game accessed entirely through REST APIs.

**Tech Stack:**
- **Rust** - Core business logic, CLI client, API interactions
- **Python (uv)** - Scripting, automation, build orchestration
- **TypeScript (bun)** - Future frontend visualizations (deferred)

## Task Management with Beads

This project uses **bd (beads)** for task tracking. Do NOT use markdown TODOs or other tracking.

**IMPORTANT:** Always use `--json` at the end of each `bd` cli call for agent-friendly output.
Good: `bd ready --json`, `bd blocked --json`
Bad: `bd stats`, `bd list`

### Quick Reference

```bash
bd ready                    # See available work (unblocked)
bd list --status in_progress  # Check active work
bd show <id>                # View issue details
bd update <id> --status in_progress  # Claim work
bd close <id> -r "Reason"   # Complete work
bd sync                     # Sync with git
```

### Creating Issues

Use skills for proper issue creation:
- `/creating-tasks` - New tasks with good descriptions
- `/discovering-issues` - Work found during other work

### Priority Scale
- `0` - Critical (security, data loss)
- `1` - High (major features, important bugs)
- `2` - Medium (default)
- `3` - Low (polish)
- `4` - Backlog

## Agent Architecture

**Available Agents** (in `.claude/agents/`):
- `rust-implementer` - Rust code implementation (has 2024 edition context)
- `task-executor` - Non-code tasks (docs, config, research)

**Built-in Agents** (via Task tool `subagent_type`):
- `Explore` - Codebase exploration and context gathering (use before task creation)
- `Plan` - Implementation planning
- `claude-code-guide` - Claude Code documentation lookup

**Delegation Pattern**: Create beads task → Delegate to appropriate agent → Agent reports completion

## Rust Standards

- Edition 2024 (`edition = "2024"` in Cargo.toml)
- Run `cargo check`, `cargo test`, `cargo clippy` before commits

## Utilities

**Beads installer** (`scripts/install_beads.py`):
```bash
python scripts/install_beads.py          # Install or upgrade
python scripts/install_beads.py --check  # Check if update available
python scripts/install_beads.py --force  # Force reinstall
```
