use serde::Deserialize;

use crate::client::{ApiResponse, BASE_URL};

/// Waypoint information from /systems/:systemSymbol/waypoints/:waypointSymbol endpoint
#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Waypoint {
    pub symbol: String,
    #[serde(rename = "type")]
    pub waypoint_type: String,
    pub system_symbol: String,
    pub x: i32,
    pub y: i32,
    pub orbitals: Vec<WaypointOrbital>,
    pub traits: Vec<WaypointTrait>,
    pub is_under_construction: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub orbits: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub faction: Option<WaypointFaction>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub modifiers: Option<Vec<WaypointModifier>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    #[allow(dead_code)]
    pub chart: Option<Chart>,
}

/// Orbital information for a waypoint
#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct WaypointOrbital {
    pub symbol: String,
}

/// Trait information describing waypoint characteristics
#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct WaypointTrait {
    pub symbol: String,
    pub name: String,
    pub description: String,
}

/// Faction control information
#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct WaypointFaction {
    pub symbol: String,
}

/// Waypoint modifier information (structure TBD based on actual API response)
#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct WaypointModifier {
    pub symbol: String,
    pub name: String,
    pub description: String,
}

/// Chart information (structure TBD based on actual API response)
#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
#[allow(dead_code)]
pub struct Chart {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub waypoint_symbol: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub submitted_by: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub submitted_on: Option<String>,
}

impl Waypoint {
    /// Pretty-print waypoint information to console
    pub fn display(&self) {
        println!("\n=== Waypoint Information ===");
        println!("Symbol: {}", self.symbol);
        println!("Type: {}", self.waypoint_type);
        println!("System: {}", self.system_symbol);
        println!("Coordinates: ({}, {})", self.x, self.y);

        if let Some(orbits) = &self.orbits {
            println!("Orbits: {}", orbits);
        }

        if let Some(faction) = &self.faction {
            println!("Faction: {}", faction.symbol);
        }

        println!("Under Construction: {}", self.is_under_construction);

        if !self.orbitals.is_empty() {
            println!("\nOrbitals:");
            for orbital in &self.orbitals {
                println!("  - {}", orbital.symbol);
            }
        }

        if !self.traits.is_empty() {
            println!("\nTraits:");
            for trait_info in &self.traits {
                println!("  - {} ({})", trait_info.name, trait_info.symbol);
                println!("    {}", trait_info.description);
            }
        }

        if let Some(modifiers) = &self.modifiers {
            if !modifiers.is_empty() {
                println!("\nModifiers:");
                for modifier in modifiers {
                    println!("  - {} ({})", modifier.name, modifier.symbol);
                    println!("    {}", modifier.description);
                }
            }
        }
    }
}

/// Fetch waypoint information from /systems/:systemSymbol/waypoints/:waypointSymbol endpoint
///
/// # Arguments
/// * `agent_token` - The Bearer token for authentication
/// * `system_symbol` - The system symbol (e.g., "X1-DF55")
/// * `waypoint_symbol` - The waypoint symbol (e.g., "X1-DF55-20250Z")
///
/// # Returns
/// * `Ok(Waypoint)` - The waypoint information
/// * `Err` - If the request fails (invalid system, invalid waypoint, auth failure, etc.)
pub async fn fetch_waypoint(
    agent_token: &str,
    system_symbol: &str,
    waypoint_symbol: &str,
) -> Result<Waypoint, Box<dyn std::error::Error>> {
    let client = reqwest::Client::new();
    let url = format!("{}/systems/{}/waypoints/{}", BASE_URL, system_symbol, waypoint_symbol);

    let response = client
        .get(&url)
        .header("Content-Type", "application/json")
        .bearer_auth(agent_token)
        .send()
        .await?;

    let status = response.status();

    if !status.is_success() {
        let error_body = response.text().await?;
        return Err(format!("Failed to fetch waypoint ({}): {}", status, error_body).into());
    }

    let api_response: ApiResponse<Waypoint> = response.json().await?;
    Ok(api_response.data)
}
