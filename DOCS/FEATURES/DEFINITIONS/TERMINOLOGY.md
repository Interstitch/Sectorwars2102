# SectorWars 2102 - Comprehensive Terminology

**Last Updated**: 2025-11-16
**Version**: 1.0
**Purpose**: Definitive reference for all game terms, concepts, and systems

---

## 🌌 Universe Structure

### Hierarchy Overview

```
Galaxy
├── Region (Central Nexus, Terran Space, Player-owned)
    ├── Zone (Security/policing boundaries)
    │   └── Sectors (assigned by sector_number range)
    └── Cluster (Navigation/organizational groups)
        └── Sectors (same sectors, different grouping)
```

**Important**: Zones and Clusters are **orthogonal dimensions** - sectors have BOTH a zone_id AND a cluster_id.

### Galaxy
The entire game universe containing all regions, sectors, and players. The galaxy consists of:
- **Central Nexus**: 5,000-sector hub region (1 zone)
- **Terran Space**: 300-sector starting region (3 zones)
- **Player-Owned Regions**: Variable sectors (100-1,000), customizable zones

### Region
A distinct area of space with its own governance and zones. Three region types exist:

**Central Nexus** (`central_nexus`)
- **Size**: 5,000 sectors
- **Zones**: 1 zone ("The Expanse")
- **Purpose**: Universal trade hub connecting all regions
- **Characteristics**: Sparse infrastructure, light policing, moderate danger
- **Access**: All players can always return via quantum warp tunnels

**Terran Space** (`terran_space`)
- **Size**: 300 sectors
- **Zones**: 3 zones (Federation Space, Border Regions, Frontier Space)
- **Purpose**: Starting region for new players
- **Characteristics**: Standard infrastructure, progressive security (high → low)
- **Access**: Default starting location

**Player-Owned Region** (`player_owned`)
- **Size**: 100-1,000 sectors (variable)
- **Zones**: 3 zones by default (Federation, Border, Frontier) - customizable
- **Purpose**: Private governance and custom rules
- **Subscription**: $25/month for ownership, $5/month for citizenship
- **Customization**:
  - Governance type (Democracy, Autocracy, Council Republic)
  - Tax rates (5-25%)
  - PvP rules and combat restrictions
  - Trade policies and bonuses
  - Immigration controls
  - Cultural identity and themes
  - Zone configuration (add/remove/adjust zones)

### Zone
**Security and policing regions within parent Regions**. Zones define law enforcement levels, danger ratings, and sector boundaries.

**Key Properties**:
- **Belongs to Region**: Each zone has a parent region
- **Sector Boundaries**: Defined by start_sector and end_sector numbers
- **Security Characteristics**: Policing level (0-10) and danger rating (0-10)
- **Orthogonal to Clusters**: Zone boundaries can split across cluster boundaries

**Zone Types**:
- **EXPANSE**: Central Nexus's single massive zone
- **FEDERATION**: High security, low danger (heavily policed space)
- **BORDER**: Moderate security, moderate danger (transition areas)
- **FRONTIER**: Low security, high danger (lawless space)

**Examples**:
- Central Nexus: "The Expanse" (sectors 1-5000, policing=3, danger=6)
- Terran Space Federation: "Federation Space" (sectors 1-100, policing=9, danger=1)
- Terran Space Border: "Border Regions" (sectors 101-200, policing=5, danger=4)
- Terran Space Frontier: "Frontier Space" (sectors 201-300, policing=2, danger=8)

### Cluster
**Navigation and organizational groups** of interconnected sectors. Clusters typically contain **10-25 sectors** linked by warp tunnels, forming local navigation networks.

**Key Properties**:
- **Belongs to Region**: Each cluster has a parent region
- **Navigation Purpose**: Helps players organize sector exploration
- **Orthogonal to Zones**: Cluster membership independent of zone assignment
- **Warp Networks**: Sectors in same cluster often have direct warp connections
- **Nebula Properties**: ~20% of clusters contain nebulae (see Nebula below)

