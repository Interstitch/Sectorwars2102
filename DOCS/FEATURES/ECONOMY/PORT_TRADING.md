# Port Trading System — Sector Wars 2102

## Overview

The port trading system forms the economic backbone of Sector Wars 2102. Each sector contains space ports where players can buy and sell commodities to earn credits. Mastering the trading system is essential for progression, as it provides the resources needed to upgrade ships, purchase equipment, and establish colonies.

## Port Classes

Space ports are categorized into different classes, each with unique buying and selling patterns:

| Port Class | Description | Buys | Sells |
|------------|-------------|------|-------|
| Class 0 (Sol) | Special case with unique mechanics | Special Goods | Special Goods |
| Class 1 | Mining Operation | Ore | Organics, Equipment |
| Class 2 | Agricultural Center | Organics | Ore, Equipment |
| Class 3 | Industrial Hub | Equipment | Ore, Organics |
| Class 4 | Distribution Center | Nothing | Everything |
| Class 5 | Collection Hub | Everything | Nothing |
| Class 6 | Mixed Market | Ore, Organics | Equipment, Fuel |
| Class 7 | Resource Exchange | Equipment, Fuel | Ore, Organics |
| Class 8 | Black Hole | Everything | Nothing (Premium) |
| Class 9 | Nova | Nothing | Everything (Premium) |
| Class 10 | Luxury Market | Gourmet Food | Technology, Luxury Goods |
| Class 11 | Advanced Tech Hub | Exotic Technology | Advanced Components |

## Core Trading Mechanics

### Commodities

The primary tradable resources in the game are:

- **Ore**: Raw materials for construction and manufacturing
- **Organics**: Food and biological products
- **Equipment**: Manufactured goods and technology
- **Fuel**: Energy for ships and stations

Additional specialized commodities:
- **Gourmet Food**: Premium food products
- **Exotic Technology**: Advanced technological components
- **Luxury Goods**: High-value items for wealthy markets

### Price Dynamics

Port prices are dynamic and influenced by several factors:

- **Supply and Demand**: Prices fluctuate based on port inventory levels
- **Port Class**: Determines base buying/selling patterns and price ranges
- **Player Activity**: Heavy trading at a port can temporarily affect prices
- **Location**: Ports in dangerous sectors generally offer better prices
- **Time**: Ports slowly regenerate inventory over time

### Basic Price Formula

The price for a commodity is calculated using:
```
Price = BasePrice × (1 - PriceVariance × CurrentQuantity / (ProductionRate × 1000))
```

Where:
- **BasePrice**: Standard value for the commodity
- **PriceVariance**: Port-specific modifier
- **CurrentQuantity**: Available units at the port
- **ProductionRate**: How quickly the port produces/consumes this commodity

## Trading Operations

### Basic Trading

To conduct trade:

1. Player must physically visit a port (be in the same sector)
2. Verify the port buys/sells desired commodities
3. Check current prices (which update in real-time)
4. Execute trade (buy or sell)
5. Each trade consumes 1 turn

### Trading Limitations

- **Cargo Capacity**: Limited by ship's cargo holds
- **Port Inventory**: Ports have finite quantities of each commodity
- **Turn Consumption**: Each trading transaction costs 1 turn
- **Location Requirement**: Must be physically present at the port

### Haggling System

The haggling system allows players to negotiate for better prices using two different approaches: numerical haggling and narrative haggling.

#### Numerical Haggling

The traditional haggling approach:

1. Player makes an initial offer (higher when selling, lower when buying)
2. Port responds with:
   - Acceptance (transaction completes at haggled price)
   - Counteroffer (player can respond with new offer)
   - Rejection (if offer is too far from acceptable range)
3. Multiple rounds of negotiation are possible (maximum 4)
4. Success depends on:
   - Port type and class
   - Offer reasonableness
   - Player's negotiation skill level
   - Random chance element

#### Narrative Haggling (AI-Powered)

A more immersive approach using advanced AI:

1. Player engages the port trader in conversation
2. Instead of just offering a price, the player crafts a persuasive statement or story
   - Example: "My cat is ill and I need to pay for meds, so I can only afford 32 credits per unit"
   - Example: "I've traveled through three hostile sectors to reach your port and lost half my cargo to pirates"
