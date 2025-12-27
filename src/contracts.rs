use serde::Deserialize;

use crate::client::SpaceTradersClient;

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
    pub expiration: String,
    pub deadline_to_accept: Option<String>,
}

/// Terms to fulfill the contract
#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ContractTerms {
    pub deadline: String,
    pub payment: ContractPayment,
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
/// * `client` - The SpaceTraders API client
///
/// # Returns
/// * `Ok(Vec<Contract>)` - List of contracts
/// * `Err` - If the request fails
pub async fn list_contracts(client: &SpaceTradersClient) -> anyhow::Result<Vec<Contract>> {
    client.get("/my/contracts").await
}

/// Accept a contract from /my/contracts/:contractId/accept endpoint
///
/// # Arguments
/// * `client` - The SpaceTraders API client
/// * `contract_id` - The contract ID to accept
///
/// # Returns
/// * `Ok(Contract)` - The updated contract after acceptance
/// * `Err` - If the request fails (invalid contract, already accepted, etc.)
pub async fn accept_contract(
    client: &SpaceTradersClient,
    contract_id: &str,
) -> anyhow::Result<Contract> {
    #[derive(Debug, Deserialize)]
    struct AcceptContractResponse {
        contract: Contract,
    }

    let path = format!("/my/contracts/{}/accept", contract_id);
    let response: AcceptContractResponse = client.post(&path).await?;
    Ok(response.contract)
}

/// Negotiate a new contract from /my/ships/:shipSymbol/negotiate/contract endpoint
///
/// # Arguments
/// * `client` - The SpaceTraders API client
/// * `ship_symbol` - The ship symbol to use for negotiation
///
/// # Returns
/// * `Ok(Contract)` - The newly negotiated contract
/// * `Err` - If the request fails (invalid ship, no negotiation available, etc.)
pub async fn negotiate_contract(
    client: &SpaceTradersClient,
    ship_symbol: &str,
) -> anyhow::Result<Contract> {
    #[derive(Debug, Deserialize)]
    struct NegotiateContractResponse {
        contract: Contract,
    }

    let path = format!("/my/ships/{}/negotiate/contract", ship_symbol);
    let response: NegotiateContractResponse = client.post(&path).await?;
    Ok(response.contract)
}
