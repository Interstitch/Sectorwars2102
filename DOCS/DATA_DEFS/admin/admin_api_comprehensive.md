# Comprehensive Admin API Specification

## Overview

This document defines all API endpoints needed for the comprehensive Admin UI functionality, building upon the existing admin_comprehensive.py endpoints and adding the missing functionality for complete administrative control.

## API Architecture

### Base URL
- Development: `http://localhost:8080/api/v1/admin`
- Production: `https://api.sectorwars2102.com/api/v1/admin`

### Authentication
All endpoints require JWT authentication with admin role verification.

### Recent Updates (2025-05-25)
- **NEW**: PUT `/sectors/{sector_id}` - Comprehensive sector editing endpoint

```typescript
headers: {
  'Authorization': `Bearer ${jwt_token}`,
  'Content-Type': 'application/json'
}
```

---

## 1. Enhanced Player Management APIs

### 1.1 Player CRUD Operations (Enhanced)

```typescript
// Get all players with advanced filtering
GET /api/admin/players
Query Parameters:
  - page: number = 1
  - limit: number = 50
  - search: string (username, email)
  - status: 'active' | 'banned' | 'inactive'
  - team_id: string
  - min_credits: number
  - max_credits: number
  - reputation_filter: string (faction:level)
  - last_login_before: ISO date
  - last_login_after: ISO date
  - sort_by: 'username' | 'credits' | 'last_login' | 'created_at'
  - sort_order: 'asc' | 'desc'

Response: {
  players: PlayerModel[],
  total: number,
  page: number,
  total_pages: number,
  filters_applied: FilterSummary
}
```

```typescript
// Comprehensive player update
PUT /api/admin/players/{id}
Body: {
  credits?: number,
  turns?: number,
  reputation?: {
    faction_id: string,
    new_value: number,
    reason: string
  }[],
  current_sector_id?: number,
  home_sector_id?: number,
  is_active?: boolean,
  admin_notes?: string,
  force_location_update?: boolean
}

Response: {
  success: boolean,
  player: PlayerModel,
  changes_applied: ChangeLog[],
  warnings?: string[]
}
```

### 1.2 Player Asset Management

```typescript
// Get player's complete asset inventory
GET /api/admin/players/{id}/assets
Response: {
  ships: ShipModel[],
  planets: PlanetModel[],
  ports: PortModel[],
  inventory: {
    attack_drones: number,
    defense_drones: number,
    mines: number,
    genesis_devices: number
  },
  total_value: number
}
```

```typescript
// Transfer assets between players
POST /api/admin/players/assets/transfer
Body: {
  from_player_id: string,
  to_player_id: string,
  assets: {
    ship_ids?: string[],
    planet_ids?: string[],
    port_ids?: string[],
    credits?: number,
    items?: {
      attack_drones?: number,
      defense_drones?: number,
      mines?: number
    }
  },
  reason: string,
  notify_players: boolean
}

Response: {
  success: boolean,
  transfer_id: string,
  summary: TransferSummary
}
```

### 1.3 Player Activity and Monitoring

```typescript
// Get player activity log
GET /api/admin/players/{id}/activity
Query Parameters:
  - days: number = 7
  - activity_types: string[] (movement, trading, combat, etc.)
  - include_details: boolean = false

Response: {
  player_id: string,
  activities: ActivityLogEntry[],
  summary: {
    total_actions: number,
    sectors_visited: number,
    credits_earned: number,
    credits_spent: number,
    combats_engaged: number
  }
}
```

```typescript
// Player emergency actions
POST /api/admin/players/{id}/emergency
Body: {
  action: 'rescue' | 'teleport' | 'restore' | 'compensate',
  parameters: {
    target_sector_id?: number,
    restore_to_date?: ISO date,
    compensation_amount?: number,
    reason: string
  }
}

Response: {
  success: boolean,
  action_taken: string,
  details: EmergencyActionDetails
}
```

---

## 2. Fleet Management APIs

### 2.1 Ship Operations

```typescript
// Get all ships with advanced filtering
GET /api/admin/ships
Query Parameters:
  - owner_id: string
  - sector_id: number
  - ship_type: ShipType
  - status: 'active' | 'destroyed' | 'maintenance'
  - maintenance_below: number (0-100)
  - last_active_before: ISO date
  - include_cargo: boolean = false
  - include_combat_stats: boolean = false

Response: {
  ships: ShipModel[],
  total: number,
  statistics: {
    by_type: Record<ShipType, number>,
    by_status: Record<string, number>,
    average_maintenance: number,
    ships_needing_attention: number
  }
}
```

