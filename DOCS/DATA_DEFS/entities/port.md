# Port Data Definition

## Overview
Ports are space stations where players can trade commodities, purchase ships and equipment, and access various services. Ports are classified by their class which determines their specific trading patterns, services, and defensive capabilities.

## Position in Galaxy Hierarchy

Ports exist within the galaxy's structure:
- Ports are located within specific **Sectors**
- Sectors are grouped into **Clusters**
- Clusters form **Regions**
- Regions make up the **Galaxy**

## Data Model

```typescript
export enum PortClass {
  CLASS_0 = 0,   // Sol System - Special mechanics
  CLASS_1 = 1,   // Mining Operation
  CLASS_2 = 2,   // Agricultural Center
  CLASS_3 = 3,   // Industrial Hub
  CLASS_4 = 4,   // Distribution Center
  CLASS_5 = 5,   // Collection Hub
  CLASS_6 = 6,   // Mixed Market
  CLASS_7 = 7,   // Resource Exchange
  CLASS_8 = 8,   // Black Hole (Premium Buyer)
  CLASS_9 = 9,   // Nova (Premium Seller)
  CLASS_10 = 10, // Luxury Market
  CLASS_11 = 11  // Advanced Tech Hub
}

export enum PortType {
  TRADING = "TRADING",
  MILITARY = "MILITARY",
  INDUSTRIAL = "INDUSTRIAL",
  MINING = "MINING",
  SCIENTIFIC = "SCIENTIFIC",
  SHIPYARD = "SHIPYARD",
  OUTPOST = "OUTPOST",
  BLACK_MARKET = "BLACK_MARKET",
  DIPLOMATIC = "DIPLOMATIC",
  CORPORATE = "CORPORATE"
}

export interface PortCommodities {
  ore: {
    quantity: number;             // Current stock
    capacity: number;             // Maximum capacity
    base_price: number;           // Base price per unit
    current_price: number;        // Current market price
    production_rate: number;      // Units produced per day
    price_variance: number;       // 0-100, volatility percentage
    buys: boolean;                // Whether port purchases this commodity
    sells: boolean;               // Whether port sells this commodity
  };
  organics: {
    quantity: number;
    capacity: number;
    base_price: number;
    current_price: number;
    production_rate: number;
    price_variance: number;
    buys: boolean;
    sells: boolean;
  };
  equipment: {
    quantity: number;
    capacity: number;
    base_price: number;
    current_price: number;
    production_rate: number;
    price_variance: number;
    buys: boolean;
    sells: boolean;
  };
  fuel: {
    quantity: number;
    capacity: number;
    base_price: number;
    current_price: number;
    production_rate: number;
    price_variance: number;
    buys: boolean;
    sells: boolean;
  };
  luxury_goods: {
    quantity: number;
    capacity: number;
    base_price: number;
    current_price: number;
    production_rate: number;
    price_variance: number;
    buys: boolean;
    sells: boolean;
  };
  gourmet_food: {
    quantity: number;
    capacity: number;
    base_price: number;
    current_price: number;
    production_rate: number;
    price_variance: number;
    buys: boolean;
    sells: boolean;
  };
  exotic_technology: {
    quantity: number;
    capacity: number;
    base_price: number;
    current_price: number;
    production_rate: number;
    price_variance: number;
    buys: boolean;
    sells: boolean;
  };
  colonists: {
    quantity: number;
    capacity: number;
    base_price: number;           // 50 credits each
    current_price: number;
    production_rate: number;
    price_variance: number;
    buys: boolean;
    sells: boolean;
  };
}

export interface PortTraderPersonality {
  type: "FEDERATION" | "BORDER" | "FRONTIER" | "LUXURY" | "BLACK_MARKET";
  haggling_difficulty: number;    // 1-10, higher = more difficult
  preferred_appeal_types: string[]; // ["survival", "logical", "emotional", "cultural"]
  memory_duration: number;        // Days to remember previous interactions
  trust_level: number;            // 0-100, affects haggling success
  quirks: string[];               // Personality traits affecting interactions
}

export interface PortDefenses {
  defense_drones: number;         // Defensive drones deployed
  max_defense_drones: number;     // Maximum drone capacity
  auto_turrets: boolean;          // Whether port has automated turrets
  defense_grid: boolean;          // Whether port has advanced defense grid
  shield_strength: number;        // 0-100, shield effectiveness
  patrol_ships: number;           // NPC ships patrolling nearby sectors
  military_contract: boolean;     // Whether faction military protects port
}

export interface PortServices {
  ship_dealer: boolean;           // Can purchase ships
  ship_repair: boolean;           // Can repair ships
  ship_maintenance: boolean;      // Can service ships
  ship_upgrades: boolean;         // Can upgrade ship components
  insurance: boolean;             // Offers ship insurance
  drone_shop: boolean;            // Sells attack/defense drones
  genesis_dealer: boolean;        // Sells Genesis Devices
  mine_dealer: boolean;           // Sells space mines
  diplomatic_services: boolean;   // Offers reputation reset services
  storage_rental: boolean;        // Commodity storage for non-owners
  market_intelligence: boolean;   // Provides trade route data
  refining_facility: boolean;     // Processes raw materials
  luxury_amenities: boolean;      // High-end services
}

export interface PortOwnership {
  owner_id: string | null;        // Player ID of owner (null if NPC-owned)
  owner_name: string | null;      // Name of owner
  team_owned: boolean;            // Whether owned by a team/syndicate
  shareholders: Array<{           // For team ownership
    player_id: string;
    ownership_percentage: number;
    voting_rights: boolean;
  }>;
  purchase_price: number;         // Original purchase price
  current_value: number;          // Current market value
  acquisition_method: "PURCHASE" | "TRADE_VOLUME" | "FACTION_STANDING" | "MISSION" | "TAKEOVER";
  
  // Revenue Management
  tariff_rate: number;            // 2-8%, fee on transactions
  docking_fee: number;            // 5-20 credits per ship
  daily_income: number;           // Credits generated daily
  monthly_revenue: number;        // Rolling 30-day revenue
  last_income_collection: Date;   // When income was last collected
  
  // Operational Settings
  preferred_traders: string[];    // Player IDs with reduced fees
  price_adjustments: {            // ±10% price modifications
    ore: number;
    organics: number;
    equipment: number;
    fuel: number;
  };
  
  // Investment and Upgrades
  upgrade_level: number;          // 0-5, port improvements
  invested_credits: number;       // Total investment in upgrades
  maintenance_costs: number;      // Monthly operational costs
  defense_budget: number;         // Monthly security spending
}

export interface PortModel {
  id: string;                     // Unique identifier
  name: string;                   // Port name
  class: PortClass;               // Port trading classification
  type: PortType;                 // Port functional type
  sector_id: number;              // Sector containing this port
  sector_uuid: string;            // Sector UUID reference
  faction_id: string;             // Controlling faction
  
  // Trading and Economics
  commodities: PortCommodities;   // Trade goods and patterns
  trader_personality: PortTraderPersonality; // AI haggling behavior
  market_volatility: number;      // 0-100, price fluctuation factor
  trade_volume: number;           // Daily transaction credits
  
  // Infrastructure and Services
  services: PortServices;         // Available services
  defenses: PortDefenses;         // Defensive capabilities
  ownership: PortOwnership | null; // Ownership information (null if NPC-owned)
  
  // Status and Metadata
  status: "OPERATIONAL" | "DAMAGED" | "UNDER_CONSTRUCTION" | "UNDER_ATTACK" | "LOCKDOWN" | "ABANDONED" | "RESTRICTED";
  created_at: Date;               // When port was created
  last_updated: Date;             // When port was last updated
  last_market_update: Date;       // When commodity prices last changed
  market_update_frequency: number; // Hours between market updates
  reputation_threshold: number;   // Minimum reputation needed for docking
  is_destroyed: boolean;          // Whether port is currently disabled
  recovery_time: Date | null;     // When port will be restored after attack
  
  // Special Properties
  is_quest_hub: boolean;          // Whether port offers special missions
  is_faction_headquarters: boolean; // Whether port is faction HQ
  special_services: string[];     // Any unique services offered
  is_player_ownable: boolean;     // Whether players can acquire this port
  acquisition_requirements: {     // Requirements to purchase
    min_trade_volume: number;     // Minimum credits traded
    min_faction_standing: string; // Required faction reputation
    base_price: number;           // Purchase price in credits
    special_missions: string[];   // Required mission completions
  };
}

export interface PortClassSpecification {
  class: PortClass;
  name: string;                   // Class description
  trading_pattern: {              // What the port buys and sells
    buys: string[];               // Commodity types purchased
    sells: string[];              // Commodity types sold
    specializes_in: string[];     // Primary focus commodities
  };
  base_purchase_price: number;    // Credits to buy port (if ownable)
  max_commodity_capacity: number; // Maximum units of each commodity
  income_multiplier: number;      // Daily income multiplier for owners
  services: string[];             // Available services by default
  defense_drone_capacity: number; // Maximum defense drones
  defense_rating: number;         // Overall defense strength
  market_update_frequency: number; // Hours between market updates
  haggling_difficulty: number;    // 1-10, difficulty of price negotiation
  commodity_price_ranges: {       // Min/max possible prices by commodity
    ore: [number, number];
    organics: [number, number];
    equipment: [number, number];
    fuel: [number, number];
    luxury_goods: [number, number];
    gourmet_food: [number, number];
    exotic_technology: [number, number];
    colonists: [number, number];
  };
}
```

