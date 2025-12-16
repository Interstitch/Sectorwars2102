# AI Specification Documents

This directory contains AI-centric documentation for system components using the AISPEC format.

## Purpose
- Architecture specifications optimized for AI assistants
- Component interfaces and behaviors
- System integration patterns
- Development guidelines for AI-assisted coding
- Terse, fact-dense documentation for quick AI parsing
- **Complementary quick reference to detailed FEATURES/ documentation**

## 📚 Dual-Layer Documentation Approach

SectorWars 2102 uses a **dual-layer documentation strategy** to serve both human readers and AI assistants:

### Layer 1: Detailed Design Documentation (FEATURES/)
- **Location**: `/DOCS/FEATURES/`
- **Format**: Comprehensive Markdown files
- **Audience**: Human developers, game designers, players
- **Style**: Narrative explanations, context, examples, lore
- **Purpose**: Deep understanding of game systems and vision
- **Example**: `FEATURES/DEFINITIONS/TERMINOLOGY.md` (668 lines of detailed explanations)

### Layer 2: AI-Optimized Quick Reference (SPECS/)
- **Location**: `/DOCS/SPECS/` (this directory)
- **Format**: Terse AISPEC files
- **Audience**: AI assistants, automated tools, rapid lookup
- **Style**: Fact-dense, structured, minimal prose
- **Purpose**: Fast parsing and context loading for AI systems
- **Example**: `GameConcepts.aispec` (terse terminology reference)

### Cross-Referencing Pattern
Each AISPEC file includes a `RELATED_SPECS` section pointing to:
- Related AISPEC files in SPECS/
- Detailed documentation in FEATURES/
- Source code files implementing the system

**Example**:
```
RELATED_SPECS:
* GameMechanics.aispec - Turn costs, combat resolution
* See FEATURES/DEFINITIONS/RESOURCE_TYPES.md for detailed resource documentation
```

### When to Use Each Layer
- **Starting a new feature?** → Read FEATURES/ for full context and design intent
- **Need quick fact lookup?** → Use SPECS/ for rapid reference
- **AI assistant context loading?** → SPECS/ optimized for token efficiency
- **Understanding game vision?** → FEATURES/ contains the soul of the game

## Current AISPEC Files

### Core System Specifications
- **`Architecture.aispec`** - System architecture overview and patterns
- **`AuthSystem.aispec`** - Authentication system specification
- **`Database.aispec`** - Database schema and data patterns
- **`GameServer.aispec`** - Game server API specification
- **`WebSocket.aispec`** - Real-time communication protocols

### Game Concepts & Mechanics
- **`GameConcepts.aispec`** ⭐ - Core terminology and conceptual framework (START HERE)
- **`GameMechanics.aispec`** - Turn-based systems, combat, trading, colonization
- **`Resources.aispec`** - Commodities, strategic resources, market dynamics
- **`Ships.aispec`** - Ship specifications, upgrades, insurance
- **`Ranking.aispec`** - Military progression system (18 ranks)

### Meta Documentation
- **`AISpecificationDoc.aispec`** - How to write and use AISPEC files

## AISPEC Format
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

## Usage Guidelines
- **Target Audience**: AI assistants, automated tools, quick reference
- **Maintenance**: Auto-updated with code changes when possible
- **Style**: Terse, fact-dense, no fluff
- **Structure**: Consistent format for AI parsing optimization

---
*AISPEC Documentation Index - Updated: 2025-12-16*
*Files: 11 AISPEC documents across 3 categories*
*Dual-layer documentation approach with FEATURES/ for detailed design*
