# Resource Types

## Overview

The economy of Sector Wars 2102 revolves around a carefully balanced set of resources that players can acquire, transport, and utilize. This resource system is designed to be accessible for new players while still offering strategic depth for veterans. Each resource type serves a specific purpose in the game ecosystem and creates distinct gameplay opportunities.

## Naming Convention

The codebase uses **lowercase_underscore** naming for all commodities:
- `ore`, `organics`, `equipment`, `fuel`, `gourmet_food`, `exotic_technology`, `luxury_goods`
- `colonists` (for population)

This convention is used consistently across database schema, all backend services, and all frontend components.

## Core Trading Commodities

Seven primary commodities form the backbone of interstellar trade:

### ore
- **Description**: Raw materials extracted from planets and asteroids
- **Usage**: Essential for construction and manufacturing
- **Price Range**: 15-45 credits per unit
- **Value Pattern**: Highest in industrial sectors, lowest near mining operations
- **Special Note**: The universal currency of construction and repair

### organics
- **Description**: Standard nutritional products, synthesized provisions, and organic materials
- **Usage**: Maintains basic population survival on planets and stations; essential for colonization
- **Price Range**: 8-25 credits per unit
- **Value Pattern**: Highest in overcrowded sectors, lowest near agricultural worlds
- **Special Note**: The minimum requirement for any colonization effort
- **Database Fields**: `planet.organics`, `planet.organics_allocation`, `team.treasury_organics`

### gourmet_food
- **Description**: Premium foodstuffs, exotic ingredients, and specialized agricultural products
- **Usage**: Enhances population growth and satisfaction on developed colonies
- **Price Range**: 30-70 credits per unit
- **Value Pattern**: Highest in wealthy sectors and luxury markets, rarely found in frontier regions
- **Special Note**: Increases colony development speed and production efficiency

### fuel
- **Description**: Refined energy sources for ships and stations
- **Usage**: Powers propulsion systems and station operations
- **Price Range**: 20-60 credits per unit
- **Value Pattern**: Highest in remote sectors, lowest near refining operations
- **Special Note**: Consumption increases with ship size and travel distance
- **Database Fields**: `planet.fuel_ore`, `planet.fuel_allocation`, `team.treasury_fuel`

### equipment
- **Description**: Advanced components and specialized equipment
- **Usage**: Enables ship upgrades and advanced infrastructure
- **Price Range**: 50-120 credits per unit
- **Value Pattern**: Highest in frontier sectors, lowest near industrial hubs
- **Special Note**: Represents a wide category of manufactured goods
- **Database Fields**: `planet.equipment`, `planet.equipment_allocation`, `team.treasury_equipment`

### exotic_technology
- **Description**: Rare prototypes, experimental devices, and recovered artifacts
- **Usage**: Powers cutting-edge ship modifications and specialized facilities
- **Price Range**: 150-300 credits per unit
- **Value Pattern**: Highest in research sectors and military outposts, rarely found in common markets
- **Special Note**: Essential for accessing the most advanced gameplay capabilities

### luxury_goods
- **Description**: Rare and desirable items sought throughout the galaxy
- **Usage**: Satisfies demand for high-end merchandise
- **Price Range**: 75-200 credits per unit
- **Value Pattern**: Highest in wealthy central sectors, lowest in specialized production zones
- **Special Note**: Highest profit margins but with more volatile markets

## Strategic Resources

Beyond basic commodities, several specialized resources provide unique strategic advantages:

### combat_drones
- **Description**: Small automated combat craft carried aboard larger ships
- **Acquisition**: Purchased at military outposts (1,000 credits each)
- **Usage**: Deployed automatically during combat encounters
- **Capacity**: Limited by ship type (0-12 drones depending on vessel)
- **Strategic Value**: Essential for both offensive and defensive operations

### colonists
- **Description**: Population units seeking new opportunities across the galaxy
- **Acquisition**: Purchased from region's Sector 1 population hub for 50 credits per unit
- **Usage**: Required for establishing and growing planetary colonies
- **Transport**: Each colonist unit occupies one cargo space
- **Strategic Value**: The foundation of territorial expansion and passive income
- **Database Fields**: `planet.colonists`, `planet.max_colonists`

### quantum_shards
- **Description**: Crystalline fragments containing exotic energy patterns
- **Acquisition**: Found in nebula regions and anomalies throughout the frontier
- **Usage**: Component for creating quantum_crystals when combined
- **Rarity**: Very rare, primarily in unexplored or dangerous regions
- **Strategic Value**: Five shards can be assembled into a single quantum_crystal

