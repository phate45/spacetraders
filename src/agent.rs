use anyhow::Result;
use serde::Deserialize;

use crate::client::SpaceTradersClient;

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
/// * `client` - The SpaceTraders API client
///
/// # Returns
/// * `Ok(Agent)` - The agent information
/// * `Err` - If the request fails
pub async fn fetch_agent(client: &SpaceTradersClient) -> Result<Agent> {
    client.get("/my/agent").await
}