**Cluster Types**: Standard, Resource Rich, Population Center, Trade Hub, Military Zone, Frontier Outpost, Contested, Special Interest

### Nebula
**Cluster-level property** creating visually stunning environments with unique gameplay mechanics. Nebulae are NOT individual sectors - they are properties of clusters that affect multiple sectors within that cluster.

**Key Characteristics**:
- **Coverage**: 30-70% of cluster sectors (rarely 100%)
- **Types**: 6 types (Crimson, Azure, Emerald, Violet, Amber, Obsidian)
- **Density Gradient**: Core sectors (100% density) vs edge sectors (30-70% density)
- **Quantum Field Strength**: 20-100 (determines quantum shard spawn rates)
- **Gameplay Impact**: Sensor interference, navigation difficulty, quantum shard gathering, combat stealth

**Nebula Types**:
- **Crimson** (Red): Very high quantum activity, quantum shards
- **Azure** (Blue): Stable quantum fields, photonic crystals
- **Emerald** (Green): Organic resources, production bonuses
- **Violet** (Purple): Exotic materials, rare spawns
- **Amber** (Orange): Radiation hazards, radioactives
- **Obsidian** (Dark): Stealth operations, sensor masking

**See**: GALAXY_COMPONENTS.md for complete nebula documentation

### Sector
The fundamental unit of space in the game. Each sector can contain:
- **Warp Tunnels** (connections to other sectors)
- **Ports** (trading stations)
- **Planets** (colonizable worlds)
- **Ships** (player and NPC vessels)
- **Drones** (defensive or offensive units)
- **Genesis Devices** (planet-creation tools)

Sectors are identified by numeric IDs (Sector 1 = Earth/Sol Station).

**Special Types**: NORMAL, NEBULA (inherits from cluster), ASTEROID_FIELD, BLACK_HOLE, RADIATION_ZONE, WARP_STORM

**Dual Grouping**: Every sector has BOTH a zone_id (security) AND cluster_id (navigation) - these are orthogonal dimensions.

### Warp Tunnel
Special pathways allowing **instantaneous travel between distant sectors**. Unlike standard warps (adjacent sectors), warp tunnels span across clusters, zones, or regions.

**Types**:
- **Natural Warp Tunnel**: Permanent, must be discovered through exploration
- **Artificial Warp Tunnel**: Player-created using Quantum Crystals (5 crystals = 25 quantum shards)

**Mechanics**:
- **Turn Cost**: 1-3 turns based on distance
- **Discovery**: Natural tunnels must be found before use
- **Access Control**: Some tunnels have factional or player restrictions
- **Disruption**: Warp storms can temporarily disable tunnels

**Artificial Tunnel Requirements**:
- Warp Jumper ship (sacrificed in construction)
- 5 Quantum Crystals (assembled from 25 Quantum Shards)
- 100,000-500,000 credits
- 7-14 real-time days build time

**See**: WARP_GATE_CONSTRUCTION.md for complete construction process

### Quantum Jump
A special ability of the **Warp Jumper** ship that allows directed movement of 5-10 sectors in a targeted direction. Has a 24-hour cooldown. Different from using warp tunnels - this is ship-based FTL, not infrastructure.

---

## 🚀 Entities & Objects

### Ship
Player-controlled spacecraft. Each ship has:
- **Cargo Capacity**: Maximum units of resources/commodities
- **Drone Capacity**: Maximum combat drones (0-12)
- **Genesis Capacity**: Maximum Genesis Devices (0-5)
- **Speed**: Sectors per turn (0.4-2.5)
- **Shield Points**: Defensive energy shields
- **Hull Points**: Structural integrity

See [SHIP_TYPES.md](./SHIP_TYPES.md) for complete ship specifications.

### Escape Pod
An indestructible survival craft. Every player has one. Key features:
- **Indestructible**: Cannot be destroyed under any circumstances
- **High Turn Cost**: Consumes substantially more turns to move between sectors
- **Credit Protection**: Player retains all credits when ejected to escape pod
- **Cargo Loss**: All cargo is lost when ship is destroyed
- **Teammate Docking**: Can dock with teammate's ship for transport

