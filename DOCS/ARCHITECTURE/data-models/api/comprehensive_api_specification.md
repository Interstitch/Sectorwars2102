# Sector Wars 2102 - Comprehensive API Specification

## Overview

This document provides a complete REST API specification for all missing and enhancement features in Sector Wars 2102, designed to integrate seamlessly with the existing API structure while adding comprehensive game functionality.

## Base Configuration

```
Base URL: {API_BASE}/api/v1
Authentication: Bearer Token (JWT)
Content-Type: application/json
Rate Limiting: 100 requests/minute per user
```

## Security Framework

### Authentication Levels
- **PUBLIC**: No authentication required
- **USER**: Requires valid player authentication
- **ADMIN**: Requires administrative privileges
- **FACTION**: Requires faction-specific permissions
- **TEAM**: Requires team membership verification

### Standard Security Headers
```http
Authorization: Bearer <jwt_token>
X-Player-ID: <player_id>
X-Team-ID: <team_id> (when applicable)
X-Request-ID: <unique_request_id>
```

---

## 1. Drone Management API

### Base Route: `/drones`

#### 1.1 Drone Inventory Management

```http
GET /drones/inventory
```
**Auth**: USER  
**Description**: Get player's drone inventory and deployments
**Response**:
```typescript
{
  "player_id": string,
  "attack_drones": number,
  "defense_drones": number,
  "ship_deployments": Array<{
    "ship_id": string,
    "attack": number,
    "defense": number
  }>,
  "planet_deployments": Array<{
    "planet_id": string,
    "defense": number
  }>,
  "sector_deployments": Array<{
    "sector_id": number,
    "defense": number
  }>,
  "port_deployments": Array<{
    "port_id": string,
    "defense": number
  }>,
  "total_deployed": number,
  "total_inventory": number
}
```

#### 1.2 Purchase Drones

```http
POST /drones/purchase
```
**Auth**: USER  
**Body**:
```typescript
{
  "drone_type": "ATTACK" | "DEFENSE",
  "quantity": number,
  "port_id": string
}
```
**Response**:
```typescript
{
  "transaction_id": string,
  "cost": number,
  "new_inventory": DroneInventory
}
```

#### 1.3 Deploy Drones

```http
POST /drones/deploy
```
**Auth**: USER  
**Body**:
```typescript
{
  "deployment_type": "SHIP" | "PLANET" | "SECTOR" | "PORT",
  "deployment_id": string,
  "drone_type": "ATTACK" | "DEFENSE",
  "quantity": number,
  "configuration": {
    "aggression_level": number,
    "target_priority": string[],
    "defend_allies": boolean,
    "auto_replace": boolean
  }
}
```

#### 1.4 Recall Drones

```http
POST /drones/recall
```
**Auth**: USER  
**Body**:
```typescript
{
  "deployment_type": "SHIP" | "PLANET" | "SECTOR" | "PORT",
  "deployment_id": string,
  "drone_type": "ATTACK" | "DEFENSE",
  "quantity": number
}
```

#### 1.5 Drone Combat History

```http
GET /drones/combat-history
```
**Auth**: USER  
**Query**: `?limit=20&offset=0&location_type=SECTOR&location_id=123`
**Response**:
```typescript
{
  "combat_results": DroneCombatResult[],
  "total_count": number,
  "statistics": {
    "total_battles": number,
    "victories": number,
    "defeats": number,
    "drones_lost": number,
    "drones_destroyed": number
  }
}
```

---

## 2. Faction System API

### Base Route: `/factions`

#### 2.1 List All Factions

```http
GET /factions
```
**Auth**: USER  
**Response**:
```typescript
{
  "factions": Array<{
    "id": string,
    "name": string,
    "short_name": string,
    "type": FactionType,
    "alignment": FactionAlignment,
    "territory_percentage": number,
    "player_reputation": number,
    "reputation_title": string
  }>
}
```

#### 2.2 Faction Details

