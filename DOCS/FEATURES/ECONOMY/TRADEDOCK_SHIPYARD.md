# TradeDock Special Station & Shipyard — Sector Wars 2102

**Last Updated**: 2025-11-16
**Status**: Design Phase - Post-Launch Feature
**Purpose**: Premium trading hub + player-driven ship construction facility

---

## Overview

**TradeDock** is a rare, multi-purpose station combining advanced trading capabilities with full shipyard facilities. Unlike standard ports, TradeDocks offer:

1. **Premium Trading Hub**: Special commodities, competitive pricing, bulk discounts
2. **Player Shipyard**: Build custom ships over time by delivering resources and paying construction fees
3. **Economic Anchor**: Regional trade centers driving player interaction and commerce

**Key Philosophy**: Player investment over instant gratification - building your own ship is a journey, not a transaction.

---

## Part 1: Trading Station Features

### Special Trading Capabilities

**Unique Commodities Available:**
- **Advanced Ship Components**: Hull plating, shield generators, engine cores
- **Rare Construction Materials**: Titanium alloys, photonic crystals, quantum shards
- **Specialized Equipment**: Advanced sensors, experimental weapons, luxury fittings
- **Bulk Resources**: Discounted prices on ORE, TECHNOLOGY, EQUIPMENT when buying 1,000+ units

**Trading Advantages:**
- **Better Pricing**: 10-15% better buy/sell spreads than standard Class 0 ports
- **Bulk Discounts**: 5% discount per 1,000 units purchased (up to 20% max)
- **No Transaction Fees**: Standard ports charge 2% transaction tax, TradeDocks charge 0%
- **Extended Inventory**: 10x larger stock than typical ports
- **Priority Docking**: TradeDock berths never full, instant docking available

**Trade Services:**
- Cargo insurance (protect against piracy losses)
- Market trend analysis (ARIA integration for price predictions)
- Trade route optimization (suggest profitable routes)
- Commodity storage (rent warehouse space, store goods long-term)

---

## Part 2: Player Shipyard System

### Construction Philosophy

**Player-Built Ships vs Pre-Fabricated:**

**Pre-Fabricated (Standard Purchase):**
- Instant delivery at shipyards
- Fixed stats, no customization
- Pay full credits upfront
- Standard quality

**Player-Built (TradeDock Construction):**
- Construction time: 3-14 real-time days
- Resource gathering required
- Construction fees paid in installments
- **Benefits**:
  - 5-15% stat bonuses (shields, hull, cargo, speed)
  - Custom paint schemes and naming
  - Ship "builder signature" (crafted by [player name])
  - Potential for unique modifications
  - Lower total cost (if you gather resources yourself)
  - Deeper personal connection to ship

### Dock Slip Rental System

**Availability:**
- Each TradeDock has 12 construction slips
- Slips can be rented by individual players or teams
- First-come, first-served basis
- Waiting list system when all slips occupied

**Rental Costs:**
| Ship Type | Slip Rental (per day) | Total Construction Days | Total Rental Cost |
|-----------|----------------------|------------------------|------------------|
| Scout Ship | 500 credits/day | 3 days | 1,500 credits |
| Fast Courier | 750 credits/day | 4 days | 3,000 credits |
| Light Freighter | 1,000 credits/day | 5 days | 5,000 credits |
| Cargo Hauler | 1,500 credits/day | 7 days | 10,500 credits |
| Defender | 2,000 credits/day | 8 days | 16,000 credits |
| Colony Ship | 2,500 credits/day | 10 days | 25,000 credits |
| Carrier | 3,500 credits/day | 14 days | 49,000 credits |
| Warp Jumper | 5,000 credits/day | 14 days | 70,000 credits |

**Rental Mechanics:**
- Rent charged daily at server reset (midnight UTC)
- Missed payments pause construction (no progress until paid)
- 3 days unpaid → construction cancelled, resources forfeited
- Can pay in advance (max 30 days)

---

## Ship Construction Process

### Step 1: Reserve Dock Slip

