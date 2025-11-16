# Terraforming System — Sector Wars 2102

**Last Updated**: 2025-11-16
**Status**: Core Feature
**Purpose**: Document Genesis Device mechanics, planet creation, and habitability improvement

---

## 🌱 Overview

**Terraforming** is the process of creating new planets or improving the habitability of existing worlds. Players use **Genesis Devices** to create planets in empty sectors or invest in long-term terraforming projects to enhance colony conditions.

**Two Terraforming Approaches**:
1. **Genesis Device Creation**: Instant planet creation in empty sectors
2. **Habitability Improvement**: Gradual enhancement of existing colonies

---

## 🧬 Genesis Device System

Genesis Devices are powerful terraforming tools that can create entirely new planets in previously empty sectors.

### Genesis Device Types

**Standard Genesis** (1 Device)
- **Cost**: 50,000 credits per device
- **Availability**: Class 7+ Technology Ports, Research Stations
- **Effect**: Creates basic planet with random characteristics
- **Starting State**: Level 1 Citadel, 100-1,000 colonists (Outpost phase)

**Enhanced Genesis** (3 Devices)
- **Cost**: 150,000 credits (3 × 50,000)
- **Effect**: Creates higher-quality planet
- **Probability**: Weighted toward better planet types (60% chance M/L/O-Class)
- **Starting State**: Level 1 Citadel, 100-1,000 colonists (Outpost phase)

**Advanced Genesis** (5 Devices + Colony Ship Sacrifice)
- **Cost**: 250,000 credits (5 × 50,000) + Colony Ship (100,000 credits)
- **Total Investment**: 350,000 credits
- **Effect**: Creates high-quality planet, **Colony Ship is destroyed**
- **Probability**: Heavy bias toward best planet types (80% chance M/L/O-Class)
- **Starting State**: **Level 2 Citadel, 5,000 colonists** (Settlement phase)
- **Bonuses**:
  - Level 1 shield generator (1,000 shield strength)
  - 4 automated turrets pre-installed
  - 25 drone capacity (vs 10 standard)
  - Level 1 resource processing facility (+10% production bonus)

---

### Genesis Device Mechanics

**Deployment Process**:
1. **Acquire Genesis Devices**
   - Purchase from Technology Ports or Research Stations
   - Transport in ship with Genesis capacity

2. **Select Empty Sector**
   - Sector must be truly empty (no planets, stations, anomalies)
   - Cannot deploy in protected sectors (faction capital zones)
   - Cannot deploy within 2 sectors of existing planets (minimum spacing)

3. **Deploy Genesis Device(s)**
   - **Standard**: Use 1 device from cargo
   - **Enhanced**: Use 3 devices from cargo
   - **Advanced**: Use 5 devices + sacrifice Colony Ship
     - Ship is consumed in the process
     - Player automatically transferred to escape pod
     - Credits and other items in cargo are preserved

4. **Planet Creation**
   - Planet generates immediately (no waiting period)
   - Planet type determined by Genesis Device type and RNG
   - Citadel created automatically
   - Starting population appears

5. **Automatic Ownership**
   - Player who deployed Genesis Device becomes owner
   - Colony immediately begins resource production
   - Player can dock and manage colony

---

### Genesis Device Planet Type Probabilities

**Standard Genesis (1 Device)**:
| Planet Type | Probability |
|-------------|-------------|
| M_CLASS (Earth-like) | 15% |
| L_CLASS (Mountainous) | 20% |
| O_CLASS (Oceanic) | 20% |
| K_CLASS (Desert) | 20% |
| H_CLASS (Volcanic) | 15% |
| D_CLASS (Barren) | 5% |
| C_CLASS (Ice) | 5% |

**Enhanced Genesis (3 Devices)**:
| Planet Type | Probability |
|-------------|-------------|
| M_CLASS (Earth-like) | 30% |
| L_CLASS (Mountainous) | 30% |
| O_CLASS (Oceanic) | 30% |
| K_CLASS (Desert) | 5% |
| H_CLASS (Volcanic) | 3% |
| D_CLASS (Barren) | 1% |
| C_CLASS (Ice) | 1% |

**Advanced Genesis (5 Devices + Colony Ship)**:
| Planet Type | Probability |
|-------------|-------------|
| M_CLASS (Earth-like) | 40% |
| L_CLASS (Mountainous) | 40% |
| O_CLASS (Oceanic) | 40% |
| K_CLASS (Desert) | 0% |
| H_CLASS (Volcanic) | 0% |
| D_CLASS (Barren) | 0% |
| C_CLASS (Ice) | 0% |

*Note: Advanced Genesis NEVER creates hostile planets (Desert, Volcanic, Barren, Ice)*

---

### Genesis Device Strategic Considerations

**Advantages**:
- Create planets in strategic locations (trade routes, defensive positions)
- No need to find unclaimed natural planets
- Instant ownership (no competition)
- Control over colony placement

**Disadvantages**:
- High cost (50,000+ credits per device)
- Random planet type (though probabilities improve with more devices)
- Cannot choose location of natural resources
- Requires ship with Genesis capacity

**When to Use Genesis Devices**:
- **Frontier Expansion**: Claim territory in unexplored regions
- **Strategic Positioning**: Create defensive outposts on critical trade routes
- **Resource Monopoly**: Place colonies near rare resource spawns
- **Team Coordination**: Establish team headquarters in central location
- **Advanced Genesis**: When you need a well-developed colony immediately (worth the Colony Ship sacrifice)

