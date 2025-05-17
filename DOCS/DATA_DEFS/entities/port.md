# Port Data Definition

## Overview
Ports are space stations where players can trade commodities, purchase ships and equipment, and access various services. Ports are classified by their size and capabilities, which affects the services they offer and their defensive capabilities.

## Position in Galaxy Hierarchy

Ports exist within the galaxy's structure:
- Ports are located within specific **Sectors**
- Sectors are grouped into **Clusters**
- Clusters form **Regions**
- Regions make up the **Galaxy**

## Data Model

```typescript
export enum PortClass {
  CLASS_1 = 1,  // Small outpost, limited services
  CLASS_2 = 2,  // Standard port, moderate services
  CLASS_3 = 3,  // Major port, full services
  CLASS_4 = 4,  // Regional hub, premium services
  CLASS_5 = 5   // Federation headquarters, maximum services
}

export interface PortCommodities {
  ore: {
    quantity: number;             // Current stock
    capacity: number;             // Maximum capacity
    base_price: number;           // Base price per unit
    current_price: number;        // Current market price
    production_rate: number;      // Units produced per day
    price_variance: number;       // 0-100, volatility percentage
  };
  organics: {
    quantity: number;
    capacity: number;
    base_price: number;
    current_price: number;
    production_rate: number;
    price_variance: number;
  };
  equipment: {
    quantity: number;
    capacity: number;
    base_price: number;
    current_price: number;
    production_rate: number;
    price_variance: number;
  };
  luxury_goods: {
    quantity: number;
    capacity: number;
    base_price: number;
    current_price: number;
    production_rate: number;
    price_variance: number;
  };
  medical_supplies: {
    quantity: number;
    capacity: number;
    base_price: number;
    current_price: number;
    production_rate: number;
    price_variance: number;
  };
  technology: {
    quantity: number;
    capacity: number;
    base_price: number;
    current_price: number;
    production_rate: number;
    price_variance: number;
  };
}

export interface PortDefenses {
  defense_drones: number;         // Defensive drones deployed
  max_defense_drones: number;     // Maximum drone capacity
  auto_turrets: boolean;          // Whether port has automated turrets (Class 4+)
  defense_grid: boolean;          // Whether port has advanced defense grid (Class 5)
  shield_strength: number;        // 0-100, shield effectiveness
}

export interface PortServices {
  ship_dealer: boolean;           // Can purchase ships
  ship_repair: boolean;           // Can repair ships
  ship_maintenance: boolean;      // Can service ships
  insurance: boolean;             // Offers ship insurance
  drone_shop: boolean;            // Sells attack/defense drones
  genesis_dealer: boolean;        // Sells Genesis Devices
  mine_dealer: boolean;           // Sells space mines
  diplomatic_services: boolean;   // Offers reputation reset services
}

export interface PortOwnership {
  owner_id: string | null;        // Player ID of owner (null if NPC-owned)
  owner_name: string | null;      // Name of owner
  purchase_price: number;         // Original purchase price
  current_value: number;          // Current market value
  tax_rate: number;               // 0-20%, fee on all transactions
  daily_income: number;           // Credits generated daily
  last_income_collection: Date;   // When income was last collected
}

export interface PortModel {
  id: string;                     // Unique identifier
  name: string;                   // Port name
  class: PortClass;               // Port size/classification
  sector_id: number;              // Sector containing this port
  faction_id: string;             // Controlling faction
  commodities: PortCommodities;   // Trade goods
  services: PortServices;         // Available services
  defenses: PortDefenses;         // Defensive capabilities
  ownership: PortOwnership | null; // Ownership information (null if not player-owned)
  created_at: Date;               // When port was created
  last_updated: Date;             // When port was last updated
  last_market_update: Date;       // When commodity prices last changed
  market_update_frequency: number; // Hours between market updates
  reputation_threshold: number;   // Minimum reputation needed for docking
  is_destroyed: boolean;          // Whether port is currently disabled
  recovery_time: Date | null;     // When port will be restored after attack
  
  // Special flags
  is_quest_hub: boolean;          // Whether port offers special missions
  is_faction_headquarters: boolean; // Whether port is faction HQ
  special_services: string[];     // Any unique services offered
}

export interface PortClassSpecification {
  class: PortClass;
  base_purchase_price: number;    // Credits to buy port
  upgrade_cost: number;           // Credits to upgrade to next class
  max_commodity_capacity: number; // Maximum units of each commodity
  income_multiplier: number;      // Daily income multiplier
  services: string[];             // Available services by default
  defense_drone_capacity: number; // Maximum defense drones
  defense_rating: number;         // Overall defense strength
  market_update_frequency: number; // Hours between market updates
  commodity_price_ranges: {       // Min/max possible prices by commodity
    ore: [number, number];
    organics: [number, number];
    equipment: [number, number];
    luxury_goods: [number, number];
    medical_supplies: [number, number];
    technology: [number, number];
  };
}
```

## Port Classes

| Class | Description | Purchase Price | Upgrade Cost | Services | Defense |
|-------|-------------|----------------|--------------|----------|---------|
| 1 | Small outpost | 250,000 | 100,000 | Basic trade, repairs | 50 drones |
| 2 | Standard port | 500,000 | 250,000 | + Ship sales, maintenance | 100 drones |
| 3 | Major port | 1,000,000 | 500,000 | + Insurance, drones, mines | 200 drones |
| 4 | Regional hub | 2,000,000 | 1,000,000 | + All ship types, Genesis Devices | 300 drones, turrets |
| 5 | Federation HQ | 5,000,000 | N/A | All services, diplomatic functions | 500 drones, defense grid |

## Port Ownership Benefits

1. **Tax Revenue**: 0.5-5% of all transactions
2. **Daily Income**: Based on port class and traffic
3. **Market Control**: Set commodity buy/sell ranges
4. **Defense Control**: Configure defensive responses
5. **Sector Influence**: Affects reputation with local faction

## Destruction and Recovery

When a port is successfully attacked and destroyed:
1. All services are temporarily unavailable
2. Port automatically regenerates after 24 hours
3. Commodities reset to baseline values
4. Ownership remains unchanged

## Special Port Types

1. **Faction Headquarters**: Enhanced security, faction-specific services
2. **Black Market Ports**: Unique illegal goods, higher prices, lower security
3. **Research Stations**: Genesis device access, special equipment
4. **Military Outposts**: Combat equipment, enhanced defenses