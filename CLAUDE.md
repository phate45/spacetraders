# spacetraders

@/home/phate/BigProjects/spacetraders/CLAUDE.local.md

## Project Overview

A SpaceTraders API client and automation project. SpaceTraders is a programmable fleet-management game accessed entirely through REST APIs.

**Tech Stack:**
- **Rust** - Core business logic, CLI client, API interactions
- **Python (uv)** - Scripting, automation, build orchestration
- **TypeScript (bun)** - Future frontend visualizations (deferred)

## Task Management with Beads

This project uses **bd (beads)** for task tracking. Do NOT use markdown TODOs or other tracking.

### Session Start
```bash
bd ready                    # See available work
bd list --status in_progress  # Check active work
bd show <id>                # Read context/notes
```

### During Work
- Always include `--description` when creating issues
- Use `--deps discovered-from:<id>` when finding work during other work
- Update status: `bd update <id> --status in_progress`

### Session End (Landing the Plane)
```bash
# 1. Create issues for remaining work
bd create "Title" -t task -p 2 -d "Description"

# 2. Update/close issues
bd close <id> -r "Completed"

# 3. Sync to git (MANDATORY)
bd sync

# 4. Verify
git status  # Should show up to date
```

### Priority Scale
- `0` - Critical (security, data loss)
- `1` - High (major features, important bugs)
- `2` - Medium (default)
- `3` - Low (polish)
- `4` - Backlog

## Agent Architecture

**Control Tower Mode**: Use `/output-style control-tower` for orchestration mode.

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
- Reference: `~/Documents/second-brain/03_Resources/Programming/Rust/Rust 2024 Edition Reference.md`
- Run `cargo check`, `cargo test`, `cargo clippy` before commits

## Project Notes

Research and work logs: `/home/phate/Documents/second-brain/01_Projects/spacetraders/`

Key documents:
- `Claude Code Configuration Research.md` - Comprehensive reference on agents, output styles, skills, .claude/rules
- `logs/YYYY-MM-DD.md` - Daily work logs

## Utilities

**Beads installer** (`scripts/install_beads.py`):
```bash
python scripts/install_beads.py          # Install or upgrade
python scripts/install_beads.py --check  # Check if update available
python scripts/install_beads.py --force  # Force reinstall
```
