# Colony Management — Sector Wars 2102

**Last Updated**: 2025-11-16
**Status**: Core Feature
**Purpose**: Document colony lifecycle, population management, and administrative actions

---

## 🏘️ Overview

**Colony Management** encompasses all player actions related to administering planetary settlements. Players manage population growth, resource allocation, defensive preparations, and colony development from initial outpost to planetary capital.

**Key Concept**: A colony is the **population** living within a **citadel** on a **planet**.

---

## 📈 Colony Lifecycle

Colonies progress through five development phases as population grows and citadels upgrade:

### Phase 1: Outpost (Citadel Level 1)

**Population**: 0-1,000 colonists
**Characteristics**:
- Initial settlement phase
- Survival-focused operations
- Basic resource production
- Minimal defensive capabilities
- High vulnerability

**Starting Population**:
- Standard colonization: 100-1,000 colonists (requires transport)
- Basic Genesis (1 device): 100-1,000 colonists (random)
- Enhanced Genesis (3 devices): 100-1,000 colonists (random)
- Advanced Genesis (Colony Ship): 5,000 colonists (starts at Settlement phase)

**Management Focus**:
- Establish resource production
- Build up population to 1,000 (citadel max capacity)
- Prepare resources for citadel upgrade

---

### Phase 2: Settlement (Citadel Level 2)

**Population**: 1,001-5,000 colonists
**Characteristics**:
- Expanding infrastructure
- Moderate production capacity
- Improved defenses (basic shield generator)
- Regional stability

**Management Focus**:
- Optimize colonist allocation for resource production
- Expand defensive drones (up to 25)
- Build toward 5,000 population for next upgrade
- Establish trade routes

---

### Phase 3: Colony (Citadel Level 3)

**Population**: 5,001-15,000 colonists
**Characteristics**:
- Established settlement
- Specialized production facilities
- Strong defensive infrastructure
- Recognized territorial claim

**Management Focus**:
- Specialize colony for specific resources
- Invest in production upgrades
- Expand defensive capabilities (up to 50 drones)
- Prepare for major colony status

---

### Phase 4: Major Colony (Citadel Level 4)

**Population**: 15,001-50,000 colonists
**Characteristics**:
- Industrial-scale operations
- Military-grade defenses
- Regional economic hub
- Strategic value

**Management Focus**:
- Maximize production efficiency
- Deploy advanced defensive systems (orbital platforms, rail guns)
- Manage large-scale resource storage
- Consider team headquarters designation

---

### Phase 5: Planetary Capital (Citadel Level 5)

**Population**: 50,001-200,000 colonists
**Characteristics**:
- Massive metropolitan center
- Empire-level production
- Fortress-level defenses
- Political and economic significance

**Management Focus**:
- Maintain optimal production balance
- Coordinate multi-colony empire
- Defend against major threats
- Generate substantial passive income

---

## 👥 Population Management

### Population Growth

**Growth Rate** (varies by planet type):
- **M_CLASS** (Earth-like): +0.5% per day
- **L_CLASS** (Mountainous): +0.3% per day
- **O_CLASS** (Oceanic): +0.4% per day
- **K_CLASS** (Desert): +0.2% per day
- **H_CLASS** (Volcanic): +0.1% per day
- **D_CLASS** (Barren): -0.1% per day (negative growth!)
- **C_CLASS** (Ice): -0.2% per day (negative growth!)

**Factors Affecting Growth**:
- ✅ Planet type (habitability)
- ✅ Resource availability (well-fed population grows faster)
- ✅ Citadel level (overcrowding penalty if at capacity)
- ✅ Defensive stability (attacks reduce growth)
- ✅ Terraforming level (improved habitability increases growth)

**Negative Growth**:
- Barren and Ice planets have **negative population growth**
- Without continuous colonist transport, population will decline
- Strategic challenge: maintain hostile world colonies through immigration

---

### Colonist Allocation

Colonists can be assigned to three resource production roles:

**Allocation Categories**:
1. **Fuel Production**: Colonists produce ore/fuel
2. **Organics Production**: Colonists produce organics
3. **Equipment Production**: Colonists produce equipment

**Allocation Mechanics**:
- Total allocation must equal total population
- Can be adjusted at any time (no cost, instant)
- Production calculated hourly based on current allocation
- Strategic decisions based on planet type efficiencies

**Example Allocations**:

**Oceanic Planet** (O_CLASS: 1.5x fuel, 0.4x organics, 0.6x equipment):
- **Optimal**: 70% fuel, 15% organics, 15% equipment (maximize fuel advantage)

**Mountainous Planet** (L_CLASS: 0.6x fuel, 0.4x organics, 1.5x equipment):
- **Optimal**: 15% fuel, 15% organics, 70% equipment (maximize equipment advantage)

**Balanced Planet** (M_CLASS: 1.0x all):
- **Flexible**: Allocate based on empire needs, no inherent advantage

---

## 🎮 Colony Management Actions

### Daily Management Tasks

**Population Monitoring**:
- Check current population and growth rate
- Ensure not overcrowded (at citadel capacity)
- Monitor resource consumption