**Requirements:**
- Docked at TradeDock station
- Sufficient credits for initial deposit (10% of total project cost)
- Choose ship type to build

**Process:**
```bash
# Dock at TradeDock
POST /api/trading/dock {"port_id": "tradedock-uuid"}

# Browse available dock slips
GET /api/tradedock/{tradedock_id}/slips

# Response:
{
  "totalSlips": 12,
  "availableSlips": 3,
  "occupiedSlips": [
    {
      "slipNumber": 1,
      "owner": "SpaceEngineer42",
      "shipType": "CARRIER",
      "progress": "45%",
      "completionDate": "2102-01-28T14:00:00Z"
    },
    ...
  ],
  "waitingList": 2
}

# Reserve a slip
POST /api/tradedock/{tradedock_id}/slips/reserve {
  "shipType": "DEFENDER",
  "slipNumber": 4,  # optional, auto-assign if omitted
  "advanceRent": 8  # pay 8 days upfront
}

# Response:
{
  "slipNumber": 4,
  "shipType": "DEFENDER",
  "deposit": 7000,  # 10% of 70k base cost
  "dailyRent": 2000,
  "constructionDays": 8,
  "totalRentCost": 16000,
  "resourcesRequired": {...},
  "laborCost": 15000,
  "estimatedCompletion": "2102-01-23T00:00:00Z"
}
```

### Step 2: Deliver Resources

**Resource Requirements (by Ship Type):**

**Scout Ship:**
- 500 ORE (hull plating)
- 300 TECHNOLOGY (sensors, engines)
- 200 EQUIPMENT (internal systems)
- **Total Value**: ~15,000 credits (if purchased at market prices)

**Light Freighter:**
- 1,200 ORE
- 600 TECHNOLOGY
- 400 EQUIPMENT
- **Total Value**: ~35,000 credits

**Defender:**
- 2,000 ORE
- 1,500 TECHNOLOGY
- 1,000 EQUIPMENT
- 500 EXOTIC_TECHNOLOGY (advanced weapon systems)
- **Total Value**: ~85,000 credits

**Cargo Hauler:**
- 2,500 ORE
- 800 TECHNOLOGY
- 1,200 EQUIPMENT
- **Total Value**: ~60,000 credits

**Carrier:**
- 5,000 ORE
- 3,000 TECHNOLOGY
- 2,500 EQUIPMENT
- 1,000 EXOTIC_TECHNOLOGY
- 500 PHOTONIC_CRYSTALS (sensor arrays)
- **Total Value**: ~200,000 credits

**Warp Jumper:**
- 3,000 ORE
- 2,000 TECHNOLOGY
- 1,500 EQUIPMENT
- 2,000 EXOTIC_TECHNOLOGY
- 1,000 QUANTUM_SHARDS
- 500 PHOTONIC_CRYSTALS
- **Total Value**: ~350,000 credits

**Delivery Mechanics:**
```bash
# Check construction project status
GET /api/tradedock/slips/{slipNumber}/project

# Deliver resources to construction project
POST /api/tradedock/slips/{slipNumber}/deliver {
  "resources": {
    "ORE": 1000,
    "TECHNOLOGY": 500,
    "EQUIPMENT": 300
  }
}

# Response:
{
  "delivered": {
    "ORE": 1000,
    "TECHNOLOGY": 500,
    "EQUIPMENT": 300
  },
  "remaining": {
    "ORE": 1000,  # still need 1000 more
    "TECHNOLOGY": 1000,
    "EQUIPMENT": 700,
    "EXOTIC_TECHNOLOGY": 500
  },
  "percentComplete": 35,
  "nextPayment": "Labor Fee: 5,000 credits due in 2 days"
}
```

**Resource Gathering Options:**
1. **Self-Gather**: Trade, mine, produce on planets (cheapest but time-consuming)
2. **Market Purchase**: Buy from ports (expensive but instant)
3. **Team Contribution**: Teammates can deliver resources to your project
4. **Mix & Match**: Gather common resources, buy rare ones

### Step 3: Pay Construction Fees