```typescript
// Ship emergency operations
POST /api/admin/ships/{id}/emergency
Body: {
  operation: 'teleport' | 'repair' | 'refuel' | 'rescue' | 'destroy',
  parameters: {
    target_sector_id?: number,
    repair_level?: number, // 0-100
    reason: string,
    notify_owner: boolean
  }
}

Response: {
  success: boolean,
  ship: ShipModel,
  operation_details: OperationDetails
}
```

```typescript
// Create new ship for player
POST /api/admin/ships/create
Body: {
  owner_id: string,
  ship_type: ShipType,
  location: {
    sector_id: number,
    port_id?: string, // If docked
    planet_id?: string // If landed
  },
  initial_condition: number = 100,
  initial_cargo?: Partial<ShipCargo>,
  custom_name?: string,
  reason: string
}

Response: {
  success: boolean,
  ship: ShipModel,
  creation_details: CreationDetails
}
```

### 2.2 Fleet Analytics

```typescript
// Fleet health report
GET /api/admin/ships/health-report
Response: {
  total_ships: number,
  ships_by_condition: {
    excellent: number, // 90-100%
    good: number,      // 70-89%
    fair: number,      // 50-69%
    poor: number,      // 25-49%
    critical: number   // 0-24%
  },
  ships_needing_attention: ShipModel[],
  maintenance_alerts: MaintenanceAlert[],
  performance_trends: PerformanceTrend[]
}
```

---

## 3. Economy Management APIs

### 3.1 Market Monitoring

```typescript
// Real-time market data
GET /api/admin/economy/market-data
Query Parameters:
  - refresh_rate: number = 30 (seconds)
  - include_history: boolean = false
  - commodities: string[] (filter specific commodities)

Response: {
  timestamp: Date,
  ports: PortMarketData[],
  global_averages: CommodityPrices,
  price_trends: PriceTrend[],
  volatility_alerts: VolatilityAlert[],
  trade_volume: TradeVolumeData
}
```

```typescript
// Market intervention
POST /api/admin/economy/intervention
Body: {
  intervention_type: 'PRICE_CAP' | 'PRICE_FLOOR' | 'SUPPLY_INJECTION' | 'EMERGENCY_SHUTDOWN',
  target: {
    port_id?: string,
    commodity?: string,
    region?: string
  },
  parameters: {
    new_price?: number,
    supply_amount?: number,
    duration_hours?: number,
    reason: string
  },
  notify_affected_players: boolean
}

Response: {
  success: boolean,
  intervention_id: string,
  affected_ports: string[],
  estimated_impact: InterventionImpact
}
```

### 3.2 Economic Analytics

```typescript
// Economy health metrics
GET /api/admin/economy/health
Response: {
  overall_health: number, // 0-100 score
  credit_circulation: {
    total_credits: number,
    velocity: number,
    inflation_rate: number
  },
  trade_metrics: {
    daily_volume: number,
    active_routes: number,
    price_stability: number
  },
  alerts: EconomicAlert[],
  recommendations: string[]
}
```

---

## 4. Combat Management APIs

### 4.1 Combat Monitoring

```typescript
// Live combat feed
GET /api/admin/combat/live
Query Parameters:
  - include_resolved: boolean = false
  - sector_filter: number[]
  - player_filter: string[]

Response: {
  active_combats: CombatEngagement[],
  recent_combats: CombatEngagement[],
  combat_statistics: {
    total_today: number,
    ongoing: number,
    disputed: number
  }
}
```

```typescript
// Combat intervention
POST /api/admin/combat/{combat_id}/intervene
Body: {
  intervention_type: 'STOP' | 'REVERSE' | 'MODIFY_OUTCOME' | 'INVALIDATE',
  reason: string,
  compensation?: {
    player_id: string,
    credits?: number,
    ships_restored?: string[],
    items_restored?: Record<string, number>
  }[],
  notify_players: boolean
}

Response: {
  success: boolean,
  intervention_id: string,
  original_outcome: CombatOutcome,
  new_outcome: CombatOutcome,
  affected_players: string[]
}
```

### 4.2 Combat Analytics

```typescript
// Combat balance analysis
GET /api/admin/combat/balance
Query Parameters:
  - time_period: number = 30 (days)
  - ship_type_filter: ShipType[]

Response: {
  ship_effectiveness: Record<ShipType, EffectivenessMetrics>,
  weapon_usage: WeaponUsageStats[],
  balance_issues: BalanceIssue[],
  recommendations: BalanceRecommendation[]
}
```

---

## 5. Universe Management APIs

### 5.1 Sector Management

