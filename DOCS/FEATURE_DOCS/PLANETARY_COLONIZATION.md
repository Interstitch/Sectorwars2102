# Planetary Colonization System — Sector Wars 2102

This document describes the planetary colonization and colonist system for Sector Wars 2102. It covers colonization methods, planet types, colony development, and resource production.

## Overview

Colonization is a core gameplay system that allows players to establish and develop planetary settlements across the galaxy. Players can colonize planets through two primary methods: traditional colonization (transporting colonists from Terra) or Genesis Device terraforming. These colonies form the foundation of a player's economic network, producing resources, generating income, and extending territorial control.

## Colonization Methods

### Traditional Colonization

- **Process**: Players acquire colonists from Terra (Earth, sector 1), transport them via ships to unclaimed planets
- **Requirements**:
  - 10,000 population units
  - 10,000 credits investment
  - Ship with sufficient colonist capacity
- **Result**: Establishes an Outpost (Phase 1 colony)
- **Advantages**: Greater control over colony specialization, predictable outcome

### Genesis Device Terraforming

- **Process**: Players use Genesis Devices to create and terraform a planet in an empty sector
- **Requirements**:
  - Genesis Devices (1, 3, or 5 depending on desired outcome)
  - Ship capable of carrying Genesis Devices
  - Empty, non-protected sector
- **Standard Genesis**: 1 device, creates random planet (basic)
- **Enhanced Genesis**: 3 devices, creates higher-quality planet (improved probability of better types)
- **Advanced Genesis**: 5 devices on a Colony Ship, consumed in the process
  - Ship is permanently sacrificed
  - Immediately creates a Settlement (Phase 2 colony) with 5,000 starting population
  - Starts with Level 2 Citadel
  - Random but weighted toward better planet types
- **Advantages**: Faster establishment, no need to transport colonists, creates planets in previously uninhabitable sectors

## Planet Types

| Type      | Description         | Fuel Prod | Organics Prod | Equip Prod | Fuel Cap | Org Cap | Equip Cap | Growth Rate |
|-----------|---------------------|-----------|--------------|------------|----------|---------|-----------|-------------|
| TERRA     | Earth (sector 1)    | 0         | 0            | 0          | ∞        | ∞       | ∞         | ∞           |
| M_CLASS   | Earth-like          | 1.0       | 1.0          | 1.0        | 10,000   | 10,000  | 10,000    | 0.5%/day    |
| L_CLASS   | Mountainous         | 0.6       | 0.4          | 1.5        | 8,000    | 5,000   | 15,000    | 0.3%/day    |
| O_CLASS   | Oceanic             | 1.5       | 0.4          | 0.6        | 15,000   | 5,000   | 8,000     | 0.4%/day    |
| K_CLASS   | Desert              | 0.4       | 1.5          | 0.6        | 5,000    | 15,000  | 8,000     | 0.2%/day    |
| H_CLASS   | Volcanic            | 1.0       | 0.0          | 2.0        | 8,000    | 0       | 15,000    | 0.1%/day    |
| D_CLASS   | Barren              | 0.0       | 0.0          | 1.5        | 0        | 0       | 20,000    | -0.1%/day   |
| C_CLASS   | Ice                 | 0.8       | 1.2          | 0.5        | 10,000   | 15,000  | 8,000     | -0.2%/day   |

### Planet Type Characteristics

#### Earth-like (M_CLASS)
- **Habitability**: Very High (95-100%)
- **Resource Balance**: Balanced across all resources
- **Colonization Difficulty**: Very Low
- **Native Life**: Often present (60% chance)
- **Special Benefit**: Highest population growth rate

#### Mountainous (L_CLASS)
- **Habitability**: Moderate (60-75%)
- **Resource Focus**: Equipment production
- **Colonization Difficulty**: Low
- **Native Life**: Sometimes present (40% chance)
- **Special Benefit**: High equipment storage capacity

#### Oceanic (O_CLASS)
- **Habitability**: Moderate (60-75%)
- **Resource Focus**: Fuel production
- **Colonization Difficulty**: Moderate
- **Native Life**: Commonly present (75% chance)
- **Special Benefit**: High fuel storage capacity

#### Desert (K_CLASS)
- **Habitability**: Low (30-45%)
- **Resource Focus**: Organics production
- **Colonization Difficulty**: Moderate
- **Native Life**: Occasionally present (25% chance)
- **Special Benefit**: High organics storage capacity

#### Volcanic (H_CLASS)
- **Habitability**: Very Low (10-25%)
- **Resource Focus**: Equipment and fuel production
- **Colonization Difficulty**: High
- **Native Life**: Rarely present (10% chance)
- **Special Benefit**: Highest equipment production multiplier

#### Barren (D_CLASS)
- **Habitability**: None (orbital habitats only)
- **Resource Focus**: Equipment production only
- **Colonization Difficulty**: Very High
- **Native Life**: Very rarely present (5% chance)
- **Special Benefit**: Highest equipment storage capacity
- **Special Challenge**: Negative population growth

#### Ice (C_CLASS)
- **Habitability**: Low (35-50%)
- **Resource Focus**: Organics production
- **Colonization Difficulty**: High
- **Native Life**: Occasionally present (30% chance)
- **Special Benefit**: High organics storage
- **Special Challenge**: Negative population growth

## Colony Development Phases