**Labor Costs (Independent of Resources):**
| Ship Type | Construction Labor Fee |
|-----------|----------------------|
| Scout Ship | 3,000 credits |
| Fast Courier | 5,000 credits |
| Light Freighter | 10,000 credits |
| Cargo Hauler | 15,000 credits |
| Defender | 25,000 credits |
| Colony Ship | 30,000 credits |
| Carrier | 50,000 credits |
| Warp Jumper | 100,000 credits |

**Payment Schedule:**
- **Initial Deposit**: 10% of total project cost (resources + labor + rent)
- **Milestone Payments**: 3 installments during construction
  - 25% progress: 30% of labor fee
  - 50% progress: 30% of labor fee
  - 75% progress: 30% of labor fee
  - 100% completion: Final 10% + delivery fee (1,000 credits)

**Example: Building a Defender**
```
Total Project Cost Breakdown:
├─ Resources: 85,000 credits (market value)
│  └─ If self-gathered: 0 credits actual cost
├─ Labor Fee: 25,000 credits
├─ Dock Rental: 16,000 credits (8 days × 2,000/day)
└─ Total: 126,000 credits (or 41,000 if resources self-gathered)

Payment Schedule:
├─ Initial Deposit: 12,600 credits (10%)
├─ 25% Milestone: 7,500 credits
├─ 50% Milestone: 7,500 credits
├─ 75% Milestone: 7,500 credits
└─ Final Delivery: 3,500 credits (2,500 labor + 1,000 delivery)

Comparison to Pre-Fab Purchase:
├─ Pre-Fab Defender: 70,000 credits (instant)
└─ Player-Built Defender: 41,000 credits (8 days, resources self-gathered)
    Savings: 29,000 credits (41% discount)
    Time Investment: 8 days construction + time to gather resources
```

### Step 4: Wait for Construction

**Construction Timeline:**
- Progress tracked in real-time (server-side)
- Construction phases:
  1. **Frame Assembly** (0-25%): Hull structure built
  2. **Systems Integration** (25-50%): Engines, power, life support installed
  3. **Outfitting** (50-75%): Cargo bays, defensive systems, sensors added
  4. **Final Assembly** (75-100%): Testing, calibration, quality assurance

**Accelerated Construction (Optional):**
- **Space Engineer Bonus**: If you have Space Engineers as teammates/employees
  - Level 1: -10% construction time
  - Level 2: -20% construction time
  - Level 3: -30% construction time
- **Rush Job**: Pay 50% extra labor fee for 2x construction speed
- **Premium Materials**: Deliver 25% extra resources for +5% ship stats

**Construction Events:**
Random events can occur during construction (5% chance per day):
- **Quality Discovery**: Free +2% stat bonus to one category
- **Resource Shortage**: Need to deliver 10% more of one resource
- **Labor Dispute**: Pay extra 2,000 credits to continue on schedule
- **Innovation**: Unlock one unique modification option
- **Inspection Delay**: Construction paused 1 day for safety review

### Step 5: Ship Delivery

**Completion:**
```bash
# Check if ship is ready
GET /api/tradedock/slips/{slipNumber}/project

# Response (when complete):
{
  "status": "COMPLETE",
  "shipReady": true,
  "completionDate": "2102-01-23T00:00:00Z",
  "finalPayment": 3500,
  "customizationAvailable": true
}

# Pay final fee and claim ship
POST /api/tradedock/slips/{slipNumber}/claim {
  "customizations": {
    "paintScheme": "CRIMSON_TIDE",
    "shipName": "Valiant Defender",
    "modifications": ["REINFORCED_HULL"]  # if unlocked
  }
}

# Response:
{
  "success": true,
  "ship": {
    "id": "new-ship-uuid",
    "type": "DEFENDER",
    "name": "Valiant Defender",
    "builder": "YourUsername",
    "builtAt": "TradeDock Alpha, Sector 42",
    "stats": {
      "cargo": 420,      # +5% bonus (base 400)
      "drones": 6,
      "shields": 735,    # +5% bonus (base 700)
      "hull": 840,       # +5% bonus (base 800)
      "speed": 1.05      # +5% bonus (base 1.0)
    },
    "modifications": ["REINFORCED_HULL"],
    "signature": "Crafted with pride by [YourUsername]"
  },
  "slipReleased": true
}
```