```typescript
// Update sector properties (NEW - 2025-05-25)
PUT /api/admin/sectors/{sector_id}
Body: {
  name?: string,                    // Sector name (max 100 chars)
  type?: SectorType,               // STANDARD, NEBULA, ASTEROID_FIELD, etc.
  description?: string,            // Optional description
  x_coord?: number,                // X coordinate
  y_coord?: number,                // Y coordinate  
  z_coord?: number,                // Z coordinate
  radiation_level?: number,        // 0.0-10.0 radiation level
  hazard_level?: number,           // 0-10 hazard rating
  resource_regeneration?: number,  // 0.0+ regeneration multiplier
  is_discovered?: boolean,         // Discovery status
  discovered_by_id?: string,       // Player UUID who discovered
  controlling_faction?: string,    // Controlling faction name
  controlling_team_id?: string,    // Controlling team UUID
  resources?: object,              // Resource configuration
  defenses?: object,               // Defense configuration
  special_features?: string[],     // Special feature array
  active_events?: object[],        // Active events array
  nav_hazards?: object,            // Navigation hazards
  nav_beacons?: object[]           // Navigation beacons
}

Response: {
  message: string,
  sector_id: string,
  sector_number: number,
  name: string
}

Errors:
  - 400: Invalid input data or validation errors
  - 404: Sector not found
  - 500: Server error
```

```typescript
// Modify sector connections
PUT /api/admin/sectors/{id}/connections
Body: {
  add_connections?: {
    target_sector_id: number,
    distance: number,
    is_warp_tunnel?: boolean,
    bidirectional?: boolean
  }[],
  remove_connections?: number[],
  reason: string
}

Response: {
  success: boolean,
  sector: SectorModel,
  connection_changes: ConnectionChange[],
  topology_impact: TopologyImpact
}
```

```typescript
// Modify sector contents
PUT /api/admin/sectors/{id}/contents
Body: {
  add_planet?: {
    planet_type: PlanetType,
    name?: string
  },
  remove_planet?: string,
  add_port?: {
    port_class: PortClass,
    name?: string
  },
  remove_port?: string,
  defenses?: {
    defense_drones?: number,
    owner_id?: string,
    mines?: number
  },
  reason: string
}

Response: {
  success: boolean,
  sector: SectorModel,
  content_changes: ContentChange[]
}
```

### 5.2 Warp Tunnel Management

```typescript
// Create artificial warp tunnel
POST /api/admin/warp-tunnels/create
Body: {
  source_sector_id: number,
  destination_sector_id: number,
  tunnel_type: 'NATURAL' | 'ARTIFICIAL',
  stability: WarpTunnelStability,
  bidirectional: boolean,
  access_control?: {
    public: boolean,
    allowed_factions?: string[],
    allowed_players?: string[]
  },
  creator_override?: string, // Admin creating on behalf of player
  reason: string
}

Response: {
  success: boolean,
  warp_tunnel: WarpTunnelModel,
  impact_analysis: TunnelImpactAnalysis
}
```

---

## 6. Team Management APIs

### 6.1 Team Operations

```typescript
// Get all teams with detailed info
GET /api/admin/teams
Query Parameters:
  - include_members: boolean = true
  - include_assets: boolean = false
  - status: 'active' | 'disbanded' | 'suspended'
  - min_members: number
  - max_members: number

Response: {
  teams: TeamModel[],
  team_statistics: {
    total_teams: number,
    average_size: number,
    most_active: string,
    resource_distribution: ResourceDistribution
  }
}
```

```typescript
// Team administrative actions
POST /api/admin/teams/{id}/action
Body: {
  action: 'DISBAND' | 'SUSPEND' | 'RESTORE' | 'FORCE_REMOVE_MEMBER' | 'TRANSFER_LEADERSHIP',
  parameters: {
    player_id?: string, // For member removal or leadership transfer
    suspension_duration?: number, // Hours
    reason: string,
    compensation?: CompensationDetails
  },
  notify_members: boolean
}

Response: {
  success: boolean,
  team: TeamModel,
  action_details: ActionDetails,
  affected_players: string[]
}
```

### 6.2 Alliance Management

```typescript
// Monitor alliance relationships
GET /api/admin/alliances
Response: {
  alliances: {
    id: string,
    team_ids: string[],
    relationship_type: 'FORMAL' | 'INFORMAL' | 'TRADE' | 'MILITARY',
    formed_at: Date,
    activity_level: number,
    resource_sharing: boolean
  }[],
  conflict_zones: ConflictZone[],
  diplomatic_status: DiplomaticStatus[]
}
```

---

## 7. Event Management APIs

### 7.1 Event Creation and Management

