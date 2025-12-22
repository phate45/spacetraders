use serde::{Deserialize, Serialize};

const BASE_URL: &str = "https://api.spacetraders.io/v2";

#[derive(Debug, Serialize)]
struct RegisterRequest {
    symbol: String,
    faction: String,
}

#[derive(Debug, Deserialize)]
struct RegisterResponse {
    data: RegisterData,
}

#[derive(Debug, Deserialize)]
struct RegisterData {
    token: String,
    agent: AgentData,
}

#[derive(Debug, Deserialize)]
struct AgentData {
    #[allow(dead_code)]
    account_id: Option<String>,
    symbol: String,
    #[allow(dead_code)]
    headquarters: String,
    #[allow(dead_code)]
    credits: i64,
    #[allow(dead_code)]
    starting_faction: String,
    #[allow(dead_code)]
    ship_count: i32,
}

/// Register a new agent with the SpaceTraders API
///
/// # Arguments
/// * `account_token` - The account token from ACCOUNT_TOKEN env variable
/// * `agent_symbol` - The symbol to register (e.g., "TANDEM_PILOT")
///
/// # Returns
/// * `Ok((token, symbol))` - The agent token and confirmed symbol
/// * `Err` - If registration fails
pub async fn register_agent(
    account_token: &str,
    agent_symbol: &str,
) -> Result<(String, String), Box<dyn std::error::Error>> {
    let client = reqwest::Client::new();
    let url = format!("{}/register", BASE_URL);

    let request_body = RegisterRequest {
        symbol: agent_symbol.to_string(),
        faction: "COSMIC".to_string(),
    };

    println!("Registering new agent with symbol: {}", agent_symbol);

    let response = client
        .post(&url)
        .header("Content-Type", "application/json")
        .bearer_auth(account_token)
        .json(&request_body)
        .send()
        .await?;

    let status = response.status();

    if !status.is_success() {
        let error_body = response.text().await?;
        return Err(format!("Registration failed ({}): {}", status, error_body).into());
    }

    let register_response: RegisterResponse = response.json().await?;

    println!("Successfully registered agent: {}", register_response.data.agent.symbol);
    println!("Starting credits: {}", register_response.data.agent.credits);
    println!("Headquarters: {}", register_response.data.agent.headquarters);

    Ok((register_response.data.token, register_response.data.agent.symbol))
}
