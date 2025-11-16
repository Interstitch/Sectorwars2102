# SectorWars 2102 - API Documentation v1

**Base URL**: `http://localhost:8080/api/v1` (development)
**Production**: `https://api.sectorwars2102.com/v1`
**Total Endpoints**: 358
**Documented**: 355 endpoints (99.2%)
**Format**: REST + WebSocket
**Authentication**: JWT Bearer tokens
**Documentation Status**: Current and validated (2025-11-16)

---

## 📚 AISPEC Documentation Index

AISPEC files provide terse, machine-readable API specifications optimized for AI assistants and quick reference. All documentation validated against actual gameserver code.

### Player-Facing APIs ✅

- **[auth.aispec](./auth.aispec)** - Authentication, OAuth (GitHub/Google/Steam), MFA, token refresh (24 endpoints)
- **[player.aispec](./player.aispec)** - Player state, statistics, ship management, first login AI dialogue (13 endpoints)
- **[trading.aispec](./trading.aispec)** - Trading operations, quantum AI, trade cascades, market analytics (31 endpoints)
- **[combat.aispec](./combat.aispec)** - Player combat (ship/planet/port), combat status, admin monitoring (6 endpoints)
- **[teams.aispec](./teams.aispec)** - Team creation, member management, treasury operations, messaging (18 endpoints)
- **[sectors-planets.aispec](./sectors-planets.aispec)** - Sector navigation, planetary colonization, genesis devices (10 endpoints)
- **[fleets-drones.aispec](./fleets-drones.aispec)** - Fleet formations, fleet battles, drone deployment, autonomous operations (29 endpoints)
- **[factions-messages.aispec](./factions-messages.aispec)** - Faction reputation, missions, player messaging (15 endpoints)

**Subtotal: 146 endpoints**

### Administrative APIs ✅

- **[admin.aispec](./admin.aispec)** - Complete admin toolset: user/player management, galaxy editing, team oversight, fleet/drone/ship management, colonization, factions, message moderation, regions, security, audit logging (123 endpoints)

**Subtotal: 123 endpoints**

### Infrastructure APIs ✅

- **[infrastructure.aispec](./infrastructure.aispec)** - System status/health, WebSocket real-time, multi-regional coordination, internationalization (i18n), payment processing (PayPal), events system, AI trading intelligence, audit logging (86 endpoints)

**Subtotal: 86 endpoints**

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

### Player-Facing APIs (146 endpoints)
- **Authentication & MFA** (24): Login (form/JSON), OAuth (GitHub/Google/Steam), TOTP MFA setup/verification, token refresh, logout
- **Player State** (13): Current state, statistics, ship details, sector movement, first login AI dialogue
- **Trading & Economy** (31): Basic trading (buy/sell/dock), quantum trading (superposition/ghost trades), trade cascades, AI recommendations, market analytics
- **Combat** (6): Engage ship/planet/port targets, combat status, flee mechanics
- **Teams & Treasury** (18): Create/join/leave teams, member management, treasury operations (12 resource types), team messaging
- **Sectors & Planets** (10): Sector discovery, planetary colonization, building upgrades, genesis device deployment, planetary defenses
- **Fleets & Drones** (29): Fleet creation/formations/battles, drone building/deployment, autonomous drone operations, batch operations
- **Factions & Messages** (15): Faction reputation system, faction missions, territory control, player-to-player messaging, message threading

### Administrative APIs (123 endpoints)
- **User & Player Management** (22): View/edit/delete players, admin statistics, player analytics
- **Galaxy Management** (16): Generate/clear galaxy, create/edit/delete sectors, warp tunnel management
- **Team Administration** (8): Team analytics, force disband, member management
- **Fleet Management** (9): Fleet oversight, force move, battle resolution
- **Drone Management** (8): Drone oversight, force recall, drone statistics
- **Ship Management** (4): Ship CRUD operations
- **Colonization Management** (3): Colony oversight
- **Faction Management** (8): Faction CRUD, territory assignment, faction war management
- **Message Moderation** (4): Flagged message review, message deletion
- **Region Management** (17): Multi-regional governance, player transfers, regional settings
- **Comprehensive Tools** (49): Analytics, monitoring, security tools, content management
- **Enhanced Security** (6): Audit logs, suspicious activity detection, ban/unban management

