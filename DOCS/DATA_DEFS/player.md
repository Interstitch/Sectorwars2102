# Player Data Definition

## Overview
Players are the user entities within the Sector Wars 2102 universe. Each player manages ships, resources, and planetary colonies while navigating through different sectors and engaging in trade and other activities.

## Properties

| Property | Type | Description | Constraints |
|----------|------|-------------|-------------|
| id | Integer | Unique identifier | Primary key, auto-increment |
| username | String(80) | Player's unique username | Unique, required, no spaces |
| email | String(120) | Player's email address | Unique, required, valid email format |
| password_hash | String(256) | Hashed password | Required, never stored in plaintext |
| credits | Integer | Current player currency | Default: 10000, non-negative |
| experience | Integer | Player's accumulated experience points | Default: 0, non-negative |
| level | Integer | Player's current level | Calculated from experience, min: 1 |
| reputation | Object | Reputation scores with various factions | See Reputation section |
| ships | Array | Player-owned ships | References to Ship entities |
| home_sector_id | Integer | Current home base sector | Foreign key to sectors table |
| current_sector_id | Integer | Player's current location | Foreign key to sectors table |
| last_login | DateTime | Timestamp of last login | UTC time |
| created_at | DateTime | Account creation timestamp | UTC time, immutable |
| is_admin | Boolean | Administrator privileges flag | Default: false |
| is_active | Boolean | Account active status | Default: true |
| is_deleted | Boolean | Soft deletion flag | Default: false |
| settings | JSON | Player preferences and settings | See Settings section |

## Reputation System
Player reputation is tracked with various factions in the game:

```json
{
  "federation": {
    "value": 0,
    "level": "Neutral",
    "history": []
  },
  "empire": {
    "value": 0,
    "level": "Neutral",
    "history": []
  },
  "traders_guild": {
    "value": 0,
    "level": "Neutral",
    "history": []
  },
  "pirates": {
    "value": 0,
    "level": "Neutral",
    "history": []
  }
}
```

Reputation values range from -1000 to 1000, with corresponding levels:
- -1000 to -751: "Hostile"
- -750 to -251: "Unfriendly"
- -250 to 249: "Neutral"
- 250 to 749: "Friendly"
- 750 to 1000: "Allied"

## Settings
Player settings are stored as a JSON object:

```json
{
  "ui": {
    "theme": "dark",
    "notifications": true,
    "sound_effects": true,
    "music_volume": 0.7
  },
  "gameplay": {
    "auto_refuel": true,
    "tutorial_completed": false,
    "difficulty": "normal"
  },
  "privacy": {
    "share_location": false,
    "visible_in_rankings": true
  }
}
```

## Relationships

| Relation | Entity | Type | Description |
|----------|--------|------|-------------|
| owns | Ship | One-to-Many | Player can own multiple ships |
| owns | Colony | One-to-Many | Player can establish multiple colonies |
| located_in | Sector | Many-to-One | Player is located in a sector |
| home_base | Sector | Many-to-One | Player's designated home sector |
| possesses | Inventory | One-to-One | Player's cargo and possessions |
| completes | Mission | Many-to-Many | Missions completed by player |
| belongs_to | Corporation | Many-to-One | Optional corporation membership |

## API Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|--------------|
| `/api/players` | GET | List all players (admin only) | Yes (Admin) |
| `/api/players/{id}` | GET | Get player details | Yes |
| `/api/players/{id}` | PUT | Update player data | Yes (Owner/Admin) |
| `/api/players/{id}` | DELETE | Delete player account | Yes (Owner/Admin) |
| `/api/players/me` | GET | Get current player data | Yes |
| `/api/players/{id}/ships` | GET | List player's ships | Yes |
| `/api/players/{id}/reputation` | GET | Get player's reputation | Yes |
| `/api/players/{id}/colonies` | GET | List player's colonies | Yes |

## Events

| Event | Payload | Description |
|-------|---------|-------------|
| `player.created` | Player ID | Triggered when new player account is created |
| `player.login` | Player ID, Timestamp | Triggered on successful login |
| `player.level_up` | Player ID, New Level | Triggered when player gains a level |
| `player.reputation_change` | Player ID, Faction, Change | Triggered when reputation changes |
| `player.sector_change` | Player ID, Old Sector, New Sector | Triggered when player moves to a new sector |

## Security Considerations
- Passwords must be hashed using bcrypt before storage
- Admin status can only be granted by existing admin users
- Personal information (email) must be encrypted at rest
- Soft deletion preserves player data for recovery
- Rate limiting implemented on login attempts