### Planet
A colonizable world found in sectors. Planets provide:
- **Resource Production**: Generate commodities automatically
- **Passive Income**: Credits from population and infrastructure
- **Strategic Value**: Territory control and team benefits

**Planet Types**:
- **Uncolonized**: Available for claiming (requires 10,000 population + 10,000 credits)
- **Colonized**: Owned by player or team, producing resources
- **Specialized**: Focused on specific production (Agricultural, Industrial, Military, Research, Balanced)

**Infrastructure**:
- **Factory**: Equipment production
- **Farm**: Organics/food production
- **Mine**: Ore extraction
- **Defense**: Turrets, shields, drones (levels 1-10)
- **Research**: Technology development

### Port (Trading Station)
A space station where players trade commodities. Ports have **classes** (0-11) that determine what they buy and sell:

- **Class 0 (Sol Station)**: Buys/sells all commodities
- **Class 1**: Buys Ore, sells Basic Food/Fuel/Technology
- **Class 2**: Buys Basic Food, sells Ore/Fuel/Technology
- **Class 3**: Buys Fuel, sells Ore/Basic Food/Technology
- **Class 4**: Buys Technology, sells Ore/Basic Food/Fuel
- **Class 5**: Buys Luxury Goods, sells Ore/Basic Food/Fuel/Technology
- **Class 6**: Buys Ore/Basic Food, sells Fuel/Technology
- **Class 7**: Buys Fuel/Technology, sells Ore/Basic Food
- **Class 8 (Black Hole)**: Buys all commodities, sells nothing
- **Class 9 (Nova)**: Sells all commodities, buys nothing
- **Class 10**: Buys Gourmet Food, sells Technology/Luxury Goods
- **Class 11**: Buys Exotic Technology, sells advanced components

**Port Actions**:
- **Dock**: Attach to port (costs 1 turn)
- **Undock**: Leave port (costs 1 turn)
- **Buy**: Purchase commodities
- **Sell**: Sell commodities
- All trading while docked is instant

### Drone
Autonomous combat unit. Types include:
- **Combat Drone**: High firepower, attacks enemies automatically
- **Mining Drone**: Collects ore and resources from sectors
- **Scout Drone**: Extended sensor range, intel gathering
- **Defense Drone**: Protects ports/planets, high shields
- **Research Drone**: Gathers data, discovers anomalies

**Drone Mechanics**:
- **Cost**: 1,000 credits each (combat drones from military outposts)
- **Deployment**: Can be deployed to sectors for autonomous operation
- **Operational Modes**: Passive, Aggressive, Defensive, Mining
- **Upgrades**: Shields, weapons, sensors, cargo, engines
- **Health**: 0-100 (can be damaged and repaired)
- **Batch Operations**: Can deploy/recall multiple drones at once

### Genesis Device
A planet-creation tool. Allows players to create new planets in empty sectors. Key features:
- **Deployment**: Creates a new colonizable planet in current sector
- **Limited Capacity**: Ships can only carry 0-5 depending on ship type
- **Strategic Use**: Enables custom territory expansion

---

## 💰 Resources & Commodities

### Credits
The universal currency. Used for:
- Purchasing ships, drones, and equipment
- Trading commodities at ports
- Colonizing planets
- Paying taxes in regional territories
- **Never lost** when ship is destroyed (stored virtually, not on ship)

### Core Trading Commodities

**Ore**
- Raw materials for construction and manufacturing
- Price: 15-45 credits per unit
- Highest value in industrial sectors

**Basic Food**
- Standard nutritional products
- Price: 8-25 credits per unit
- Required for colonization and population survival

**Gourmet Food**
- Premium foodstuffs and exotic ingredients
- Price: 30-70 credits per unit
- Enhances colony development and production efficiency

**Fuel**
- Refined energy for ships and stations
- Price: 20-60 credits per unit
- Consumption increases with ship size

**Technology**
- Advanced components and equipment
- Price: 50-120 credits per unit
- Enables upgrades and infrastructure

