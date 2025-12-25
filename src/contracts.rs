use serde::Deserialize;

use crate::agent::{ApiResponse, BASE_URL};

/// Contract between agent and faction
#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Contract {
    pub id: String,
    pub faction_symbol: String,
    #[serde(rename = "type")]
    pub contract_type: String,
    pub terms: ContractTerms,
    pub accepted: bool,
    pub fulfilled: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub deadline_to_accept: Option<String>,
}

/// Terms to fulfill the contract
#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ContractTerms {
    pub deadline: String,
    pub payment: ContractPayment,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub deliver: Option<Vec<ContractDeliverGood>>,
}

/// Payment details for contract completion
#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ContractPayment {
    pub on_accepted: i64,
    pub on_fulfilled: i64,
}

/// Details of a delivery requirement
#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ContractDeliverGood {
    pub trade_symbol: String,
    pub destination_symbol: String,
    pub units_required: i32,
    pub units_fulfilled: i32,
}

impl Contract {
    /// Pretty-print contract information to console
    pub fn display(&self) {
        println!("\n=== Contract {} ===", self.id);
        println!("Faction: {}", self.faction_symbol);
        println!("Type: {}", self.contract_type);
        println!("Status: {}", if self.accepted {
            if self.fulfilled { "Fulfilled" } else { "Accepted" }
        } else {
            "Pending Acceptance"
        });

        if let Some(deadline) = &self.deadline_to_accept
            && !self.accepted {
                println!("Accept By: {}", deadline);
            }

        println!("\nPayment:");
        println!("  On Acceptance: {} credits", self.terms.payment.on_accepted);
        println!("  On Fulfillment: {} credits", self.terms.payment.on_fulfilled);
        println!("  Total: {} credits",
            self.terms.payment.on_accepted + self.terms.payment.on_fulfilled);

        println!("Deadline: {}", self.terms.deadline);

        if let Some(deliveries) = &self.terms.deliver
            && !deliveries.is_empty() {
                println!("\nDelivery Requirements:");
                for delivery in deliveries {
                    println!("  - {}: {}/{} units to {}",
                        delivery.trade_symbol,
                        delivery.units_fulfilled,
                        delivery.units_required,
                        delivery.destination_symbol);
                }
            }
    }
}

/// List all contracts for the agent from /my/contracts endpoint
///
/// # Arguments
/// * `agent_token` - The Bearer token for authentication
///
/// # Returns
/// * `Ok(Vec<Contract>)` - List of contracts
/// * `Err` - If the request fails
pub async fn list_contracts(agent_token: &str) -> Result<Vec<Contract>, Box<dyn std::error::Error>> {
    let client = reqwest::Client::new();
    let url = format!("{}/my/contracts", BASE_URL);

    let response = client
        .get(&url)
        .header("Content-Type", "application/json")
        .bearer_auth(agent_token)
        .send()
        .await?;

    let status = response.status();

    if !status.is_success() {
        let error_body = response.text().await?;
        return Err(format!("Failed to list contracts ({}): {}", status, error_body).into());
    }

    let api_response: ApiResponse<Vec<Contract>> = response.json().await?;
    Ok(api_response.data)
}

/// Accept a contract from /my/contracts/:contractId/accept endpoint
///
/// # Arguments
/// * `agent_token` - The Bearer token for authentication
/// * `contract_id` - The contract ID to accept
///
/// # Returns
/// * `Ok(Contract)` - The updated contract after acceptance
/// * `Err` - If the request fails (invalid contract, already accepted, etc.)
pub async fn accept_contract(
    agent_token: &str,
    contract_id: &str,
) -> Result<Contract, Box<dyn std::error::Error>> {
    let client = reqwest::Client::new();
    let url = format!("{}/my/contracts/{}/accept", BASE_URL, contract_id);

    let response = client
        .post(&url)
        .header("Content-Type", "application/json")
        .bearer_auth(agent_token)
        .send()
        .await?;

    let status = response.status();

    if !status.is_success() {
        let error_body = response.text().await?;
        return Err(format!("Failed to accept contract ({}): {}", status, error_body).into());
    }

    #[derive(Debug, Deserialize)]
    struct AcceptContractResponse {
        contract: Contract,
    }

    let api_response: ApiResponse<AcceptContractResponse> = response.json().await?;
    Ok(api_response.data.contract)
}

/// Negotiate a new contract from /my/ships/:shipSymbol/negotiate/contract endpoint
///
/// # Arguments
/// * `agent_token` - The Bearer token for authentication
/// * `ship_symbol` - The ship symbol to use for negotiation
///
/// # Returns
/// * `Ok(Contract)` - The newly negotiated contract
/// * `Err` - If the request fails (invalid ship, no negotiation available, etc.)
pub async fn negotiate_contract(
    agent_token: &str,
    ship_symbol: &str,
) -> Result<Contract, Box<dyn std::error::Error>> {
    let client = reqwest::Client::new();
    let url = format!("{}/my/ships/{}/negotiate/contract", BASE_URL, ship_symbol);

    let response = client
        .post(&url)
        .header("Content-Type", "application/json")
        .bearer_auth(agent_token)
        .send()
        .await?;

    let status = response.status();

    if !status.is_success() {
        let error_body = response.text().await?;
        return Err(format!("Failed to negotiate contract ({}): {}", status, error_body).into());
    }

    #[derive(Debug, Deserialize)]
    struct NegotiateContractResponse {
        contract: Contract,
    }

    let api_response: ApiResponse<NegotiateContractResponse> = response.json().await?;
    Ok(api_response.data.contract)
}