```http
GET /factions/{faction_id}
```
**Auth**: USER  
**Response**: `FactionModel`

#### 2.3 Player Reputation with Faction

```http
GET /factions/{faction_id}/reputation
```
**Auth**: USER  
**Response**:
```typescript
{
  "faction_id": string,
  "player_id": string,
  "reputation_value": number,
  "reputation_level": number,
  "reputation_title": string,
  "benefits": string[],
  "unlocked_items": string[],
  "unlocked_areas": number[],
  "discount_percentage": number,
  "next_level_requirements": {
    "points_needed": number,
    "missions_required": number,
    "restrictions": string[]
  }
}
```

#### 2.4 Faction Relations

```http
GET /factions/{faction_id}/relations
```
**Auth**: USER  
**Response**:
```typescript
{
  "faction_id": string,
  "relations": FactionRelation[]
}
```

#### 2.5 Faction Territory

```http
GET /factions/{faction_id}/territory
```
**Auth**: USER  
**Response**:
```typescript
{
  "faction_id": string,
  "territory": FactionTerritory,
  "influence_map": {
    "regions": Record<string, number>,
    "clusters": Record<string, number>,
    "sectors": Record<string, number>
  }
}
```

#### 2.6 Faction Missions

```http
GET /factions/{faction_id}/missions
```
**Auth**: USER  
**Response**:
```typescript
{
  "available_missions": Array<{
    "id": string,
    "title": string,
    "description": string,
    "reward": number,
    "reputation_gain": number,
    "requirements": string[],
    "time_limit": number,
    "difficulty": string
  }>
}
```

#### 2.7 Accept Faction Mission

```http
POST /factions/{faction_id}/missions/{mission_id}/accept
```
**Auth**: USER  
**Response**:
```typescript
{
  "mission_id": string,
  "accepted_at": Date,
  "expires_at": Date,
  "objectives": Array<{
    "id": string,
    "description": string,
    "completed": boolean
  }>
}
```

---

## 3. Message System API

### Base Route: `/messages`

#### 3.1 Message Inbox

```http
GET /messages
```
**Auth**: USER  
**Query**: `?type=PLAYER_TO_PLAYER&status=UNREAD&limit=50&offset=0`
**Response**:
```typescript
{
  "messages": MessageModel[],
  "total_count": number,
  "unread_count": number,
  "statistics": MessageStatistics
}
```

#### 3.2 Send Message

```http
POST /messages
```
**Auth**: USER  
**Body**:
```typescript
{
  "message_type": MessageType,
  "recipient_ids": string[],
  "subject": string,
  "body": string,
  "priority": MessagePriority,
  "attachments": MessageAttachment[],
  "coordinates": MessageCoordinates[],
  "expires_at": Date,
  "requires_confirmation": boolean
}
```

#### 3.3 Reply to Message

```http
POST /messages/{message_id}/reply
```
**Auth**: USER  
**Body**:
```typescript
{
  "body": string,
  "include_original": boolean,
  "attachments": MessageAttachment[]
}
```

#### 3.4 Mark Message as Read

```http
PATCH /messages/{message_id}/read
```
**Auth**: USER

#### 3.5 Delete Message

```http
DELETE /messages/{message_id}
```
**Auth**: USER

#### 3.6 Message Conversations

```http
GET /messages/conversations
```
**Auth**: USER  
**Response**:
```typescript
{
  "conversations": ConversationSummary[]
}
```

#### 3.7 Team Messages

```http
GET /messages/team/{team_id}
```
**Auth**: TEAM  
**Response**:
```typescript
{
  "team_messages": MessageModel[],
  "team_id": string,
  "participant_count": number
}
```

#### 3.8 Broadcast to Sector

```http
POST /messages/sector-broadcast
```
**Auth**: USER  
**Body**:
```typescript
{
  "sector_id": number,
  "subject": string,
  "body": string,
  "priority": MessagePriority
}
```

---

## 4. Advanced Trading API

### Base Route: `/trading`

