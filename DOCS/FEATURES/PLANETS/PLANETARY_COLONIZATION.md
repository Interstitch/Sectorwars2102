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

## Population Acquisition & Colonist Flow

### Overview: From Humans to Colonists

The transformation from acquired population to working colonists follows this sequence:

1. **Purchase POPULATION Commodity** - Players buy "POPULATION" units from Sector 1 ports (50 credits/unit)
2. **Transport in Cargo** - POPULATION units occupy cargo space (1 cargo space per unit) during transport
3. **Colonize Planet** - Upon colonization, POPULATION units become **colonists** on the planet
4. **Allocate to Roles** - Colonists are assigned to production roles (fuel, organics, equipment)

### Detailed Flow

#### Step 1: Acquiring Population from Sector 1

Every region has a **Sector 1** containing a population hub planet and station:
- **Location**: Sector 1 of any region (Earth in Terran Space, other hubs in player regions)
- **Commodity**: POPULATION (50 credits per unit, fixed price)
- **Availability**: Unlimited supply at Sector 1 ports
- **Trading**: Use standard trading endpoints (`POST /trading/buy`)

**Example Purchase:**
```bash
# Dock at Sol Station (Terran Space, Sector 1)
POST /trading/dock {"port_id": "sol-station-uuid"}

# Purchase 10,000 population units (500,000 credits)
POST /trading/buy {
  "port_id": "sol-station-uuid",
  "resource_type": "POPULATION",
  "quantity": 10000
}
# Result: 10,000 cargo spaces occupied, 500,000 credits deducted
```

#### Step 2: Transporting Population

- **Cargo Requirement**: Each POPULATION unit occupies 1 cargo space
- **Ship Selection**: Choose ships with sufficient cargo capacity
  - Light Freighter: 20 cargo → 20 population max
  - Standard Freighter: 50 cargo → 50 population max
  - Heavy Freighter: 100 cargo → 100 population max
  - Mega Freighter: 200 cargo → 200 population max
- **Multiple Trips**: For 10,000 population colonization requirement, multiple transport runs needed
- **No Special Handling**: POPULATION is treated like any other cargo commodity during transport

#### Step 3: Colonization - Population Becomes Colonists

When colonizing a planet, POPULATION units are converted to **colonists**:

**Colonization Requirements:**
- 10,000 POPULATION units in cargo
- 10,000 credits
- Uncolonized planet

**Colonization Process:**
```bash
# Move to target planet's sector
POST /player/move/{sector_id}

# Land on planet (if needed)
POST /player/land/{planet_id}

# Colonize planet
POST /api/planets/colonize {
  "planet_id": "target-planet-uuid"
}

# Result:
# - 10,000 POPULATION units removed from cargo
# - 10,000 credits deducted
# - Planet status → COLONIZED
# - Planet.colonists = 10,000 (available for allocation)
# - Planet.population = 10,000 (total inhabitants)
```

**Key Transformation:**
- **POPULATION (commodity)** → **colonists (planet workforce)**
- Colonists can be allocated to production roles
- Population represents total inhabitants (grows over time via natural growth)

#### Step 4: Colonist Allocation to Production Roles

Once colonists are on a planet, they can be assigned to production:

**Available Roles:**
- **Fuel Production** - Colonists mine/refine fuel resources
- **Organics Production** - Colonists farm and produce food/biologicals
- **Equipment Production** - Colonists manufacture technology and goods

**Allocation Rules:**
- Total allocated cannot exceed `planet.colonists`
- Colonists can be reassigned at any time
- Unallocated colonists produce nothing but consume fewer resources
- Allocation affects production rates based on planet type efficiency

**Example Allocation:**
```bash
PUT /api/planets/{planetId}/allocate {
  "fuel": 3000,      # 3,000 colonists → fuel production
  "organics": 4000,  # 4,000 colonists → organics production
  "equipment": 3000  # 3,000 colonists → equipment production
}
# Total: 10,000 colonists allocated
# Unused: 0 colonists
```

### Colonist Management

#### Transport System
- **Loading Colonists:**
  - Only possible at Terra (sector 1)
  - Ship must be landed on Terra
  - Ship capacity enforced
  - Cost: 50 credits per colonist
- **Unloading Colonists:**
  - Only to player-owned planets
  - Planet capacity enforced (sum of all roles)
  - By default, unloaded colonists are distributed evenly

