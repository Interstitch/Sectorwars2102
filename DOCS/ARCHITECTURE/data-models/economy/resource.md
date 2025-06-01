# Resource Data Definition

## Overview

Resources in Sector Wars 2102 form the backbone of the game's economy. Players collect, transport, and trade various commodities between ports, planets, and other players. Each resource type has different uses, value, and availability across the galaxy, creating economic opportunities and strategic decisions for players.

## Data Model

```typescript
export enum ResourceCategory {
  BASIC = "BASIC",               // Primary trade commodities
  LUXURY = "LUXURY",             // High-value special goods
  STRATEGIC = "STRATEGIC",       // Military and special use resources
  RAW = "RAW"                    // Unprocessed materials
}

export enum ResourceRarity {
  COMMON = "COMMON",             // Widely available
  UNCOMMON = "UNCOMMON",         // Moderately available
  RARE = "RARE",                 // Hard to find
  VERY_RARE = "VERY_RARE"        // Extremely scarce
}

export interface ResourcePriceRange {
  min_price: number;             // Minimum possible price per unit
  max_price: number;             // Maximum possible price per unit
  base_price: number;            // Standard market price per unit
  federation_modifier: number;   // Price modifier in Federation space
  border_modifier: number;       // Price modifier in Border regions
  frontier_modifier: number;     // Price modifier in Frontier regions
}

export interface ResourceYieldData {
  sector_yield: {                // Mining yield from sector resources
    asteroid_min: number;        // Minimum yield from asteroids
    asteroid_max: number;        // Maximum yield from asteroids
    gas_cloud_min: number;       // Minimum yield from gas clouds
    gas_cloud_max: number;       // Maximum yield from gas clouds
    special_source_min: number;  // Minimum yield from special sources
    special_source_max: number;  // Maximum yield from special sources
  };
  planet_production_rates: {     // Production rates by planet type
    [planetType: string]: number; // 0-10 production rating
  };
}

export interface ResourceUseData {
  ship_fuel_value: number;       // Value as ship fuel (if applicable)
  colonist_food_value: number;   // Value as colonist food (if applicable)
  manufacturing_value: number;   // Value in manufacturing (if applicable)
  research_value: number;        // Value in research (if applicable)
  faction_demands: {             // Faction-specific value
    [faction: string]: number;   // Higher value = more in demand
  };
}

export interface ResourceTradeData {
  illegal_in_regions: string[];  // Regions where trade is prohibited
  contraband_penalty: number;    // Reputation penalty if caught smuggling
  market_volatility: number;     // 0-100 price fluctuation tendency
  price_decay_rate: number;      // How quickly price normalizes after fluctuation
  trade_volume_impact: number;   // How trading affects market prices
  affected_by_events: string[];  // Events that impact this resource
}

export interface ResourceModel {
  id: string;                    // Unique identifier
  name: string;                  // Resource name
  code: string;                  // Short code (e.g., "ORE", "TECH")
  category: ResourceCategory;    // Resource classification
  rarity: ResourceRarity;        // Availability classification
  created_at: Date;              // When resource was added to game
  
  // Price and Economics
  price_range: ResourcePriceRange; // Price information
  cargo_space: number;           // Cargo units per resource unit
  trade_data: ResourceTradeData; // Trade-related information
  
  // Production and Sources
  yield_data: ResourceYieldData; // Production/mining information
  natural_sources: string[];     // Natural source types
  manufactured: boolean;         // Whether resource can be manufactured
  manufacturing_inputs?: {       // Required inputs if manufactured
    [resourceId: string]: number; // Resource ID: quantity required
  };
  
  // Usage
  use_data: ResourceUseData;     // Usage information
  can_be_refined: boolean;       // Whether can be refined into other resources
  refining_outputs?: {           // Products when refined
    [resourceId: string]: number; // Resource ID: quantity produced
  };
  consumption_rate: number;      // How quickly resource is used
  
  // Special Properties
  is_hazardous: boolean;         // Whether special handling required
  special_storage: boolean;      // Whether special storage required
  decay_rate: number;            // 0-100, how quickly resource degrades
  special_effects: string[];     // Any special gameplay effects
  description: string;           // Human-readable description
}
```

## Primary Resource Types

### Basic Commodities

1. **Ore**
   - **Category**: BASIC
   - **Rarity**: COMMON
   - **Base Price**: 10-30 credits
   - **Sources**: Asteroids, planets, mining operations
   - **Uses**: Manufacturing, construction, planetary development
   - **Special**: Primary industrial resource

2. **Organics**
   - **Category**: BASIC
   - **Rarity**: COMMON
   - **Base Price**: 15-40 credits
   - **Sources**: Planets, agricultural operations
   - **Uses**: Food, colonist support, manufacturing
   - **Special**: Required for colonist sustenance

3. **Equipment**
   - **Category**: BASIC
   - **Rarity**: UNCOMMON
   - **Base Price**: 30-60 credits
   - **Sources**: Manufacturing ports, industrial planets
   - **Uses**: Ship repair, colonist support, construction
   - **Special**: Critical for maintenance and development

4. **Luxury Goods**
   - **Category**: LUXURY
   - **Rarity**: UNCOMMON
   - **Base Price**: 50-100 credits
   - **Sources**: Specialized ports, developed planets
   - **Uses**: Trade, reputation boosting, colonist happiness
   - **Special**: High profit margin, lower volume

5. **Medical Supplies**
   - **Category**: STRATEGIC
   - **Rarity**: UNCOMMON
   - **Base Price**: 40-80 credits
   - **Sources**: Research facilities, specialized manufacturing
   - **Uses**: Colonist health, emergency response
   - **Special**: Critical during certain events

6. **Technology**
   - **Category**: STRATEGIC
   - **Rarity**: RARE
   - **Base Price**: 75-150 credits
   - **Sources**: Research ports, advanced manufacturing
   - **Uses**: Ship upgrades, special devices, planetary improvements
   - **Special**: Required for advanced operations

## Resource Mechanics

### Trade and Economics
1. **Market Forces**: Supply and demand affect prices at ports
2. **Regional Variations**: Different regions have different resource availability
3. **Price Fluctuations**: Events and player activity impact prices
4. **Trade Routes**: Established paths between resource sources and markets

### Resource Collection
1. **Mining**: Extraction from asteroids and special sector features
2. **Planetary Production**: Generated by colonized planets
3. **Manufacturing**: Created from other resources at facilities
4. **Trading**: Purchased from ports and other players

### Resource Storage
1. **Ship Cargo**: Limited by ship cargo capacity
2. **Port Storage**: Available at owned ports
3. **Planetary Storage**: Available on colonized planets
4. **Team Storage**: Shared among team members

### Special Resource Mechanics
1. **Contraband**: Some resources illegal in certain regions
2. **Hazardous Materials**: Special handling requirements
3. **Perishable Goods**: Degrade over time
4. **Special Resources**: Unique resources with specific applications