#### 4.1 Market Analysis

```http
GET /trading/market-analysis
```
**Auth**: USER  
**Query**: `?resource_type=ALL&region_id=region1&days=7`
**Response**:
```typescript
{
  "resource_analysis": Array<{
    "resource_type": string,
    "current_price": number,
    "price_trend": "RISING" | "FALLING" | "STABLE",
    "volatility": number,
    "trading_volume": number,
    "best_buy_locations": Array<{
      "port_id": string,
      "sector_id": number,
      "price": number,
      "quantity": number
    }>,
    "best_sell_locations": Array<{
      "port_id": string,
      "sector_id": number,
      "price": number,
      "demand": number
    }>
  }>,
  "market_predictions": Array<{
    "resource_type": string,
    "predicted_price": number,
    "confidence": number,
    "time_horizon": string
  }>
}
```

#### 4.2 Trade Route Optimization

```http
POST /trading/optimize-route
```
**Auth**: USER  
**Body**:
```typescript
{
  "start_sector": number,
  "cargo_capacity": number,
  "available_credits": number,
  "risk_tolerance": "LOW" | "MEDIUM" | "HIGH",
  "max_jumps": number,
  "excluded_sectors": number[],
  "preferred_resources": string[]
}
```
**Response**:
```typescript
{
  "optimal_route": Array<{
    "step": number,
    "sector_id": number,
    "port_id": string,
    "action": "BUY" | "SELL",
    "resource_type": string,
    "quantity": number,
    "price": number,
    "profit_margin": number
  }>,
  "total_profit": number,
  "total_time": number,
  "risk_assessment": string
}
```

#### 4.3 Trading Contracts

```http
GET /trading/contracts
```
**Auth**: USER  
**Response**:
```typescript
{
  "available_contracts": Array<{
    "id": string,
    "client_name": string,
    "resource_type": string,
    "quantity": number,
    "delivery_sector": number,
    "payment": number,
    "deadline": Date,
    "reputation_requirement": number
  }>
}
```

#### 4.4 Accept Trading Contract

```http
POST /trading/contracts/{contract_id}/accept
```
**Auth**: USER

#### 4.5 Commodity Futures

```http
GET /trading/futures
```
**Auth**: USER  
**Response**:
```typescript
{
  "futures_contracts": Array<{
    "resource_type": string,
    "delivery_date": Date,
    "strike_price": number,
    "current_premium": number,
    "volatility": number
  }>
}
```

#### 4.6 Price Alerts

```http
POST /trading/price-alerts
```
**Auth**: USER  
**Body**:
```typescript
{
  "resource_type": string,
  "trigger_condition": "ABOVE" | "BELOW",
  "trigger_price": number,
  "notification_method": "IN_GAME" | "MESSAGE"
}
```

---

## 5. Team Management API

### Base Route: `/teams`

#### 5.1 Create Team

```http
POST /teams
```
**Auth**: USER  
**Body**:
```typescript
{
  "name": string,
  "description": string,
  "type": "CORPORATION" | "ALLIANCE" | "GUILD",
  "is_public": boolean,
  "max_members": number,
  "join_requirements": {
    "min_reputation": number,
    "required_skills": string[],
    "application_required": boolean
  }
}
```

#### 5.2 Team Details

```http
GET /teams/{team_id}
```
**Auth**: USER  
**Response**:
```typescript
{
  "id": string,
  "name": string,
  "description": string,
  "type": string,
  "created_at": Date,
  "member_count": number,
  "max_members": number,
  "is_public": boolean,
  "leader": {
    "id": string,
    "name": string
  },
  "members": Array<{
    "id": string,
    "name": string,
    "role": string,
    "joined_at": Date,
    "last_active": Date
  }>,
  "statistics": {
    "total_missions_completed": number,
    "total_credits_earned": number,
    "territory_controlled": number,
    "reputation_by_faction": Record<string, number>
  }
}
```

#### 5.3 Join Team Application