**Player-Built Ship Benefits:**
- **Stat Bonuses**: 5-15% across all categories (RNG + quality of materials)
- **Personalization**: Custom name, paint scheme, builder signature
- **Modifications**: 1-3 unique modifications (unlocked through construction events)
- **Resale Value**: +20% resale value due to quality craftsmanship
- **Pride of Ownership**: Built it yourself, deeper connection
- **Cost Savings**: 30-50% cheaper if resources self-gathered

---

## TradeDock Locations & Scarcity

### Distribution

**Rarity**: TradeDocks are extremely rare strategic assets

**Central Nexus**: 3 TradeDocks
- TradeDock Alpha (Sector 1245)
- TradeDock Beta (Sector 3890)
- TradeDock Gamma (Sector 4721)

**Terran Space**: 1 TradeDock
- Sol TradeDock (Sector 50)

**Player Regions**: 0-1 TradeDock depending on region size
- Regions 500+ sectors: 1 TradeDock allowed
- Smaller regions: No TradeDock (must travel to Central Nexus)

**Total Galaxy**: ~4-8 TradeDocks across entire universe

### Strategic Value

**Control & Ownership:**
- TradeDocks are NPC-owned infrastructure (neutral)
- Cannot be destroyed or captured
- Player regions can pay to construct new TradeDock (1 per region max):
  - Cost: 50,000,000 credits
  - Construction time: 90 real-time days
  - Requires 500,000 ORE + 300,000 TECHNOLOGY + 200,000 EQUIPMENT
  - Region owner receives 5% of all shipyard fees as income

**Competition:**
- Limited dock slips create natural scarcity
- Waiting lists form at popular TradeDocks
- Players may travel to distant TradeDocks to find available slips
- Strategic resource gathering near TradeDocks

---

## Economic Balance

### Cost Comparison: Pre-Fab vs Player-Built

**Example: Defender**

**Pre-Fabricated Purchase:**
- Cost: 70,000 credits
- Time: Instant
- Stats: Base (shields 700, hull 800, cargo 400)
- Effort: Dock at shipyard, click buy

**Player-Built (Self-Gathered Resources):**
- Resources: 2,000 ORE + 1,500 TECH + 1,000 EQUIP + 500 EXOTIC
  - Market value: 85,000 credits
  - Actual cost if gathered: 0 credits (just time/effort)
- Labor: 25,000 credits
- Rent: 16,000 credits
- **Total: 41,000 credits + resource gathering time**
- **Time: 8 days construction + gathering time**
- **Stats: +5-15% bonuses (shields 735-805, hull 840-920, cargo 420-460)**
- **Effort: High (trade routes, resource delivery, payment schedule)**

**Player-Built (All Resources Purchased):**
- Resources: 85,000 credits
- Labor: 25,000 credits
- Rent: 16,000 credits
- **Total: 126,000 credits**
- **Time: 8 days**
- **Verdict: Not worth it unless you value customization/bonuses**

**Sweet Spot**: Gather 50-70% of resources, buy rare materials
- Example: Gather ORE/TECH/EQUIP (60k value), buy EXOTIC_TECHNOLOGY (25k)
- Total cost: 66,000 credits (saves 4k vs pre-fab, gets bonuses)

### Balancing Factors

**Why Player-Build?**
✅ Cost savings if self-gathering (30-50% discount)
✅ Stat bonuses (5-15% better performance)
✅ Customization (paint, name, modifications)
✅ Crafting gameplay loop (satisfying progression)
✅ Team collaboration (friends help gather)
✅ Economic gameplay (resource trading, market arbitrage)

**Why Buy Pre-Fab?**
✅ Instant delivery (no waiting)
✅ No resource gathering required
✅ Simple transaction (just credits)
✅ Emergency replacements (ship destroyed, need new one fast)
✅ No risk of construction events/delays

