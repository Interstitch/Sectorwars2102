# Player Data Definition

## Overview
Players are the user entities within the Sector Wars 2102 galaxy. Each player manages ships, resources, and planetary colonies while navigating through different sectors and engaging in trade and other activities.

## Properties

| Property | Type | Description | Constraints |
|----------|------|-------------|-------------|
| id | String | Unique identifier | Primary key, UUID |
| username | String(80) | Player's unique username | Unique, required, no spaces |
| email | String(120) | Player's email address | Unique, required, valid email format |
| password_hash | String(256) | Hashed password | Required, never stored in plaintext |
| credits | Integer | Current player currency | Default: 10000, non-negative |
| turns | Integer | Available movement/action turns | Default: 1000, max: 5000, resets daily |
| reputation | Object | Reputation scores with factions | See Reputation section |
| ships | Array | Player-owned ships | References to Ship entities |
| current_ship_id | String | Currently active ship | Foreign key to ships table |
| home_sector_id | Integer | Current home base sector | Foreign key to sectors table |
| current_sector_id | Integer | Player's current location | Foreign key to sectors table |
| is_ported | Boolean | Whether docked at port | Default: false |
| is_landed | Boolean | Whether landed on planet | Default: false |
| planets_owned | Array | Owned planets | References to Planet entities |
| ports_owned | Array | Owned ports | References to Port entities |
| team_id | String | Team membership | Foreign key to teams table, nullable |
| attack_drones | Integer | Offensive drones in inventory | Default: 0, non-negative |
| defense_drones | Integer | Defensive drones in inventory | Default: 0, non-negative |
| mines | Integer | Space mines in inventory | Default: 0, non-negative |
| insurance | Object | Ship insurance details | See Insurance section |
| last_login | DateTime | Timestamp of last login | UTC time |
| created_at | DateTime | Account creation timestamp | UTC time, immutable |
| turn_reset_at | DateTime | Timestamp of last turn reset | UTC time |
| is_admin | Boolean | Administrator privileges flag | Default: false |
| is_active | Boolean | Account active status | Default: true |
| is_deleted | Boolean | Soft deletion flag | Default: false |
| settings | JSON | Player preferences and settings | See Settings section |

## Reputation System
Player reputation is tracked with six major factions in the game:

```json
{
  "terran_federation": {
    "value": 0,
    "level": "Neutral",
    "history": []
  },
  "mercantile_guild": {
    "value": 0,
    "level": "Neutral",
    "history": []
  },
  "frontier_coalition": {
    "value": 0,
    "level": "Neutral",
    "history": []
  },
  "astral_mining_consortium": {
    "value": 0,
    "level": "Neutral",
    "history": []
  },
  "nova_scientific_institute": {
    "value": 0,
    "level": "Neutral",
    "history": []
  },
  "fringe_alliance": {
    "value": 0,
    "level": "Neutral",
    "history": []
  }
}
```

Reputation values range from -800 to 800, with corresponding levels:
- -800 to -701: "Public Enemy" (-8)
- -700 to -601: "Criminal" (-7)
- -600 to -501: "Outlaw" (-6)
- -500 to -401: "Pirate" (-5)
- -400 to -301: "Smuggler" (-4)
- -300 to -201: "Untrustworthy" (-3)
- -200 to -101: "Suspicious" (-2)
- -100 to -1: "Questionable" (-1)
- 0: "Neutral" (0)
- 1 to 100: "Recognized" (+1)
- 101 to 200: "Acknowledged" (+2)
- 201 to 300: "Trusted" (+3)
- 301 to 400: "Respected" (+4)
- 401 to 500: "Valued" (+5)
- 501 to 600: "Honored" (+6)
- 601 to 700: "Revered" (+7)
- 701 to 800: "Exalted" (+8)

## Settings
Player settings are stored as a JSON object:

```json
{
  "ui": {
    "theme": "dark",
    "notifications": true,
    "sound_effects": true,
    "music_volume": 0.7,
    "auto_refresh_rate": 30
  },
  "gameplay": {
    "auto_refuel": true,
    "auto_repair": false,
    "default_drone_deployment": 0,
    "combat_retreat_threshold": 25,
    "cat_companion": false
  },
  "privacy": {
    "share_location": false,
    "visible_in_rankings": true,
    "show_online_status": true,
    "accept_team_invites": true
  },
  "notifications": {
    "combat_alerts": true,
    "team_messages": true,
    "market_opportunities": false,
    "planet_updates": true
  }
}
```

## Insurance
Ship insurance details are stored as an object:

```json
{
  "active": true,
  "expires_at": "2023-12-31T23:59:59Z",
  "premium_paid": 10000,
  "covered_ships": ["ship_id_1", "ship_id_2"],
  "deductible_percentage": 15,
  "claims_made": 1,
  "last_claim": "2023-11-15T14:22:10Z"
}
```

## Relationships

| Relation | Entity | Type | Description |
|----------|--------|------|-------------|
| owns | Ship | One-to-Many | Player can own multiple ships |
| pilots | Ship | One-to-One | Player's currently active ship |
| owns | Planet | One-to-Many | Player can own multiple planets |
| owns | Port | One-to-Many | Player can own multiple ports |
| located_in | Sector | Many-to-One | Player is located in a sector |
| home_base | Sector | Many-to-One | Player's designated home sector |
| member_of | Team | Many-to-One | Optional team membership |
| has | Reputation | One-to-Many | Reputation with each faction |