```http
POST /teams/{team_id}/apply
```
**Auth**: USER  
**Body**:
```typescript
{
  "application_message": string
}
```

#### 5.4 Manage Team Applications

```http
GET /teams/{team_id}/applications
```
**Auth**: TEAM (Leader/Officer)  
**Response**:
```typescript
{
  "applications": Array<{
    "id": string,
    "applicant_id": string,
    "applicant_name": string,
    "message": string,
    "applied_at": Date,
    "status": "PENDING" | "APPROVED" | "REJECTED"
  }>
}
```

#### 5.5 Approve/Reject Application

```http
POST /teams/{team_id}/applications/{application_id}/{action}
```
**Auth**: TEAM (Leader/Officer)  
**Path Parameters**: `action: "approve" | "reject"`

#### 5.6 Team Roles and Permissions

```http
GET /teams/{team_id}/roles
```
**Auth**: TEAM  
**Response**:
```typescript
{
  "roles": Array<{
    "name": string,
    "permissions": string[],
    "member_count": number
  }>,
  "available_permissions": string[]
}
```

#### 5.7 Assign Team Role

```http
POST /teams/{team_id}/members/{member_id}/role
```
**Auth**: TEAM (Leader)  
**Body**:
```typescript
{
  "role": string
}
```

#### 5.8 Team Treasury

```http
GET /teams/{team_id}/treasury
```
**Auth**: TEAM  
**Response**:
```typescript
{
  "balance": number,
  "transactions": Array<{
    "id": string,
    "type": "DEPOSIT" | "WITHDRAWAL" | "MISSION_REWARD",
    "amount": number,
    "description": string,
    "member_id": string,
    "timestamp": Date
  }>,
  "pending_payouts": Array<{
    "mission_id": string,
    "amount": number,
    "distribution": Record<string, number>
  }>
}
```

#### 5.9 Team Missions

```http
GET /teams/{team_id}/missions
```
**Auth**: TEAM  
**Response**:
```typescript
{
  "active_missions": Array<{
    "id": string,
    "title": string,
    "description": string,
    "assigned_members": string[],
    "progress": number,
    "deadline": Date
  }>,
  "completed_missions": Array<{
    "id": string,
    "title": string,
    "completed_at": Date,
    "reward": number,
    "participants": string[]
  }>
}
```

---

## 6. Region Navigation API

### Base Route: `/navigation`

#### 6.1 Galaxy Map

```http
GET /navigation/galaxy-map
```
**Auth**: USER  
**Response**:
```typescript
{
  "regions": Array<{
    "id": string,
    "name": string,
    "coordinates": {x: number, y: number, z: number},
    "cluster_count": number,
    "faction_control": Record<string, number>,
    "accessibility": "PUBLIC" | "RESTRICTED" | "FACTION_ONLY"
  }>,
  "warp_tunnels": Array<{
    "id": string,
    "origin_sector": number,
    "destination_sector": number,
    "travel_time": number,
    "toll_cost": number,
    "restrictions": string[]
  }>
}
```

#### 6.2 Region Details

```http
GET /navigation/regions/{region_id}
```
**Auth**: USER  
**Response**:
```typescript
{
  "id": string,
  "name": string,
  "description": string,
  "coordinates": {x: number, y: number, z: number},
  "clusters": Array<{
    "id": string,
    "name": string,
    "sector_count": number,
    "dominant_faction": string
  }>,
  "notable_features": string[],
  "travel_advisories": string[],
  "security_level": number
}
```

#### 6.3 Calculate Route

```http
POST /navigation/calculate-route
```
**Auth**: USER  
**Body**:
```typescript
{
  "origin_sector": number,
  "destination_sector": number,
  "route_preferences": {
    "avoid_hostile_factions": boolean,
    "use_warp_tunnels": boolean,
    "minimize_cost": boolean,
    "minimize_time": boolean,
    "max_security_risk": number
  }
}
```
**Response**:
```typescript
{
  "route": Array<{
    "sector_id": number,
    "region_id": string,
    "travel_method": "NORMAL" | "WARP_TUNNEL",
    "travel_time": number,
    "fuel_cost": number,
    "security_risk": number,
    "faction_territory": string
  }>,
  "total_distance": number,
  "total_time": number,
  "total_cost": number,
  "risk_assessment": string
}
```