3. The AI trader (powered by OpenAI or Anthropic API) evaluates:
   - Creativity and originality of the approach
   - Relevance to the specific port and context
   - Emotional appeal and persuasiveness
   - Reasonableness of the implied price
4. The AI responds naturally, either accepting, countering, or rejecting
5. This creates unique, dynamic conversations that vary by port personality

#### Anti-Exploitation Measures

To maintain game balance and prevent exploitation:

1. **Uniqueness Enforcement**: The system maintains a database of all previously used haggling statements
   - Exact matches are automatically rejected
   - AI analyzes semantic similarity to catch slight variations
   - "My cat is sick..." vs. "My cat is ill..." would be caught as too similar
2. **Port Memory**: Individual ports remember past interactions with specific players
   - Repeated appeals to the same trader are less effective
   - Different port classes respond differently to certain types of appeals
3. **Context Awareness**: The AI evaluates if the story makes sense in the game context
   - References to Earth concerns when in deep space may seem suspicious
   - Mentions of specific events are cross-checked with player history
4. **Complexity Scaling**: As player reputation increases, the AI expects more sophisticated negotiation
   - New players can use simpler appeals
   - Veteran traders face more skeptical port merchants

#### Haggling Risks

- If a port rejects your final offer, you cannot trade that commodity during this visit
- Excessive lowballing or obviously false stories may cause the port to refuse further negotiations
- Reputation impacts: particularly egregious or offensive haggling attempts may damage standing with certain factions

#### Port Personality Traits

Each port has a distinct trader personality that influences haggling success:

- **Federation Ports**: Formal, rule-following, respond to logical appeals and fair trade practices
- **Border Ports**: Practical, no-nonsense, appreciate direct honesty and tales of survival
- **Frontier Ports**: Rugged, independent, value self-reliance and risk-taking stories
- **Luxury Hubs**: Sophisticated, status-conscious, receptive to cultural references and high-society appeals
- **Black Market**: Suspicious, opportunistic, respond to hints of shared risk and mutual benefit

Port personalities are influenced by:
- Location in the galaxy
- Controlling faction
- Port class
- Local economic conditions
- Recent player interactions

#### Haggling Skill Development

Players can improve their haggling effectiveness:

- **Reputation**: Building positive relationships with specific ports improves success rates
- **Trade History**: Demonstrating reliable trading patterns builds credibility
- **Factions**: Gaining standing with a faction improves haggling with all its associated ports
- **Learning**: The system tracks which approaches work for each player with different port types
- **Creativity Premium**: Particularly creative or entertaining haggling attempts may succeed even when the price differential is larger

#### AI Implementation

The narrative haggling system leverages advanced AI technologies:

- **LLM Integration**: Uses OpenAI or Anthropic APIs to evaluate haggling statements
- **Embedding Analysis**: Converts haggling attempts to vector embeddings for similarity comparison
- **Contextual Awareness**: The AI has access to relevant game state like player location, inventory, and history
- **Personality Simulation**: Port traders have consistent personality traits that influence responses
- **Adaptive Difficulty**: The system adjusts expectations based on player experience and success rate

The system maintains a balance between gameplay challenge and player creativity, ensuring haggling remains engaging without becoming either too easy or too frustrating.

#### Example Narrative Haggling Interaction

**Context**: Player attempting to buy Ore at a Border Region port (Class 1)

**Market Price**: 38 credits per unit  
**Player's Target**: 32 credits per unit

**Player**: "I've just come through the Veridian Nebula and lost two of my drones fighting off pirates. I'm desperate for ore to repair my shield generators before my next jump. The best I can offer is 32 credits per unit."

**Port AI Evaluation**:
- Context check: Player's ship does show some damage
- Location check: Veridian Nebula is indeed a dangerous region nearby
- Creativity assessment: Original story specific to game context
- Price differential: 15.8% below market (within acceptable range for sympathy appeal)
- Personality match: Border port traders respect survival stories and direct honesty

**Port Trader Response**: "Hmm, the Veridian pirates have been getting bold lately. I've lost two supply ships there myself last month. Tell you what - I can do 34 credits per unit, but that's as low as I can go. The refinery boss would have my hide if I went any lower."