### 1. Outpost
- **Population**: 100-1,000 colonists
- **Structures**: Basic landing pad, prefab shelters, emergency life support
- **Production**: Minimal resource gathering, survey operations
- **Defense**: None to minimal (1-2 automated turrets)
- **Requirements**: Standard colonization or Basic Genesis
- **Citadel Level**: 1

### 2. Settlement
- **Population**: 1,000-10,000 colonists
- **Structures**: Small spaceport, permanent habitats, basic manufacturing
- **Production**: Essential resource production, limited exports
- **Defense**: Basic (perimeter sensors, 4-8 defensive turrets)
- **Requirements**: 
  - Standard: 50 resource units, 1,000 credits, 3 turns development time
  - Immediate: Advanced Genesis with Colony Ship sacrifice
- **Citadel Level**: 2

### 3. Colony
- **Population**: 10,000-100,000 colonists
- **Structures**: Regular spaceport, specialized industries, research facilities
- **Production**: Specialized goods, moderate exports
- **Defense**: Standard (defensive shield, 10-20 turrets, small drone squadron)
- **Requirements**: 200 resource units, 5,000 credits, 5 turns development time
- **Citadel Level**: 3

### 4. Major Colony
- **Population**: 100,000-1,000,000 colonists
- **Structures**: Large spaceport, heavy industry, advanced research centers
- **Production**: High-value goods, substantial exports
- **Defense**: Advanced (reinforced shields, 25-40 turrets, multiple drone squadrons)
- **Requirements**: 500 resource units, 15,000 credits, 8 turns development time
- **Citadel Level**: 4

### 5. Planetary Capital
- **Population**: 1,000,000+ colonists
- **Structures**: Massive spaceport complex, orbital facilities, planetary-scale industries
- **Production**: Premium goods, vast exports, unique technologies
- **Defense**: Superior (layered shield system, 50+ turrets, planetary defense fleet)
- **Requirements**: 1,500 resource units, 50,000 credits, 12 turns development time
- **Citadel Level**: 5

## Colonist Management

### Transport System
- **Loading Colonists:**
  - Only possible at Terra (sector 1)
  - Ship must be landed on Terra
  - Ship capacity enforced
  - Cost: 50 credits per colonist
- **Unloading Colonists:**
  - Only to player-owned planets
  - Planet capacity enforced (sum of all roles)
  - By default, unloaded colonists are distributed evenly

### Resource Production Roles
- **Fuel Production**: Generates fuel resources
- **Organics Production**: Generates food and biological materials
- **Equipment Production**: Generates manufactured goods and technology

### Allocation & Growth
- **Allocation:**
  - Colonists can be reassigned between roles (total remains constant)
  - Allocation affects production rates based on planet type efficiency
- **Growth:**
  - Calculated per planet type (see growth rate in Planet Types table)
  - Growth distributed proportionally across production roles
  - Negative growth possible on hostile worlds (D_CLASS and C_CLASS)
  - Growth affected by colony development phase and upgrades

### Production Calculation
- Base formula: `resource += colonists_in_role * planet_type_efficiency * hours_elapsed * (1 + upgrade_bonus)`
- Storage capacity limited by colony phase and specialized upgrades
- Production stops when storage is full

## Colony Specialization

Colonies can be specialized to enhance specific aspects of their operation:

### Industrial
- **Focus**: Manufacturing, processing, heavy industry
- **Benefits**: +30% equipment production, +20% ship building speed
- **Unique Buildings**: Automated factories, orbital shipyards, refineries

### Agricultural
- **Focus**: Food production, biological products
- **Benefits**: +50% organics production, +25% population growth
- **Unique Buildings**: Vast farm complexes, bio-labs, hydroponics towers

### Mining
- **Focus**: Resource extraction, raw materials
- **Benefits**: +40% fuel production, access to rare elements
- **Unique Buildings**: Deep mines, automated excavators, processing facilities

### Research
- **Focus**: Scientific advancement, technology development
- **Benefits**: +35% research speed, unique technology options
- **Unique Buildings**: Research campuses, experimental labs, observation centers

### Commercial
- **Focus**: Trade, finance, services
- **Benefits**: +40% credit generation, +25% trade good prices
- **Unique Buildings**: Trade centers, financial exchanges, luxury resorts

### Military
- **Focus**: Defense, training, strategic operations
- **Benefits**: +50% defense effectiveness, faster ship repairs
- **Unique Buildings**: Military academies, defense networks, fleet bases

## Planetary Defense Systems

Colonies can be protected with various defensive installations:

### Ground Defenses
- **Automated Turret Network**: Anti-drone defenses
- **Planetary Shield Generator**: Protection against bombardment
- **Anti-Orbital Missile Silos**: Weapons targeting ships in orbit
- **Gravity Disruption Array**: Makes precise targeting difficult

### Orbital Defenses
- **Mine Fields**: Explosive devices against intruders
- **Stationed Drones**: Automated defense drones that patrol the orbital space
- **Defensive Grid**: Complete defensive perimeter

## Special Cases

### Terra (Sector 1)
- Always exists, cannot be destroyed or owned
- Unlimited colonists for transport (cost: 50 credits each)
- No production, upgrades, or colonist allocation
- Dedicated UI for colonist loading

### Genesis-Created Planets
- Planet type determined by number of Genesis Devices used
- Advanced Genesis (Colony Ship sacrifice) provides immediate Settlement-level colony
- Starting population of 5,000 (compared to standard 100)
- Level 2 Citadel already constructed
- Better weighted probabilities for desirable planet types