#### 6.4 Warp Tunnel Status

```http
GET /navigation/warp-tunnels
```
**Auth**: USER  
**Response**:
```typescript
{
  "tunnels": Array<{
    "id": string,
    "origin_sector": number,
    "destination_sector": number,
    "status": "ACTIVE" | "INACTIVE" | "UNDER_CONSTRUCTION",
    "toll_cost": number,
    "travel_time": number,
    "capacity": number,
    "current_usage": number,
    "restrictions": string[],
    "controlled_by": string
  }>
}
```

#### 6.5 Sector Exploration

```http
GET /navigation/sectors/{sector_id}/scan
```
**Auth**: USER  
**Response**:
```typescript
{
  "sector_id": number,
  "scan_results": {
    "planets": Array<{
      "id": string,
      "type": string,
      "colonizable": boolean,
      "resources": string[],
      "owner": string | null
    }>,
    "ports": Array<{
      "id": string,
      "class": number,
      "faction": string,
      "services": string[]
    }>,
    "anomalies": Array<{
      "type": string,
      "description": string,
      "coordinates": {x: number, y: number, z: number}
    }>,
    "hazards": string[],
    "traffic_level": number
  }
}
```

---

## 7. Enhanced Security API

### Base Route: `/security`

#### 7.1 Security Status

```http
GET /security/status
```
**Auth**: USER  
**Response**:
```typescript
{
  "player_id": string,
  "security_level": number,
  "faction_standings": Record<string, number>,
  "active_bounties": Array<{
    "faction": string,
    "amount": number,
    "reason": string,
    "expires_at": Date
  }>,
  "criminal_record": Array<{
    "crime": string,
    "location": string,
    "date": Date,
    "penalty": string
  }>,
  "recent_violations": Array<{
    "violation": string,
    "severity": number,
    "date": Date
  }>
}
```

#### 7.2 Bounty System

```http
GET /security/bounties
```
**Auth**: USER  
**Response**:
```typescript
{
  "available_bounties": Array<{
    "target_id": string,
    "target_name": string,
    "reward": number,
    "crime": string,
    "last_known_sector": number,
    "danger_level": string,
    "posted_by": string,
    "expires_at": Date
  }>
}
```

#### 7.3 Post Bounty

```http
POST /security/bounties
```
**Auth**: USER  
**Body**:
```typescript
{
  "target_id": string,
  "reward_amount": number,
  "reason": string,
  "evidence": string
}
```

#### 7.4 Security Violations

```http
GET /security/violations
```
**Auth**: ADMIN  
**Query**: `?player_id=player123&severity=HIGH&limit=50`
**Response**:
```typescript
{
  "violations": Array<{
    "id": string,
    "player_id": string,
    "violation_type": string,
    "severity": number,
    "location": string,
    "timestamp": Date,
    "evidence": string,
    "status": "ACTIVE" | "RESOLVED" | "APPEALED"
  }>
}
```

#### 7.5 Faction Security Response

```http
GET /security/faction-response/{faction_id}
```
**Auth**: USER  
**Response**:
```typescript
{
  "faction_id": string,
  "security_policies": {
    "patrol_frequency": number,
    "contraband_enforcement": number,
    "violation_penalties": Record<string, string>
  },
  "player_status": {
    "security_clearance": string,
    "travel_restrictions": string[],
    "monitoring_level": number
  }
}
```

---

## 8. Player Analytics API

### Base Route: `/analytics`

#### 8.1 Player Statistics

