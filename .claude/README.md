# Claude Code Configuration

This directory configures Claude Code to operate as a **Control Tower**—an orchestration layer that manages work through task graphs and agent delegation rather than direct implementation.

## Architecture

```
Control Tower (main Claude instance)
├── Delegates to specialized subagents
├── Tracks work in beads (.beads/)
└── Maintains session continuity via notes and logs
```

The Control Tower doesn't write code directly. It plans, delegates, and synthesizes.

## Directory Structure

### `agents/`
Subagent definitions for specialized work:
- **rust-implementer** — Rust code implementation (has 2024 edition context)
- **task-executor** — Non-code tasks (docs, config, research)

### `hooks/`
Lifecycle hooks that run at specific events:
- **load-control-tower-context.sh** — Injects Control Tower context at session start

### `output-styles/`
Response formatting configurations:
- **control-tower.md** — Defines orchestration behavior and session protocols

### `skills/`
Reusable skill definitions invoked via `/skill-name`:
- **agent-working** — Core workflow for subagents executing tasks
- **beads** — Task tracking with dependency graphs
- **creating-tasks** — Issue creation with proper descriptions
- **discovering-issues** — Logging work found during other work
- **landing-the-plane** — Session-end protocol
- **writing-work-logs** — Work session documentation

### `plans/`
Implementation plans generated during planning mode.

## Key Files

| File | Purpose |
|------|---------|
| `settings.json` | Permissions, hooks, MCP servers (committed) |
| `settings.local.json` | Local overrides (gitignored) |
| `control-tower-context.md` | Communication style, collaboration guidelines |

## How It Works

1. **Session Start**: Hook loads Control Tower context, `session-start.py` reports task graph state
2. **During Work**: Control Tower creates beads tasks, delegates to agents, tracks progress
3. **Session End**: Update notes, write work log, sync beads, push to remote
