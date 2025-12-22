# Plan: Hit /my/agent Endpoint

**Goal:** Working code that manages agent token lifecycle and fetches agent info.

---

## Decisions

| Decision | Choice |
|----------|--------|
| Config format | TOML (add `toml` crate) |
| Agent symbol | `TANDEM_PILOT` |
| Config file | `.spacetraders.toml` (gitignored) |

---

## Token Model

| Token | Purpose | Lifetime | Source |
|-------|---------|----------|--------|
| ACCOUNT_TOKEN | Register new agents | Persistent | Env var |
| AGENT_TOKEN | All API calls | Weekly (server reset) | Config file |

**Flow:** Check config for AGENT_TOKEN → if missing, use ACCOUNT_TOKEN to register `TANDEM_PILOT` → store token → proceed.

---

## Tasks

### 1. Set up dependencies + minimal test
**Files:** `Cargo.toml`, `src/main.rs`

- Add deps: tokio, reqwest (json), serde (derive), serde_json, toml
- Minimal `cargo run` hitting `GET /` (server status, no auth)
- Validates HTTP stack works

### 2. Implement config file with token management
**Files:** `src/main.rs` (or `src/config.rs`), `.spacetraders.toml`, `.gitignore`

- TOML config with `agent_token` and `agent_symbol` fields
- On startup: load config, check for token
- If missing: read ACCOUNT_TOKEN from env, POST `/register` with symbol `TANDEM_PILOT`
- Store returned agent token to config file
- Add `.spacetraders.toml` to `.gitignore`

### 3. Implement /my/agent fetch and response logging
**Files:** `src/main.rs`

- Define Agent struct matching API response
- GET `/my/agent` with Bearer token from config
- Pretty-print agent info

---

## Endpoint Reference

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/` | GET | None | Server status (test) |
| `/register` | POST | Bearer ACCOUNT_TOKEN | Create agent, get AGENT_TOKEN |
| `/my/agent` | GET | Bearer AGENT_TOKEN | Fetch agent details |

---

## Beads Tasks (to create)

```
1. [task] P2 "Set up HTTP deps and validate with server status endpoint"
   - No blockers

2. [task] P2 "Implement TOML config and token lifecycle management"
   - Blocked by #1

3. [task] P2 "Implement /my/agent fetch and response logging"
   - Blocked by #2
```

---

## Success Criteria

- [ ] `cargo run` with empty config auto-registers TANDEM_PILOT
- [ ] Token persisted to `.spacetraders.toml`
- [ ] Subsequent runs reuse stored token
- [ ] Agent info (symbol, credits, HQ, ships) printed to console
- [ ] No secrets in git