**Exotic Technology**
- Rare prototypes and experimental devices
- Price: 150-300 credits per unit
- Essential for advanced capabilities

**Luxury Goods**
- Rare and desirable high-end merchandise
- Price: 75-200 credits per unit
- Highest profit margins, volatile markets

### Strategic Resources

**Population (Colonists)**
- Colonists seeking new worlds
- Cost: 50 credits per unit (purchased from Earth/Sector 1)
- Usage: Required for colonizing planets (minimum 10,000 units)
- Transport: Each unit occupies 1 cargo space
- Growth: Population grows naturally over time on planets

**Quantum Shards**
- Crystalline fragments with exotic energy
- Acquisition: Found in nebulae and anomalies
- Rarity: Very rare, dangerous regions
- Usage: Five shards combine to make one Quantum Crystal

**Quantum Crystals**
- Powerful energy matrices
- Creation: Assemble five Quantum Shards at specialized facilities
- Usage: Essential for constructing player-created warp tunnels
- Rarity: Extremely rare due to shard collection difficulty

**Prismatic Ore**
- Unique molecular structure mineral
- Rarity: Extremely rare (1 in 10,000 asteroids)
- Usage: Ultra-lightweight hull reinforcement, superior ship construction

**Photonic Crystals**
- Naturally occurring nebula crystals
- Rarity: Very rare (specific nebula types only)
- Usage: Advanced sensors and energy weapon enhancement

---

## 🧠 AI Systems

### ARIA (Adaptive Reactive Intelligence Assistant)
Your personal AI companion that grows and evolves with you throughout the game. ARIA is designed to enhance your trading experience through personalized intelligence.

**Core Capabilities**:
- **Trading Intelligence**: Real-time market analysis and pattern recognition
- **Market Manipulation Detection**: Identifies suspicious trading patterns with confidence levels
- **Strategic Optimization**: Recommendations for optimal trade timing and route planning
- **Personal Trading Pattern Evolution**: Learns YOUR specific preferences, risk tolerance, and successful strategies
- **Natural Language Chat Interface**: Conversational trading assistance with context awareness
- **Exploration-Based Learning**: Only knows sectors YOU have visited (personal, not generic AI)
- **Encrypted Memory**: Triple-encrypted personal data (π, e, φ, γ constants) stored locally
- **Cross-System Intelligence**: Integrates combat, exploration, and colony management insights
- **3D Strategic Overlays**: Visual recommendations in galaxy visualization
- **Ghost Trading Simulation**: Risk-free trade testing before real execution
- **Mobile Voice Integration**: Natural speech recognition and audio notifications

**Learning Modes**:
- **Educational Mode**: Explains quantum concepts for beginners
- **Expert Mode**: Advanced quantum mechanics terminology and analysis
- **Research Mode**: Deep quantum physics insights and theory

**First Login Role**: During first login, ARIA takes the role of a Security Guard, using dynamic AI dialogue to challenge and verify player identity through adaptive questioning.

**Privacy**: Your ARIA memories are yours alone. No two ARIA instances are identical - she becomes uniquely yours through your shared experiences.

### Trading Intelligence AI
System that learns from player behavior to provide:
- Personalized trading recommendations
- Route optimization
- Market trend prediction
- Price forecasting
- Risk assessment for specific trades
- Performance statistics and learning metrics

---

## 👥 Player Systems

### Turns
The fundamental action currency. Key mechanics:
- **Daily Allocation**: 1,000 turns per day
- **Turn Costs**: Most actions consume turns (travel, trading, combat initiation, planetary development)
- **No Turn Cost**: Defending against attacks, upgrading ships
- **No Carryover**: Unused turns do not accumulate to next day
- **Strategic Resource**: Turn management crucial for daily progress

**Turn Costs by Action**:
- Sector travel: 1 turn (modified by ship speed)
- Docking: 1 turn
- Undocking: 1 turn
- Trading (buy/sell): 0 turns while docked
- Combat initiation: Varies
- Defending: 0 turns