#### Resource Production Roles
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

## Future: Colonist Profession System

**Status:** Planned for post-launch implementation

### Overview

The current colonist system uses generic workers assigned to three production roles (fuel, organics, equipment). Future updates will introduce **specialized professions** that provide unique bonuses, unlock advanced capabilities, and create deeper strategic choices.

### Planned Professions

#### Engineering Professions
- **Space Engineers** - Specialize in ship construction and repair
  - Bonus: +25% ship repair speed on planets with Space Engineers
  - Unlock: Advanced ship upgrade facilities
  - Training Time: 30 days (real-time)

- **Structural Engineers** - Specialize in building construction
  - Bonus: -20% building upgrade costs
  - Unlock: Unique defensive structures
  - Training Time: 25 days

- **Mining Engineers** - Specialize in resource extraction
  - Bonus: +30% fuel/ore production efficiency
  - Unlock: Deep core mining facilities
  - Training Time: 20 days

#### Scientific Professions
- **Research Scientists** - Accelerate technological research
  - Bonus: +40% research speed
  - Unlock: Breakthrough technologies (quantum drives, advanced sensors)
  - Training Time: 40 days

- **Agricultural Scientists** - Optimize food production
  - Bonus: +35% organics production, +15% population growth
  - Unlock: Genetically modified crops, hydroponics
  - Training Time: 30 days

- **Medical Professionals** - Improve colonist health and growth
  - Bonus: +20% population growth, disease prevention
  - Unlock: Advanced medical facilities
  - Training Time: 35 days

#### Military Professions
- **Combat Pilots** - Man defensive fighters and combat drones
  - Bonus: +50% planetary defense drone effectiveness
  - Unlock: Elite fighter squadrons
  - Training Time: 25 days

- **Defense Coordinators** - Manage planetary defenses
  - Bonus: +30% turret/shield effectiveness
  - Unlock: Integrated defense networks
  - Training Time: 30 days

- **Strategic Analysts** - Provide intelligence and tactical bonuses
  - Bonus: Early warning system for incoming attacks
  - Unlock: Sector scanning capabilities
  - Training Time: 35 days

#### Economic Professions
- **Trade Specialists** - Optimize commercial operations
  - Bonus: +25% credit generation from trade routes
  - Unlock: Private trade agreements with NPC factions
  - Training Time: 20 days

- **Industrial Managers** - Improve manufacturing efficiency
  - Bonus: +35% equipment production
  - Unlock: Automated factory systems
  - Training Time: 25 days

### Profession System Mechanics

#### Training & Conversion
- **Training Centers**: Planets with Level 3+ Citadels can train specialists
- **Training Time**: Real-time days (accelerated with Research facilities)
- **Training Cost**: Credits + resources based on profession complexity
- **Conversion**: Generic colonists → specialized professions (irreversible)
- **Capacity**: Maximum profession specialization based on colony development phase

**Training Example:**
```bash
# Train 100 generic colonists to become Space Engineers
POST /api/planets/{planetId}/professions/train {
  "profession": "SPACE_ENGINEER",
  "quantity": 100,
  "accelerate": false  # true = pay credits to speed up
}

# Response:
{
  "profession": "SPACE_ENGINEER",
  "trainees": 100,
  "completionDate": "2102-02-15T10:00:00Z",  # 30 days from now
  "cost": {
    "credits": 50000,
    "equipment": 1000
  }
}
```

#### Profession Limitations
- **Max Specialization**: Based on colony development phase
  - Outpost (Phase 1): No profession training
  - Settlement (Phase 2): 10% of colonists can specialize
  - Colony (Phase 3): 25% of colonists can specialize
  - Major Colony (Phase 4): 50% of colonists can specialize
  - Planetary Capital (Phase 5): 75% of colonists can specialize

- **Required Facilities**: Specific buildings needed for certain professions
  - Space Engineers → Orbital Shipyard (Level 2+)
  - Research Scientists → Research Lab (Level 3+)
  - Combat Pilots → Military Academy (Level 2+)

#### Multi-Role Professions
Some advanced professions can fill multiple roles simultaneously:

- **Versatile Engineers**: Can contribute to both equipment production AND ship repair
- **Agri-Scientists**: Produce organics while also researching agricultural tech
- **Combat-Engineers**: Maintain defenses while also contributing to equipment production

