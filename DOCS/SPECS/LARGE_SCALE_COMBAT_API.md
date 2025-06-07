# Large-Scale Combat API Specification

**Version**: 1.0  
**Purpose**: API endpoints for 100v100+ combat system  
**Base URL**: `/api/v1/combat/large-scale/`

---

## Authentication

All endpoints require valid JWT token with combat permissions:
```http
Authorization: Bearer <jwt_token>
```

---

## Battle Management

### POST /battles/create
Create a new large-scale battle

**Request Body:**
```json
{
  "battle_type": "sector_siege" | "fleet_engagement" | "resource_raid",
  "sector_id": "uuid",
  "max_participants": 200,
  "duration_limit": 3600,
  "stakes": {
    "sector_control": true,
    "resource_deposits": ["quantum_ore", "rare_metals"],
    "credits": 50000
  },
  "restrictions": {
    "max_fleet_value": 1000000,
    "allowed_ship_types": ["corvette", "destroyer", "carrier"],
    "max_units_per_player": 50
  }
}
```

**Response:**
```json
{
  "battle_id": "uuid",
  "status": "recruiting",
  "created_at": "2025-01-07T10:30:00Z",
  "join_deadline": "2025-01-07T11:00:00Z",
  "estimated_start": "2025-01-07T11:05:00Z"
}
```

### POST /battles/{battle_id}/join
Join an existing battle

**Request Body:**
```json
{
  "side": "attacker" | "defender",
  "units": [
    {
      "type": "assault_drone",
      "quantity": 25,
      "loadout": "standard_assault"
    },
    {
      "type": "destroyer_class",
      "quantity": 2,
      "loadout": "anti_drone_configuration"
    }
  ],
  "formation": "defensive_wall",
  "tactics": "balanced"
}
```

### GET /battles/{battle_id}/status
Get current battle status

**Response:**
```json
{
  "battle_id": "uuid",
  "status": "in_progress",
  "current_turn": 15,
  "turn_timer": 180,
  "participants": {
    "attackers": 3,
    "defenders": 2,
    "total_units": 247
  },
  "performance": {
    "turn_processing_time": 2.3,
    "server_load": 0.65
  }
}
```

---

## Real-time Battle Feed

### WebSocket: /ws/battles/{battle_id}
Real-time battle updates

**Connection:**
```javascript
const socket = new WebSocket('wss://api.sectorwars.com/ws/battles/uuid');
socket.onmessage = (event) => {
  const update = JSON.parse(event.data);
  handleBattleUpdate(update);
};
```

**Update Message Types:**

#### Unit Actions
```json
{
  "type": "unit_action",
  "timestamp": "2025-01-07T10:30:15.234Z",
  "turn": 15,
  "action": {
    "unit_id": "drone_001",
    "action_type": "attack",
    "target_id": "enemy_ship_005",
    "damage": 450,
    "result": "hit"
  }
}
```

#### Formation Changes
```json
{
  "type": "formation_update",
  "player_id": "uuid",
  "new_formation": "aggressive_advance",
  "affected_units": ["unit_001", "unit_002", "unit_003"]
}
```

#### Turn Completion
```json
{
  "type": "turn_complete",
  "turn": 15,
  "duration": 2.1,
  "casualties": {
    "attackers": 8,
    "defenders": 12
  },
  "next_turn_eta": 3
}
```

---

## Battle Commands

### POST /battles/{battle_id}/commands
Submit battle commands

**Request Body:**
```json
{
  "commands": [
    {
      "unit_ids": ["drone_001", "drone_002"],
      "command": "attack",
      "target": "enemy_position_alpha",
      "priority": 1
    },
    {
      "unit_ids": ["ship_001"],
      "command": "move",
      "destination": {"x": 150, "y": 200},
      "formation": "escort_drones"
    }
  ],
  "tactical_modifier": "coordinated_assault"
}
```

**Response:**
```json
{
  "commands_accepted": 2,
  "commands_rejected": 0,
  "estimated_execution": "next_turn",
  "warnings": []
}
```

---

## Analytics & Reporting

### GET /battles/{battle_id}/analytics
Battle performance analytics

**Response:**
```json
{
  "battle_summary": {
    "duration": 1847,
    "total_turns": 23,
    "units_destroyed": 89,
    "damage_dealt": 450000,
    "tactical_moves": 156
  },
  "player_performance": [
    {
      "player_id": "uuid",
      "units_commanded": 45,
      "damage_dealt": 125000,
      "units_lost": 12,
      "tactical_score": 8.7,
      "mvp_actions": ["flanking_maneuver", "defensive_hold"]
    }
  ],
  "economic_impact": {
    "total_value_destroyed": 2500000,
    "salvage_available": 375000,
    "repair_costs": 180000
  }
}
```

