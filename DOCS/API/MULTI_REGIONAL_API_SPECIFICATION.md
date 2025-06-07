# Multi-Regional API Specification

## Overview

This document provides comprehensive API specifications for the Multi-Regional System in SectorWars 2102. The API enables regional governance, Central Nexus management, and inter-regional functionality.

## Base URL

```
Production: https://api.sectorwars2102.com/api/v1
Development: http://localhost:8080/api/v1
```

## Authentication

All API endpoints require authentication via JWT Bearer tokens.

```http
Authorization: Bearer <jwt_token>
```

### Authentication Endpoints

```http
POST /auth/login/json
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}

Response:
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## Regional Governance API

### Base Path: `/regions`

#### Get My Region
Retrieve information about the user's owned region.

```http
GET /regions/my-region
Authorization: Bearer <token>

Response 200:
{
  "id": "uuid",
  "name": "string",
  "display_name": "string",
  "owner_id": "uuid",
  "subscription_tier": "standard",
  "subscription_status": "active",
  "status": "active",
  "governance_type": "democracy|autocracy|council",
  "voting_threshold": 0.60,
  "election_frequency_days": 90,
  "constitutional_text": "string",
  "tax_rate": 0.15,
  "trade_bonuses": {
    "ore": 1.5,
    "food": 1.3,
    "technology": 1.0,
    "luxury": 1.0,
    "energy": 1.0
  },
  "economic_specialization": "trade",
  "starting_credits": 2500,
  "starting_ship": "scout",
  "language_pack": {
    "greeting": "string",
    "farewell": "string",
    "currency_symbol": "string",
    "motto": "string"
  },
  "aesthetic_theme": {
    "primary_color": "#hex",
    "secondary_color": "#hex",
    "font_family": "string",
    "logo_style": "string"
  },
  "traditions": {
    "key": "value"
  },
  "total_sectors": 500,
  "active_players_30d": 150,
  "total_trade_volume": 1000000.00,
  "created_at": "2025-06-01T12:00:00Z",
  "updated_at": "2025-06-01T12:00:00Z"
}

Response 404:
{
  "detail": "No region found for this user"
}
```

#### Get Regional Statistics
Retrieve comprehensive statistics for the user's region.

```http
GET /regions/my-region/stats
Authorization: Bearer <token>

Response 200:
{
  "total_population": 250,
  "citizen_count": 150,
  "resident_count": 75,
  "visitor_count": 25,
  "average_reputation": 73.5,
  "total_revenue": 150000.00,
  "trade_volume_30d": 1000000.00,
  "active_elections": 2,
  "pending_policies": 3,
  "treaties_count": 1,
  "planets_count": 45,
  "ports_count": 120,
  "ships_count": 890
}
```

#### Update Economic Configuration
Update economic settings for the user's region.

```http
PUT /regions/my-region/economy
Authorization: Bearer <token>
Content-Type: application/json

{
  "tax_rate": 0.18,
  "starting_credits": 3000,
  "trade_bonuses": {
    "ore": 2.0,
    "food": 1.5,
    "technology": 1.8,
    "luxury": 1.2,
    "energy": 1.6
  },
  "economic_specialization": "mining"
}

Response 200:
{
  "message": "Economic configuration updated successfully"
}

Response 400:
{
  "detail": "Trade bonus for ore must be between 1.0 and 3.0"
}