**Resource Collection**:
- Withdraw produced resources from planet storage
- Transfer to ships for transport to markets
- Manage storage capacity (production stops when full)

**Colonist Allocation Adjustment**:
- Rebalance based on resource needs
- Adapt to market price changes
- Optimize for planet type efficiencies

**Defensive Checks**:
- Monitor drone count and health
- Check shield strength
- Review recent attack logs (if any)

---

### Strategic Management Tasks

**Citadel Upgrades**:
- Track progress toward upgrade requirements
- Stockpile required resources
- Plan upgrade timing (construction takes days)
- See [CITADEL_SYSTEM.md](./CITADEL_SYSTEM.md) for upgrade details

**Production Upgrades**:
- Invest in ore/organics/equipment production upgrades
- Each level: +10% production for that resource
- Max upgrade level: 10 per resource
- Prioritize based on colony specialization

**Defensive Investments**:
- Deploy additional drones (cost: 1,000 credits each)
- Upgrade shield generators
- Install orbital platforms (Level 4+ citadels)
- Deploy rail gun batteries (Level 4+ citadels)
- See [PLANETARY_DEFENSE.md](./PLANETARY_DEFENSE.md) for details

**Terraforming Projects**:
- Invest in habitability improvements
- Increase population growth rate
- Reduce negative environmental effects
- See [TERRAFORMING.md](./TERRAFORMING.md) for details

---

### Ownership and Transfers

**Ownership Rights**:
- Only colony owner can manage population allocation
- Only owner can initiate citadel upgrades
- Only owner can access safe storage
- Only owner can grant/revoke landing rights

**Transfer Ownership**:
- Owner can transfer colony to another player
- Recipient must accept transfer
- Transfer fee: 5% of estimated colony value
- All citadel upgrades, defenses, and safe contents transfer
- Production continues uninterrupted

**Abandoned Colonies**:
- If owner inactive for 90 days, colony enters "abandoned" state
- Other players can claim abandoned colonies
- Claim cost: 50,000 credits + 5,000 ore/organics/equipment
- Prevents colony decay from inactive players

---

### Landing Rights Management

**Access Control**:
- Owner can grant or deny landing rights to specific players
- Team members can be granted automatic landing rights
- Deny list prevents specific players from landing
- Useful for protecting colonies from raids

**Landing Rights Actions**:
- **Public Access**: Anyone can land (default for trading hubs)
- **Team Only**: Only team members can land (secure territory)
- **Private**: Only owner can land (maximum security)
- **Custom Whitelist**: Specific players granted access
- **Deny List**: Block hostile players from landing

---

## 📊 Colony Performance Metrics

Players can view detailed colony statistics:

**Population Metrics**:
- Current population / Max capacity
- Growth rate (% per day)
- Days until citadel capacity reached
- Historical population graph

**Production Metrics**:
- Resource production rates (units per hour)
- Storage capacity remaining
- Days until storage full (at current rate)
- Total production since colonization

**Economic Metrics**:
- Estimated colony value (based on citadel level, population, upgrades)
- Total credits invested
- Return on investment (production value vs investment)
- Passive income rate

**Defensive Metrics**:
- Current defensive strength rating (0-100 scale)
- Drone count and health
- Shield strength and regeneration rate
- Recent attack history

---

## 🌍 Multi-Colony Empire Management

Players owning multiple colonies face empire-level management challenges:

**Resource Distribution**:
- Balance production across colonies based on planet types
- Specialize each colony for optimal output
- Coordinate resource transport between colonies

**Defensive Strategy**:
- Identify high-value colonies requiring heavy defense
- Establish defensive perimeters across territory
- Coordinate team defense of strategic colonies

**Economic Optimization**:
- Calculate empire-wide production efficiency
- Identify underperforming colonies for improvement
- Plan expansion based on resource needs

**Example Multi-Colony Empire**:
```
Player Empire: 5 Colonies
├── Colony Alpha (Oceanic, Level 4) - Fuel specialist
├── Colony Beta (Mountainous, Level 3) - Equipment specialist
├── Colony Gamma (M-Class, Level 5) - Capital, balanced production
├── Colony Delta (Desert, Level 2) - Organics specialist
└── Colony Epsilon (Volcanic, Level 2) - High-risk equipment production
```

---

## 🔗 Related Systems

- **Citadel System**: [CITADEL_SYSTEM.md](./CITADEL_SYSTEM.md) - Structure, levels, upgrades
- **Planetary Defense**: [PLANETARY_DEFENSE.md](./PLANETARY_DEFENSE.md) - Defensive systems
- **Resource Production**: [PLANETARY_PRODUCTION.md](./PLANETARY_PRODUCTION.md) - Production mechanics
- **Terraforming**: [TERRAFORMING.md](./TERRAFORMING.md) - Planet creation and habitability improvement
- **Colonization**: [PLANETARY_COLONIZATION.md](./PLANETARY_COLONIZATION.md) - Initial colonization process

---

**Last Updated**: 2025-11-16
**Status**: Core Feature - Ready for Implementation
**Related Systems**: Citadel, Defense, Production, Terraforming
