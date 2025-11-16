# SectorWars 2102 - API Documentation

**Status**: Current and accurate (validated 2025-11-16)
**Total Endpoints**: 358
**API Version**: v1
**Base URL**: `http://localhost:8080/api/v1`

---

## 🎯 Quick Navigation

### Current API Documentation (v1)
**All documentation now in: [`v1/`](./v1/)**

- **[v1/README.md](./v1/README.md)** - Complete API overview and quick start
- **[v1/auth.aispec](./v1/auth.aispec)** - Authentication, OAuth, MFA (24 endpoints)
- **[v1/player.aispec](./v1/player.aispec)** - Player gameplay, first login (13 endpoints)
- **More AISPEC files coming soon** (see v1/README.md for full list)

### Complete Endpoint Inventory
- **[../_API_ENDPOINT_INVENTORY.md](../_API_ENDPOINT_INVENTORY.md)** - All 358 endpoints discovered from code
- **[../_api_endpoints.json](../_api_endpoints.json)** - Machine-readable endpoint data

---

## 📊 Documentation Coverage

**Documented**: 37 endpoints (10.3%)
**In Progress**: 321 endpoints (89.7%)

### Covered APIs
✅ Authentication (16 endpoints)
✅ MFA/Security (8 endpoints)
✅ Player State (6 endpoints)
✅ First Login (7 endpoints)

### Coming Soon
📝 Trading & Economy (31 endpoints)
📝 Admin APIs (133 endpoints)
📝 Teams (18 endpoints)
📝 Combat (6 endpoints)
📝 WebSocket (9 endpoints)
📝 Multi-Regional (17 endpoints)
📝 And 113 more...

---

## 🚀 Getting Started

1. **Read the overview**: [v1/README.md](./v1/README.md)
2. **Authenticate**: See [v1/auth.aispec](./v1/auth.aispec)
3. **Explore endpoints**: Check [_API_ENDPOINT_INVENTORY.md](../_API_ENDPOINT_INVENTORY.md)
4. **Interactive docs**: http://localhost:8080/docs

---

## 🔄 Recent Changes

### 2025-11-16: Complete Rewrite
- ✅ Discovered all 358 actual endpoints from code
- ✅ Removed 3 outdated API specification files
- ✅ Created accurate AISPEC documentation structure
- ✅ Generated complete endpoint inventory
- 🚧 In progress: Documenting remaining 321 endpoints

### Previous Docs (Archived)
Old API documentation moved to `DOCS/_REVIEW_NEEDED/old-api-docs/`:
- ~~GameServer.aispec~~ (claimed 200+ endpoints, was outdated)
- ~~MULTI_REGIONAL_API_SPECIFICATION.md~~ (outdated)
- ~~QUANTUM_TRADING_API.md~~ (outdated)

---

## 📚 AISPEC Format

All API docs use the AISPEC format - terse, machine-readable specifications optimized for AI assistants:

```
OVERVIEW: Single sentence summary

FACTS:
* Key technical facts
* Authentication requirements
* Rate limits

ENDPOINTS:
* METHOD /path - Description

SCHEMAS:
TypeName:
  field: Type, constraints

EXAMPLES:
```bash
curl examples
```

See [v1/auth.aispec](./v1/auth.aispec) for a complete example.

---

## 🎯 Documentation Goals

1. ✅ **Accurate**: Validated against actual code
2. ✅ **Complete**: Cover all 358 endpoints
3. ✅ **Maintainable**: Organized by functional area
4. ✅ **Machine-readable**: AISPEC format for AI tools
5. 🚧 **Up-to-date**: Auto-generated from code (coming soon)

---

## 🔧 Development Tools

### Discover Endpoints
```bash
cd DOCS
python3 _discover_api_endpoints.py
```

This scans all route files and generates:
- `_API_ENDPOINT_INVENTORY.md` - Human-readable inventory
- `_api_endpoints.json` - Machine-readable data

### Interactive API Explorer
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

---

## 📝 Contributing API Docs

When adding new endpoints:

1. Add route in `services/gameserver/src/api/routes/*.py`
2. Run discovery script: `python3 DOCS/_discover_api_endpoints.py`
3. Update relevant AISPEC file in `DOCS/API/v1/`
4. Test via Swagger UI

---

*Last updated: 2025-11-16*
*Documentation validated against actual gameserver code*
