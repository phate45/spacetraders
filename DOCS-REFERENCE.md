# SpaceTraders API Documentation Reference

**API Version:** 2.3.0
**Repository:** https://github.com/SpaceTradersAPI/api-docs
**Main Documentation:** https://docs.spacetraders.io
**Base URL:** https://api.spacetraders.io/v2

---

## Overview

This document provides a comprehensive reference of the SpaceTraders API documentation available locally in the `./api-docs` directory. It catalogs all documented endpoints, data models, and game concepts found in the OpenAPI specification and model definitions.

### What's Included

The `./api-docs` repository contains:

- **OpenAPI 3.0 Specification** (`reference/SpaceTraders.json`) - Complete API definition with all endpoints, parameters, and response schemas
- **Model Definitions** (`models/*.json`) - 76 individual JSON schema files defining all data structures
- **Documentation** (`docs/overview.md`) - Getting started guide and gameplay overview
- **Configuration Files** - Stoplight Studio and Redocly configuration for API documentation rendering

### Repository Structure

```
api-docs/
├── docs/
│   └── overview.md              # Getting started and gameplay overview
├── models/                      # 76 individual model definitions (JSON)
├── reference/
│   └── SpaceTraders.json        # Complete OpenAPI 3.0 specification
├── .github/workflows/           # CI/CD workflows
├── redocly.yaml                 # Redocly API documentation config
├── .stoplight.json              # Stoplight Studio config
├── README.md                    # Repository overview
└── .git/                        # Git history and metadata
```

---

## Documented Endpoints

All endpoints are grouped by functional category as defined in the OpenAPI specification.

### Global Endpoints

Core game status and registration.

| Method | Path | Summary |
|--------|------|---------|
| `GET` | `/` | Get Status - Check game server status, announcements, reset dates, and leaderboards |
| `POST` | `/register` | Register New Agent - Create a new agent tied to a faction with starting resources |

### Agent Endpoints

Retrieve information about agents (yourself and others).

| Method | Path | Summary |
|--------|------|---------|
| `GET` | `/my/agent` | Get Agent - Fetch your own agent details |
| `GET` | `/agents` | List Agents - Fetch all agents in the game (paginated) |
| `GET` | `/agents/{agentSymbol}` | Get Public Agent - Fetch a specific public agent's details |

### Faction Endpoints

Retrieve faction information and relationships.

| Method | Path | Summary |
|--------|------|---------|
| `GET` | `/factions` | List Factions - Paginated list of all factions |
| `GET` | `/factions/{factionSymbol}` | Get Faction - Get details for a specific faction |

### Contract Endpoints

Manage contracts between your agent and factions.

| Method | Path | Summary |
|--------|------|---------|
| `GET` | `/my/contracts` | List Contracts - Paginated list of your agent's contracts |
| `GET` | `/my/contracts/{contractId}` | Get Contract - Get details for a specific contract |
| `POST` | `/my/contracts/{contractId}/accept` | Accept Contract - Accept a contract offer |
| `POST` | `/my/contracts/{contractId}/deliver` | Deliver Cargo to Contract - Deliver required goods to contract destination |
| `POST` | `/my/contracts/{contractId}/fulfill` | Fulfill Contract - Complete contract (all deliveries met) |

### Fleet Endpoints

Manage your fleet of ships and their operations.

#### Ship Management

| Method | Path | Summary |
|--------|------|---------|
| `GET` | `/my/ships` | List Ships - Paginated list of your ships |
| `POST` | `/my/ships` | Purchase Ship - Buy a ship from a shipyard |
| `GET` | `/my/ships/{shipSymbol}` | Get Ship - Get details of a specific ship |
| `GET` | `/my/ships/{shipSymbol}/cargo` | Get Ship Cargo - View current cargo inventory |
| `GET` | `/my/ships/{shipSymbol}/mounts` | Get Mounts - List installed mounts on the ship |
| `GET` | `/my/ships/{shipSymbol}/modules` | Get Ship Modules - List installed modules on the ship |
| `GET` | `/my/ships/{shipSymbol}/cooldown` | Get Ship Cooldown - Check reactor cooldown status |
| `GET` | `/my/ships/{shipSymbol}/nav` | Get Ship Nav - Get navigation details and status |
| `GET` | `/my/ships/{shipSymbol}/scrap` | Get Scrap Ship - Check scrap value and materials |
| `GET` | `/my/ships/{shipSymbol}/repair` | Get Repair Ship - Check repair costs and materials |

