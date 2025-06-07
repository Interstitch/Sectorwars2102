# Trading System Complete Specification

## Overview

The trading system is the core economic engine of Sectorwars2102. Players buy low, sell high, and manage supply chains across the galaxy.

## Components

### 1. Port Trading Interface

#### UI Requirements
```typescript
interface TradingUI {
  portInfo: {
    name: string;
    type: PortType;
    faction: string;
    techLevel: number;
  };
  
  commodities: {
    available: Commodity[];
    prices: PriceData[];
    inventory: PlayerInventory;
  };
  
  controls: {
    buyButton: ActionButton;
    sellButton: ActionButton;
    quantitySlider: RangeInput;
    confirmDialog: Modal;
  };
}
```

#### User Flow
1. Player docks at port (automatic when entering port sector)
2. Trading interface opens showing:
   - Port information header
   - Two columns: "Port Selling" | "You Have"
   - Current prices with trend indicators
   - Player credits and cargo space
3. Player selects commodity and quantity
4. Confirmation shows profit/loss calculation
5. Transaction completes with animation
6. Port prices update based on transaction

### 2. Commodity System

#### Base Commodities
```typescript
enum CommodityType {
  // Tier 1 - Basic Goods
  FOOD = "food",
  WATER = "water", 
  OXYGEN = "oxygen",
  FUEL = "fuel",
  
  // Tier 2 - Industrial
  METALS = "metals",
  ELECTRONICS = "electronics",
  MACHINERY = "machinery",
  CHEMICALS = "chemicals",
  
  // Tier 3 - Advanced
  COMPUTERS = "computers",
  WEAPONS = "weapons",
  LUXURIES = "luxuries",
  MEDICINES = "medicines",
  
  // Tier 4 - Rare
  QUANTUM_CORES = "quantum_cores",
  ALIEN_ARTIFACTS = "alien_artifacts",
  DARK_MATTER = "dark_matter"
}
```

#### Price Calculation
```typescript
function calculatePrice(
  commodity: CommodityType,
  port: Port,
  supply: number,
  demand: number,
  techLevel: number,
  events: MarketEvent[]
): number {
  const basePrice = COMMODITY_BASE_PRICES[commodity];
  const supplyFactor = 2 - (supply / 100); // 0.0 to 2.0
  const demandFactor = demand / 100; // 0.0 to 2.0
  const techFactor = getTechMultiplier(commodity, techLevel);
  const eventFactor = getEventMultiplier(events);
  
  return Math.round(
    basePrice * supplyFactor * demandFactor * techFactor * eventFactor
  );
}
```

### 3. Supply & Demand Mechanics

#### Dynamic Market
- Each port tracks supply/demand for each commodity
- Trading affects supply/demand:
  - Buying reduces supply, increases price
  - Selling increases supply, reduces price
- Markets slowly rebalance over time
- Cross-port arbitrage opportunities

#### Port Specialization
```typescript
interface PortSpecialization {
  agricultural: {
    produces: ["food", "water", "oxygen"],
    demands: ["machinery", "chemicals", "electronics"]
  },
  industrial: {
    produces: ["metals", "machinery", "electronics"],
    demands: ["food", "water", "luxuries"]
  },
  technological: {
    produces: ["computers", "weapons", "quantum_cores"],
    demands: ["metals", "chemicals", "alien_artifacts"]
  },
  luxury: {
    produces: ["luxuries", "medicines"],
    demands: ["food", "electronics", "alien_artifacts"]
  }
}
```

### 4. Trading Routes

#### Route Planning
```typescript
interface TradeRoute {
  id: string;
  name: string;
  waypoints: {
    portId: string;
    action: "buy" | "sell";
    commodity: CommodityType;
    quantity: number;
  }[];
  estimatedProfit: number;
  estimatedTime: number;
  fuelCost: number;
}
```

#### Automated Trading
- Players can save profitable routes
- AI suggests optimal routes based on:
  - Current prices
  - Travel distance
  - Fuel costs
  - Cargo capacity
  - Risk factors

### 5. Advanced Features

#### Contracts System
```typescript
interface TradeContract {
  id: string;
  client: string;
  commodity: CommodityType;
  quantity: number;
  deliverTo: string;
  deadline: Date;
  payment: number;
  penalty: number;
  reputation: number;
}
```

#### Market Manipulation
- Large trades affect entire regions
- Players can corner markets
- Price wars between traders
- Economic warfare options

#### Black Market
- Illegal goods (weapons, contraband)
- Higher profits, higher risks
- Requires reputation with smugglers
- Avoid security scans

### 6. UI/UX Design

#### Desktop Layout
```
┌─────────────────────────────────────────┐
│ [Port Name] - [Port Type] - [Tech Level]│
├─────────────────┬───────────────────────┤
│ PORT SELLING    │ YOUR CARGO            │
├─────────────────┼───────────────────────┤
│ Food      100cr │ Food      x50         │
│ [Buy] ████░░░░  │ [Sell] ████░░░░       │
│                 │                       │
│ Metals    250cr │ Metals    x0          │
│ [Buy] ████░░░░  │ [Sell] (disabled)     │
├─────────────────┴───────────────────────┤
│ Credits: 15,000  Cargo: 50/100          │
└─────────────────────────────────────────┘
```

#### Mobile Layout
- Single column with tabs
- Swipe between buy/sell
- Large touch targets
- Simplified quantity selection

### 7. Integration Points

#### Backend APIs
- `GET /api/ports/{portId}/commodities`
- `POST /api/trade/buy`
- `POST /api/trade/sell`
- `GET /api/market/prices`
- `WS /api/market/updates`

#### Real-time Updates
- Price changes via WebSocket
- Other player trades affect market
- Event notifications
- Contract deadlines

### 8. Balancing Parameters

```typescript
const TRADING_CONFIG = {
  maxPriceFluctuation: 0.5, // ±50% from base
  marketRebalanceRate: 0.1, // 10% per hour
  transactionFee: 0.02, // 2% tax
  bulkDiscount: 0.05, // 5% for large trades
  reputationBonus: 0.1, // 10% better prices
  blackMarketMultiplier: 2.5 // 250% profit
};
```

## Implementation Priority

1. **Core Trading** (Must Have)
   - Basic buy/sell interface
   - Price display
   - Inventory management

2. **Market Dynamics** (Should Have)
   - Supply/demand effects
   - Price fluctuations
   - Port specializations

3. **Advanced Features** (Nice to Have)
   - Trade routes
   - Contracts
   - Black market

## Success Metrics

- Average session includes 5+ trades
- 80% of players understand trading within 5 minutes
- Price arbitrage creates emergent gameplay
- Economy remains balanced over time