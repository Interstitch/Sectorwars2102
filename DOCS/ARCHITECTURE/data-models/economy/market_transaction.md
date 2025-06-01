# Market Transaction Data Definition

## Overview

The Market Transaction system in Sector Wars 2102 tracks all trading activities between players and ports, recording buying and selling of commodities, ships, and equipment. This data is crucial for market analytics, price trend visualization, and economic modeling within the game economy.

## Position in Galaxy Hierarchy

Market Transactions occur within the galaxy's economic framework:
- Transactions occur primarily at **Ports** within **Sectors**
- Transaction data aggregates at **Cluster** and **Region** levels
- Global economic indices are calculated at the **Galaxy** level

## Data Model

```typescript
export enum TransactionType {
  BUY = "BUY",                 // Player purchases from port
  SELL = "SELL",               // Player sells to port
  PLAYER_TO_PLAYER = "P2P",    // Direct trade between players
  MARKET_ADJUSTMENT = "ADJUST" // Automatic market correction
}

export enum TransactionStatus {
  PENDING = "PENDING",         // Transaction initiated but not completed
  COMPLETED = "COMPLETED",     // Successfully completed transaction
  FAILED = "FAILED",           // Transaction failed to complete
  CANCELED = "CANCELED"        // Transaction canceled by player
}

export interface TransactionParty {
  entity_type: string;         // "player", "port", "team", etc.
  entity_id: string;           // ID of the entity
  entity_name: string;         // Display name
  faction_id?: string;         // Associated faction if relevant
}

export interface TransactionItem {
  item_type: string;           // "resource", "ship", "equipment", etc.
  item_id: string;             // Specific identifier if applicable
  item_name: string;           // Display name
  quantity: number;            // Number of items
  unit_price: number;          // Price per unit
  total_price: number;         // Total transaction amount
  quality?: number;            // Item quality if applicable (0-100)
}

export enum HagglingType {
  NONE = "NONE",                  // No haggling applied
  NUMERICAL = "NUMERICAL",        // Traditional number-based haggling
  NARRATIVE = "NARRATIVE"         // AI-powered narrative haggling
}

export interface PriceModifier {
  reason: string;              // Reason for modification
  percentage: number;          // Positive or negative adjustment
  flat_amount: number;         // Flat adjustment (if any)
  applied_to: string;          // "unit_price" or "total"
}

export interface HagglingData {
  type: HagglingType;          // Type of haggling used
  rounds: {                    // Haggling interaction history
    offer_type: string;        // "initial", "counter", "final"
    party: string;             // "player" or "port"
    offer_price: number;       // Price offered
    narrative?: string;        // Narrative content if used
    success_rate: number;      // 0-100 calculated success probability
    accepted: boolean;         // Whether offer was accepted
  }[];
  final_adjustment: number;    // Final price adjustment percentage
  trader_personality?: string; // Port trader personality type
  similarity_score?: number;   // How similar to previous attempts (0-100)
  creativity_score?: number;   // Creativity rating of narrative (0-100)
  context_score?: number;      // Contextual appropriateness (0-100)
}

export interface MarketCondition {
  port_id: string;             // Port where transaction occurred
  sector_id: number;           // Sector containing port
  supply_level: number;        // 0-100 supply availability
  demand_level: number;        // 0-100 demand strength
  market_trend: string;        // "rising", "falling", "stable"
  price_volatility: number;    // 0-100 price fluctuation rate
}

export interface TransactionTax {
  tax_type: string;            // Type of tax/fee
  tax_rate: number;            // Percentage rate
  tax_amount: number;          // Total amount collected
  recipient_id: string;        // Entity receiving tax
  recipient_type: string;      // "port_owner", "faction", etc.
}

export interface MarketTransactionModel {
  id: string;                  // Unique identifier
  transaction_type: TransactionType; // Type of transaction
  status: TransactionStatus;   // Current transaction status
  created_at: Date;            // When transaction initiated
  completed_at: Date | null;   // When transaction completed
  
  // Transaction Parties
  buyer: TransactionParty;     // Purchasing entity
  seller: TransactionParty;    // Selling entity
  
  // Transaction Details
  items: TransactionItem[];    // Items in transaction
  total_amount: number;        // Total transaction value
  currency: string;            // Currency type (usually credits)
  price_modifiers: PriceModifier[]; // Applied price adjustments
  reputation_used: boolean;    // Whether reputation affected price
  
  // Location and Market Data
  location: {
    port_id: string;           // Where transaction occurred
    sector_id: number;
    cluster_id: string;
    region_id: string;
  };
  market_condition: MarketCondition; // Market state at transaction time
  
  // Financials
  taxes: TransactionTax[];     // Taxes and fees applied
  net_buyer_payment: number;   // What buyer actually paid
  net_seller_received: number; // What seller actually received
  
  // Haggling Data
  haggling_data?: HagglingData; // Detailed haggling interaction if applied
  
  // Metadata
  port_class?: number;         // Port class where transaction occurred
  port_owner_id?: string;      // ID of port owner (if player-owned)
  owner_tariff_rate?: number;  // Owner's tariff percentage if applicable
  related_transaction_ids: string[]; // For multi-part transactions
  notes: string;               // Additional transaction notes
  turn_cost: number;           // Number of turns consumed by transaction
}

export interface MarketHistoryQuery {
  item_type?: string;          // Filter by item type
  location_type?: string;      // "port", "sector", "cluster", "region"
  location_id?: string;        // Specific location ID
  time_period: {               // Time range to query
    start: Date;
    end: Date;
  };
  player_id?: string;          // Specific player's transactions
  aggregation?: string;        // "none", "daily", "weekly", "monthly"
}

export interface PriceTrend {
  item_type: string;           // Resource or item type
  location_id: string;         // Where trend is measured
  location_type: string;       // "port", "sector", "cluster", "region"
  timeframe: {                 // Analysis period
    start: Date;
    end: Date;
  };
  data_points: {               // Historical price points
    timestamp: Date;
    price: number;
    volume: number;
    volatility: number;
  }[];
  analysis: {                  // Trend analysis
    direction: string;         // "up", "down", "stable"
    strength: number;          // 0-100 trend strength
    volatility: number;        // 0-100 price stability
    predicted_movement: number; // Expected price movement
  };
}
```