### Gameplay Impact

#### Strategic Depth
- **Specialization Choices**: Players must choose which professions to prioritize
- **Planet Roles**: Planets develop distinct identities (military base, research hub, industrial center)
- **Long-term Planning**: Training times encourage strategic foresight
- **Trade-offs**: Specialized colonists are more effective but less flexible

#### Economic Impact
- **Credit Sinks**: Training costs provide meaningful expenditure for wealthy players
- **Resource Requirements**: Training consumes resources, creating demand
- **Production Efficiency**: Well-trained colonies outproduce generic-colonist planets

#### Military Impact
- **Defensive Power**: Planets with Combat Pilots and Defense Coordinators are significantly harder to conquer
- **Fleet Support**: Planets with Space Engineers become strategic repair/refit bases
- **Intelligence Advantage**: Strategic Analysts provide tactical information

### Profession UI Concepts

#### Planet Management Screen
```
┌─────────────────────────────────────────────┐
│ Planet: New Terra (Colony Phase)            │
├─────────────────────────────────────────────┤
│ Total Colonists: 50,000                     │
│ Specialized: 12,500 (25%)                   │
│ Generic Workers: 37,500 (75%)               │
├─────────────────────────────────────────────┤
│ PROFESSIONS:                                │
│ ┌─────────────────────────────────────────┐ │
│ │ Space Engineers:     1,200   [+25%]     │ │
│ │ Mining Engineers:    3,500   [+30%]     │ │
│ │ Research Scientists: 2,800   [+40%]     │ │
│ │ Combat Pilots:       2,000   [+50%]     │ │
│ │ Trade Specialists:   3,000   [+25%]     │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ [Train New Profession] [Manage Allocation] │
└─────────────────────────────────────────────┘
```

#### Training Queue
```
┌─────────────────────────────────────────────┐
│ TRAINING QUEUE                              │
├─────────────────────────────────────────────┤
│ 1. Space Engineers (100) - 15 days left     │
│    └─ Cost: 50,000 credits, 1,000 equipment │
│                                             │
│ 2. Research Scientists (50) - 25 days left  │
│    └─ Cost: 75,000 credits, 500 tech        │
│                                             │
│ [Add to Queue] [Cancel Training] [Rush (€)] │
└─────────────────────────────────────────────┘
```

### Implementation Priority

**Phase 1: Core Professions (Post-Launch)**
- Space Engineers (ship repair bonus)
- Mining Engineers (fuel production bonus)
- Trade Specialists (credit generation)

**Phase 2: Military & Research (Q2 Post-Launch)**
- Combat Pilots (defense bonus)
- Research Scientists (research speed)
- Defense Coordinators (defense systems)

**Phase 3: Advanced Professions (Q3 Post-Launch)**
- Multi-role professions
- Unique profession abilities
- Profession-specific events and missions

### Database Schema Changes (Future)

```python
# New model: ColonistProfession
class ColonistProfession(Base):
    __tablename__ = "colonist_professions"

    id = Column(UUID, primary_key=True)
    planet_id = Column(UUID, ForeignKey("planets.id"))
    profession_type = Column(Enum(ProfessionType))  # SPACE_ENGINEER, etc.
    quantity = Column(Integer)  # Number of colonists with this profession
    training_started = Column(DateTime, nullable=True)
    training_complete = Column(DateTime, nullable=True)
    level = Column(Integer, default=1)  # Profession expertise level (1-10)
    bonus_multiplier = Column(Float, default=1.0)

# New model: ProfessionTrainingQueue
class ProfessionTrainingQueue(Base):
    __tablename__ = "profession_training_queue"

    id = Column(UUID, primary_key=True)
    planet_id = Column(UUID, ForeignKey("planets.id"))
    profession_type = Column(Enum(ProfessionType))
    quantity = Column(Integer)
    started_at = Column(DateTime)
    completes_at = Column(DateTime)
    cost_paid = Column(JSONB)  # {credits: X, equipment: Y, ...}
    status = Column(String)  # TRAINING, COMPLETE, CANCELLED
```

### Related Documentation
- See [Planetary Production](./PLANETARY_PRODUCTION.md) for current production mechanics
- See [Planetary Defense](./PLANETARY_DEFENSE.md) for defense systems
- Future: PROFESSION_SYSTEM.md (dedicated profession documentation)

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