---

## 🌍 Habitability Improvement (Existing Colonies)

Players can invest in long-term terraforming projects to improve existing colony conditions.

### Terraforming Projects

**Level 1: Basic Environmental Stabilization**
- **Cost**: 100,000 credits + 10,000 ore + 5,000 organics
- **Time**: 72 hours (3 days) real-time
- **Effect**: +5% population growth rate
- **Prerequisite**: Citadel Level 2+

**Level 2: Atmospheric Processing**
- **Cost**: 250,000 credits + 25,000 ore + 15,000 organics
- **Time**: 120 hours (5 days) real-time
- **Effect**: +10% population growth rate (cumulative: +15% total)
- **Prerequisite**: Citadel Level 3+, Level 1 terraform complete

**Level 3: Climate Regulation**
- **Cost**: 500,000 credits + 50,000 ore + 30,000 organics
- **Time**: 168 hours (7 days) real-time
- **Effect**: +15% population growth rate (cumulative: +30% total)
- **Prerequisite**: Citadel Level 4+, Level 2 terraform complete

**Level 4: Ecosystem Engineering**
- **Cost**: 1,000,000 credits + 100,000 ore + 60,000 organics
- **Time**: 240 hours (10 days) real-time
- **Effect**: +20% population growth rate (cumulative: +50% total)
- **Prerequisite**: Citadel Level 5, Level 3 terraform complete

**Level 5: Full Terraforming (Maximum)**
- **Cost**: 2,000,000 credits + 200,000 ore + 120,000 organics
- **Time**: 336 hours (14 days) real-time
- **Effect**: +25% population growth rate (cumulative: +75% total)
- **Prerequisite**: Citadel Level 5, Level 4 terraform complete
- **Additional Bonus**: Planet type improves by one tier (if applicable)

---

### Terraforming Benefits by Planet Type

**Hostile Planet Rescue**:

**Barren Planet** (D_CLASS: -0.1% growth):
- Level 1 terraform: -0.1% → +0.15% (+5% of base, adjusted)
- Level 5 terraform: -0.1% → +0.65% (viable colony!)
- **Planet Type Upgrade**: D_CLASS → H_CLASS (still challenging, but habitable)

**Ice Planet** (C_CLASS: -0.2% growth):
- Level 1 terraform: -0.2% → +0.05% (+5% of base, adjusted)
- Level 5 terraform: -0.2% → +0.55% (viable colony!)
- **Planet Type Upgrade**: C_CLASS → K_CLASS (desert, much more habitable)

**Enhanced Growth Planets**:

**M-Class Planet** (0.5% growth):
- Level 1 terraform: 0.5% → 0.525% (+5%)
- Level 5 terraform: 0.5% → 0.875% (+75%)
- **No Planet Type Upgrade**: Already optimal (M-Class is best)

**Strategic Value**: Terraforming hostile planets is expensive but enables long-term colonization of strategically important locations.

---

## 🎮 Terraforming Strategies

### Early Game (Limited Credits)

**Standard Genesis Device** (50,000 credits)
- Most cost-effective planet creation
- Accept random planet type
- Reroll by abandoning and trying again (expensive but possible)

### Mid Game (Moderate Resources)

**Enhanced Genesis** (150,000 credits)
- Better planet type probabilities
- Reduced risk of hostile planets
- Establish specialized resource colonies

**OR**

**Habitability Improvement Level 1-2** (100,000-350,000 credits)
- Improve existing colonies
- More reliable than gambling on Genesis RNG
- Boost production through higher population growth

### Late Game (High Investment Capacity)

**Advanced Genesis** (350,000 credits + Colony Ship)
- Instant Settlement-level colony (skip Outpost phase)
- Best planet type probabilities
- Strategic outpost creation in contested regions
- Worth the Colony Ship sacrifice for team headquarters

**OR**

**Full Terraforming Level 5** (3,850,000 credits total across all levels)
- Transform hostile planet into productive colony
- +75% population growth
- Planet type upgrade
- Long-term payoff for patient players

---

## 📊 Terraforming ROI Analysis

**Advanced Genesis Example**:
- **Investment**: 350,000 credits
- **Starting State**: 5,000 colonists, Level 2 Citadel, Settlement phase
- **Production Boost**: 5x multiplier vs Outpost
- **Break-Even Time**: ~30 days of passive production
- **Strategic Value**: Immediate defensive stronghold

**Level 5 Terraform Example** (Barren → Volcanic upgrade):
- **Investment**: 3,850,000 credits (all terraform levels)
- **Growth Improvement**: -0.1%/day → +0.65%/day
- **Long-Term Gain**: Viable colony in hostile location
- **Break-Even Time**: ~180 days (6 months) of production
- **Strategic Value**: Permanent colony in otherwise uninhabitable territory

---

## 🔗 Related Systems

- **Colonization**: [PLANETARY_COLONIZATION.md](./PLANETARY_COLONIZATION.md) - Initial colonization methods
- **Citadel System**: [CITADEL_SYSTEM.md](./CITADEL_SYSTEM.md) - Colony infrastructure
- **Colony Management**: [COLONY_MANAGEMENT.md](./COLONY_MANAGEMENT.md) - Population and administration
- **Resource Production**: [PLANETARY_PRODUCTION.md](./PLANETARY_PRODUCTION.md) - Economic output

---

**Last Updated**: 2025-11-16
**Status**: Core Feature - Ready for Implementation
**Related Systems**: Colonization, Citadel, Colony Management, Production