### Team
A cooperative alliance of up to **4 players maximum**. Teams provide:
- **Shared Resources**: Team treasury with 12 resource types
- **Collective Defense**: Coordinated territory protection
- **Team Planets**: Shared production benefits
- **Fleet Operations**: Multi-ship coordinated combat
- **Member Permissions**: Configurable roles (Leader, Officer, Member)
  - Can invite new members
  - Can kick members
  - Can manage treasury
  - Can create/manage fleets

**Team Treasury Resources**:
Ore, Basic Food, Gourmet Food, Fuel, Technology, Exotic Technology, Luxury Goods, Population, Quantum Shards, Quantum Crystals, Prismatic Ore, Photonic Crystals

### Fleet
Team-based coordinated combat unit. Features:
- **Team Requirement**: Player must be in a team to create/manage fleets
- **Formations**: Standard, Wedge, Defensive, Offensive, Scatter
- **Roles**: Attacker, Defender, Scout, Support, Commander
- **Status**: Forming, Ready, Deployed, In Combat, Disbanded
- **Statistics**: Total firepower, shields, hull, average speed, morale, supply level
- **Fleet Battles**: Multi-ship coordinated combat operations

**Formation Effects**:
- **Standard**: Balanced offense/defense
- **Wedge**: +20% offense, -10% defense
- **Defensive**: +30% defense, -20% offense
- **Offensive**: +30% offense, -30% defense
- **Scatter**: +30% evasion, -40% coordination

### Reputation
A numeric value (-1000 to +1000) representing standing with each faction. Affects:
- **Trading Prices**: Higher reputation = better prices
- **Mission Availability**: Unlock harder missions with higher reputation
- **Territory Access**: Hostile factions may attack on sight
- **Special Rewards**: Faction-exclusive items and bonuses

**Reputation Levels**:
- **-1000 to -500 (Hostile)**: Attacked on sight, no trading
- **-499 to -100 (Unfriendly)**: High prices, basic missions only
- **-99 to +99 (Neutral)**: Normal prices, standard missions
- **+100 to +499 (Friendly)**: Discount prices, advanced missions
- **+500 to +1000 (Allied)**: Best prices, elite missions, special rewards

### Faction
NPC organizations that control territory and offer missions. Players can:
- Build reputation through missions, trading, and territorial defense
- Access faction-exclusive missions based on reputation
- Benefit from pricing modifiers in faction-controlled ports
- Receive territory information about faction-controlled sectors

**Faction Missions by Difficulty**:
- **Easy**: +10-50 reputation, basic rewards
- **Medium**: +50-150 reputation, good rewards
- **Hard**: +150-300 reputation, excellent rewards
- **Extreme**: +300-500 reputation, legendary rewards

**Mission Types**: Delivery, Combat, Reconnaissance, Escort, Defense

### Messages
In-game communication system supporting:
- **Player-to-Player**: Direct private messages
- **Team Broadcast**: Messages to all team members
- **Message Threading**: Conversation organization
- **Priority Levels**: Low, Normal, High, Urgent
- **Moderation**: Flagging system for abuse prevention
- **Message Status**: Read/unread tracking

---

## ⚔️ Combat & Defense

### Combat Initiation
Starting combat **costs turns**. Can target:
- **Ships**: Other player or NPC vessels
- **Planets**: Colonized worlds
- **Ports**: Trading stations
- **Drones**: Autonomous units

### Combat Defense
Defending against attacks **costs zero turns**. Players automatically defend when:
- Another player attacks your ship
- Your planet is targeted
- Your drones are attacked
- You enter hostile territory

### Combat Resolution
Determined by:
- **Number of Drones**: Both attacker and defender
- **Ship Type**: Defensive capabilities and firepower
- **Shields**: Energy defensive layer
- **Hull**: Structural integrity
- **Random Elements**: Tactical decisions and luck
- **Formation** (for fleets): Formation bonuses/penalties

### Shield Points
Energy-based defensive layer. Shields:
- Absorb damage before hull takes hits
- Regenerate slowly over time
- Can be upgraded with technology
- Vary by ship type (150-900 points)

