# SectorWars 2102 - API Documentation v1

**Base URL**: `http://localhost:8080/api/v1` (development)
**Production**: `https://api.sectorwars2102.com/v1`
**Total Endpoints**: 358
**Format**: REST + WebSocket
**Authentication**: JWT Bearer tokens

---

## 📚 AISPEC Documentation Index

AISPEC files provide terse, machine-readable API specifications optimized for AI assistants and quick reference.

### Core Player APIs
- **[auth.aispec](./auth.aispec)** - Authentication, OAuth, MFA (16 endpoints)
- **[player.aispec](./player.aispec)** - Player state, first login (13 endpoints)
- **trading.aispec** - Trading, economy, AI recommendations (31 endpoints) *[coming soon]*
- **combat.aispec** - Combat systems (6 endpoints) *[coming soon]*
- **teams.aispec** - Team management, treasury (18 endpoints) *[coming soon]*

### Game Systems
- **sectors.aispec** - Sector navigation (2 endpoints) *[coming soon]*
- **planets.aispec** - Planetary management (8 endpoints) *[coming soon]*
- **fleets.aispec** - Fleet management (13 endpoints) *[coming soon]*
- **drones.aispec** - Drone operations (16 endpoints) *[coming soon]*
- **factions.aispec** - Faction systems (8 endpoints) *[coming soon]*
- **messages.aispec** - In-game messaging (7 endpoints) *[coming soon]*

### Admin APIs
- **admin-core.aispec** - Core admin features (22 endpoints) *[coming soon]*
- **admin-comprehensive.aispec** - Comprehensive management (49 endpoints) *[coming soon]*
- **admin-ships.aispec** - Ship management (4 endpoints) *[coming soon]*
- **admin-combat.aispec** - Combat oversight (5 endpoints) *[coming soon]*
- **admin-economy.aispec** - Economy management (5 endpoints) *[coming soon]*
- **admin-colonization.aispec** - Colonization oversight (3 endpoints) *[coming soon]*

### Infrastructure
- **websocket.aispec** - Real-time WebSocket (9 endpoints) *[coming soon]*
- **system.aispec** - Status, health, audit (24 endpoints) *[coming soon]*
- **multi-regional.aispec** - Regional governance (17 endpoints) *[coming soon]*
- **payment.aispec** - PayPal subscriptions (8 endpoints) *[coming soon]*
- **translation.aispec** - i18n translation (13 endpoints) *[coming soon]*

---

## 🚀 Quick Start

### Authentication

1. **Login** to get JWT tokens:
```bash
curl -X POST http://localhost:8080/api/v1/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{"username": "player1", "password": "password123"}'
```

2. **Use token** in subsequent requests:
```bash
curl -X GET http://localhost:8080/api/v1/player/state \
  -H "Authorization: Bearer {your_access_token}"
```

3. **Refresh token** when it expires:
```bash
curl -X POST http://localhost:8080/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "{your_refresh_token}"}'
```

---

## 📊 API Categories

### Player Gameplay (108 endpoints)
- **Authentication** (16): Login, OAuth, MFA
- **Player State** (13): Stats, ships, movement
- **Trading** (23): Buy/sell, markets, AI recommendations
- **Combat** (6): Player combat, fleeing
- **Teams** (18): Create, join, manage teams
- **Fleets** (13): Fleet operations
- **Drones** (16): Drone deployment
- **Messages** (7): In-game communication
- **Factions** (8): Faction interactions

### Admin Tools (133 endpoints)
- **Core Admin** (22): Galaxy, players, sectors
- **Comprehensive** (49): Ships, ports, analytics, security
- **Ships** (4): Ship CRUD operations
- **Combat** (5): Combat monitoring, intervention
- **Economy** (5): Market management
- **Colonization** (3): Planet oversight
- **Fleets** (9): Fleet management
- **Drones** (8): Drone admin
- **Factions** (8): Faction admin
- **Messages** (4): Message moderation
- **Enhanced** (6): Advanced admin features

### Game Systems (77 endpoints)
- **Sectors** (2): Sector navigation
- **Planets** (8): Planetary management
- **Economy** (8): Economy endpoints
- **Events** (8): Dynamic events
- **AI Systems** (9): AI trading intelligence
- **First Login** (7): Onboarding flow
- **Multi-Regional** (17): Regional governance, nexus
- **Translation** (13): i18n support
- **WebSocket** (9): Real-time connections

### Infrastructure (40 endpoints)
- **System Status** (18): Health, metrics
- **Audit** (4): Audit logs
- **Payment** (8): PayPal integration
- **Security** (8): MFA management
- **Debug** (2): Development tools (dev only)

---

## 🔒 Authentication

All endpoints (except `/status/*` and `/auth/login*`) require JWT authentication:

```
Authorization: Bearer {access_token}
```

### Token Lifecycle
- **Access Token**: 1 hour expiration
- **Refresh Token**: 7 days with sliding window
- **MFA**: Required for admin accounts

---

## 📝 Response Format

### Success Response
```json
{
  "data": { ... },
  "meta": {
    "timestamp": "2025-11-16T12:00:00Z"
  }
}
```

### Error Response
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { ... }
  }
}
```

### Common Error Codes
- `401 UNAUTHORIZED`: Missing or invalid token
- `403 FORBIDDEN`: Insufficient permissions
- `404 NOT_FOUND`: Resource not found
- `422 VALIDATION_ERROR`: Invalid request data
- `429 RATE_LIMIT_EXCEEDED`: Too many requests
- `500 INTERNAL_SERVER_ERROR`: Server error

---

## 🌐 Multi-Regional Architecture

SectorWars 2102 supports player-owned regional territories:

- **Central Nexus**: Hub connecting all regions (5000 sectors)
- **Regional Territories**: Player-owned galaxies with custom rules
- **Cross-Regional Travel**: Via quantum warp tunnels
- **Regional Governance**: Democratic voting, economic policies

See `multi-regional.aispec` for details.

---

## 🔌 WebSocket Connections

Real-time updates available via WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8080/api/v1/ws/connect');
ws.send(JSON.stringify({
  type: 'AUTH',
  token: 'your_jwt_token'
}));
```

See `websocket.aispec` for full specification.

---

## 📊 Interactive API Documentation

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **OpenAPI JSON**: http://localhost:8080/openapi.json

---

## 🔧 Development Tools

### Test Endpoints (dev/test only)
- `POST /test/seed-data` - Seed test data
- `POST /test/reset-database` - Reset database

### Debug Endpoints (dev only)
- `GET /debug/config` - View configuration
- `POST /debug/simulate-error` - Test error handling

---

## 📚 Complete Endpoint Inventory

For a complete list of all 358 endpoints, see:
- **[DOCS/_API_ENDPOINT_INVENTORY.md](../../_API_ENDPOINT_INVENTORY.md)**
- **[DOCS/_api_endpoints.json](../../_api_endpoints.json)**

---

## 🚧 API Versioning

Current version: **v1**

Breaking changes will result in a new version (v2, etc.). All v1 endpoints will remain supported for minimum 6 months after deprecation notice.

---

## 📝 Rate Limiting

- **Default**: 100 requests/minute per IP
- **Authenticated**: 1000 requests/minute per user
- **Admin**: 5000 requests/minute
- **AI Endpoints**: 10 requests/minute (prevent abuse)

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1634567890
```

---

## 🆘 Support

- **Issues**: https://github.com/yourusername/Sectorwars2102/issues
- **Documentation**: This directory
- **API Changes**: Check git commits for changelog

---

*Generated 2025-11-16 - SectorWars 2102 API Documentation v1*