**Player**: "I appreciate that. My navigation system is also damaged, so I had to manually plot my course here. 34 is fair - you've got a deal."

**Result**: Trade executes at 34 credits per unit (10.5% discount)

In this example, the player crafted a contextually appropriate appeal that resonated with the Border port trader's personality. The AI verified aspects of the story against game state, assessed its originality, and responded with a natural counter that acknowledged the player's situation while maintaining port profit margins.

#### Failed Haggling Example

**Context**: Player attempting to sell Luxury Goods at a Frontier port (Class 5)

**Market Price**: 105 credits per unit  
**Player's Target**: 130 credits per unit

**Player**: "My cat is seriously ill and I need to pay for expensive medications. I need at least 130 credits per unit to cover the vet costs."

**Port AI Evaluation**:
- Database check: Almost identical to a previously used haggling line
- Context mismatch: References to cats and veterinarians are not contextually appropriate in frontier space
- Logical inconsistency: Selling luxury goods in deep space to pay for a pet's treatment on a distant planet
- Price differential: 23.8% above market (outside reasonable range)
- Similarity detection: Vector embedding shows high similarity to known haggling attempts

**Port Trader Response**: "A cat? Out here in the frontier? *laughs gruffly* Look, I've heard that one before from another trader last week. I don't appreciate being taken for a fool. My offer stands at 105 credits, take it or leave it. And maybe come up with something more believable next time."

**Result**: Haggling fails, player must accept market price or try another approach

This example illustrates how the system detects and responds to inappropriate or unoriginal haggling attempts. The AI identified both contextual inconsistencies and similarity to previous attempts, resulting in a negative trader response that reinforces the importance of creative, contextually appropriate haggling.

## Special Trading Locations

### Sol System (Sector 1)

Earth's main port offers unique trading opportunities:

- **Special Equipment**: Only location to purchase certain ship upgrades
- **Colonists**: Source of population units for colonization (50 credits each)
- **Ship Upgrades**: Additional cargo holds can be purchased
- **Special Resources**: Unique commodities only available at Sol

Prices at Sol fluctuate on a daily cycle following a predictable pattern, creating opportunities for savvy traders.

### Premium Ports

- **Black Hole Ports (Class 8)**: Pay premium prices for all commodities but sell nothing
- **Nova Ports (Class 9)**: Sell all commodities at discounted prices but buy nothing
- **Luxury Markets (Class 10)**: Specialized in high-end goods with volatile pricing
- **Advanced Tech Hubs (Class 11)**: Trade in exotic technology with substantial profit potential

## Trading Strategies

### Route Planning

Effective trading requires finding profitable routes:

- **Complementary Ports**: Find pairs of ports with matching buy/sell patterns
- **Hub-and-Spoke**: Use central trading hubs to distribute goods
- **Circuit Routes**: Create closed loops of ports with complementary needs
- **Risk-Reward Balance**: Higher profits often require travel through dangerous sectors

### Market Influence

Player trading affects local economies:

- **Market Saturation**: Selling too much of one commodity will lower its value
- **Supply Shortages**: Buying large quantities will raise prices
- **Recovery Time**: Markets slowly recover to equilibrium if left alone
- **Cooperative Impact**: Multiple players trading the same commodities can significantly impact prices

### Ship Specialization

Different ships offer trading advantages:

- **Cargo Haulers**: Maximum cargo capacity for bulk trading
- **Fast Couriers**: Rapid transit between markets, sacrificing capacity
- **Specialized Transports**: Some ships have bonuses for specific commodity types

## Trading Interface

The trading interface provides:

- Current buy/sell prices for all commodities
- Port inventory levels
- Ship cargo status
- Trading history
- Haggling controls
- Transaction confirmation

## Advanced Port Mechanics

### Port Production

- Ports produce resources over time based on their class
- Production rates vary between ports
- Maximum storage is limited to approximately 10 days of production

### Port Occupation

- Only one player can trade at a port at any given time
- Trading locks the port briefly to prevent concurrent transactions
- If a port is busy, players must wait before trading

### Port Specializations

Some ports have unique specializations:

- **Military Outposts**: Sell drones and defensive equipment
- **Shipyards**: Offer ship repairs and upgrades
- **Research Stations**: Trade in specialized technological components
- **Luxury Markets**: Deal in high-value, low-volume goods