### Infrastructure APIs (86 endpoints)
- **System Status & Health** (18): Health checks, metrics (CPU/memory/requests), uptime, maintenance mode, feature flags
- **WebSocket Real-Time** (9): Player/sector/team/combat/market/chat event streams, admin monitoring
- **Multi-Regional Coordination** (17): Region listing, governance, voting, cross-regional travel, regional economy stats
- **Internationalization** (13): Language support, translations, contributor management, translation approval
- **Payment Processing** (8): PayPal subscription creation/management, webhook handling, payment history
- **Events System** (8): Dynamic events, participation, rewards, leaderboards
- **AI Trading Intelligence** (9): Trading recommendations, route optimization, market analysis, price prediction, risk assessment
- **Audit Logging** (4): Player/admin action history, security event tracking

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

- **Central Nexus**: Hub connecting all regions (default starting region)
- **Player-Owned Regions**: Custom galaxies with configurable rules and governance
- **Regional Governance**: Democratic voting on policies, proposals, and rule changes
- **Cross-Regional Travel**: Via quantum warp tunnels in the Central Nexus
- **Regional Economy**: Isolated economies with regional rankings and statistics
- **Territory Creation**: Players can create new regions with ownership tokens

See `infrastructure.aispec` (Multi-Regional Coordination section) for complete API details.

---

## 🔌 WebSocket Connections

Real-time game updates available via WebSocket:

```javascript
const ws = new WebSocket('ws://localhost:8080/api/v1/ws/connect');

// Authenticate
ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'your_jwt_token'
  }));
};

// Subscribe to channels
ws.send(JSON.stringify({
  type: 'subscribe',
  channels: ['player', 'sector:42', 'team:team-uuid', 'market']
}));

// Handle events
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Event:', message.type, message.data);
};
```

**Event Types**: player.update, sector.ship_entered, combat.started, market.price_changed, team.message, notification

See `infrastructure.aispec` (WebSocket Real-Time section) for full specification.

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

For a complete list of all 358 endpoints discovered from source code:
- **[../../_API_ENDPOINT_INVENTORY.md](../../_API_ENDPOINT_INVENTORY.md)** - Human-readable inventory
- **[../../_api_endpoints.json](../../_api_endpoints.json)** - Machine-readable JSON data
- **[../../_discover_api_endpoints.py](../../_discover_api_endpoints.py)** - Auto-discovery script

**Documentation Coverage**: 355/358 endpoints (99.2%)
**Undocumented**: 3 debug/test-only endpoints (intentionally excluded)

---

## 🚧 API Versioning

**Current Version**: v1
**Status**: Production-ready and stable

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

## 🆘 Support & Contributing

- **Issues**: https://github.com/yourusername/Sectorwars2102/issues
- **API Documentation**: See AISPEC files in this directory
- **Endpoint Discovery**: Run `python DOCS/_discover_api_endpoints.py` to scan route files
- **Contributing**: When adding new endpoints, update the relevant AISPEC file

---

## 📋 Documentation Maintenance

All AISPEC files validated against actual gameserver code on 2025-11-16.

To update documentation:
1. Add/modify endpoints in `services/gameserver/src/api/routes/*.py`
2. Run `python DOCS/_discover_api_endpoints.py` to update inventory
3. Update relevant AISPEC file(s) in this directory
4. Test via Swagger UI at http://localhost:8080/docs

---

*Last Updated: 2025-11-16 - SectorWars 2102 API Documentation v1*
*Documentation validated against gameserver source code*
*Coverage: 355/358 endpoints (99.2%)*
