mod agent;
mod client;
mod config;
mod contracts;
mod waypoint;

use agent::fetch_agent;
use anyhow::{Context, Result};
use client::SpaceTradersClient;
use config::Config;
use contracts::list_contracts;
use waypoint::fetch_waypoint;

#[tokio::main]
async fn main() -> Result<()> {
    println!("=== SpaceTraders Client ===\n");

    // Load or create config
    let mut config = Config::load()?;
    println!("Config loaded from .spacetraders.toml");

    // Check if we have a token
    if !config.has_token() {
        println!("No agent token found. Starting registration process...\n");

        // Read ACCOUNT_TOKEN from environment
        let account_token = std::env::var("ACCOUNT_TOKEN")
            .context("ACCOUNT_TOKEN environment variable not set")?;

        // Register with TANDEM_PILOT symbol
        let agent_symbol = "TANDEM_PILOT";
        let (token, confirmed_symbol) = SpaceTradersClient::register(&account_token, agent_symbol).await?;

        // Store token and symbol in config
        config.agent_token = Some(token);
        config.agent_symbol = Some(confirmed_symbol);
        config.save()?;

        println!("\nAgent token saved to .spacetraders.toml");
    } else {
        println!("Agent token found in config");
        if let Some(symbol) = &config.agent_symbol {
            println!("Agent symbol: {}", symbol);
        }
    }

    println!("\n=== Token Status ===");
    println!("Token present: {}", config.has_token());
    if let Some(token) = &config.agent_token {
        // Display first and last 4 characters for verification
        if token.len() > 8 {
            println!("Token: {}...{}", &token[..4], &token[token.len()-4..]);
        } else {
            println!("Token: <present>");
        }
    }

    // Fetch and display agent information
    if let Some(token) = &config.agent_token {
        // Create API client
        let client = SpaceTradersClient::new(token.clone());

        println!("\nFetching agent information...");
        match fetch_agent(&client).await {
            Ok(agent) => {
                agent.display();

                // Fetch and display headquarters waypoint
                // Headquarters format is like "X1-DF55-20250Z"
                // System symbol is the first two parts: "X1-DF55"
                let headquarters = &agent.headquarters;
                let system_symbol = headquarters
                    .rsplit_once('-')
                    .map(|(left, _)| left)
                    .unwrap_or(headquarters);

                println!("\nFetching waypoint information for headquarters...");
                match fetch_waypoint(&client, system_symbol, headquarters).await {
                    Ok(waypoint) => waypoint.display(),
                    Err(e) => eprintln!("Error fetching waypoint: {}", e),
                }

                // Fetch and display contracts
                println!("\nFetching contracts...");
                match list_contracts(&client).await {
                    Ok(contracts) => {
                        if contracts.is_empty() {
                            println!("No contracts available.");
                        } else {
                            println!("Found {} contract(s):", contracts.len());
                            for contract in contracts {
                                contract.display();
                            }
                        }
                    },
                    Err(e) => eprintln!("Error fetching contracts: {}", e),
                }
            },
            Err(e) => eprintln!("Error fetching agent: {}", e),
        }
    }

    Ok(())
}
