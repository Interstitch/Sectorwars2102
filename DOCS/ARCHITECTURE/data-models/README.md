# Sector Wars 2102 Data Definitions

This directory contains structured data definitions for all major game entities and systems. Files are organized into logical categories for easier navigation and maintenance.

## Directory Structure

### `/entities`
Core game objects that players interact with directly:
- `ship.md` - Player ships and ship types
- `planet.md` - Colonizable planets
- `port.md` - Trading and service stations
- `drone.md` - Combat and utility drones
- `genesis_device.md` - Terraforming devices

### `/galaxy`
Structure of the game universe:
- `galaxy.md` - Top-level universe organization
- `region.md` - Major regions of space
- `cluster.md` - Groupings of related sectors
- `sector.md` - Individual navigable units of space
- `warp_tunnel.md` - Fast travel connections

### `/player`
Player-specific systems:
- `player.md` - Core player model and properties
- `first_login.md` - New player onboarding experience
- `reputation.md` - Player standing with factions
- `team.md` - Player groups and cooperation
- `message.md` - Communication between players

### `/economy`
Economic and trade systems:
- `market_transaction.md` - Trading and transaction logs
- `resource.md` - Tradable commodities and resources

### `/combat`
Combat-related systems:
- `combat_log.md` - Combat event recording and analysis

### `/gameplay`
Other gameplay systems:
- `faction.md` - NPC factions and their properties

## Data Definition Format

Each data definition file follows a standard structure:

1. **Overview** - Brief explanation of the entity/system
2. **Data Model** - TypeScript interfaces and enums
3. **Feature-specific sections** - Details on special mechanics
4. **Integration points** - How this system connects to others
5. **API Endpoints** - Related API routes (when applicable)
6. **Events** - Event triggers and payloads (when applicable)

## Usage Guidelines

- When adding new systems, create files in the appropriate directory
- When creating relationships between systems, reference the full path to the related definition
- Maintain consistent formatting across all definition files
- Update this index when adding new files