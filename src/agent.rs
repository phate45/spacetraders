use serde::Deserialize;

pub const BASE_URL: &str = "https://api.spacetraders.io/v2";

/// Generic API response wrapper that handles the data envelope
#[derive(Debug, Deserialize)]
pub struct ApiResponse<T> {
    pub data: T,
}

/// Agent information from /my/agent endpoint
#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Agent {
    pub account_id: Option<String>,
    pub symbol: String,
    pub headquarters: String,
    pub credits: i64,
    pub starting_faction: String,
    pub ship_count: i32,
}

impl Agent {
    /// Pretty-print agent information to console
    pub fn display(&self) {
        println!("\n=== Agent Information ===");
        println!("Symbol: {}", self.symbol);
        println!("Credits: {}", self.credits);
        println!("Headquarters: {}", self.headquarters);
        println!("Starting Faction: {}", self.starting_faction);
        println!("Ship Count: {}", self.ship_count);
        if let Some(account_id) = &self.account_id {
            println!("Account ID: {}", account_id);
        }
    }
}

/// Fetch agent information from /my/agent endpoint
///
/// # Arguments
/// * `agent_token` - The Bearer token for authentication
///
/// # Returns
/// * `Ok(Agent)` - The agent information
/// * `Err` - If the request fails
pub async fn fetch_agent(agent_token: &str) -> Result<Agent, Box<dyn std::error::Error>> {
    let client = reqwest::Client::new();
    let url = format!("{}/my/agent", BASE_URL);

    let response = client
        .get(&url)
        .header("Content-Type", "application/json")
        .bearer_auth(agent_token)
        .send()
        .await?;

    let status = response.status();

    if !status.is_success() {
        let error_body = response.text().await?;
        return Err(format!("Failed to fetch agent ({}): {}", status, error_body).into());
    }

    let api_response: ApiResponse<Agent> = response.json().await?;
    Ok(api_response.data)
}