### quantum_crystals
- **Description**: Powerful energy matrices formed by combining quantum_shards
- **Acquisition**: Created by assembling five quantum_shards at specialized facilities
- **Usage**: Essential component for warp gate construction and advanced propulsion
- **Rarity**: Extremely rare due to the difficulty of collecting sufficient shards
- **Strategic Value**: Enables players to construct warp gates between distant sectors
- **Database Fields**: `team.treasury_quantum_crystals`

## Rare Materials

A limited set of extremely valuable materials exist for advanced players to seek:

### prismatic_ore
- **Description**: Mineral with unique molecular structure found in specific asteroid fields
- **Rarity Level**: Extremely rare (found in approximately 1 in 10,000 asteroids)
- **Primary Use**: Ultra-lightweight hull reinforcement and advanced ship construction
- **Strategic Value**: Allows construction of superior ships with exceptional durability
- **Acquisition Challenge**: Requires extensive asteroid field exploration and mining

### photonic_crystals
- **Description**: Naturally occurring crystals that form only in certain nebula conditions
- **Rarity Level**: Very rare (found only in specific types of nebulae)
- **Primary Use**: Advanced sensors and energy weapon enhancement
- **Strategic Value**: Dramatically improves ship detection and weapon capabilities
- **Acquisition Challenge**: Requires navigation through dangerous nebula clouds

## Resource Economy

### Port System

The galactic economy operates through specialized ports. Trading patterns are defined in `station.py:get_trading_pattern()`:

- **Class 0** (Sol Station): buys=[special_goods], sells=[special_goods, colonists]
- **Class 1**: buys=[ore], sells=[organics, equipment]
- **Class 2**: buys=[organics], sells=[ore, equipment]
- **Class 3**: buys=[equipment], sells=[ore, organics]
- **Class 4** (Distribution): buys=[], sells=[ore, organics, equipment, fuel]
- **Class 5** (Collection): buys=[ore, organics, equipment, fuel], sells=[]
- **Class 6**: buys=[ore, organics], sells=[equipment, fuel]
- **Class 7**: buys=[equipment, fuel], sells=[ore, organics]
- **Class 8** (Black Hole): buys=[ore, organics, equipment, fuel], sells=[]
- **Class 9** (Nova): buys=[], sells=[ore, organics, equipment, fuel]
- **Class 10**: buys=[gourmet_food], sells=[luxury_goods, exotic_technology]
- **Class 11**: buys=[exotic_technology], sells=[advanced_components]

### Market Dynamics

The value of resources follows economic principles:

- **Supply and Demand**: Prices adjust based on local availability and need
- **Regional Variations**: Different regions value resources differently
- **Distance Premium**: Goods transported further typically command higher prices
- **Player Impact**: High trading volume in a sector temporarily affects values

## Resource Acquisition Methods

### Trading
- Purchase commodities where they're cheap, transport to where they're valuable
- Focus on efficient routes between complementary ports
- Maximize cargo capacity and optimize travel paths
- Adapt to market conditions and competition

### Production
- Establish colonies on planets to generate specific resources
- Invest in infrastructure to improve production efficiency
- Wait for automated resource generation over time
- Specialize planets for optimal output of particular commodities

### Combat
- Attack traders or pirates to seize their cargo
- Defend valuable sectors to control resource sources
- Conduct raids on strategic targets
- Salvage resources from abandoned ships or stations

### Exploration
- Discover uncharted sectors with valuable resource deposits
- Locate rare materials in dangerous or remote regions
- Map efficient trade routes between distant markets
- Find hidden sources of quantum shards and rare materials

## Resource Usage

### Ship Enhancement
- Purchase and outfit ships with better components
- Add drone bays and combat capabilities
- Improve cargo capacity and speed
- Install specialized equipment for specific tasks

### Warp Gate Construction
- Collect Quantum Shards from anomalies and nebulae
- Combine shards into Quantum Crystals at special facilities
- Utilize crystals to establish direct warp connections between sectors
- Create custom trade and travel networks across the galaxy

### Colonial Development
- Establish new colonies on planets
- Upgrade infrastructure to improve production
- Expand population to increase output
- Build defensive installations to protect investments

### Strategic Advancements
- Research special technologies using rare materials
- Create custom ship modifications with unique advantages
- Unlock access to restricted sectors and opportunities
- Gain competitive advantages through resource control
- Utilize Exotic Technology to develop unprecedented capabilities

## Design Philosophy

The resource system in Sector Wars 2102 follows several key principles:

1. **Elegant Simplicity**: Core resources are few enough to be easily understood
2. **Strategic Depth**: Resource interactions create complex gameplay decisions
3. **Progression Path**: Clear advancement from basic trading to rare resource acquisition
4. **Multiple Strategies**: Support for different playstyles (trader, explorer, combatant)
5. **Risk vs. Reward**: More valuable resources come with greater challenges to obtain