### Hull Points
Structural integrity of ship. Hull:
- Takes damage after shields depleted
- Represents ship destruction when reaching 0
- Can be repaired at ports
- Varies by ship type (200-900 points)

### Citadel
Planetary defense structure. Can be upgraded in levels (1-10):
- **Turrets**: Automated defensive weapons
- **Shields**: Planetary energy barriers
- **Drones**: Automated defense craft

---

## 🏛️ Governance & Politics

### Governance Types

**Democracy**
- Citizens vote on policies and elections
- Majority rule on proposals
- Elected representatives
- Voting periods with configurable thresholds

**Autocracy**
- Owner-controlled governance
- Unilateral decision-making
- Rapid policy implementation
- No citizen voting required

**Council Republic**
- Elected council of representatives
- Council votes on proposals
- Balanced power structure
- Representative democracy

### Policy Proposals
Governance changes that can be voted on:
- **Tax Rates**: Regional revenue collection (5-25%)
- **PvP Rules**: Combat restrictions and regulations
- **Trade Policies**: Economic bonuses and restrictions
- **Immigration**: Entry requirements and controls
- **Starting Credits**: New citizen initial resources (100-10,000)
- **Economic Specialization**: Trade bonuses by resource type (1.0-3.0x)

### Elections
Democratic selection of leadership positions:
- **Governor**: Regional leader
- **Council Members**: Representative body
- **Ambassadors**: Inter-regional diplomats
- **Term Management**: Fixed term lengths
- **Candidate Platforms**: Campaign promises and goals
- **Weighted Votes**: Voting power based on citizen status

---

## 🌐 Infrastructure & Technical

### Multi-Regional Architecture
The game's technical foundation supporting multiple concurrent regional territories:
- **Docker-Based Deployment**: Containerized services
- **Regional Isolation**: Dedicated databases per region
- **Auto-Scaling**: Dynamic resource allocation
- **Central Nexus Services**: Universal functionality
- **Monitoring Stack**: Prometheus and Grafana integration

### Internationalization (i18n)
Multi-language support system providing:
- **10+ Languages**: English, Spanish, French, German, etc.
- **Dynamic Translation**: Runtime language switching
- **Translation Workflow**: Community contribution system
- **Coverage Statistics**: Translation completeness tracking
- **Contributor Management**: Credit for translators
- **Translation Approval**: Moderator review process

### WebSocket
Real-time event streaming system providing:
- **Player Events**: player.update notifications
- **Sector Events**: ship_entered, ship_left alerts
- **Combat Events**: combat.started, combat.round updates
- **Market Events**: price_changed notifications
- **Team Events**: Team messages and alerts
- **Chat Events**: Real-time messaging
- **Admin Events**: Administrative monitoring stream

**Event Channels**:
- `/ws/player` - Player-specific stream
- `/ws/sector/{sector_id}` - Sector event stream
- `/ws/team/{team_id}` - Team event stream
- `/ws/combat/{combat_id}` - Combat event stream
- `/ws/market` - Market price updates
- `/ws/chat` - Chat messages
- `/ws/admin` - Admin monitoring (admin only)

### PayPal Integration
Subscription payment processing for:
- **Regional Ownership**: $25/month
- **Galactic Citizenship**: $5/month
- **Subscription Management**: Create, cancel, upgrade/downgrade
- **Webhook Handling**: Payment notifications
- **Grace Periods**: Handling payment failures
- **Payment History**: Transaction records

### Events System
Dynamic game events providing:
- **Event Types**: Combat, Trading, Exploration, Special
- **Participation**: Player enrollment and tracking
- **Rewards**: Credits, items, reputation, exclusive content
- **Leaderboards**: Competitive rankings
- **Time-Limited**: Start/end times with maximum participants

---

## 📊 Player Progression

### Metrics
Player advancement measured through:
- **Credit Accumulation**: Total wealth earned
- **Planets Owned**: Territory control
- **Citadel Levels**: Defensive infrastructure development
- **Ports Owned**: Commercial infrastructure
- **Ships Owned**: Fleet size and composition
- **Reputation Levels**: Standing with factions
- **Trading DNA Evolution**: AI learning progress
- **Military Rank**: Achievement-based progression (see RANKING_SYSTEM.md)