#### Ship Navigation

| Method | Path | Summary |
|--------|------|---------|
| `POST` | `/my/ships/{shipSymbol}/dock` | Dock Ship - Dock at current location |
| `POST` | `/my/ships/{shipSymbol}/orbit` | Orbit Ship - Enter orbit at current location |
| `POST` | `/my/ships/{shipSymbol}/navigate` | Navigate Ship - Travel to waypoint in system |
| `POST` | `/my/ships/{shipSymbol}/warp` | Warp Ship - Jump to a different system |
| `POST` | `/my/ships/{shipSymbol}/jump` | Jump Ship - Jump via jump gate |
| `PATCH` | `/my/ships/{shipSymbol}/nav` | Patch Ship Nav - Update navigation flight mode |

#### Ship Operations

| Method | Path | Summary |
|--------|------|---------|
| `POST` | `/my/ships/{shipSymbol}/refuel` | Refuel Ship - Refuel at current location |
| `POST` | `/my/ships/{shipSymbol}/chart` | Create Chart - Chart uncharted waypoints (gain reward) |
| `POST` | `/my/ships/{shipSymbol}/scan/systems` | Scan Systems - Scan nearby systems |
| `POST` | `/my/ships/{shipSymbol}/scan/waypoints` | Scan Waypoints - Scan nearby waypoints |
| `POST` | `/my/ships/{shipSymbol}/scan/ships` | Scan Ships - Scan nearby ships |
| `POST` | `/my/ships/{shipSymbol}/negotiate/contract` | Negotiate Contract - Create new contract with faction |

#### Resource Extraction

| Method | Path | Summary |
|--------|------|---------|
| `POST` | `/my/ships/{shipSymbol}/survey` | Create Survey - Survey waypoint deposits (asteroid field, gas giant) |
| `POST` | `/my/ships/{shipSymbol}/extract` | Extract Resources - Mine resources from waypoint |
| `POST` | `/my/ships/{shipSymbol}/extract/survey` | Extract Resources with Survey - Use survey to target specific deposits |
| `POST` | `/my/ships/{shipSymbol}/siphon` | Siphon Resources - Siphon gases from gas giants |
| `POST` | `/my/ships/{shipSymbol}/refine` | Ship Refine - Convert raw materials to processed goods |

#### Cargo Management

| Method | Path | Summary |
|--------|------|---------|
| `POST` | `/my/ships/{shipSymbol}/purchase` | Purchase Cargo - Buy goods from market |
| `POST` | `/my/ships/{shipSymbol}/sell` | Sell Cargo - Sell goods to market |
| `POST` | `/my/ships/{shipSymbol}/jettison` | Jettison Cargo - Discard cargo |
| `POST` | `/my/ships/{shipSymbol}/transfer` | Transfer Cargo - Transfer cargo between ships |

#### Ship Modifications

| Method | Path | Summary |
|--------|------|---------|
| `POST` | `/my/ships/{shipSymbol}/mounts/install` | Install Mount - Install a mount on the ship |
| `POST` | `/my/ships/{shipSymbol}/mounts/remove` | Remove Mount - Remove a mount from the ship |
| `POST` | `/my/ships/{shipSymbol}/modules/install` | Install Ship Module - Install a module |
| `POST` | `/my/ships/{shipSymbol}/modules/remove` | Remove Ship Module - Remove a module |

#### Ship Maintenance

| Method | Path | Summary |
|--------|------|---------|
| `POST` | `/my/ships/{shipSymbol}/repair` | Repair Ship - Repair ship damage and wear |
| `POST` | `/my/ships/{shipSymbol}/scrap` | Scrap Ship - Disassemble ship for parts and credits |

### Systems Endpoints

Explore the game universe - systems, waypoints, and locations.

#### Universe Navigation

| Method | Path | Summary |
|--------|------|---------|
| `GET` | `/systems` | List Systems - Paginated list of all systems |
| `GET` | `/systems/{systemSymbol}` | Get System - Get details of a specific system |
| `GET` | `/systems/{systemSymbol}/waypoints` | List Waypoints in System - Paginated waypoints in a system |
| `GET` | `/systems/{systemSymbol}/waypoints/{waypointSymbol}` | Get Waypoint - Get details of a specific waypoint |

#### Location Services