**Target Audience:**
- **Builders**: Players who enjoy crafting, long-term projects, optimization
- **Traders**: Use resource gathering as trading opportunity
- **Teams**: Coordinate resource delivery, share costs
- **Wealthy Players**: Pay for rush jobs + premium materials for max bonuses
- **New Players**: Save credits by gathering common resources early game

---

## UI & Gameplay Flow

### TradeDock Station Interface

```
┌──────────────────────────────────────────────────────────────────┐
│ ⚓ TRADEDOCK ALPHA - SECTOR 1245                                 │
├──────────────────────────────────────────────────────────────────┤
│ [TRADING HUB]  [SHIPYARD]  [STORAGE]  [SERVICES]                │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│ 🏗️  SHIPYARD - CONSTRUCTION SLIPS                                │
│                                                                   │
│ Available Slips: 3 / 12                                          │
│ Waiting List: 2 players                                          │
│                                                                   │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ SLIP #4 - AVAILABLE                                        │  │
│ │                                                            │  │
│ │ [RESERVE THIS SLIP]                                       │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ SLIP #1 - IN USE                                           │  │
│ │ Owner: SpaceEngineer42                                     │  │
│ │ Ship: CARRIER                                              │  │
│ │ Progress: ████████████░░░░░░ 65%                          │  │
│ │ Completion: 5 days, 3 hours                                │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│ ┌────────────────────────────────────────────────────────────┐  │
│ │ YOUR ACTIVE PROJECT - SLIP #7                              │  │
│ │ Ship: DEFENDER "Valiant Defender"                          │  │
│ │ Progress: ████████████████░░ 85%                           │  │
│ │ Phase: Final Assembly                                      │  │
│ │                                                            │  │
│ │ Resources Delivered: ✅ COMPLETE                           │  │
│ │ Next Payment: 2,500 credits (Final + Delivery)             │  │
│ │ Estimated Completion: 1 day, 7 hours                       │  │
│ │                                                            │  │
│ │ [VIEW DETAILS] [MAKE PAYMENT] [CUSTOMIZE]                 │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│ [BROWSE SHIP TYPES] [WAITING LIST] [MY PROJECTS]                │
└──────────────────────────────────────────────────────────────────┘
```

### Construction Project Detail View

```
┌──────────────────────────────────────────────────────────────────┐
│ 🏗️  CONSTRUCTION PROJECT - SLIP #7                               │
│ DEFENDER "Valiant Defender"                                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│ PROGRESS: 85% ████████████████████████████░░░░░                 │
│ Phase: Final Assembly (Testing & Calibration)                    │
│ Completion: 1 day, 7 hours                                       │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│ RESOURCES DELIVERED:                                             │
│ ✅ ORE: 2,000 / 2,000                                            │
│ ✅ TECHNOLOGY: 1,500 / 1,500                                     │
│ ✅ EQUIPMENT: 1,000 / 1,000                                      │
│ ✅ EXOTIC_TECHNOLOGY: 500 / 500                                  │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│ PAYMENT SCHEDULE:                                                │
│ ✅ Initial Deposit: 12,600 credits (PAID)                        │
│ ✅ 25% Milestone: 7,500 credits (PAID)                           │
│ ✅ 50% Milestone: 7,500 credits (PAID)                           │
│ ✅ 75% Milestone: 7,500 credits (PAID)                           │
│ ⏳ Final Payment: 3,500 credits (DUE AT COMPLETION)              │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│ STATS PROJECTION (Estimated +8% bonuses):                        │
│ Cargo: 432 units (+32 from base 400)                             │
│ Shields: 756 points (+56 from base 700)                          │
│ Hull: 864 points (+64 from base 800)                             │
│ Speed: 1.08 sectors/turn (+0.08 from base 1.0)                   │
│ Drones: 6 (unchanged)                                            │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│ CONSTRUCTION EVENTS:                                             │
│ • Day 2: Quality Discovery - Hull bonus increased to +10%        │
│ • Day 5: Innovation Unlocked - REINFORCED_HULL modification      │
│                                                                   │
├──────────────────────────────────────────────────────────────────┤
│ CUSTOMIZATION OPTIONS:                                           │
│ Paint Scheme: [Select...] ▼                                      │
│ Ship Name: Valiant Defender                                      │
│ Modifications: [REINFORCED_HULL] (unlocked via event)            │
│                                                                   │
│ [PREVIEW SHIP] [CANCEL PROJECT] [PROJECT HISTORY]                │
└──────────────────────────────────────────────────────────────────┘
```

