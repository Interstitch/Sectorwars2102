# Zone Data Definition

## Overview

Zones in Sector Wars 2102 represent **security and policing regions within parent Regions**. Each zone defines the security level, danger rating, and sector boundaries within its parent region. Zones provide the framework for law enforcement, pirate activity, and player safety across different areas of space.

**Key Concept**: Zones belong to **Regions** (not the Galaxy). Each region defines its own zones based on its region type.

## Position in Galaxy Hierarchy

Zones occupy a specific level in the galaxy's structure:

```
Galaxy
├── Region (Central Nexus, Terran Space, Player-owned)
    ├── Zone (Security/policing boundaries)
    │   └── Sectors (assigned to zones by sector_number)
    └── Cluster (Navigation/organizational groups)
        └── Sectors (same sectors, different grouping)
```

**Important**: Zones and Clusters are **orthogonal dimensions**:
- A sector has BOTH a zone_id (security/policing) AND a cluster_id (navigation)
- Zone boundaries are arbitrary (defined by start_sector/end_sector ranges)
- Zone boundaries can split across cluster boundaries

## Data Model

```python
class Zone(Base):
    """Zone - Security/Policing Region within a parent Region"""
    __tablename__ = "zones"

    # Identity
    id: UUID                      # Unique identifier
    region_id: UUID               # Parent region (FOREIGN KEY)

    # Naming
    name: str                     # Zone name ("The Expanse", "Federation Space", etc.)
    zone_type: str                # EXPANSE, FEDERATION, BORDER, FRONTIER

    # Sector Boundaries (arbitrary, can cross clusters)
    start_sector: int             # First sector number in zone (inclusive)
    end_sector: int               # Last sector number in zone (inclusive)
    sector_count: int             # Calculated: end_sector - start_sector + 1

    # Security Characteristics
    policing_level: int           # 0-10 (0=lawless, 10=maximum security)
    danger_rating: int            # 0-10 (0=completely safe, 10=extremely dangerous)

    # Timestamps
    created_at: DateTime
    updated_at: DateTime

    # Relationships
    region: Region                # Parent region
    sectors: List[Sector]         # All sectors within this zone's boundaries

    # Constraints
    # - start_sector >= 1
    # - end_sector >= start_sector
    # - policing_level between 0 and 10
    # - danger_rating between 0 and 10
```

## Zone Types by Region

### Central Nexus Zones

**Region Type**: `central_nexus`
**Total Sectors**: 5000
**Number of Zones**: 1

| Zone Name | Zone Type | Sectors | Policing | Danger | Description |
|-----------|-----------|---------|----------|--------|-------------|
| The Expanse | EXPANSE | 1-5000 | 3 | 6 | Vast, sparse region with light policing |

**Characteristics**:
- Single massive zone covering entire region
- Light policing (sparse population)
- Moderate danger
- Reduced infrastructure (5% ports, 10% planets, 0.3x warp density)

### Terran Space Zones

**Region Type**: `terran_space`
**Total Sectors**: 300
**Number of Zones**: 3

| Zone Name | Zone Type | Sectors | Policing | Danger | Description |
|-----------|-----------|---------|----------|--------|-------------|
| Federation Space | FEDERATION | 1-100 | 9 | 1 | Heavily policed, very safe |
| Border Regions | BORDER | 101-200 | 5 | 4 | Moderate policing, some danger |
| Frontier Space | FRONTIER | 201-300 | 2 | 8 | Light policing, high danger |

**Characteristics**:
- Three zones dividing region into thirds
- Progressive security degradation from Fed → Border → Frontier
- Standard infrastructure distribution

### Player-Owned Region Zones

**Region Type**: `player_owned`
**Total Sectors**: 100-1000 (variable)
**Number of Zones**: 3 (default)

| Zone Name | Zone Type | Sectors | Policing | Danger | Description |
|-----------|-----------|---------|----------|--------|-------------|
| Federation Space | FEDERATION | 1-33% | 9 | 1 | Heavily policed, very safe |
| Border Regions | BORDER | 34%-67% | 5 | 4 | Moderate policing, some danger |
| Frontier Space | FRONTIER | 68%-100% | 2 | 8 | Light policing, high danger |

**Characteristics**:
- Three zones dividing region into dynamic thirds
- Default configuration (can be customized when region purchased)
- Players may add/remove/adjust zones during region creation

## Zone Characteristics

### Policing Level (0-10)

- **9-10**: Maximum security (Federation Space)
  - Heavy patrol presence
  - Illegal activities immediately punished
  - Safe for new players

- **4-6**: Moderate security (Border Regions)
  - Occasional patrols
  - Some illegal activity tolerated
  - Mixed player activity

- **0-3**: Light/No security (Frontier Space, The Expanse)
  - Minimal patrol presence
  - Lawless regions
  - High risk, high reward