## Economic Balance

The port trading system maintains game balance through:

- **Geographic Distribution**: Port types are strategically placed to encourage exploration
- **Travel Costs**: The time and turns required to move between ports
- **Price Elasticity**: Diminishing returns on flooding markets
- **Risk-Reward Relationship**: More profitable opportunities exist in dangerous sectors
- **Inventory Limitations**: Preventing unlimited trading at a single port

## Port Ownership

### Acquiring Trading Outposts

Certain ports in the frontier and border regions can be purchased by players who demonstrate significant trading commitment:

- **Eligible Ports**: Small to medium trading outposts in non-Federation space
- **Acquisition Methods**:
  - **Trade Volume**: Conducting significant trade (100,000+ credits) at a port
  - **Investment**: Direct purchase (250,000 - 2,000,000 credits depending on port class and location)
  - **Faction Standing**: Reaching "Trusted" or "Allied" status with the controlling faction
  - **Missions**: Completing special trade-related missions for the port authorities

### Ownership Benefits

Once a player owns a port, they gain several advantages:

- **Tariff Income**: Collect 2-8% of all transactions conducted by other players at the port
- **Supply Priority**: First access to limited commodities when they restock
- **Price Adjustments**: Ability to modify base prices within certain limits (±10%)
- **Storage**: Free storage for personal commodities at the port
- **Reputation**: Increased standing with local factions
- **Port Upgrades**: Option to invest in port improvements that increase value and traffic
- **Economic Intelligence**: Detailed reports on trade flows and regional market trends
- **Port Missions**: Ability to create special trade missions for other players

### Port Revenue System

Port ownership provides a passive income stream through various mechanisms:

#### Tariff Collection
- **Transaction Fee**: 2-8% of all trades (owner-configurable within limits)
- **Volume Scaling**: Fee percentage can be adjusted based on transaction size
- **Preferred Trader Program**: Reduced rates for high-volume or trusted traders
- **Collection Method**: Credits automatically deposited into owner's account daily

#### Additional Revenue Streams
- **Docking Fees**: Small charge for ships using port facilities (5-20 credits)
- **Service Charges**: Revenue from repair bays, refueling, and other services
- **Storage Rental**: Fees from non-owners storing commodities at the port
- **Information Sales**: Selling market data to traders and trading corporations
- **Specialty Services**: Custom manufacturing, refining, or processing

#### Revenue Example

A medium-sized border port might generate:
- 10,000 credits daily in basic tariffs (5% on 200,000 credit transaction volume)
- 2,000 credits from docking fees and services
- 3,000 credits from specialty operations (if upgraded)

Total: ~15,000 credits per day passive income (~450,000 per month)
Investment Return Period: ~6-12 months for initial port purchase

#### Revenue Management

Port owners must manage their revenue streams:
- **Reinvestment**: Upgrading port facilities to increase future income
- **Defense Budget**: Maintaining security to protect revenue
- **Marketing**: Attracting more traders to increase transaction volume
- **Competitive Pricing**: Balancing tariffs against neighboring ports
- **Relationship Management**: Maintaining good standing with trading factions

### Port Management

Owners must manage their ports to maintain profitability:

- **Tariff Settings**: Setting rates too high discourages traders, too low reduces income
- **Security Investment**: Hiring defense forces to protect the port from pirates and hostile players
- **Infrastructure**: Upgrading trading facilities to increase capacity and efficiency
- **Services**: Adding repair bays, refueling stations, and other amenities to attract traders
- **Advertising**: Broadcasting port specialties on galactic trading networks
- **Special Orders**: Creating missions for other players to fulfill specific commodity needs

### Port Development

Ports can be improved through owner investment:

#### Trading Upgrades
- **Extended Storage** (25,000 - 100,000 credits)
  - Increases commodity storage capacity by 25-100%
  - Allows for stockpiling during market fluctuations
  - Improves resilience against supply shocks
- **Market Intelligence** (50,000 credits)
  - Provides real-time data on prices at connected ports
  - Identifies arbitrage opportunities automatically
  - Shows commodity supply/demand forecasts
