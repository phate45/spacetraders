# Plan: CLI Integration

## Summary

Add argh-based CLI layer over existing SpaceTraders API implementation. Four command groups: `config`, `agent`, `waypoint`, `contract`. Pretty output by default, `--json` flag for machine-readable output (implementation separated into distinct phases).

## Motivation

Current `main.rs` auto-executes a sequence of read-only API calls. This works for demos but not for interactive use. A proper CLI structure enables:
- Selective command execution (don't call all endpoints every time)
- Action commands that require explicit user intent (accept contract, negotiate)
- Machine-readable output for scripting and agent integration
- Extensibility for future commands (ships, navigation, etc.)

## Files

**Create:**
- `src/cli.rs` - CLI structs and command dispatch

**Modify:**
- `Cargo.toml` - Add argh dependency
- `src/main.rs` - Replace hardcoded flow with CLI dispatch
- `src/config.rs` - Add methods for listing/getting config values
- `src/agent.rs` - Add `Serialize` derive for JSON output
- `src/waypoint.rs` - Add `Serialize` derive for JSON output
- `src/contracts.rs` - Add `Serialize` derive for JSON output

## Phases

### Phase 1: CLI Skeleton

**Description:**
Add argh dependency and create CLI module with top-level structure. This establishes the command/subcommand pattern that all other phases build on.

**Design:**
- Add `argh = "0.1"` to Cargo.toml
- Create `src/cli.rs` with:
  - `TopLevel` struct: `--json` flag + `#[argh(subcommand)]` field
  - `Command` enum: `Config`, `Agent`, `Waypoint`, `Contract` variants
  - Placeholder structs for each command group
- Update `main.rs` to parse args and stub dispatch
- Note: argh requires `--json` BEFORE subcommand: `spacetraders --json config list`

**Acceptance Criteria:**
- `cargo check` passes
- `spacetraders --help` shows top-level help with command list
- `spacetraders config --help` shows "not implemented" or placeholder
- CLI skeleton established for subsequent phases

### Phase 2: Config Command

**Description:**
Implement `config list` and `config get <key>` subcommands for inspecting `.spacetraders.toml`.

**Design:**
- Add `ConfigCommand` enum with `List` and `Get` variants
- `config list`: Display all config keys and values (mask token)
- `config get <key>`: Display specific key value
  - Valid keys: `agent_token`, `agent_symbol`
  - Error on invalid key
- Reuse existing `Config::load()` from `config.rs`

**Acceptance Criteria:**
- `spacetraders config list` shows all config values with masked token
- `spacetraders config get agent_symbol` shows agent symbol
- `spacetraders config get invalid_key` shows error
- No API calls made (config is local)

### Phase 3: Agent Command

**Description:**
Implement `agent info` and `agent register` subcommands. This wraps `fetch_agent()` and `SpaceTradersClient::register()`.

**Design:**
- Add `AgentCommand` enum with `Info` and `Register` variants
- `agent info`: Call `fetch_agent()`, display with existing `Agent::display()`
- `agent register`:
  - Accept `--symbol <name>` option (default: prompt or error if missing)
  - Require `ACCOUNT_TOKEN` env var
  - Call `SpaceTradersClient::register()`
  - Save token to config
- Both commands need config for token/saving

**Acceptance Criteria:**
- `spacetraders agent info` displays agent information
- `spacetraders agent register --symbol PILOT_NAME` registers new agent
- Agent info shows error if no token configured
- Registration saves token to `.spacetraders.toml`

### Phase 4: Waypoint Command

**Description:**
Implement `waypoint info [system] [waypoint]` subcommand with optional arguments defaulting to headquarters.

**Design:**
- Add `WaypointCommand` enum with `Info` variant
- `waypoint info`:
  - If both args provided: fetch that waypoint
  - If no args: fetch agent first, extract HQ, fetch HQ waypoint
  - System symbol derived from waypoint (strip last segment)
- Use existing `fetch_waypoint()` and `Waypoint::display()`

**Acceptance Criteria:**
- `spacetraders waypoint info` shows headquarters waypoint
- `spacetraders waypoint info X1-DF55 X1-DF55-20250Z` shows specific waypoint
- Error if waypoint not found
- Error if no token configured

### Phase 5: Contract Command

**Description:**
Implement `contract list`, `contract accept <id>`, `contract negotiate <ship>` subcommands.

**Design:**
- Add `ContractCommand` enum with `List`, `Accept`, `Negotiate` variants
- `contract list`: Call `list_contracts()`, display each with `Contract::display()`
- `contract accept <id>`: Call `accept_contract()`, display updated contract
- `contract negotiate <ship>`: Call `negotiate_contract()`, display new contract
- Use existing functions from `contracts.rs`

**Acceptance Criteria:**
- `spacetraders contract list` shows all contracts
- `spacetraders contract accept CONTRACT_ID` accepts and displays contract
- `spacetraders contract negotiate SHIP_SYMBOL` negotiates and displays new contract
- Appropriate errors for invalid IDs, missing ships, already accepted, etc.

### Phase 6: JSON Flag Plumbing

**Description:**
Wire the `--json` flag through the command dispatch so commands can conditionally output JSON.

**Design:**
- `TopLevel.json` flag already exists from Phase 1
- Pass flag through to command execution context
- Create `OutputFormat` enum or simple bool
- Commands receive format preference but don't implement JSON yet
- Prepare for Phase 7 implementation

**Acceptance Criteria:**
- `--json` flag is parsed and propagated to command handlers
- Commands still output pretty format (JSON impl in Phase 7)
- No regression in existing functionality
- Foundation ready for JSON output

**Parallel:** no (depends on Phase 1-5)

### Phase 7: JSON Output

**Description:**
Add `Serialize` derives to model structs and implement JSON output branch in display logic.

**Design:**
- Add `serde::Serialize` derive to: `Agent`, `Contract`, `ContractTerms`, `ContractPayment`, `ContractDeliverGood`, `Waypoint`, `WaypointTrait`, `WaypointOrbital`, `WaypointFaction`, `WaypointModifier`, `Config`
- In each command handler, check output format:
  - Pretty: Use existing `display()` methods
  - JSON: Use `serde_json::to_string_pretty()` and print
- Config output as JSON object with masked token

**Acceptance Criteria:**
- `spacetraders --json agent info` outputs valid JSON
- `spacetraders --json contract list` outputs JSON array
- `spacetraders --json config list` outputs JSON object
- All commands support `--json` flag
- JSON output parseable by jq

**Parallel:** no (depends on Phase 6)