| Method | Path | Summary |
|--------|------|---------|
| `GET` | `/systems/{systemSymbol}/waypoints/{waypointSymbol}/market` | Get Market - View market (imports, exports, transactions) |
| `GET` | `/systems/{systemSymbol}/waypoints/{waypointSymbol}/shipyard` | Get Shipyard - View available ships and prices |
| `GET` | `/systems/{systemSymbol}/waypoints/{waypointSymbol}/jump-gate` | Get Jump Gate - View connected systems from jump gate |
| `GET` | `/systems/{systemSymbol}/waypoints/{waypointSymbol}/construction` | Get Construction Site - View construction details |
| `POST` | `/systems/{systemSymbol}/waypoints/{waypointSymbol}/construction/supply` | Supply Construction Site - Deliver materials to construction site |

### Data Endpoints

Game data that persists across resets.

| Method | Path | Summary |
|--------|------|---------|
| `GET` | `/market/supply-chain` | Get Supply Chain - Global supply chain data |

---

## Data Models

The API defines 76 core data models, organized by functional domain.

### Agent Models

| Model | Description |
|-------|-------------|
| **Agent** | Agent details including symbol, headquarters, credits, and ship count |

### Ship Models

| Model | Description |
|-------|-------------|
| **Ship** | Ship details including registration, navigation, and condition |
| **ShipRegistration** | Public registration information of a ship |
| **ShipNav** | Navigation information and route details |
| **ShipNavStatus** | Current status of the ship (docked, in orbit, etc.) |
| **ShipNavFlightMode** | Ship's set speed when traveling between waypoints or systems |
| **ShipNavRoute** | Routing information for most recent transit or current location |
| **ShipNavRouteWaypoint** | Destination or departure waypoint of a ship's route |
| **ShipNavRouteWaypointDeprecated** | Deprecated waypoint routing model |
| **ShipCargo** | Ship cargo details including inventory items |
| **ShipCargoItem** | Individual cargo item with type and quantity |
| **ShipFuel** | Fuel tank details including consumption |
| **ShipCrew** | Crew service and maintenance details |
| **ShipFrame** | Frame specification determining modules, mounts, and fuel capacity |
| **ShipEngine** | Engine specification affecting travel speed |
| **ShipReactor** | Reactor specification for powering ship systems |
| **ShipModule** | Module providing capabilities like storage or crew quarters |
| **ShipMount** | Mount installed on ship exterior for weapons/tools |
| **ShipRequirements** | Installation requirements for modules and mounts |
| **ShipType** | Predefined ship template type |
| **ShipRole** | Registered role of the ship |
| **ShipComponentCondition** | Repairable condition of a component (0=needs repair, 1=perfect) |
| **ShipComponentIntegrity** | Permanent wear over time (0=degraded, 1=perfect) |
| **ShipComponentQuality** | Quality affecting scrap value (higher=more parts returned) |
| **ShipConditionEvent** | Damage or wear event reducing component condition |

### System & Location Models

| Model | Description |
|-------|-------------|
| **System** | System details including faction presence and waypoints |
| **SystemSymbol** | Symbol identifier for a system |
| **SystemType** | Type of system (e.g., NEUTRON_STAR, RED_STAR) |
| **SystemWaypoint** | Waypoint details within a system |
| **SystemFaction** | Faction presence in a system |
| **Waypoint** | Location details (planet, moon, space station, etc.) |
| **WaypointSymbol** | Symbol identifier for a waypoint |
| **WaypointType** | Type of waypoint (PLANET, MOON, ASTEROID_FIELD, SPACE_STATION, etc.) |
| **WaypointTrait** | Trait details of a waypoint |
| **WaypointTraitSymbol** | Unique identifier of a waypoint trait |
| **WaypointModifier** | Modifier applied to a waypoint |
| **WaypointModifierSymbol** | Unique identifier of a waypoint modifier |
| **WaypointFaction** | Faction controlling a waypoint |
| **WaypointOrbital** | Orbital body orbiting a parent waypoint |
| **ConnectedSystem** | System connected via jump gate |
| **Chart** | Chart record showing who discovered a waypoint |
| **ScannedSystem** | Details of a scanned system |
| **ScannedWaypoint** | Details of a scanned waypoint |

### Market & Trade Models