## Port Classes and Trading Patterns

| Class | Name | Description | Buys | Sells | Special Features |
|-------|------|-------------|------|-------|------------------|
| 0 | Sol System | Earth's main port | Special Goods | Special Goods, Colonists, Ship Upgrades | Unique equipment, predictable price cycles |
| 1 | Mining Operation | Resource extraction | Ore | Organics, Equipment | High ore capacity, industrial focus |
| 2 | Agricultural Center | Food production | Organics | Ore, Equipment | Biological products, food specialization |
| 3 | Industrial Hub | Manufacturing | Equipment | Ore, Organics | Advanced manufacturing, tech production |
| 4 | Distribution Center | Trade hub | Nothing | Everything | Wide selection, competitive prices |
| 5 | Collection Hub | Resource gathering | Everything | Nothing | Pays premium for all goods |
| 6 | Mixed Market | General trading | Ore, Organics | Equipment, Fuel | Balanced trading, moderate prices |
| 7 | Resource Exchange | Commodity trading | Equipment, Fuel | Ore, Organics | Inverse of Class 6, resource focus |
| 8 | Black Hole | Premium buyer | Everything | Nothing | Pays premium prices, dangerous location |
| 9 | Nova | Premium seller | Nothing | Everything | Sells at discount, dangerous location |
| 10 | Luxury Market | High-end goods | Gourmet Food | Technology, Luxury Goods | Exclusive items, wealthy clientele |
| 11 | Advanced Tech Hub | Technology center | Exotic Technology | Advanced Components | Cutting-edge tech, research facilities |