- **Automated Trading** (75,000 credits)
  - Enables setting of buy/sell rules for automatic execution
  - Works even when owner is offline
  - Limited to 25% of normal trading volume

#### Facility Upgrades
- **Shipyard** (150,000 credits)
  - Allows ship repairs and minor upgrades
  - Generates additional revenue from visiting ships
  - Attracts more traffic to the port
- **Refining Facility** (200,000 credits)
  - Processes raw materials into higher-value commodities
  - Creates unique processed goods exclusive to your port
  - Improves profit margins by 15-30%
- **Luxury Amenities** (100,000 credits)
  - Attracts wealthy traders and increases transaction volume
  - Opens special luxury goods market
  - Improves owner's reputation with high-status factions

#### Defense Upgrades
- **Automated Defense Grid** (125,000 credits)
  - Provides basic protection against pirate raids
  - Reduced insurance costs for traders visiting the port
  - Lower chance of inventory loss
- **Security Patrol** (25,000 credits/month)
  - Hired NPC ships patrol surrounding sectors
  - Warns of incoming threats
  - Escorts friendly ships in the vicinity
- **Military Contract** (500,000 credits)
  - Faction military provides significant protection
  - Dramatically reduces successful attack chance
  - Requires high faction standing to purchase

### Port Acquisition Competition

When a port becomes available for purchase, multiple players may compete for ownership:

- **First-Mover Advantage**: First player to meet criteria gets first option to purchase
- **Bidding Wars**: If multiple qualified players express interest, an auction system activates
- **Faction Influence**: Higher faction standing gives priority in contested acquisitions
- **Port Authority Decision**: NPC port authority evaluates trade history, reputation, and bid
- **Purchase Grace Period**: 24-hour real-time window to complete transaction once approved

### Port Defense

Owned ports can be targeted by other players and NPCs:

- **Pirate Raids**: Random events requiring defensive response
- **Competitor Sabotage**: Other players may attempt to disrupt operations
- **Hostile Takeovers**: Players can challenge ownership through economic or military means
- **Defense Options**: Automated turrets, drone squadrons, hired NPC defenders

### Port Takeovers

A player's ownership of a port is not permanent and can be challenged:

#### Economic Takeovers
- **Buyout Offer**: Players can offer to buy the port from current owner at premium
- **Trade War**: Deliberately undercutting a port's prices to reduce its revenue
- **Embargoes**: Organizing other players to boycott a specific port
- **Faction Manipulation**: Reducing owner's standing with controlling faction
- **Debt Leverage**: If owner fails to pay port maintenance fees for extended period

#### Military Takeovers
- **Restricted to Frontier Space**: Only ports in lawless regions can be seized by force
- **Attack Process**:
  1. Formal declaration of intent (24-hour warning)
  2. Siege period where port defenses must be overcome
  3. Final assault on port control center
  4. Ownership transfers if attack succeeds
- **Attacker Costs**: Significant resource investment and potential ship loss
- **Defender Advantage**: More cost-effective to defend than attack
- **Team Requirement**: Typically requires coordinated team effort to succeed

#### Takeover Cooldown Period
- **Stabilization**: Newly acquired ports have a 7-day protection period
- **Recovery**: Port productivity reduced by 50% for 3 days after ownership change
- **Reputation Impact**: Aggressive takeovers damage faction standing
- **Diminishing Returns**: Multiple takeovers in short period face increasing difficulty

### Team Port Ownership

Multiple players can share ownership of larger ports:

- **Syndicate Model**: Players form a trade syndicate with ownership shares
- **Profit Sharing**: Tariff income distributed according to ownership percentage
- **Cooperative Defense**: Team members can contribute to port defense
- **Voting Rights**: Major decisions require majority shareholder approval

## Strategic Considerations

- **Market Knowledge**: Knowing which ports buy/sell which goods is valuable information
- **Economic Intelligence**: Tracking price trends can reveal opportunities
- **Inventory Management**: Balancing cargo space with diverse commodities
- **Risk Assessment**: Weighing the dangers of traveling through hostile sectors
- **Team Coordination**: Sharing trading information with teammates provides advantages
- **Port Network**: Establishing ownership of strategically located ports creates a trading empire
- **Trade Route Control**: Owning ports along profitable trade routes maximizes revenue