```http
GET /analytics/player-stats
```
**Auth**: USER  
**Response**:
```typescript
{
  "player_id": string,
  "gameplay_metrics": {
    "total_playtime": number,
    "sectors_visited": number,
    "missions_completed": number,
    "credits_earned": number,
    "faction_reputation_average": number
  },
  "combat_statistics": {
    "battles_won": number,
    "battles_lost": number,
    "drones_deployed": number,
    "ships_destroyed": number
  },
  "economic_statistics": {
    "trades_completed": number,
    "profit_margin_average": number,
    "resources_traded": Record<string, number>
  },
  "exploration_statistics": {
    "planets_discovered": number,
    "anomalies_found": number,
    "warp_tunnels_used": number
  }
}
```

#### 8.2 Performance Trends

```http
GET /analytics/trends
```
**Auth**: USER  
**Query**: `?period=30&metric=credits_earned`
**Response**:
```typescript
{
  "metric": string,
  "period_days": number,
  "data_points": Array<{
    "date": Date,
    "value": number
  }>,
  "trend": "IMPROVING" | "DECLINING" | "STABLE",
  "percentage_change": number,
  "benchmarks": {
    "player_percentile": number,
    "average_performance": number
  }
}
```

#### 8.3 Leaderboards

```http
GET /analytics/leaderboards
```
**Auth**: USER  
**Query**: `?category=credits&timeframe=weekly&limit=100`
**Response**:
```typescript
{
  "category": string,
  "timeframe": string,
  "rankings": Array<{
    "rank": number,
    "player_id": string,
    "player_name": string,
    "value": number,
    "change_from_previous": number
  }>,
  "player_rank": number,
  "total_participants": number
}
```

---

## Error Response Format

All API endpoints use consistent error response format:

```typescript
{
  "error": {
    "code": string,
    "message": string,
    "details": Record<string, any>,
    "timestamp": Date,
    "request_id": string
  }
}
```

### Common Error Codes
- `AUTHENTICATION_REQUIRED`: Missing or invalid authentication
- `INSUFFICIENT_PERMISSIONS`: User lacks required permissions
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `VALIDATION_ERROR`: Request data validation failed
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INSUFFICIENT_CREDITS`: Not enough credits for operation
- `FACTION_RESTRICTION`: Operation restricted by faction rules
- `TEAM_PERMISSION_DENIED`: Team-specific permission required

## Rate Limiting

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Pagination

For paginated endpoints:

```typescript
{
  "data": T[],
  "pagination": {
    "total": number,
    "page": number,
    "per_page": number,
    "total_pages": number,
    "has_next": boolean,
    "has_prev": boolean
  }
}
```

## WebSocket Events

Real-time events for key game mechanics:

```typescript
// Message received
{
  "event": "message_received",
  "data": {
    "message": MessageModel,
    "conversation_id": string
  }
}

// Drone combat occurred
{
  "event": "drone_combat",
  "data": {
    "combat_result": DroneCombatResult,
    "player_involved": boolean
  }
}

// Team activity
{
  "event": "team_activity",
  "data": {
    "team_id": string,
    "activity_type": string,
    "description": string,
    "participants": string[]
  }
}

// Faction reputation change
{
  "event": "reputation_changed",
  "data": {
    "faction_id": string,
    "old_value": number,
    "new_value": number,
    "reason": string
  }
}
```

## Integration Points

### With Existing API Structure
- All new routes integrate with current authentication system
- Consistent with existing response format patterns
- Extends current admin API with new management endpoints
- Maintains compatibility with existing WebSocket infrastructure

### Database Integration
- Utilizes existing player, sector, and port models
- Extends with new models for drones, factions, messages, teams
- Maintains referential integrity with current schema
- Supports existing analytics and reporting systems

### Frontend Integration
- Designed for React component consumption
- Supports real-time updates via WebSocket events
- Compatible with existing state management patterns
- Enables progressive feature rollout

This comprehensive API specification provides the foundation for implementing all missing features while maintaining consistency with the existing system architecture and ensuring scalable, secure gameplay experiences.