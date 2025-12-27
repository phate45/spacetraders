# Plan: Centralize API Client Architecture

## Summary

Refactor scattered reqwest client usage into a unified `SpaceTradersClient` struct. Eliminates ~120 lines of duplicated HTTP boilerplate across 6 functions, centralizes authentication, and migrates error handling from `Box<dyn Error>` to `anyhow`.

## Motivation

The codebase creates 5+ fresh `reqwest::Client` instances per request cycle, with identical boilerplate for headers, auth, status checking, and error handling repeated in every API function. Before adding CLI commands and more endpoints, the foundation needs to be clean.

**Goals:**
- Single reusable HTTP client
- Centralized auth token handling
- Consistent error handling with context
- Domain functions reduced to 2-3 lines each

## Files

**Create:**
- `src/client.rs` - SpaceTradersClient, ApiResponse<T>, BASE_URL

**Modify:**
- `Cargo.toml` - Add anyhow dependency
- `src/main.rs` - Create client, pass to functions, update error handling
- `src/agent.rs` - Remove BASE_URL/ApiResponse, refactor fetch_agent
- `src/waypoint.rs` - Refactor fetch_waypoint
- `src/contracts.rs` - Refactor 3 contract functions

**Delete:**
- `src/registration.rs` - Move register() to SpaceTradersClient::register()

## Phases

### Phase 1: Foundation

**Description:**
Add anyhow dependency and create the new client module without breaking existing code. This establishes the new infrastructure alongside the old.

**Design:**
Create `src/client.rs` with:
- `BASE_URL` constant
- `ApiResponse<T>` generic wrapper (moved from agent.rs)
- `SpaceTradersClient` struct with `client: Client` and `token: String` fields
- Methods: `new()`, `get<T>()`, `post<T>()`, `post_json<T, B>()`, `handle_response<T>()`
- Static method: `register()` for agent registration (no token required)

```rust
impl SpaceTradersClient {
    pub fn new(token: impl Into<String>) -> Self
    pub async fn register(account_token: &str, symbol: &str) -> Result<(String, String)>
    pub async fn get<T: DeserializeOwned>(&self, path: &str) -> Result<T>
    pub async fn post<T: DeserializeOwned>(&self, path: &str) -> Result<T>
    pub async fn post_json<T, B: Serialize>(&self, path: &str, body: &B) -> Result<T>
}
```

Add `mod client;` to main.rs but don't use it yet.

**Acceptance Criteria:**
- `anyhow = "1"` in Cargo.toml
- `src/client.rs` exists with full implementation
- `cargo check` passes
- Existing code unchanged and functional

### Phase 2: Migrate agent.rs

**Description:**
Refactor fetch_agent to use SpaceTradersClient. This is the first migration, establishing the pattern for other modules.

**Design:**
- Change signature: `fetch_agent(token: &str)` → `fetch_agent(client: &SpaceTradersClient)`
- Replace 20-line body with: `client.get("/my/agent").await`
- Remove `BASE_URL` and `ApiResponse<T>` from agent.rs (now in client.rs)
- Keep `Agent` struct and `impl Agent` display method
- Update main.rs to create client and pass to fetch_agent

**Acceptance Criteria:**
- fetch_agent uses client parameter
- No duplicate BASE_URL in agent.rs
- main.rs creates SpaceTradersClient instance
- `cargo check` passes

### Phase 3: Migrate waypoint.rs

**Description:**
Refactor fetch_waypoint to use SpaceTradersClient.

**Design:**
- Change signature to take `client: &SpaceTradersClient`
- Replace body with path formatting + `client.get(&path).await`
- Remove imports from agent.rs
- Update main.rs call site

**Acceptance Criteria:**
- fetch_waypoint uses client parameter
- No imports from agent.rs
- `cargo check` passes

### Phase 4: Migrate contracts.rs

**Description:**
Refactor all three contract functions (list_contracts, accept_contract, negotiate_contract) to use SpaceTradersClient.

**Design:**
- Update all three function signatures to take `client: &SpaceTradersClient`
- list_contracts: `client.get("/my/contracts").await`
- accept_contract: `client.post(&path).await` (POST with no body)
- negotiate_contract: `client.post(&path).await`
- Handle nested response types where needed (some endpoints return `{ contract: Contract }`)
- Remove imports from agent.rs

**Acceptance Criteria:**
- All three functions use client parameter
- No imports from agent.rs
- `cargo check` passes

### Phase 5: Migrate registration and cleanup

**Description:**
Delete registration.rs (function moved to SpaceTradersClient::register), migrate config.rs to anyhow, and remove all Box<dyn Error> from codebase.

**Design:**
- Delete `src/registration.rs`
- Remove `mod registration;` from main.rs
- Update main.rs registration flow to use `SpaceTradersClient::register()`
- Update Config::load() and Config::save() to return `anyhow::Result`
- Update main() return type to `anyhow::Result<()>`
- Search for remaining `Box<dyn std::error::Error>` and eliminate

**Acceptance Criteria:**
- registration.rs deleted
- No `Box<dyn Error>` in codebase
- All functions return `anyhow::Result<T>`
- `cargo check` passes
- `cargo clippy` clean
- `cargo run` works end-to-end

## Before/After

**Before (fetch_agent - 20 lines):**
```rust
pub async fn fetch_agent(agent_token: &str) -> Result<Agent, Box<dyn std::error::Error>> {
    let client = reqwest::Client::new();
    let url = format!("{}/my/agent", BASE_URL);
    let response = client.get(&url)
        .header("Content-Type", "application/json")
        .bearer_auth(agent_token)
        .send().await?;
    let status = response.status();
    if !status.is_success() {
        let error_body = response.text().await?;
        return Err(format!("Failed to fetch agent ({}): {}", status, error_body).into());
    }
    let api_response: ApiResponse<Agent> = response.json().await?;
    Ok(api_response.data)
}
```

**After (fetch_agent - 3 lines):**
```rust
pub async fn fetch_agent(client: &SpaceTradersClient) -> Result<Agent> {
    client.get("/my/agent").await
}
```
