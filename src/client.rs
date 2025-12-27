use anyhow::{Context, Result};
use reqwest::{Client, Response};
use serde::{de::DeserializeOwned, Deserialize, Serialize};

pub const BASE_URL: &str = "https://api.spacetraders.io/v2";

/// Generic API response wrapper that handles the data envelope
#[derive(Debug, Deserialize)]
pub struct ApiResponse<T> {
    pub data: T,
}

/// SpaceTraders API client with authentication
pub struct SpaceTradersClient {
    client: Client,
    token: String,
}

impl SpaceTradersClient {
    /// Create a new API client with the given authentication token
    ///
    /// # Arguments
    /// * `token` - The Bearer token for authentication
    pub fn new(token: String) -> Self {
        Self {
            client: Client::new(),
            token,
        }
    }

    /// Make a GET request to the API
    ///
    /// # Arguments
    /// * `path` - The API path (e.g., "/my/agent")
    ///
    /// # Returns
    /// * `Ok(T)` - The deserialized response data
    /// * `Err` - If the request fails
    pub async fn get<T: DeserializeOwned>(&self, path: &str) -> Result<T> {
        let url = format!("{}{}", BASE_URL, path);
        let response = self
            .client
            .get(&url)
            .header("Content-Type", "application/json")
            .bearer_auth(&self.token)
            .send()
            .await
            .context("Failed to send GET request")?;

        self.handle_response(response).await
    }

    /// Make a POST request to the API without a body
    ///
    /// # Arguments
    /// * `path` - The API path
    ///
    /// # Returns
    /// * `Ok(T)` - The deserialized response data
    /// * `Err` - If the request fails
    pub async fn post<T: DeserializeOwned>(&self, path: &str) -> Result<T> {
        let url = format!("{}{}", BASE_URL, path);
        let response = self
            .client
            .post(&url)
            .header("Content-Type", "application/json")
            .bearer_auth(&self.token)
            .send()
            .await
            .context("Failed to send POST request")?;

        self.handle_response(response).await
    }

    /// Make a POST request with a JSON body
    ///
    /// # Arguments
    /// * `path` - The API path
    /// * `body` - The request body to serialize as JSON
    ///
    /// # Returns
    /// * `Ok(T)` - The deserialized response data
    /// * `Err` - If the request fails
    pub async fn post_json<T: DeserializeOwned, B: Serialize>(
        &self,
        path: &str,
        body: &B,
    ) -> Result<T> {
        let url = format!("{}{}", BASE_URL, path);
        let response = self
            .client
            .post(&url)
            .header("Content-Type", "application/json")
            .bearer_auth(&self.token)
            .json(body)
            .send()
            .await
            .context("Failed to send POST request with JSON body")?;

        self.handle_response(response).await
    }

    /// Handle the API response and extract the data field
    ///
    /// # Arguments
    /// * `response` - The HTTP response from the API
    ///
    /// # Returns
    /// * `Ok(T)` - The deserialized data from the response
    /// * `Err` - If the response indicates failure or cannot be parsed
    async fn handle_response<T: DeserializeOwned>(&self, response: Response) -> Result<T> {
        let status = response.status();

        if !status.is_success() {
            let error_body = response
                .text()
                .await
                .unwrap_or_else(|_| "<unable to read error body>".to_string());
            anyhow::bail!("API request failed ({}): {}", status, error_body);
        }

        let api_response: ApiResponse<T> = response
            .json()
            .await
            .context("Failed to parse API response")?;

        Ok(api_response.data)
    }

    /// Register a new agent with the SpaceTraders API (no token required)
    ///
    /// # Arguments
    /// * `account_token` - The account token from ACCOUNT_TOKEN env variable
    /// * `agent_symbol` - The symbol to register (e.g., "TANDEM_PILOT")
    ///
    /// # Returns
    /// * `Ok((token, symbol))` - The agent token and confirmed symbol
    /// * `Err` - If registration fails
    pub async fn register(account_token: &str, agent_symbol: &str) -> Result<(String, String)> {
        #[derive(Serialize)]
        struct RegisterRequest {
            symbol: String,
            faction: String,
        }

        #[derive(Deserialize)]
        struct RegisterData {
            token: String,
            agent: AgentData,
        }

        #[derive(Deserialize)]
        struct AgentData {
            symbol: String,
        }

        let client = Client::new();
        let url = format!("{}/register", BASE_URL);

        let request_body = RegisterRequest {
            symbol: agent_symbol.to_string(),
            faction: "COSMIC".to_string(),
        };

        let response = client
            .post(&url)
            .header("Content-Type", "application/json")
            .bearer_auth(account_token)
            .json(&request_body)
            .send()
            .await
            .context("Failed to send registration request")?;

        let status = response.status();

        if !status.is_success() {
            let error_body = response
                .text()
                .await
                .unwrap_or_else(|_| "<unable to read error body>".to_string());
            anyhow::bail!("Registration failed ({}): {}", status, error_body);
        }

        let api_response: ApiResponse<RegisterData> = response
            .json()
            .await
            .context("Failed to parse registration response")?;

        Ok((api_response.data.token, api_response.data.agent.symbol))
    }
}