### Danger Rating (0-10)

- **0-3**: Very safe
  - Rare hostile encounters
  - Protected trade routes
  - Low risk gameplay

- **4-7**: Moderate danger
  - Occasional pirate activity
  - Some combat expected
  - Balanced risk/reward

- **8-10**: Extremely dangerous
  - Frequent hostile encounters
  - High pirate activity
  - High risk, high reward

## Zone Assignment Logic

Sectors are assigned to zones based on their `sector_number`:

```python
def get_zone_for_sector(sector_number: int, zones: List[Zone]) -> Zone:
    """Find which zone a sector belongs to"""
    for zone in zones:
        if zone.start_sector <= sector_number <= zone.end_sector:
            return zone
    return None  # Sector not in any zone
```

**Example** (Terran Space):
- Sector 50 → Federation Space (1-100)
- Sector 150 → Border Regions (101-200)
- Sector 275 → Frontier Space (201-300)

## Database Schema

```sql
CREATE TABLE zones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    region_id UUID NOT NULL REFERENCES regions(id) ON DELETE CASCADE,

    name VARCHAR(200) NOT NULL,
    zone_type VARCHAR(50) NOT NULL,

    start_sector INTEGER NOT NULL,
    end_sector INTEGER NOT NULL,

    policing_level INTEGER NOT NULL DEFAULT 5,
    danger_rating INTEGER NOT NULL DEFAULT 5,

    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT check_start_sector_positive CHECK (start_sector >= 1),
    CONSTRAINT check_end_after_start CHECK (end_sector >= start_sector),
    CONSTRAINT check_policing_range CHECK (policing_level >= 0 AND policing_level <= 10),
    CONSTRAINT check_danger_range CHECK (danger_rating >= 0 AND danger_rating <= 10)
);

CREATE INDEX ix_zones_region_id ON zones(region_id);
```

## API Endpoints

### Get Zones for a Region

```
GET /api/v1/admin/regions/{region_id}/zones
```

**Response**:
```json
{
  "region_id": "uuid",
  "zones": [
    {
      "id": "uuid",
      "region_id": "uuid",
      "name": "Federation Space",
      "zone_type": "FEDERATION",
      "start_sector": 1,
      "end_sector": 100,
      "sector_count": 100,
      "policing_level": 9,
      "danger_rating": 1,
      "created_at": "2025-11-16T...",
      "actual_sector_count": 100,
      "avg_security_level": 7.5
    }
  ],
  "total_zones": 3
}
```

### Get Zone Details

```
GET /api/v1/admin/regions/{region_id}/zones/{zone_id}
```

**Response**: Single zone object with statistics

## Zone vs Cluster

**Common Confusion**: Zones and Clusters both group sectors, but serve different purposes:

| Aspect | Zone | Cluster |
|--------|------|---------|
| Purpose | Security/policing | Navigation/organization |
| Belongs to | Region | Region |
| Boundaries | start_sector to end_sector | Sectors grouped by proximity |
| Relationship to Sectors | Sectors have zone_id | Sectors have cluster_id |
| Can cross each other? | Yes (orthogonal) | Yes (orthogonal) |
| Player visible? | Via security indicators | Via navigation UI |

**Example**:
- Sector 150 might be in "Border Regions" zone (security)
- Same sector is in "Alpha Cluster" (navigation)
- These are independent groupings

## Gameplay Impact

### Zone-Based Mechanics

1. **Law Enforcement**
   - High policing zones: Faction police respond to crimes
   - Low policing zones: Lawless, player-driven justice

2. **Pirate Activity**
   - High danger zones: More frequent NPC pirate encounters
   - Low danger zones: Rare hostile NPCs

3. **Player Behavior**
   - Federation: Restricted PvP, reputation penalties
   - Border: Limited PvP restrictions
   - Frontier: Unrestricted PvP

4. **Resource Distribution**
   - Frontier zones: Higher resource abundance, harder to find
   - Federation zones: Lower abundance, easier access

## Zone Migration & Alembic

Zone creation is handled by Alembic migration:

```
alembic/versions/a1b2c3d4e5f6_create_regional_zones.py
```

**Migration Actions**:
1. Creates `zones` table
2. Adds `zone_id` column to `sectors` table
3. Populates zones for each region based on `region_type`
4. Assigns sectors to zones based on `sector_number`
5. Removes deprecated `galaxy_zones` table (if exists)

## See Also

- [Region Data Model](region.md) - Parent regions containing zones
- [Sector Data Model](sector.md) - Individual sectors assigned to zones
- [Cluster Data Model](cluster.md) - Orthogonal navigation grouping
- [TERMINOLOGY.md](../../TERMINOLOGY.md) - Hierarchy definitions