### POST /battles/{battle_id}/replay
Generate battle replay

**Request Body:**
```json
{
  "format": "video" | "data" | "highlight_reel",
  "quality": "standard" | "high" | "cinematic",
  "perspective": "tactical" | "cinematic" | "first_person",
  "include_audio": true
}
```

---

## Administrative Endpoints

### GET /admin/battles/performance
System performance metrics

**Response:**
```json
{
  "active_battles": 47,
  "average_turn_time": 2.8,
  "server_capacity": {
    "current_load": 0.73,
    "max_battles": 100,
    "scaling_trigger": 0.85
  },
  "quality_metrics": {
    "player_satisfaction": 0.91,
    "cheat_attempts": 0,
    "uptime": 0.998
  }
}
```

### POST /admin/battles/{battle_id}/intervene
Emergency battle intervention

**Request Body:**
```json
{
  "action": "pause" | "terminate" | "rollback",
  "reason": "cheating_detected" | "server_issues" | "player_request",
  "compensation": {
    "refund_costs": true,
    "restore_units": true,
    "bonus_credits": 10000
  }
}
```

---

## Error Handling

### Standard Error Response
```json
{
  "error": {
    "code": "BATTLE_FULL",
    "message": "This battle has reached maximum participants",
    "details": {
      "max_participants": 200,
      "current_participants": 200,
      "suggested_battles": ["uuid1", "uuid2"]
    }
  }
}
```

### Common Error Codes
- `BATTLE_FULL`: Battle at capacity
- `INSUFFICIENT_UNITS`: Player doesn't have required units
- `INVALID_FORMATION`: Formation not allowed for unit types
- `BATTLE_ENDED`: Attempting action on completed battle
- `RATE_LIMITED`: Too many commands submitted
- `CHEAT_DETECTED`: Suspicious activity detected
- `SERVER_OVERLOAD`: System temporarily unavailable

---

## Rate Limiting

### Command Submission
- **Free Tier**: 5 commands per turn
- **Premium Tier**: 15 commands per turn
- **Guild Commander**: 25 commands per turn

### API Calls
- **Standard**: 100 requests per minute
- **Battle Participants**: 300 requests per minute
- **Spectators**: 60 requests per minute

---

## Data Compression

### WebSocket Message Compression
Large battle updates use binary compression:

```javascript
// Example decompression
function decompressBattleUpdate(compressedData) {
  const buffer = new Uint8Array(compressedData);
  const decompressed = pako.inflate(buffer, { to: 'string' });
  return JSON.parse(decompressed);
}
```

### Spatial Data Optimization
Unit positions use efficient encoding:

```json
{
  "units": {
    "encoding": "delta_compressed",
    "data": "base64_encoded_binary_data",
    "reference_point": {"x": 1000, "y": 1000}
  }
}
```

---

## Integration Examples

### JavaScript Client
```javascript
class LargeScaleBattleClient {
  constructor(battleId, authToken) {
    this.battleId = battleId;
    this.authToken = authToken;
    this.socket = null;
  }
  
  async connectToBattle() {
    this.socket = new WebSocket(
      `wss://api.sectorwars.com/ws/battles/${this.battleId}`,
      [],
      { headers: { Authorization: `Bearer ${this.authToken}` }}
    );
    
    this.socket.onmessage = (event) => {
      const update = JSON.parse(event.data);
      this.handleBattleUpdate(update);
    };
  }
  
  async submitCommands(commands) {
    const response = await fetch(
      `/api/v1/combat/large-scale/battles/${this.battleId}/commands`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.authToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ commands })
      }
    );
    
    return response.json();
  }
}
```

### Python Backend Integration
```python
import asyncio
import aiohttp

class BattleManager:
    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.headers = {'Authorization': f'Bearer {auth_token}'}
    
    async def create_large_battle(self, battle_config):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                '/api/v1/combat/large-scale/battles/create',
                json=battle_config,
                headers=self.headers
            ) as response:
                return await response.json()
    
    async def monitor_battle_performance(self, battle_id):
        async with aiohttp.ClientSession() as session:
            while True:
                async with session.get(
                    f'/api/v1/combat/large-scale/battles/{battle_id}/status',
                    headers=self.headers
                ) as response:
                    status = await response.json()
                    
                    if status['performance']['turn_processing_time'] > 5.0:
                        await self.scale_resources(battle_id)
                    
                    await asyncio.sleep(10)
```

---

This API specification supports the large-scale combat vision while maintaining enterprise-grade security, performance, and scalability.