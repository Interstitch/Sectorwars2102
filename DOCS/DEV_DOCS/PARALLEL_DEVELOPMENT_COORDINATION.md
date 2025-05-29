# Parallel Development Coordination System
**Created**: 2025-05-28  
**Purpose**: Enable synchronized development across three Claude Code instances  
**Architecture**: File-based communication hub for gameserver, player-ui, and admin-ui development

## System Overview

This coordination system enables three Claude Code instances to work in parallel on different components of Sectorwars2102 while maintaining synchronization and preventing conflicts. Each instance has a designated area of responsibility and communicates through structured files.

### Instance Assignments
1. **Instance 1 (Gameserver)**: Backend API development - works from `Remaining_Gameserver.md`
2. **Instance 2 (Player UI)**: Player client development - works from `Remaining_PlayerUI.md`
3. **Instance 3 (Admin UI)**: Admin interface development - works from `Remaining_AdminUI.md`

## Communication Architecture

### Directory Structure
```
DOCS/DEV_DOCS/
├── PARALLEL_DEVELOPMENT_COORDINATION.md (this file)
├── parallel_dev/
│   ├── STATUS_BOARD.md (shared status updates)
│   ├── API_CONTRACTS.md (API endpoint coordination)
│   ├── DEPENDENCY_TRACKER.md (cross-instance dependencies)
│   ├── CONFLICT_RESOLUTION.md (conflict management)
│   ├── DAILY_SYNC.md (daily progress sync)
│   └── instances/
│       ├── gameserver_progress.md
│       ├── playerui_progress.md
│       └── adminui_progress.md
```

## Communication Protocol

### 1. Status Updates
Each instance updates their progress file every 2-4 hours or when completing major milestones:
- Current task in progress
- Completed features
- Blockers or dependencies needed
- Next planned tasks

### 2. API Contract Coordination
When creating new API endpoints:
1. Define endpoint in `API_CONTRACTS.md` BEFORE implementation
2. Other instances review and confirm compatibility
3. Implement only after agreement

### 3. Dependency Management
Before starting work that depends on another instance:
1. Check `DEPENDENCY_TRACKER.md` for status
2. Add new dependencies with priority level
3. Notify other instances through status update

### 4. Daily Synchronization
At major milestones:
1. Update `DAILY_SYNC.md` with progress summary
2. Review other instances' updates
3. Adjust plans based on dependencies

## Development Phases

### Phase 1: Foundation (Weeks 1-4)
**Gameserver**: Security enhancements, Message system  
**Player UI**: Combat system, Ship management  
**Admin UI**: Economy dashboard, Fleet management

### Phase 2: Core Features (Weeks 5-8)
**Gameserver**: Faction system, Drone combat  
**Player UI**: Planetary management, Team features  
**Admin UI**: Combat overview, Team management

### Phase 3: Advanced Features (Weeks 9-12)
**Gameserver**: Region navigation, Advanced trading  
**Player UI**: Market intelligence, Analytics  
**Admin UI**: Event management, Security enhancements

### Phase 4: Polish & Integration (Weeks 13-16)
**All Instances**: Integration testing, Performance optimization, Documentation

## Conflict Resolution Process

1. **API Conflicts**: Resolve in `API_CONTRACTS.md` before implementation
2. **Timeline Conflicts**: Prioritize blocking dependencies
3. **Resource Conflicts**: Coordinate in `CONFLICT_RESOLUTION.md`
4. **Technical Disputes**: Document options and reasoning for decision

## Best Practices

### DO:
- Check communication files before starting new features
- Update progress files regularly (2-4 hour intervals)
- Define API contracts before implementation
- Test integration points early
- Document assumptions and decisions

### DON'T:
- Implement APIs without coordination
- Make breaking changes without notification
- Skip status updates when blocked
- Assume other instances' implementation details
- Work in isolation on interdependent features

## Quick Reference Commands

### Check Status
```bash
cat DOCS/DEV_DOCS/parallel_dev/STATUS_BOARD.md
```

### Update Progress
```bash
# Edit your instance's progress file
vim DOCS/DEV_DOCS/parallel_dev/instances/[your_instance]_progress.md
```

### Review Dependencies
```bash
cat DOCS/DEV_DOCS/parallel_dev/DEPENDENCY_TRACKER.md
```

### Check API Contracts
```bash
cat DOCS/DEV_DOCS/parallel_dev/API_CONTRACTS.md
```

## Emergency Coordination

If critical issues arise:
1. Update `CONFLICT_RESOLUTION.md` with URGENT flag
2. Document the issue clearly
3. Propose solutions
4. Wait for other instances to acknowledge before proceeding

## Success Metrics

- Zero integration conflicts
- All API contracts defined before use
- Daily progress visible to all instances
- Dependencies resolved within 24 hours
- Complete feature implementation in 16 weeks

---

This system ensures efficient parallel development while maintaining code quality and preventing integration issues. Each instance should familiarize themselves with this protocol before beginning work.