```typescript
// Create dynamic event
POST /api/admin/events/create
Body: {
  event_type: 'COMBAT_TOURNAMENT' | 'TRADE_COMPETITION' | 'EXPLORATION_CHALLENGE' | 'SPECIAL_SCENARIO',
  name: string,
  description: string,
  parameters: {
    duration_hours: number,
    eligibility: {
      min_level?: number,
      max_level?: number,
      required_reputation?: ReputationRequirement[],
      team_only?: boolean,
      sector_restrictions?: number[]
    },
    rewards: {
      first_place: RewardStructure,
      runner_up: RewardStructure,
      participation: RewardStructure
    },
    special_rules?: string[]
  },
  scheduling: {
    start_time: Date,
    registration_opens?: Date,
    registration_closes?: Date
  }
}

Response: {
  success: boolean,
  event: GameEvent,
  event_id: string,
  estimated_participation: number
}
```

```typescript
// Manage active events
PUT /api/admin/events/{id}/manage
Body: {
  action: 'START' | 'PAUSE' | 'RESUME' | 'STOP' | 'EXTEND' | 'MODIFY_REWARDS',
  parameters?: {
    extension_hours?: number,
    new_rewards?: RewardStructure,
    reason: string
  }
}

Response: {
  success: boolean,
  event: GameEvent,
  participants_affected: number,
  notifications_sent: number
}
```

### 7.2 Event Analytics

```typescript
// Event participation analytics
GET /api/admin/events/{id}/analytics
Response: {
  event: GameEvent,
  participation: {
    registered: number,
    active: number,
    completed: number,
    dropped_out: number
  },
  engagement_metrics: {
    average_session_time: number,
    repeat_participation_rate: number,
    satisfaction_score: number
  },
  performance_data: EventPerformanceData[]
}
```

---

## 8. Analytics and Reporting APIs

### 8.1 Comprehensive Analytics

```typescript
// Player analytics dashboard
GET /api/admin/analytics/players
Query Parameters:
  - time_period: number = 30 (days)
  - segment: 'new' | 'active' | 'returning' | 'at_risk'
  - metrics: string[] (retention, engagement, monetization)

Response: {
  total_players: number,
  active_players: number,
  new_registrations: number,
  retention_rates: {
    day_1: number,
    day_7: number,
    day_30: number
  },
  engagement_metrics: {
    average_session_time: number,
    sessions_per_user: number,
    feature_usage: FeatureUsageData[]
  },
  player_segments: PlayerSegmentData[]
}
```

```typescript
// Generate custom report
POST /api/admin/reports/generate
Body: {
  report_type: 'PLAYER_ACTIVITY' | 'ECONOMIC_HEALTH' | 'COMBAT_BALANCE' | 'CONTENT_USAGE' | 'CUSTOM',
  parameters: {
    time_range: {
      start_date: Date,
      end_date: Date
    },
    filters: Record<string, any>,
    metrics: string[],
    grouping: string[],
    format: 'JSON' | 'CSV' | 'PDF'
  },
  schedule?: {
    recurring: boolean,
    frequency: 'DAILY' | 'WEEKLY' | 'MONTHLY',
    recipients: string[]
  }
}

Response: {
  success: boolean,
  report_id: string,
  download_url?: string,
  scheduled_id?: string,
  estimated_completion: Date
}
```

---

## 9. Real-time and WebSocket APIs

### 9.1 Real-time Updates

```typescript
// WebSocket connection for real-time admin updates
WS /api/admin/realtime
Message Types:
  - PLAYER_MOVEMENT
  - COMBAT_STARTED
  - COMBAT_ENDED
  - MARKET_ALERT
  - SYSTEM_ALERT
  - SECURITY_ALERT

Subscription Format: {
  subscribe_to: string[],
  filters?: Record<string, any>
}
```

### 9.2 System Monitoring

```typescript
// System health dashboard
GET /api/admin/system/health
Response: {
  server_status: {
    cpu_usage: number,
    memory_usage: number,
    disk_usage: number,
    active_connections: number
  },
  database_status: {
    connection_pool: number,
    query_performance: QueryPerformanceMetrics,
    slow_queries: SlowQuery[]
  },
  game_metrics: {
    active_players: number,
    api_response_times: ResponseTimeMetrics,
    error_rates: ErrorRateMetrics
  },
  alerts: SystemAlert[]
}
```

---

## Error Handling

### Standard Error Response Format
```typescript
{
  success: false,
  error: {
    code: string,
    message: string,
    details?: any,
    timestamp: Date,
    request_id: string
  }
}
```

### Common Error Codes
- `PERMISSION_DENIED`: Insufficient admin permissions
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `VALIDATION_ERROR`: Request data validation failed
- `OPERATION_FAILED`: Operation couldn't be completed
- `RATE_LIMITED`: Too many requests
- `SYSTEM_ERROR`: Internal server error

## Rate Limiting

### Endpoint Rate Limits
- Read operations: 100 requests/minute
- Write operations: 30 requests/minute
- Bulk operations: 10 requests/minute
- Report generation: 5 requests/hour

This comprehensive API specification provides all the endpoints needed to support the full Admin UI functionality while maintaining security, performance, and reliability standards.