| Model | Description |
|-------|-------------|
| **Market** | Market details including imports, exports, and transaction history |
| **MarketTradeGood** | Trade good offered at a market |
| **MarketTransaction** | Record of a market transaction (buy/sell) |
| **TradeGood** | A good that can be traded for currency or other goods |
| **TradeSymbol** | The symbol identifier of a trade good |
| **SupplyLevel** | Supply level of a trade good (ABUNDANT, COMMON, MODERATE, SCARCE) |
| **ActivityLevel** | Activity level of a trade good (WEAK, MODERATE, STRONG) |

### Resource Extraction Models

| Model | Description |
|-------|-------------|
| **Extraction** | Extraction operation details |
| **ExtractionYield** | Yield from an extraction operation |
| **Survey** | Resource survey of a waypoint with deposit details |
| **SurveyDeposit** | Surveyed deposit of a mineral or resource |
| **Siphon** | Siphon operation details for gas giants |
| **SiphonYield** | Yield from a siphon operation |

### Contract Models

| Model | Description |
|-------|-------------|
| **Contract** | Contract details between agent and faction |
| **ContractTerms** | Terms to fulfill the contract |
| **ContractDeliverGood** | Details of a delivery requirement (type, units, destination) |
| **ContractPayment** | Payment details for contract completion |

### Faction Models

| Model | Description |
|-------|-------------|
| **Faction** | Faction details including headquarters and traits |
| **FactionSymbol** | Symbol identifier for a faction |
| **FactionTrait** | Trait of a faction |
| **FactionTraitSymbol** | Unique identifier of a faction trait |

### Shipyard Models

| Model | Description |
|-------|-------------|
| **Shipyard** | Shipyard details including available ships and transactions |
| **ShipyardShip** | Ship available for purchase at a shipyard |
| **ShipyardTransaction** | Record of a shipyard transaction |

### Transaction Models

| Model | Description |
|-------|-------------|
| **MarketTransaction** | Result of a market transaction |
| **ShipyardTransaction** | Result of a shipyard transaction |
| **ShipModificationTransaction** | Result of installing/removing mounts or modules |
| **RepairTransaction** | Result of a repair operation |
| **ScrapTransaction** | Result of scrapping a ship |

### Scanning Models

| Model | Description |
|-------|-------------|
| **ScannedShip** | Ship details detected by scanner |
| **ScannedSystem** | System details detected by scanner |
| **ScannedWaypoint** | Waypoint details detected by scanner |

### Utility Models

| Model | Description |
|-------|-------------|
| **Cooldown** | Reactor cooldown period preventing certain actions |
| **Meta** | Pagination metadata for list endpoints |
| **Construction** | Construction details of a waypoint |
| **ConstructionMaterial** | Required construction materials |
| **JumpGate** | Jump gate connecting systems |

---

## Game Concepts

The SpaceTraders API implements several core game concepts:

### Core Gameplay

- **Agents** - Player-controlled entities with capital (credits), ships, and reputation
- **Factions** - Organizations competing for universe control; agents align with one faction at start
- **Systems & Waypoints** - Universe geography; systems contain waypoints (planets, moons, stations)
- **Ships** - Agent-owned vessels with components (frame, reactor, engine), mounts, and modules
- **Cargo** - Trade goods transported between waypoints; basis of economy and contracts

### Economic Systems

- **Markets** - Waypoint markets with imports, exports, and supply/demand
- **Trade Routes** - Profit opportunities by exploiting price differences across markets
- **Supply Chain** - Global supply chain data available via `/market/supply-chain`
- **Shipyard** - Purchase and upgrade ships at shipyards

### Mission System

- **Contracts** - Agreements with factions to deliver goods, mine resources, or complete tasks
- **Contract Terms** - Defined deliverables and payment terms
- **Faction Reputation** - Reputation affects available contracts and pricing

### Ship Operations

- **Navigation** - Travel between waypoints (navigate) or systems (warp/jump)
- **Mining/Extraction** - Extract resources from asteroids and planets
- **Siphoning** - Extract gases from gas giants
- **Refining** - Convert raw materials to processed goods
- **Trading** - Buy and sell cargo at markets
- **Scanning** - Discover nearby systems, waypoints, and ships
- **Charting** - Discover and claim waypoint discoveries for credits

### Ship Systems

- **Components** - Frame, reactor, engine determining capabilities and condition
- **Modules** - Additional capabilities (storage, quarters, sensors, etc.)
- **Mounts** - Weapons and tools (mining lasers, gas siphons, etc.)
- **Cooldown** - Reactor limitations; certain actions trigger cooldown preventing further actions
- **Condition & Integrity** - Components degrade over time; repairs restore condition
- **Fuel** - Ships consume fuel when traveling