---

## Database Schema

```python
# TradeDock station model
class TradeDock(Base):
    __tablename__ = "tradedocks"

    id = Column(UUID, primary_key=True)
    name = Column(String, nullable=False)  # "TradeDock Alpha"
    sector_id = Column(Integer, ForeignKey("sectors.id"))
    region_id = Column(UUID, ForeignKey("regions.id"))
    total_slips = Column(Integer, default=12)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    construction_slips = relationship("ConstructionSlip", back_populates="tradedock")
    sector = relationship("Sector", back_populates="tradedocks")

# Construction slip model
class ConstructionSlip(Base):
    __tablename__ = "construction_slips"

    id = Column(UUID, primary_key=True)
    tradedock_id = Column(UUID, ForeignKey("tradedocks.id"))
    slip_number = Column(Integer, nullable=False)  # 1-12
    status = Column(String, default="AVAILABLE")  # AVAILABLE, RESERVED, IN_PROGRESS, COMPLETE
    rented_by = Column(UUID, ForeignKey("players.id"), nullable=True)
    daily_rent = Column(Integer, nullable=True)
    rent_paid_until = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tradedock = relationship("TradeDock", back_populates="construction_slips")
    project = relationship("ShipConstructionProject", back_populates="slip", uselist=False)

# Ship construction project model
class ShipConstructionProject(Base):
    __tablename__ = "ship_construction_projects"

    id = Column(UUID, primary_key=True)
    slip_id = Column(UUID, ForeignKey("construction_slips.id"), unique=True)
    player_id = Column(UUID, ForeignKey("players.id"))
    ship_type = Column(String, nullable=False)  # DEFENDER, CARRIER, etc.

    # Timeline
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    estimated_completion = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True), nullable=True)
    construction_days = Column(Integer)  # 3-14 days

    # Resources
    resources_required = Column(JSONB)  # {ORE: 2000, TECH: 1500, ...}
    resources_delivered = Column(JSONB, default={})

    # Payments
    total_labor_cost = Column(Integer)
    deposit_paid = Column(Boolean, default=False)
    milestone_25_paid = Column(Boolean, default=False)
    milestone_50_paid = Column(Boolean, default=False)
    milestone_75_paid = Column(Boolean, default=False)
    final_payment_paid = Column(Boolean, default=False)

    # Progress
    progress_percent = Column(Float, default=0.0)  # 0-100
    current_phase = Column(String)  # FRAME, SYSTEMS, OUTFITTING, FINAL

    # Bonuses & customization
    stat_bonuses = Column(JSONB, default={})  # {shields: 1.08, hull: 1.10, ...}
    modifications = Column(ARRAY(String), default=[])  # Unlocked modifications
    paint_scheme = Column(String, nullable=True)
    ship_name = Column(String, nullable=True)

    # Events
    construction_events = Column(JSONB, default=[])  # Log of events during construction

    # Relationships
    slip = relationship("ConstructionSlip", back_populates="project")
    player = relationship("Player", back_populates="construction_projects")
```

---

## API Endpoints

