# SectorWars 2102 Documentation Architecture

## 🔍 Documentation Audit & Quality Reports

**Last Major Update**: 2025-11-16
**API Documentation**: ✅ Complete rewrite (355/358 endpoints = 99.2% coverage)

### API Documentation Status

**NEW**: Complete API documentation rewrite with 10 AISPEC files validated against actual code
- See **[API/README.md](./API/README.md)** for full API documentation overview
- See **[API/v1/README.md](./API/v1/README.md)** for v1 API quick start guide
- Auto-discovery tool: `python3 _discover_api_endpoints.py`

### Documentation Quality Tools

```bash
# Discover all API endpoints from source code
python3 _discover_api_endpoints.py

# Generate API endpoint inventory
# Creates: _API_ENDPOINT_INVENTORY.md and _api_endpoints.json
```

**Recent Improvements:**
- ✅ API documentation validated against gameserver source code
- ✅ 355/358 endpoints documented in AISPEC format
- ✅ Removed 3 outdated API specification files
- ✅ Created organized v1 documentation structure

---

## 📚 Documentation Philosophy

This documentation system uses a **multi-layer architecture** designed for different audiences and consumption patterns:

- **SPECS/** - Machine-readable specifications (AISPEC format) 
- **API/** - Complete API documentation with examples
- **ARCHITECTURE/** - System design and technical architecture
- **FEATURES/** - Business requirements and feature specifications  
- **GUIDES/** - Implementation guides and tutorials
- **STATUS/** - Live development tracking and coordination
- **ARCHIVE/** - Historical decisions and completed work

## 🎯 Documentation Layers

### Layer 1: SPECS/ (Machine-Readable)
**Target**: AI assistants, automated tools, quick reference
**Format**: AISPEC (terse, fact-dense)
**Maintenance**: Auto-updated with code changes

### Layer 2: API/ (Developer Interface)
**Target**: Frontend/backend integration
**Format**: OpenAPI + examples
**Maintenance**: Generated from code annotations

### Layer 3: ARCHITECTURE/ (Technical Design)
**Target**: Senior developers, system architects
**Format**: Technical diagrams + explanations
**Maintenance**: Updated with major architectural changes

### Layer 4: FEATURES/ (Business Requirements)
**Target**: Product managers, stakeholders, new developers
**Format**: User stories + acceptance criteria
**Maintenance**: Updated during planning phases

### Layer 5: GUIDES/ (How-To)
**Target**: Developers implementing features
**Format**: Step-by-step instructions + code examples
**Maintenance**: Updated when processes change

### Layer 6: STATUS/ (Live Tracking)
**Target**: Development team coordination
**Format**: Real-time status boards
**Maintenance**: Updated daily/weekly

## 🔄 Information Flow

```
SPECS/ ←→ API/ ←→ ARCHITECTURE/
   ↓         ↓         ↓
FEATURES/ → GUIDES/ → STATUS/
   ↓         ↓         ↓
      ARCHIVE/ (all decisions flow here)
```

## 📋 Directory Structure (Updated 2025-12-09)

```
DOCS/
├── README.md (this file)
├── SPECS/              # AISPEC format, AI-optimized (13 files)
│   ├── README.md
│   ├── Architecture.aispec
│   ├── AuthSystem.aispec
│   ├── Database.aispec
│   ├── DevEnvironment.aispec
│   ├── GameConcepts.aispec
│   ├── GameMechanics.aispec
│   ├── GameServer.aispec
│   ├── Ranking.aispec
│   ├── Resources.aispec
│   ├── Ships.aispec
│   ├── WebSocket.aispec
│   └── AISpecificationDoc.aispec
├── API/                # Complete API documentation (99.2% coverage)
│   ├── README.md           # API overview & navigation
│   └── v1/                 # API v1 documentation (10 AISPEC files)
│       ├── README.md
│       ├── auth.aispec, player.aispec, trading.aispec
│       ├── combat.aispec, teams.aispec, sectors-planets.aispec
│       ├── fleets-drones.aispec, factions-messages.aispec
│       ├── admin.aispec, infrastructure.aispec
│       └── comprehensive_api_specification.md
├── ARCHITECTURE/       # Technical system design
│   └── data-models/    # Comprehensive entity definitions (24 files)
│       ├── combat/, economy/, entities/
│       ├── galaxy/, gameplay/, player/, system/
│       └── multi_regional_overview.md
├── FEATURES/           # Business requirements & implementations (35 files)
│   ├── README.md           # Feature index and navigation
│   ├── DEFINITIONS/        # Core terminology, rules, resources, ships
│   ├── GAMEPLAY/           # Combat, reputation, teams, first login
│   ├── ECONOMY/            # Trading, ports, markets
│   ├── GALAXY/             # Galaxy generation, warp gates, sectors
│   ├── PLANETS/            # Colonization, defense, citadels
│   ├── AI_SYSTEMS/         # ARIA AI, security systems
│   ├── INFRASTRUCTURE/     # Multi-regional, i18n, real-time
│   └── WEB_INTERFACES/     # Admin UI, Player UI
├── STATUS/             # Live development tracking
│   ├── DEVELOPMENT_STATE_2025-12-06.md
│   └── ARIA_IMPLEMENTATION_AUDIT.md
└── _TOOLS/             # Documentation utilities (Python scripts, JSON)
    ├── _discover_api_endpoints.py
    ├── _analyze_accuracy.py
    ├── _generate_inventory.py
    ├── _api_endpoints.json
    ├── _accuracy_report.json
    └── _inventory.json
```

## 🎨 Document Templates

### AISPEC Format
```
OVERVIEW: Single sentence summary
FACTS: 
* Key technical facts
* Dependencies and constraints
* Performance characteristics
ENDPOINTS: API endpoints with brief descriptions
FILES: Relevant source code paths
EXAMPLES: Minimal working examples
```

### API Documentation Format
```
# Endpoint Name
**URL**: `POST /api/v1/endpoint`
**Auth**: Required/Optional
**Purpose**: What this endpoint does

## Request
[JSON schema or TypeScript interface]

## Response
[JSON schema with examples]

## Examples
[curl commands and responses]

## Error Codes
[Common error scenarios]
```

## 🔧 Maintenance Strategy

- **SPECS/**: Updated when core systems change
- **API/**: Generated from code discovery tools
- **ARCHITECTURE/**: Updated during architectural reviews
- **FEATURES/**: Updated during sprint planning
- **STATUS/**: Updated with development milestones

## ✅ Recent Organization Improvements

**Documentation Cleanup (2025-12-09)**:
- ✅ Fixed broken file references in FEATURES/README.md and TURN_SYSTEM.md
- ✅ Updated directory structure to reflect actual contents
- ✅ Organized utility scripts into `_TOOLS/` directory
- ✅ Removed references to non-existent directories
- ✅ Cleaned up empty directories and stale file references
- ✅ Merged specification files into FEATURES/ documentation:
  - combat-interface → COMBAT_MECHANICS.md
  - ship-management → SHIP_MANAGEMENT.md
  - team-systems → TEAM_SYSTEMS.md
  - trading-system → PORT_TRADING.md
- ✅ Removed _REVIEW_NEEDED/ directory (all content consolidated)

**API Documentation Update (2025-11-16)**:
- ✅ Complete API documentation rewrite with 355/358 endpoints documented
- ✅ All AISPEC files validated against gameserver source code
- ✅ Created auto-discovery tool for endpoint inventory
- ✅ Organized API documentation into logical v1 structure

**Note**: Target 7-layer architecture: SPECS → API → ARCHITECTURE → FEATURES → GUIDES → STATUS → ARCHIVE. Currently implemented: SPECS, API, ARCHITECTURE, FEATURES, STATUS. Future: GUIDES, ARCHIVE directories.

---
*Documentation Architecture v1.3 - Updated: 2025-12-09*