# Claude Code Instance Startup Prompts

This document contains the initial prompts to provide to each Claude Code instance when starting parallel development on Sectorwars2102.

## Current Status (2025-05-29)
- **Instance 1 (Gameserver)**: Phase 3 60% COMPLETE 🔄 - Admin APIs implemented, Enhanced Ship Management next
- **Instance 2 (Player UI)**: Phase 3 COMPLETE ✅ - Market Intelligence & Player Analytics implemented  
- **Instance 3 (Admin UI)**: Phase 3 Part 2 COMPLETE ✅ - AI Trading Intelligence fully implemented

---

## Instance 1: Gameserver (Backend) Developer

**Copy and paste this prompt to start Instance 1:**

```
I am working on the Sectorwars2102 gameserver backend implementation. I am Instance 1 of 3 Claude Code instances working in parallel.

Current Status: Phase 3 60% COMPLETE 🔄
- Phase 1: Security & Messaging System - COMPLETE
  - OWASP security middleware with comprehensive headers
  - Rate limiting and input validation
  - Audit logging system with database persistence
  - Full message system with threading and notifications
- Phase 2: Combat Mechanics - COMPLETE
  - Faction System: 6 factions with reputation, territory control, missions
  - Drone Combat: 5 drone types, deployment system, combat simulation
  - Fleet Battles: Models and database structure ready
- Phase 3: Admin APIs & Advanced Features - 60% COMPLETE
  - Admin Economy Dashboard API: 4 endpoints with market intervention
  - Admin Combat Overview API: 4 endpoints with live monitoring
  - Economy Analytics Service: Market data, metrics, alerts, intervention
  - Combat Analytics Service: Live feed, intervention, balance analysis
  - AI Trading Intelligence System: Database structure ready

My responsibilities:
- Working from DOCS/DEV_DOCS/Remaining_Gameserver.md
- Implementing all backend API features and services
- Focus on Phase 3: Enhanced Ship Management, Region Navigation, and Advanced Trading
- Coordinating with other instances via DOCS/DEV_DOCS/parallel_dev/

Please:
1. Read DOCS/DEV_DOCS/PARALLEL_DEVELOPMENT_COORDINATION.md to understand the communication system
2. Review DOCS/DEV_DOCS/Remaining_Gameserver.md for Phase 3 tasks
3. Check DOCS/DEV_DOCS/parallel_dev/STATUS_BOARD.md for current status
4. Update DOCS/DEV_DOCS/parallel_dev/instances/gameserver_progress.md with my status
5. Continue Phase 3 implementation (Enhanced Ship Management next priority)

Important context:
- All game components run in Docker containers
- Using PostgreSQL with SQLAlchemy ORM
- Faction/Drone enums use string columns for PostgreSQL compatibility
- Admin APIs completed - Admin UI team unblocked
- Economy & Combat Analytics Services fully implemented
- Enhanced Ship Management is next priority for Phase 3

I should check the parallel_dev communication files every 2-4 hours and update my progress regularly. I need to define APIs in API_CONTRACTS.md before implementing them.
```

---

## Instance 2: Player UI Developer

**Copy and paste this prompt to start Instance 2:**

```
I am working on the Sectorwars2102 player UI (player-client) implementation. I am Instance 2 of 3 Claude Code instances working in parallel.

Current Status: PHASE 3 COMPLETE ✅
- Phase 1: Combat & Ship Management - COMPLETE
- Phase 2: Planetary & Team Features - COMPLETE  
- Phase 3: Market Intelligence & Player Analytics - COMPLETE
  - Market Intelligence: MarketAnalyzer, PricePredictor, RouteOptimizer, CompetitionMonitor
  - Player Analytics: PlayerAnalytics, AchievementTracker, ProgressVisualizer, GoalManager, Leaderboards
  - API Integration: Updated api.ts with all Phase 3 endpoints
  - Documentation: Complete API contracts and implementation summary

My responsibilities:
- Working from DOCS/DEV_DOCS/Remaining_PlayerUI.md
- Implementing all player-facing UI features
- Focus on Phase 4: Polish & Advanced Features OR Social Features Foundation
- Coordinating with other instances via DOCS/DEV_DOCS/parallel_dev/

Please:
1. Read DOCS/DEV_DOCS/PARALLEL_DEVELOPMENT_COORDINATION.md to understand the communication system
2. Review DOCS/DEV_DOCS/Remaining_PlayerUI.md for Phase 4 tasks or remaining work
3. Check DOCS/DEV_DOCS/parallel_dev/STATUS_BOARD.md for current status
4. Update DOCS/DEV_DOCS/parallel_dev/instances/playerui_progress.md with my status
5. Begin implementing next phase features or assist with integration tasks

Important context:
- All Phase 3 components ready for backend integration
- API endpoints documented in API_CONTRACTS.md (Phase 3 section)
- Components follow consistent TypeScript patterns with responsive CSS
- Real API integration ready, no mocks needed for Phase 3 components

I should check the parallel_dev communication files every 2-4 hours and update my progress regularly. I need to check API_CONTRACTS.md for API definitions and DEPENDENCY_TRACKER.md for blockers.
```