## Market Transaction Features

1. **Transaction Recording**: All trade activities between players, ports, and other entities are recorded in detail
2. **Price History**: Historical price data for commodities and goods across all ports
3. **Market Analysis**: Trends, volatility, and forecasting tools for economic planning
4. **Tax Collection**: Recording of all fees, tariffs, and taxes collected during transactions
5. **Haggling Impact**: Tracking the effects of narrative haggling on transaction prices

## Price Calculation Factors

1. **Base Price**: Standard price for each commodity or item
2. **Supply & Demand**: Local port supply/demand affecting prices
3. **Player Reputation**: Influence of faction standing on prices
4. **Port Class**: Higher class ports offer more stable prices
5. **Region Effects**: Region-based price modifiers
6. **Haggling Success**: Narrative bargaining outcomes
7. **Market Volatility**: Random fluctuations based on market conditions
8. **Faction Control**: Additional modifiers based on controlling faction

## Market Analysis Applications

1. **Trade Route Planning**: Identification of profitable trade routes
2. **Economic Forecasting**: Prediction of future market conditions
3. **Port Investment Analysis**: Evaluation of port purchase/upgrade opportunities
4. **Market Manipulation Detection**: Identification of player-driven market distortions
5. **Economic Health Monitoring**: Overall galaxy economic condition assessment

## Data Retention Policies

1. **Recent Transactions**: Complete data for past 30 days
2. **Medium-Term History**: Summarized daily data for past 90 days
3. **Long-Term Trends**: Weekly aggregated data kept indefinitely
4. **Player History**: All transactions involving a specific player kept for account lifetime

## Port Ownership Data

Port ownership represents a significant economic feature, tracking player-owned trading ports:

```typescript
export enum PortOwnershipStatus {
  AVAILABLE = "AVAILABLE",         // Port available for purchase
  PLAYER_OWNED = "PLAYER_OWNED",   // Owned by individual player
  TEAM_OWNED = "TEAM_OWNED",       // Owned by player team
  FACTION_OWNED = "FACTION_OWNED", // Owned by NPC faction
  CONTESTED = "CONTESTED"          // Ownership under dispute
}

export enum PortUpgradeType {
  STORAGE = "STORAGE",              // Increased commodity storage
  MARKET_INTELLIGENCE = "MARKET_INTELLIGENCE", // Price data across network
  AUTOMATED_TRADING = "AUTOMATED_TRADING", // Rule-based automatic trading
  SHIPYARD = "SHIPYARD",            // Ship repair and upgrades
  REFINING = "REFINING",            // Process raw materials
  LUXURY_AMENITIES = "LUXURY_AMENITIES", // Attract wealthy traders
  DEFENSE_GRID = "DEFENSE_GRID",    // Basic protection
  SECURITY_PATROL = "SECURITY_PATROL", // Active defense
  MILITARY_CONTRACT = "MILITARY_CONTRACT" // Faction protection
}

export interface PortUpgrade {
  type: PortUpgradeType;           // Upgrade type
  level: number;                   // Upgrade level (for multi-level upgrades)
  installed_at: Date;              // When upgrade was added
  expires_at?: Date;               // If temporary upgrade
  maintenance_cost: number;        // Recurring cost (if any)
  benefits: {                      // Effects of upgrade
    metric: string;                // What is affected
    value: number;                 // Effect magnitude
  }[];
}

export interface PortRevenue {
  period_start: Date;              // Start of revenue period
  period_end: Date;                // End of revenue period
  transaction_count: number;       // Number of transactions
  total_volume: number;            // Total credit volume
  tariff_revenue: number;          // Revenue from tariffs
  service_revenue: number;         // Revenue from services
  docking_revenue: number;         // Revenue from docking fees
  special_revenue: number;         // Other revenue streams
  total_revenue: number;           // Total income
  maintenance_costs: number;       // Operating costs
  net_profit: number;              // Final profit after costs
}

export interface PortOwnershipModel {
  port_id: string;                 // Port identifier
  port_name: string;               // Display name
  port_class: number;              // Port class (0-11)
  sector_id: number;               // Location sector
  ownership_status: PortOwnershipStatus; // Current ownership state
  
  // Current Ownership
  owner_id?: string;               // Current owner ID (player or team)
  owner_type: string;              // "player", "team", "faction"
  owner_name: string;              // Display name of owner
  acquired_at?: Date;              // When current owner gained control
  purchase_price?: number;         // Price paid by current owner
  
  // Port Configuration
  tariff_rate: number;             // Current tariff percentage (2-8%)
  docking_fee: number;             // Fee for using port
  preferred_traders: string[];     // IDs of traders with special rates
  faction_alignment: string;       // Aligned faction (affects reputation)
  
  // Port Development
  upgrades: PortUpgrade[];         // Installed upgrades
  current_value: number;           // Estimated port value
  defense_rating: number;          // 0-100 security level
  
  // Financial Data
  daily_revenue: PortRevenue;      // Last day's revenue
  weekly_revenue: PortRevenue;     // Last week's revenue
  monthly_revenue: PortRevenue;    // Last month's revenue
  lifetime_revenue: PortRevenue;   // All-time revenue data
  
  // Ownership History
  ownership_history: {             // Previous owners
    owner_id: string;
    owner_type: string;
    owner_name: string;
    period_start: Date;
    period_end: Date;
    acquisition_method: string;    // "purchase", "conquest", etc.
  }[];
  
  // Special Trading Conditions
  special_orders: {                // Current port requests
    resource_id: string;
    resource_name: string;
    quantity: number;
    price_bonus: number;           // Premium over standard price
    expires_at: Date;
  }[];
  export_restrictions: string[];   // Resources restricted from export
  import_restrictions: string[];   // Resources restricted from import
  
  // Operational Status
  active_status: boolean;          // Whether port is operational
  last_attack: Date | null;        // When port was last attacked
  recovery_status: number;         // 0-100 recovery from damage
  player_reputation_requirements: number; // Min reputation to use port
}
```