Response 422:
{
  "detail": [
    {
      "loc": ["body", "tax_rate"],
      "msg": "ensure this value is greater than or equal to 0.05",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

#### Update Governance Configuration
Update governance settings for the user's region.

```http
PUT /regions/my-region/governance
Authorization: Bearer <token>
Content-Type: application/json

{
  "governance_type": "democracy",
  "voting_threshold": 0.65,
  "election_frequency_days": 60,
  "constitutional_text": "We the citizens of this region..."
}

Response 200:
{
  "message": "Governance configuration updated successfully"
}

Response 400:
{
  "detail": "Invalid governance type"
}
```

#### Create Policy Proposal
Create a new policy proposal for democratic voting.

```http
POST /regions/my-region/policies
Authorization: Bearer <token>
Content-Type: application/json

{
  "policy_type": "tax_rate",
  "title": "Reduce Regional Tax Rate",
  "description": "Proposal to reduce tax rate to stimulate economic growth",
  "proposed_changes": {
    "tax_rate": 0.12
  },
  "voting_duration_days": 7
}

Response 200:
{
  "message": "Policy proposal created successfully",
  "policy_id": "uuid"
}

Response 404:
{
  "detail": "Player record not found"
}
```

#### List Regional Policies
Get all policies for the user's region.

```http
GET /regions/my-region/policies
Authorization: Bearer <token>

Response 200:
[
  {
    "id": "uuid",
    "policy_type": "tax_rate",
    "title": "Reduce Regional Tax Rate",
    "description": "Proposal to reduce tax rate...",
    "proposed_changes": {
      "tax_rate": 0.12
    },
    "proposed_by": "uuid",
    "proposed_at": "2025-06-01T12:00:00Z",
    "voting_closes_at": "2025-06-08T12:00:00Z",
    "votes_for": 15,
    "votes_against": 8,
    "status": "voting",
    "approval_percentage": 65.2
  }
]
```

#### Start Election
Start a new election for a regional position.

```http
POST /regions/my-region/elections
Authorization: Bearer <token>
Content-Type: application/json

{
  "position": "governor",
  "voting_duration_days": 7,
  "candidates": ["uuid1", "uuid2"]
}

Response 200:
{
  "message": "Election for governor started successfully",
  "election_id": "uuid"
}

Response 409:
{
  "detail": "An active election for governor already exists"
}
```

#### List Regional Elections
Get all elections for the user's region.

```http
GET /regions/my-region/elections
Authorization: Bearer <token>

Response 200:
[
  {
    "id": "uuid",
    "position": "governor",
    "candidates": [
      {
        "player_id": "uuid",
        "player_name": "PlayerName",
        "platform": "Economic Growth Platform",
        "vote_count": 25
      }
    ],
    "voting_opens_at": "2025-06-01T12:00:00Z",
    "voting_closes_at": "2025-06-08T12:00:00Z",
    "results": null,
    "status": "active"
  }
]
```

#### List Regional Treaties
Get all treaties involving the user's region.

```http
GET /regions/my-region/treaties
Authorization: Bearer <token>

Response 200:
[
  {
    "id": "uuid",
    "region_a_name": "Alpha Sector",
    "region_b_name": "Beta Industrial",
    "treaty_type": "trade_agreement",
    "terms": {
      "trade_bonus": 1.2,
      "duration_days": 90
    },
    "signed_at": "2025-06-01T12:00:00Z",
    "expires_at": "2025-08-30T12:00:00Z",
    "status": "active"
  }
]
```

#### Update Cultural Identity
Update cultural identity for the user's region.

```http
PUT /regions/my-region/culture
Authorization: Bearer <token>
Content-Type: application/json

{
  "language_pack": {
    "greeting": "Welcome to Alpha Sector!",
    "farewell": "Safe travels, trader!",
    "currency_symbol": "ATC",
    "motto": "Prosperity Through Commerce"
  },
  "aesthetic_theme": {
    "primary_color": "#FFD700",
    "secondary_color": "#1E3A8A",
    "font_family": "Trade Gothic",
    "logo_style": "corporate_modern"
  },
  "traditions": {
    "founding_day": "Annual Trade Festival",
    "merchant_honors": "Monthly trader awards"
  }
}

Response 200:
{
  "message": "Cultural identity updated successfully"
}
```

#### List Regional Members
Get members of the user's region with pagination.

```http
GET /regions/my-region/members?limit=50&offset=0
Authorization: Bearer <token>

Response 200:
[
  {
    "player_id": "uuid",
    "username": "PlayerName",
    "membership_type": "citizen",
    "reputation_score": 85,
    "local_rank": "Senator",
    "voting_power": 1.5,
    "joined_at": "2025-05-01T12:00:00Z",
    "last_visit": "2025-06-01T10:30:00Z",
    "total_visits": 45
  }
]
```

## Central Nexus API

### Base Path: `/nexus`

#### Get Nexus Status
Check if Central Nexus exists and get basic information.

```http
GET /nexus/status
Authorization: Bearer <token>

Response 200 (Exists):
{
  "exists": true,
  "status": "active",
  "nexus_id": "uuid",
  "created_at": "2025-06-01T12:00:00Z",
  "total_sectors": 5000,
  "total_ports": 500,
  "total_planets": 250,
  "governance_type": "galactic_council",
  "economic_specialization": "universal_hub"
}

Response 200 (Does not exist):
{
  "exists": false,
  "status": "not_generated",
  "total_sectors": 0,
  "total_ports": 0,
  "total_planets": 0
}
```

#### Get Nexus Statistics
Get comprehensive Central Nexus statistics.

```http
GET /nexus/stats
Authorization: Bearer <token>

Response 200:
{
  "total_sectors": 5000,
  "total_ports": 500,
  "total_planets": 250,
  "total_warp_gates": 100,
  "active_players": 1500,
  "daily_traffic": 50000,
  "districts": [
    {
      "district_type": "commerce_central",
      "sectors": 500,
      "avg_security": 8.5,
      "avg_development": 9.2
    },
    {
      "district_type": "industrial_zone",
      "sectors": 600,
      "avg_security": 6.0,
      "avg_development": 7.5
    }
  ]
}
```

#### List Districts
Get list of all Central Nexus districts.

```http
GET /nexus/districts
Authorization: Bearer <token>

Response 200:
[
  {
    "district_type": "commerce_central",
    "name": "Commerce Central",
    "sector_range": [1, 500],
    "sectors_count": 500,
    "ports_count": 50,
    "planets_count": 25,
    "security_level": 8.5,
    "development_level": 9.2,
    "current_traffic": 8.8
  },
  {
    "district_type": "diplomatic_quarter",
    "name": "Diplomatic Quarter",
    "sector_range": [501, 800],
    "sectors_count": 300,
    "ports_count": 30,
    "planets_count": 15,
    "security_level": 9.0,
    "development_level": 8.5,
    "current_traffic": 6.2
  }
]
```

#### Get District Details
Get detailed information about a specific district.

```http
GET /nexus/districts/{district_type}
Authorization: Bearer <token>

Response 200:
{
  "district_type": "commerce_central",
  "total_sectors": 500,
  "sector_range": [1, 500],
  "sample_sectors": [
    {
      "sector_number": 1,
      "security_level": 8,
      "development_level": 9,
      "traffic_level": 8
    },
    {
      "sector_number": 50,
      "security_level": 9,
      "development_level": 10,
      "traffic_level": 9
    }
  ],
  "sample_ports": [
    {
      "sector_id": 1,
      "port_class": "A",
      "port_type": "Trade Hub",
      "docking_fee": 500
    }
  ],
  "sample_planets": [
    {
      "sector_id": 25,
      "planet_type": "Urban",
      "population": 1000000,
      "development_level": 9
    }
  ]
}

Response 400:
{
  "detail": "Invalid district type: invalid_district"
}
```

#### Generate Central Nexus
Generate or regenerate the Central Nexus galaxy.

```http
POST /nexus/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "force_regenerate": false,
  "preserve_player_data": true,
  "districts_to_regenerate": ["commerce_central", "industrial_zone"]
}

Response 200 (New generation):
{
  "message": "Central Nexus generation started",
  "task_id": "uuid",
  "estimated_duration_minutes": 18
}

Response 409 (Already exists):
{
  "detail": "Central Nexus already exists. Use force_regenerate=true to regenerate."
}

Response 200 (Regeneration):
{
  "message": "Central Nexus regeneration started",
  "task_id": "uuid",
  "estimated_duration_minutes": 20,
  "preserve_player_data": true
}
```

#### Regenerate District
Regenerate a specific district within the Central Nexus.

```http
POST /nexus/districts/{district_type}/regenerate?preserve_player_data=true
Authorization: Bearer <token>

Response 200:
{
  "message": "District commerce_central regeneration started",
  "task_id": "uuid",
  "estimated_duration_minutes": 3
}

Response 400:
{
  "detail": "Invalid district type: invalid_district"
}

Response 404:
{
  "detail": "Central Nexus not found"
}
```

## Error Responses

### Standard HTTP Status Codes

#### 400 Bad Request
```json
{
  "detail": "Invalid request parameters or data"
}
```

#### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

#### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

#### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

#### 409 Conflict
```json
{
  "detail": "Resource already exists or conflicts with current state"
}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

API requests are rate limited to prevent abuse:

- **Public endpoints**: 100 requests per minute
- **Authenticated endpoints**: 1000 requests per minute
- **Admin endpoints**: 500 requests per minute
- **Generation endpoints**: 5 requests per hour

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1625097600
```

## Validation Rules

### Economic Configuration
- `tax_rate`: 0.05 ≤ value ≤ 0.25
- `starting_credits`: 100 ≤ value ≤ 10000
- `trade_bonuses`: 1.0 ≤ value ≤ 3.0 for each resource

### Governance Configuration
- `voting_threshold`: 0.1 ≤ value ≤ 0.9
- `election_frequency_days`: 30 ≤ value ≤ 365
- `governance_type`: "democracy" | "autocracy" | "council"

### Policy Configuration
- `voting_duration_days`: 1 ≤ value ≤ 30
- `policy_type`: "tax_rate" | "pvp_rules" | "trade_policy" | "immigration" | "defense" | "cultural"

### Election Configuration
- `voting_duration_days`: 1 ≤ value ≤ 30
- `position`: "governor" | "council_member" | "ambassador" | "trade_commissioner"

## WebSocket API

Real-time updates for regional events and Central Nexus status.

### Connection
```javascript
const ws = new WebSocket('wss://api.sectorwars2102.com/ws');
ws.send(JSON.stringify({
  type: 'authenticate',
  token: 'jwt_token'
}));
```

### Message Types

#### Regional Updates
```json
{
  "type": "regional_update",
  "region_id": "uuid",
  "event": "policy_vote" | "election_result" | "member_joined",
  "data": {}
}
```

#### Central Nexus Updates
```json
{
  "type": "nexus_update",
  "event": "generation_progress" | "district_regenerated",
  "data": {
    "progress_percentage": 45,
    "estimated_remaining_minutes": 8
  }
}
```

## SDK Integration

### JavaScript/TypeScript SDK

```typescript
import { SectorWarsAPI } from '@sectorwars/api-sdk';

const api = new SectorWarsAPI({
  baseURL: 'https://api.sectorwars2102.com/api/v1',
  apiKey: 'your-api-key'
});

// Regional operations
const region = await api.regions.getMyRegion();
await api.regions.updateEconomicConfig({
  taxRate: 0.18,
  tradeBonuses: { ore: 2.0 }
});

// Central Nexus operations
const nexusStatus = await api.nexus.getStatus();
const districts = await api.nexus.getDistricts();
```

### Python SDK

```python
from sectorwars_api import SectorWarsAPI

api = SectorWarsAPI(
    base_url='https://api.sectorwars2102.com/api/v1',
    api_key='your-api-key'
)

# Regional operations
region = api.regions.get_my_region()
api.regions.update_economic_config(
    tax_rate=0.18,
    trade_bonuses={'ore': 2.0}
)

# Central Nexus operations
nexus_status = api.nexus.get_status()
districts = api.nexus.get_districts()
```

## Testing Endpoints

### Health Check
```http
GET /health
Response 200:
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-06-01T12:00:00Z"
}
```

### API Version
```http
GET /version
Response 200:
{
  "version": "1.0.0",
  "build": "12345",
  "environment": "production"
}
```

---

**API Version:** 1.0.0  
**Last Updated:** June 1, 2025  
**Contact:** api-support@sectorwars2102.com  