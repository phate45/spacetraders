use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;

const CONFIG_FILE: &str = ".spacetraders.toml";

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Config {
    pub agent_token: Option<String>,
    pub agent_symbol: Option<String>,
}

impl Config {
    /// Load config from .spacetraders.toml, creating default if missing
    pub fn load() -> Result<Self> {
        let path = Path::new(CONFIG_FILE);

        if path.exists() {
            let contents = fs::read_to_string(path)
                .context("Failed to read config file")?;
            let config: Config = toml::from_str(&contents)
                .context("Failed to parse config file")?;
            Ok(config)
        } else {
            // Create default config with no token
            let config = Config {
                agent_token: None,
                agent_symbol: None,
            };
            config.save()?;
            Ok(config)
        }
    }

    /// Save config to .spacetraders.toml
    pub fn save(&self) -> Result<()> {
        let toml_string = toml::to_string_pretty(self)
            .context("Failed to serialize config")?;
        fs::write(CONFIG_FILE, toml_string)
            .context("Failed to write config file")?;
        Ok(())
    }

    /// Check if agent token is present
    pub fn has_token(&self) -> bool {
        self.agent_token.is_some() && !self.agent_token.as_ref().unwrap().is_empty()
    }
}