### Colonization
Process of claiming planets:
- **Requirements**: 10,000 population units + 10,000 credits
- **Development**: Build infrastructure (Factory, Farm, Mine, Defense, Research)
- **Specialization**: Focus on specific resource production
- **Passive Income**: Automatic credit and resource generation
- **Population Growth**: Natural expansion over time

---

## 🎮 Game Mechanics

### Ship Speed Modifier
Affects turn cost for travel:
- **Fast Ships** (2.0+ sectors/turn): Move farther per turn
- **Slow Ships** (0.4-0.75 sectors/turn): Limited range per turn
- **Escape Pod**: Substantially higher turn cost (inefficient propulsion)

### Docking
Attaching to a port to enable trading:
- **Dock Cost**: 1 turn
- **Undock Cost**: 1 turn
- **Trading While Docked**: Instant, no additional turns
- **Multiple Trades**: Can execute many trades per docking

### Market Dynamics
Economic simulation including:
- **Supply and Demand**: Prices adjust based on availability
- **Regional Variations**: Different sector values
- **Distance Premium**: Farther transport = higher potential profit
- **Player Impact**: High trading volume affects prices
- **Faction Modifiers**: Reputation affects pricing

### Ship Insurance
Protection against ship loss:
- **Purchase Location**: Friendly ports
- **Purpose**: Offset replacement costs
- **Payout**: Partial ship value on destruction

---

## 🔧 Special Mechanics

### Cat Boost
Hidden first login mechanic:
- **Trigger**: Mentioning the orange cat during first login dialogue
- **Effect**: +15% persuasion bonus with Security Guard
- **Purpose**: Rewards observation and roleplay engagement

### Ship Tier Difficulty
Dynamic guard skepticism during first login:
- **Higher-Value Ships**: More difficult to claim (Scout Ship, Cargo Freighter)
- **Default Ship**: Easy to verify (Escape Pod)
- **Negotiation Skill**: Evaluated through AI dialogue analysis

### Negotiation Skill
Player dialogue evaluation affecting:
- **Persuasion Success**: 25% bonus if strong negotiation detected
- **Trade Advantages**: Future flag for better trading deals
- **Guard Suspicion**: Weak skills increase skepticism

---

## 📱 User Interface

### Admin UI
Administrative interface providing:
- **User Management**: View, edit, delete players
- **Galaxy Management**: Generate, clear, edit sectors
- **Team Administration**: Oversight and moderation
- **Fleet Management**: Monitor and intervene in battles
- **Economy Monitoring**: Track trading and inflation
- **Security Tools**: Suspicious activity detection, ban management
- **Content Management**: Announcements, events, news
- **Audit Logging**: Action history and reports

### Player UI (Client)
Player-facing interface featuring:
- **Dashboard**: Overview of player status, ship, credits, turns
- **Galaxy Map**: Navigate sectors, view routes
- **Trading Interface**: Buy/sell commodities with ARIA AI assistance
- **ARIA Chat**: AI companion interface with market recommendations
- **Fleet Management**: Create and manage team fleets
- **Planetary Management**: Colonization, building, production
- **Team Interface**: Messaging, treasury, member management
- **Messages**: Player communication and notifications

### 3D Galaxy Visualization
Interactive 3D representation showing:
- **Quantum Particles**: Trading activity intensity
- **Sector Quantum Fields**: Color-coded opportunities (green/red)
- **ARIA Insights**: AI recommendations overlaid
- **Quantum Tunnels**: Optimal trade routes
- **Manipulation Warnings**: Suspicious activity alerts
- **Mobile VR Ready**: Optimized for mobile VR experience

---

*This terminology document serves as the authoritative reference for all SectorWars 2102 concepts. When in doubt about game mechanics, definitions, or systems, refer to this document first.*

---
**Version History**:
- v1.0 (2025-11-16): Initial comprehensive compilation