## Port Ownership System

### Acquisition Methods
- **Trade Volume**: 100,000+ credits traded at the port
- **Direct Purchase**: 250,000 - 2,000,000 credits (varies by class and location)
- **Faction Standing**: "Trusted" or "Allied" status with controlling faction
- **Special Missions**: Complete port-specific trading missions

### Ownership Benefits
- **Tariff Income**: 2-8% of all player transactions
- **Supply Priority**: First access to limited commodities
- **Price Control**: Adjust base prices within ±10%
- **Free Storage**: Personal commodity storage at the port
- **Port Upgrades**: Invest in facility improvements
- **Economic Intelligence**: Detailed trade flow reports
- **Mission Creation**: Create special trade missions for other players

### Revenue Streams
- **Transaction Tariffs**: Primary income source
- **Docking Fees**: 5-20 credits per visiting ship
- **Service Charges**: Revenue from repairs, refueling, upgrades
- **Storage Rental**: Fees from non-owners storing goods
- **Information Sales**: Market data and trade route intelligence
- **Specialty Services**: Custom manufacturing and processing

### Port Management
- **Tariff Optimization**: Balance income against trade volume
- **Security Investment**: Defense against pirates and hostile players
- **Infrastructure Upgrades**: Improve capacity and services
- **Marketing**: Attract traders through competitive pricing
- **Relationship Management**: Maintain faction standing

### Competitive Dynamics
- **Acquisition Competition**: Multiple players may bid for available ports
- **Economic Warfare**: Price competition and trade route manipulation
- **Military Takeovers**: Direct assault (frontier regions only)
- **Defensive Cooperation**: Team-based port protection
- **Market Manipulation**: Coordinated efforts to influence trade

## Haggling and AI Trader Personality

### Trader Types by Location
- **Federation Ports**: Formal, rule-following, logical appeals work best
- **Border Ports**: Practical, honest, survival stories resonate
- **Frontier Ports**: Rugged, independent, risk-taking appreciated
- **Luxury Hubs**: Sophisticated, cultural references valued
- **Black Market**: Suspicious, mutual benefit appeals effective

### Anti-Exploitation Systems
- **Uniqueness Database**: Prevents reuse of haggling statements
- **Semantic Analysis**: Detects similar attempts with different wording
- **Port Memory**: Individual traders remember past interactions
- **Context Verification**: Cross-checks stories against game state
- **Adaptive Difficulty**: Expectations scale with player experience

### Haggling Success Factors
- **Creativity**: Original, contextually appropriate appeals
- **Relevance**: Stories that fit the port's personality and location
- **Reasonableness**: Price requests within acceptable ranges
- **Reputation**: Player standing with port and faction
- **Consistency**: Reliable trading patterns build trust

## Destruction and Recovery

When a port is successfully attacked and destroyed:
1. All services temporarily unavailable
2. Port automatically regenerates after 24 hours
3. Commodities reset to baseline values
4. Ownership remains unchanged
5. Defensive systems require manual reactivation

## Special Port Features

### Sol System (Class 0)
- **Unique Equipment**: Ship upgrades only available at Earth
- **Colonist Source**: Population units for planetary colonization
- **Price Cycles**: Predictable daily price fluctuations
- **Advanced Services**: Premium ship modifications and rare technology

### Premium Locations
- **Black Hole Ports**: Extreme danger, maximum profit potential
- **Nova Ports**: Hazardous environment, discounted goods
- **Faction Headquarters**: Enhanced security, exclusive faction services
- **Research Stations**: Genesis device access, experimental technology

### Specialized Services
- **Shipyards**: Ship construction and major modifications
- **Diplomatic Centers**: Reputation management and faction negotiations
- **Military Outposts**: Combat equipment and tactical support
- **Trade Exchanges**: Market data and route optimization tools