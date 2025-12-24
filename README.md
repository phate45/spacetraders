# SpaceTraders

A Rust client for the [SpaceTraders](https://spacetraders.io) API—a programmable fleet-management game played entirely through REST endpoints.

```
Stars guide cargo ships
Through the cosmic trade routes vast
Wealth among the void
```

## Current Status

**Early development.** The client handles agent registration and token lifecycle:

- Registers new agents via account token
- Persists agent tokens to `.spacetraders.toml`
- Fetches and displays agent information

## Requirements

- Rust (edition 2024)
- A SpaceTraders account token (set as `ACCOUNT_TOKEN` environment variable)

## Usage

```bash
# First run: registers agent and saves token
ACCOUNT_TOKEN=your_account_token cargo run

# Subsequent runs: uses saved token
cargo run
```

The client stores credentials in `.spacetraders.toml` (gitignored).

## Project Structure

```
.beads/              # Task tracking (beads issue tracker)
.claude/             # Claude Code agent configuration
├── agents/          # Specialized subagent definitions
├── hooks/           # Lifecycle hooks
├── output-styles/   # Response formatting
└── skills/          # Reusable skill definitions
plans/               # Implementation plans
scripts/             # Python utilities (uv)
src/
├── main.rs          # Entry point, token lifecycle orchestration
├── agent.rs         # Agent info fetching (/my/agent)
├── config.rs        # TOML config management
└── registration.rs  # Agent registration (/register)
```

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Core | Rust | API client, business logic |
| Scripts | Python (uv) | Automation, orchestration |
| Frontend | TypeScript (bun) | Visualizations (deferred) |

## License

MIT