## API Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|--------------|
| `/api/v1/players` | GET | List all players (admin only) | Yes (Admin) |
| `/api/v1/players/{id}` | GET | Get player details | Yes |
| `/api/v1/players/{id}` | PUT | Update player data | Yes (Owner/Admin) |
| `/api/v1/players/{id}` | DELETE | Delete player account | Yes (Owner/Admin) |
| `/api/v1/players/me` | GET | Get current player data | Yes |
| `/api/v1/players/{id}/ships` | GET | List player's ships | Yes |
| `/api/v1/players/{id}/reputation` | GET | Get player's reputation | Yes |
| `/api/v1/players/{id}/planets` | GET | List player's planets | Yes |
| `/api/v1/players/{id}/ports` | GET | List player's ports | Yes |
| `/api/v1/players/me/turn-reset` | POST | Reset player's turns (once per day) | Yes |
| `/api/v1/players/{id}/insurance` | GET | View insurance details | Yes (Owner/Admin) |
| `/api/v1/players/{id}/insurance` | POST | Purchase insurance | Yes (Owner) |
| `/api/v1/players/{id}/team` | GET | View team membership | Yes |
| `/api/v1/players/{id}/team` | POST | Join a team | Yes (Owner) |
| `/api/v1/players/{id}/team` | DELETE | Leave current team | Yes (Owner) |
| `/api/v1/players/first-login/start` | POST | Start first login experience | Yes |
| `/api/v1/players/first-login/dialogue` | POST | Submit dialogue response | Yes |
| `/api/v1/players/first-login/complete` | POST | Complete first login flow | Yes |
| `/api/v1/players/{id}/first-login` | GET | Get first login data | Yes (Owner/Admin) |

## Events

| Event | Payload | Description |
|-------|---------|-------------|
| `player.created` | Player ID | Triggered when new player account is created |
| `player.login` | Player ID, Timestamp | Triggered on successful login |
| `player.first_login_started` | Player ID, Session ID | Triggered when first login dialogue begins |
| `player.first_login_completed` | Player ID, Session ID, Outcome | Triggered when first login process completes |
| `player.reputation_change` | Player ID, Faction, Value, Level | Triggered when reputation changes |
| `player.sector_change` | Player ID, Old Sector, New Sector | Triggered when player moves to a new sector |
| `player.ship_change` | Player ID, Ship ID | Triggered when player changes active ship |
| `player.turns_reset` | Player ID, New Turn Count | Triggered when daily turns reset |
| `player.planet_acquired` | Player ID, Planet ID | Triggered when player acquires a planet |
| `player.port_acquired` | Player ID, Port ID | Triggered when player acquires a port |
| `player.combat` | Player ID, Target ID, Outcome | Triggered during combat |
| `player.team_joined` | Player ID, Team ID | Triggered when player joins a team |
| `player.team_left` | Player ID, Team ID | Triggered when player leaves a team |
| `player.insurance_purchase` | Player ID, Details | Triggered when player buys insurance |
| `player.insurance_claim` | Player ID, Ship ID | Triggered when player claims insurance |

## Security Considerations
- Passwords must be hashed using bcrypt before storage
- Admin status can only be granted by existing admin users
- Personal information (email) must be encrypted at rest
- Soft deletion preserves player data for recovery
- Rate limiting implemented on login attempts
- Turn reset requires 24-hour cooldown to prevent abuse
- Insurance claims must validate ship ownership and destruction records
- Team joining has a 24-hour cooldown after leaving a team

## Code Interface

```typescript
export interface PlayerReputation {
  value: number;
  level: string;
  history: {
    timestamp: Date;
    change: number;
    reason: string;
  }[];
}

export interface PlayerFactionReputations {
  terran_federation: PlayerReputation;
  mercantile_guild: PlayerReputation;
  frontier_coalition: PlayerReputation;
  astral_mining_consortium: PlayerReputation;
  nova_scientific_institute: PlayerReputation;
  fringe_alliance: PlayerReputation;
}

export interface PlayerInsurance {
  active: boolean;
  expires_at: Date;
  premium_paid: number;
  covered_ships: string[];
  deductible_percentage: number;
  claims_made: number;
  last_claim: Date | null;
}

export interface PlayerFirstLoginData {
  completed: boolean;                // Whether first login process is complete
  session_id: string | null;         // Reference to FirstLoginSession
  awarded_ship: string | null;       // Ship type awarded during first login
  negotiation_skill: string | null;  // Assessed negotiation skill level
  persuasion_score: number | null;   // Final persuasion score (0-1)
  chosen_name: string | null;        // Name chosen during dialogue
  completed_at: Date | null;         // When first login was completed
  trade_bonus_active: boolean;       // Whether negotiation bonus is active
  notoriety_penalty_active: boolean; // Whether reputation penalty is active
}

export interface PlayerModel {
  id: string;
  username: string;
  email: string;
  password_hash: string;
  credits: number;
  turns: number;
  reputation: PlayerFactionReputations;
  ships: string[];
  current_ship_id: string | null;
  home_sector_id: number;
  current_sector_id: number;
  is_ported: boolean;
  is_landed: boolean;
  planets_owned: string[];
  ports_owned: string[];
  team_id: string | null;
  attack_drones: number;
  defense_drones: number;
  mines: number;
  insurance: PlayerInsurance | null;
  first_login: PlayerFirstLoginData;  // First login experience data
  last_login: Date;
  created_at: Date;
  turn_reset_at: Date;
  is_admin: boolean;
  is_active: boolean;
  is_deleted: boolean;
  settings: Record<string, any>;
}
```