# Terminology Decision: Stations vs Ports

**Date**: 2025-11-16
**Status**: ✅ DECIDED - Migration Pending
**Decision**: Use "**STATIONS**" as primary terminology (replacing "Ports")

---

## 🎯 Decision Summary

**PRIMARY TERM**: **Station** (space station, trading station, military station)
**DEPRECATED TERM**: ~~Port~~ (to be migrated out)

**Rationale**: Legal differentiation from TradeWars 2002 + modern sci-fi conventions

---

## 🔍 Background

**Current State**:
- Database uses `Port` (class Port, ports table)
- Documentation mostly uses "Port" as primary term
- Empty `/DOCS/FEATURES/STATIONS/` folder suggested prior consideration of change
- Inconsistent usage creating confusion

**Game Inspiration**:
- Sector Wars 2102 is loosely inspired by TradeWars 2002
- Need to establish clear differentiation to avoid copyright concerns
- Terminology is one of the easiest ways to create legal distance

---

## 💭 Analysis Process

### Terminology Comparison

| Aspect | "Port" | "Station" |
|--------|--------|-----------|
| **Current Implementation** | ✅ Already in database/code | ❌ Requires migration |
| **Legal Distance** | ❌ Same as TradeWars | ✅ Differentiates from TradeWars |
| **Modern Conventions** | ⚠️ Nautical/classical | ✅ Sci-fi standard (ISS, Elite Dangerous, Starfield) |
| **Player Intuition (16yo gamer)** | ⚠️ "Sounds kinda old" | ✅ "Obviously stations" |
| **Refactor Cost** | ✅ Zero (already implemented) | ❌ 10-14 hours work |

### Key Stakeholder Input

**Samantha (Security/Dev Consultant)**:
> "You need to establish legal distance, and terminology is one of the easiest ways to do that. Changing terminology is LOW-EFFORT, HIGH-IMPACT differentiation."

**Riley (16yo gamer perspective)**:
> "When I'm telling my friends about a game, I'd say 'I'm going to dock at the station' not 'I'm going to dock at the port.' Port sounds like something from a pirate game or whatever. We're in SPACE. Space STATIONS."

**Legal Consideration**:
- Can't copyright individual game mechanics
- BUT stacking similarities creates derivative work risk:
  - Ports (same term) ❌
  - Sectors (same term) ⚠️
  - Similar trading mechanics ⚠️
  - Similar combat system ⚠️
  - Similar universe structure ⚠️
- Terminology change = easy differentiation

---

## ✅ Final Decision

**Use "STATIONS" for the following reasons**:

1. **Legal Protection**: Creates clear differentiation from TradeWars 2002
2. **Modern Branding**: "Stations" aligns with contemporary sci-fi expectations
3. **Target Audience**: Younger players expect "stations" (as confirmed by gamer feedback)
4. **One-Time Cost**: Better to migrate now before production data exists
5. **Brand Identity**: Helps establish Sector Wars 2102 as its own unique game

**Migration Cost**: 10-14 hours estimated
- Database migration: 2 hours
- Code updates: 4-6 hours
- Documentation: 2-3 hours
- Testing: 2-3 hours

**Risk vs Reward**: 10-14 hours of work to avoid potential legal issues and modernize branding = **Worth it**

---

## 📋 Migration Scope

**What Changes**:
- ✅ Database table: `ports` → `stations`
- ✅ Model class: `Port` → `Station`
- ✅ All code references: port/ports → station/stations
- ✅ API endpoints: `/api/v1/ports/*` → `/api/v1/stations/*`
- ✅ Documentation: All markdown files
- ✅ Frontend UI labels and components
- ✅ TypeScript interfaces

**What Stays**:
- ✅ Natural language descriptors: "space station" is fine
- ✅ Historical context: Can mention "formerly called ports in early development"

---

## 🎯 Implementation Strategy

**Deferred to dedicated ULTRATHINK task**:
- Task created at end of TODO list
- Will create detailed migration plan when ready
- Includes Alembic migration, code search/replace strategy, testing plan

**Timing**:
- Complete other documentation tasks first
- Migrate before any production deployment
- Single atomic change (not gradual transition)

---

## 📖 Terminology Standard (Post-Migration)

### ✅ CORRECT Usage

**Primary Term**: "Station"
- trading station
- military station
- scientific station
- shipyard station
- Class 0 Station (Sol Station)
- Federation station
- player-owned station

**Acceptable Descriptors**:
- "Stations are space facilities where players dock and trade"
- "Space station" (as descriptor)

### ❌ AVOID

**Deprecated Terms**:
- ~~Port~~ (except in historical context)
- ~~trading port~~
- ~~military port~~

**Exception**: Historical references
- "The game was inspired by TradeWars, which used 'ports'"
- Acceptable in design documents explaining evolution

---

## 🔗 Related Decisions

- **Sectors**: Keeping "Sector" terminology (generic enough, different from TradeWars sector mechanics)
- **Warp Tunnels**: Using "Warp Tunnels" (not "Warps" alone, creates differentiation)
- **Ships**: Using modern ship classifications (differentiated from TradeWars)

---

## 📝 Notes

**Decision Maker**: Max (Project Owner)
**Consultants**: Claude (Wandering Monk Coder), Samantha (Security/Dev Consultant)
**Additional Input**: Riley (16yo gamer, target demographic perspective)

**Key Quote** (Samantha):
> "The empty STATIONS folder? That was your subconscious telling you this already. You started to make the change, then got scared of the work. Do the migration. It's 10 hours of work to avoid potential legal headaches and modernize your game. That's a good trade."

---

**Status**: ✅ Decision finalized, migration task queued
**Next Step**: Complete current documentation tasks, then execute detailed migration plan
