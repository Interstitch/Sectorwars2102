# Enhanced Player Analytics - API Specification

*Created: June 1, 2025*  
*Version: 1.0*  
*Status: SPECIFICATION - Pending Implementation*

## 📋 Overview

This document defines the API endpoints required for the Enhanced Player Analytics feature. These endpoints provide comprehensive player management capabilities including advanced filtering, bulk operations, asset management, and real-time monitoring.

## 🔐 Authentication

All endpoints require admin authentication using JWT tokens.

```http
Authorization: Bearer <admin_jwt_token>
X-Admin-Role: superadmin|gamemaster|moderator
```

## 📡 Base URL

```
https://api.sectorwars2102.com/api/v1/admin
```

## 🎯 Endpoints

### 1. Player Management

#### Get Enhanced Player List
```http
GET /players/enhanced
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | integer | No | Page number (default: 1) |
| limit | integer | No | Items per page (default: 20, max: 100) |
| sort_by | string | No | Sort field (credits, last_login, username, turns, created_at) |
| sort_order | string | No | Sort direction (asc, desc) |
| search | string | No | Search in username, email, or ID |
| filter_status | string | No | Filter by status (active, inactive, banned, all) |
| filter_team | string | No | Filter by team ID |
| min_credits | integer | No | Minimum credits filter |
| max_credits | integer | No | Maximum credits filter |
| last_login_after | datetime | No | Filter by last login date |
| last_login_before | datetime | No | Filter by last login date |
| has_ships | boolean | No | Filter players with ships |
| has_planets | boolean | No | Filter players with planets |
| has_ports | boolean | No | Filter players with ports |
| online_only | boolean | No | Show only online players |
| suspicious_only | boolean | No | Show only suspicious activity |
| include_assets | boolean | No | Include asset counts (default: true) |
| include_activity | boolean | No | Include activity metrics (default: true) |

**Response:**
```json
{
  "success": true,
  "data": {
    "players": [
      {
        "id": "uuid",
        "user_id": "uuid",
        "username": "player123",
        "email": "player@example.com",
        "credits": 50000,
        "turns": 150,
        "current_sector_id": 42,
        "status": "active",
        "is_online": true,
        "team_id": "uuid",
        "team_name": "Space Pirates",
        "created_at": "2025-01-01T00:00:00Z",
        "last_login": "2025-06-01T12:00:00Z",
        "assets": {
          "ships_count": 3,
          "planets_count": 2,
          "ports_count": 1,
          "total_value": 250000
        },
        "activity": {
          "session_count_today": 2,
          "actions_today": 45,
          "total_trade_volume": 180000,
          "combat_rating": 1250,
          "suspicious_activity": false
        },
        "location": {
          "sector_id": 42,
          "sector_name": "Alpha Centauri",
          "is_ported": true,
          "port_id": "uuid",
          "is_landed": false
        }
      }
    ],
    "total_count": 523,
    "page": 1,
    "page_size": 20,
    "total_pages": 27
  },
  "metrics": {
    "query_time_ms": 45,
    "cache_hit": false
  }
}
```

#### Get Player Details
```http
GET /players/{player_id}/detailed
```

**Response:**
```json
{
  "success": true,
  "data": {
    "player": {
      "id": "uuid",
      "username": "player123",
      "email": "player@example.com",
      "credits": 50000,
      "turns": 150,
      "current_sector_id": 42,
      "status": "active",
      "created_at": "2025-01-01T00:00:00Z",
      "assets": {
        "ships": [...],
        "planets": [...],
        "ports": [...],
        "inventory": {
          "drones": 10,
          "mines": 5,
          "genesis_devices": 1
        }
      },
      "reputation": {
        "federation": 100,
        "sectorwars_corp": -50,
        "bounty_hunters": 0,
        "smugglers_guild": 75,
        "cyborg_collective": -100,
        "pirate_confederation": 25
      },
      "statistics": {
        "total_kills": 15,
        "total_deaths": 3,
        "ports_destroyed": 2,
        "planets_captured": 5,
        "total_experience": 12500
      },
      "aria_assistant": {
        "trust_level": 0.78,
        "recommendations_accepted": 127,
        "recommendations_total": 189,
        "data_points": 2847,
        "model_status": "trained",
        "trading_style": "aggressive",
        "last_interaction": "2025-06-01T11:48:00Z"
      }
    }
  }
}
```

#### Update Player
```http
PUT /players/{player_id}/comprehensive
```

**Request Body:**
```json
{
  "username": "new_username",
  "email": "new@example.com",
  "credits": 60000,
  "turns": 200,
  "current_sector_id": 1,
  "status": "active",
  "team_id": "uuid",
  "justification": "Player requested name change"
}
```

### 2. Real-time Analytics

#### Get Real-time Metrics
```http
GET /analytics/real-time
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_players": 1523,
    "total_active_players": 487,
    "players_online_now": 89,
    "total_credits_circulation": 75000000,
    "average_session_time": 2.5,
    "new_players_today": 12,
    "retention_rate_7_day": 68.5,
    "suspicious_activity_alerts": 3,
    "server_metrics": {
      "cpu_usage": 45.2,
      "memory_usage": 62.8,
      "active_connections": 89,
      "requests_per_minute": 1250
    }
  },
  "timestamp": "2025-06-01T12:00:00Z"
}
```

### 3. Bulk Operations

#### Execute Bulk Operation
```http
POST /players/bulk-operations
```

**Request Body:**
```json
{
  "operation_type": "credits",
  "action": "add",
  "value": 10000,
  "player_ids": ["uuid1", "uuid2", "uuid3"],
  "reason": "Event participation reward",
  "notify_players": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "operation_id": "uuid",
    "affected_count": 3,
    "status": "processing",
    "estimated_completion": "2025-06-01T12:01:00Z"
  }
}
```

#### Get Bulk Operation Status
```http
GET /players/bulk-operations/{operation_id}/status
```

### 4. Asset Management

#### Get Player Assets Detailed
```http
GET /players/{player_id}/assets/detailed
```

**Response:**
```json
{
  "success": true,
  "data": {
    "ships": [
      {
        "id": "uuid",
        "name": "SS Enterprise",
        "type": "battleship",
        "current_sector": 42,
        "health": 85,
        "shields": 100,
        "cargo": {...},
        "equipment": [...],
        "value": 150000
      }
    ],
    "planets": [...],
    "ports": [...],
    "total_asset_value": 520000
  }
}
```

#### Transfer Assets
```http
POST /players/{player_id}/assets/transfer
```

**Request Body:**
```json
{
  "asset_type": "ship",
  "asset_id": "uuid",
  "to_player_id": "uuid",
  "reason": "Compensation for lost ship",
  "admin_notes": "Player filed support ticket #1234"
}
```

### 5. Emergency Operations

#### Execute Emergency Action
```http
POST /players/{player_id}/emergency/{action}
```

**Actions:**
- `teleport_home` - Teleport to starting sector
- `teleport_safe` - Teleport to nearest safe sector
- `rescue_ship` - Recover stranded ship
- `clear_debt` - Clear all debts
- `reset_turns` - Reset to default turns
- `end_combat` - Force end active combat
- `remove_bounty` - Clear all bounties

**Request Body:**
```json
{
  "reason": "Player stuck in inaccessible sector",
  "parameters": {
    "target_sector": 1
  }
}
```

### 6. Intervention Management

#### Get Intervention Queue
```http
GET /interventions/queue
```

**Query Parameters:**
- priority: high|medium|low|all
- status: pending|in_progress|resolved|all
- assigned_to: admin_id or "me"

**Response:**
```json
{
  "success": true,
  "data": {
    "interventions": [
      {
        "id": "uuid",
        "player_id": "uuid",
        "player_name": "player123",
        "priority": "high",
        "category": "stuck_player",
        "description": "Player trapped in sector with no fuel",
        "status": "pending",
        "created_at": "2025-06-01T11:00:00Z",
        "assigned_to": null
      }
    ],
    "total_count": 12,
    "pending_count": 8,
    "high_priority_count": 3
  }
}
```

#### Create Intervention
```http
POST /interventions
```

**Request Body:**
```json
{
  "player_id": "uuid",
  "priority": "high",
  "category": "economic_issue",
  "description": "Player lost credits due to market bug",
  "initial_action": "Investigating transaction logs"
}
```

### 7. WebSocket Events

#### Connection
```
wss://api.sectorwars2102.com/ws/admin/analytics
```

#### Subscribe to Updates
```json
{
  "type": "subscribe",
  "channels": ["player_updates", "metrics", "alerts"]
}
```

#### Event Types

**Player Update Event:**
```json
{
  "type": "player_update",
  "player_id": "uuid",
  "update_type": "login|logout|transaction|combat|location",
  "data": {...},
  "timestamp": "2025-06-01T12:00:00Z"
}
```

**Metrics Update Event:**
```json
{
  "type": "metrics_update",
  "data": {
    "players_online": 92,
    "active_combats": 3,
    "transactions_per_minute": 45
  },
  "timestamp": "2025-06-01T12:00:00Z"
}
```

**Alert Event:**
```json
{
  "type": "alert",
  "alert_id": "uuid",
  "severity": "high|medium|low",
  "category": "security|economic|system",
  "title": "Suspicious Trading Activity Detected",
  "description": "Player X transferred 90% of assets in 5 minutes",
  "player_id": "uuid",
  "timestamp": "2025-06-01T12:00:00Z"
}
```

## 🔍 Error Responses

### Standard Error Format
```json
{
  "success": false,
  "error": {
    "code": "INVALID_PLAYER_ID",
    "message": "Player not found",
    "details": {
      "player_id": "invalid-uuid"
    }
  },
  "timestamp": "2025-06-01T12:00:00Z"
}
```

### Common Error Codes
| Code | Description | HTTP Status |
|------|-------------|-------------|
| UNAUTHORIZED | Invalid or missing auth token | 401 |
| FORBIDDEN | Insufficient permissions | 403 |
| INVALID_PLAYER_ID | Player not found | 404 |
| INVALID_PARAMETERS | Invalid request parameters | 400 |
| OPERATION_FAILED | Operation could not be completed | 500 |
| RATE_LIMITED | Too many requests | 429 |

## 📊 Rate Limiting

- Standard endpoints: 100 requests per minute
- Bulk operations: 10 requests per minute
- WebSocket connections: 5 per admin account
- Emergency actions: 20 per hour

## 🔄 Pagination

All list endpoints support pagination with these parameters:
- `page`: Page number (1-based)
- `limit`: Items per page (max 100)
- Response includes: `total_count`, `page`, `page_size`, `total_pages`

## 🚀 Performance Requirements

- List endpoints: < 200ms response time
- Detail endpoints: < 100ms response time
- Bulk operations: < 5s for 1000 players
- WebSocket latency: < 50ms
- Cache TTL: 60 seconds for list data

---

*This specification defines the complete API surface for Enhanced Player Analytics. Implementation should follow RESTful principles and maintain backward compatibility.*