### Advanced Features

- **Jump Gates** - Shortcuts between distant systems
- **Surveys** - Target specific deposits when extracting (higher yield for surveyed resources)
- **Construction Sites** - Incomplete waypoints requiring community resource delivery
- **Orbital Mechanics** - Ships dock to access markets/shipyards, orbit for navigation/extraction

---

## Known Gaps & Incomplete Documentation

The following areas are referenced in the API but not fully documented locally:

### Documented But Sparse

1. **Endpoint Request/Response Bodies** - The OpenAPI spec defines request bodies for POST endpoints (e.g., survey payload for extract, cargo transfer details), but detailed schema documentation isn't included in text form. Full details require parsing the OpenAPI JSON.

2. **Status Codes & Error Responses** - Error handling and error response schemas are defined in OpenAPI but not detailed in markdown documentation. Examples of error scenarios aren't provided.

3. **Pagination** - The `Meta` model handles pagination, but details on cursor-based vs offset pagination and limits aren't documented locally.

4. **Rate Limiting** - No documentation on rate limits or throttling strategy is available locally.

### Likely External-Only Content

The following areas are likely documented only on https://docs.spacetraders.io and not in the api-docs repository:

1. **Game Concepts Deep Dive** - Referenced in overview but hosted at https://docs.spacetraders.io/game-concepts/agents-and-factions
   - Agent and faction mechanics details
   - Economy and market mechanics
   - Contracts system mechanics
   - Advanced strategy guides

2. **API Guide & Best Practices** - Located at https://docs.spacetraders.io/api-guide/open-api-spec
   - Authentication patterns
   - Request/response examples with real data
   - Common workflows and patterns
   - Error handling examples
   - Rate limit details

3. **Quickstart Tutorial** - Interactive guide at https://docs.spacetraders.io/quickstart/new-game
   - Step-by-step first API calls
   - Agent creation walkthrough
   - Interactive testing environment

4. **Community & Examples** - Discord and community resources
   - User-built client libraries
   - Example automation scripts
   - Strategy discussions
   - Community insights on optimal paths

5. **Advanced Features Documentation** - Potential features not yet documented locally:
   - Detailed mounting/module installation rules and compatibility
   - Component condition/integrity degradation rates
   - Exact cooldown calculations for different actions
   - Survey quality and yield algorithms
   - Construction site requirements and completion mechanics

6. **Game Balancing Data**
   - Ship type capabilities and costs
   - Mining yield rates
   - Fuel consumption tables
   - Repair/upgrade material costs
   - Market price ranges and volatility

### Roadmap Features (Not Yet Implemented)

These are listed in the overview but have no API documentation yet:

- Scavenging derelict ships
- Webhooks for event notifications
- Ancient artifact hunting
- Diplomatic envoy missions
- Private game worlds
- Bounty hunting and piracy
- GraphQL API
- Advanced NPC behavior and rumors

---

## Using This Reference

### For Implementation

When implementing SpaceTraders client functionality:

1. **Check this file first** for endpoint paths, method types, and general data structure names
2. **Cross-reference with OpenAPI spec** (`reference/SpaceTraders.json`) for complete request/response details
3. **Review individual model files** in `models/` for detailed schema definitions
4. **For advanced patterns, consult external docs** at https://docs.spacetraders.io for examples and best practices

### For Integration Testing

Use the endpoint listing to verify coverage of all major functionality areas. The spec version (2.3.0) should match your implementation's API compatibility level.

### Mapping to External Docs

When a feature requires deeper understanding:

- **Game mechanics** → https://docs.spacetraders.io/game-concepts/agents-and-factions
- **API patterns** → https://docs.spacetraders.io/api-guide/open-api-spec
- **Getting started** → https://docs.spacetraders.io/quickstart/new-game
- **Live spec** → https://docs.spacetraders.io (interactive testing)

---

## Summary Statistics

| Category | Count |
|----------|-------|
| **Endpoints** | 61 (44 GET, 1 PATCH, 16 POST) |
| **Data Models** | 76 |
| **API Tags** | 7 (Global, Agents, Contracts, Factions, Fleet, Systems, Data) |
| **API Version** | 2.3.0 |
| **OpenAPI Version** | 3.0.x |

---

*This reference was generated from the contents of `./api-docs` and reflects the SpaceTraders API as documented in the OpenAPI specification and model files. See "Known Gaps" section for areas requiring external documentation consultation.*