---

## Instance 3: Admin UI Developer

**Copy and paste this prompt to start Instance 3:**

```
I am working on the Sectorwars2102 admin UI implementation. I am Instance 3 of 3 Claude Code instances working in parallel.

Current Status: PHASE 3 PART 2 COMPLETE ✅ - AI Trading Intelligence Implemented
- Phase 1: All dashboards complete (Economy, Fleet, Combat, Team) ✅
- Phase 2: Security, Analytics, Colonization complete ✅  
- Phase 3 Part 1: MFA Integration, Mock Removal, WebSocket, Performance, Mobile ✅
- Phase 3 Part 2: AI Trading Intelligence complete ✅
  - AI Trading Dashboard with model management
  - Market Prediction Interface with accuracy tracking
  - Route Optimization Display with visual comparisons  
  - Player Behavior Analytics with segmentation
  - Extended WebSocket service with AI-specific events

My responsibilities:
- Working from DOCS/DEV_DOCS/Remaining_AdminUI.md
- Implementing all admin-facing UI features
- Focus on Phase 4: Event Management System OR Advanced Business Intelligence
- Coordinating with other instances via DOCS/DEV_DOCS/parallel_dev/

Please:
1. Read DOCS/DEV_DOCS/PARALLEL_DEVELOPMENT_COORDINATION.md to understand the communication system
2. Review DOCS/DEV_DOCS/AdminUI_AI_Trading_Intelligence_Complete.md to see Phase 3 Part 2 completion
3. Check DOCS/DEV_DOCS/parallel_dev/STATUS_BOARD.md for current status
4. Update DOCS/DEV_DOCS/parallel_dev/instances/adminui_progress.md with my status
5. Begin implementing Event Management System (last major Phase 1 feature) or move to Phase 4

Important context:
- All mock APIs have been removed - using real gameserver APIs only
- WebSocket integration complete with real-time updates across all dashboards
- Performance optimized with code splitting and lazy loading
- Fully mobile responsive design implemented
- AI Trading Intelligence system complete with 4 major components
- Running in Docker container on port 3001
- 90% feature complete across all documented systems

I should check the parallel_dev communication files every 2-4 hours and update my progress regularly. I need to check API_CONTRACTS.md for API definitions and DEPENDENCY_TRACKER.md for blockers.
```

---

## Important Reminders for All Instances

1. **Communication is Key**: Check the parallel_dev folder every 2-4 hours
2. **Update Progress**: Keep your instance progress file current
3. **API First**: Define APIs in API_CONTRACTS.md before implementing
4. **Track Dependencies**: Update DEPENDENCY_TRACKER.md when blocked
5. **Resolve Conflicts**: Use CONFLICT_RESOLUTION.md for disagreements
6. **Daily Sync**: Update DAILY_SYNC.md at the end of each day

---

## Quick Reference Paths

All instances should bookmark these paths:
- Communication Hub: `DOCS/DEV_DOCS/parallel_dev/`
- Status Board: `DOCS/DEV_DOCS/parallel_dev/STATUS_BOARD.md`
- API Contracts: `DOCS/DEV_DOCS/parallel_dev/API_CONTRACTS.md`
- Dependencies: `DOCS/DEV_DOCS/parallel_dev/DEPENDENCY_TRACKER.md`
- Your Progress: `DOCS/DEV_DOCS/parallel_dev/instances/[your_instance]_progress.md`

---

**Created**: 2025-05-28  
**Last Updated**: 2025-05-29 (Admin UI Phase 3 Part 2 AI Trading Intelligence complete)  
**Purpose**: Standardize instance startup for parallel development