```python
# TradeDock shipyard endpoints
router = APIRouter(prefix="/api/tradedock", tags=["tradedock"])

# List TradeDocks in galaxy
GET /api/tradedock/list

# Get specific TradeDock details + available slips
GET /api/tradedock/{tradedock_id}

# Get dock slip availability
GET /api/tradedock/{tradedock_id}/slips

# Reserve a construction slip
POST /api/tradedock/{tradedock_id}/slips/reserve
Body: {ship_type, slip_number (optional), advance_rent}

# Get project status
GET /api/tradedock/slips/{slip_id}/project

# Deliver resources to project
POST /api/tradedock/slips/{slip_id}/deliver
Body: {resources: {ORE: 1000, TECH: 500}}

# Make payment (milestone or final)
POST /api/tradedock/slips/{slip_id}/payment
Body: {payment_type: "MILESTONE_25" | "MILESTONE_50" | "MILESTONE_75" | "FINAL"}

# Customize ship (during construction or at completion)
POST /api/tradedock/slips/{slip_id}/customize
Body: {paint_scheme, ship_name, modifications}

# Claim completed ship
POST /api/tradedock/slips/{slip_id}/claim

# Cancel project (forfeit resources/payments)
POST /api/tradedock/slips/{slip_id}/cancel
```

---

## Integration with Game Systems

### Profession System (Space Engineers)

Players with **Space Engineers** profession can assist with construction:

**Benefits:**
- **Construction Speed**: -10% to -30% construction time (Level 1-3)
- **Quality Bonus**: +2% to +5% extra stat bonuses (Level 1-3)
- **Cost Reduction**: -5% to -15% labor fees (Level 1-3)
- **Modification Chance**: +10% to +30% chance for construction events (Level 1-3)

**Mechanic:**
- Assign Space Engineers to your project
- Engineers must be on your team or hired as contractors
- Each engineer assigned provides stacking bonuses (max 3 engineers)
- Engineers paid daily rate from project owner

### Team Coordination

**Team Benefits:**
- **Shared Projects**: Team members can contribute resources to any teammate's project
- **Pooled Payments**: Team treasury can pay milestone fees
- **Fleet Building**: Coordinate construction of multiple ships simultaneously
- **Specialization**: Some teammates gather, others build, others pay

**Example Team Workflow:**
```
Team "Star Builders" building 3 ships:
├─ Player A: Building Defender (Slip #3)
│  └─ Player B delivers ORE (1,000 units)
│  └─ Player C delivers TECHNOLOGY (750 units)
│  └─ Team treasury pays milestone fees
│
├─ Player B: Building Cargo Hauler (Slip #7)
│  └─ Player A delivers EQUIPMENT (600 units)
│  └─ Player D pays from personal credits
│
└─ Player C: Building Carrier (Slip #11)
   └─ All teammates contribute resources
   └─ Space Engineer (Player D) assigned for bonuses
```

---

## Future Enhancements

### Planned Features (Post-Launch)

**Advanced Modifications:**
- Weapon system upgrades
- Experimental engine configurations
- Unique cosmetic options
- Performance tuning options

**Construction Blueprints:**
- Save ship configurations as blueprints
- Share blueprints with team/faction
- Sell blueprints to other players
- Blueprint marketplace

**TradeDock Expansion:**
- Player regions can upgrade TradeDock capacity (12 → 24 slips)
- Special event slips (limited-time unique ships)
- Celebrity builder endorsements
- Ship showcases and competitions

**Warp Jumper Construction:**
- Require player to discover "lost blueprints" through exploration
- Multi-stage construction (hull, quantum drive, warp generator)
- Material gathering from multiple regions
- 30+ day construction timeline

---

## Related Documentation

- [Ships.aispec](../../SPECS/Ships.aispec) - Ship types and stats
- [PORT_TRADING.md](./PORT_TRADING.md) - Standard trading mechanics
- [PLANETARY_COLONIZATION.md](../PLANETS/PLANETARY_COLONIZATION.md) - Space Engineers profession
- [TURN_SYSTEM.md](../GAMEPLAY/TURN_SYSTEM.md) - Turn costs and economy

---

**Status**: Design complete, ready for implementation planning
**Estimated Development Time**: 4-6 weeks (Phase 1: Basic shipyard)
**Priority**: High - Adds deep crafting system and economic gameplay loop
**Last Updated**: 2025-11-16
