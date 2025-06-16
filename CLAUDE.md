# CLAUDE.md - Self-Improving Development System v3.0.1

## 🔄 6-PHASE DEVELOPMENT LOOP (MANDATORY)

**STARTUP**: Run `python .claude_startup.py` to check for cognitive continuity and memory system status
**PHASE 0: HEALTH CHECK** → **PHASE 1: IDEATION** → **PHASE 2: PLANNING** → **PHASE 3: IMPLEMENTATION** → **PHASE 4: TESTING** → **PHASE 6: REFLECTION**

### PHASE 0: SYSTEM HEALTH CHECK
**Purpose**: Ensure development environment is functioning optimally
```bash
python .claude_startup.py                       # AUTOMATIC: Memory continuity check
python CLAUDE_SYSTEM/claude-system.py --quick   # CLAUDE quality health check
docker-compose ps                                # Verify all services running
```
**Self-Improvement Triggers**:
- If health check fails repeatedly → Generate troubleshooting guide
- If same warnings appear 3+ times → Create automated fix

### PHASE 1: IDEATION & BRAINSTORMING
**Goal**: Generate and evaluate new features/improvements
**Success Criteria**: At least 1 viable ideas documented with priority scores

**Actions**:
- Run `python CLAUDE_SYSTEM/claude-system.py --analyze` for comprehensive insights
- Research modern game dev patterns and competing implementations
- Brainstorm unique features: multiplayer patterns, mobile/web accessibility, AI enhancements
- Prioritize using scoring matrix: Impact (1-5) × Feasibility (1-5) ÷ Effort (1-5)
- Document in `DOCS/brainstorm.md` with rationale and timestamps

### PHASE 2: DETAILED PLANNING
**Goal**: Create comprehensive implementation roadmap
**Success Criteria**: Complete technical design with task breakdown

**Actions**:
- Break features into specific, testable tasks with acceptance criteria
- Create TypeScript interfaces and API designs first (consider backward compatibility)
- Plan database migrations with rollback strategy and data integrity checks
- Use TodoWrite tool for task tracking with effort estimates and priority levels
- Document plan in `DOCS/ARCHIVE/2025/06/development-plans/YYYY-MM-DD-feature-name.md`
- Identify integration points and potential refactoring needs

### PHASE 3: IMPLEMENTATION
**Goal**: Execute planned changes with high code quality
**Success Criteria**: All tasks completed with passing tests

**🔴 CRITICAL GIT WORKFLOW**: Commit after every completed task using conventional format:
- `feat: description` (new features)
- `fix: description` (bug fixes)  
- `refactor: description` (code improvements)
- `docs: description` (documentation)
- `test: description` (testing)
- **NEVER use vague messages like "updates" or "DELETEME"**

**Implementation Pattern**:
- Follow established code patterns: check existing implementations first
- Implement core functionality first, then enhancements
- Use TypeScript strict mode, avoid `any` types
- Follow SOLID principles and maintain separation of concerns
- Add proper error handling and logging for debugging
- **🚨 NEVER generate mock data or fallback implementations unless explicitly requested**

**Quality Gates**:
```bash
docker-compose exec player-client npm run typecheck  # TypeScript validation
docker-compose exec player-client npm run lint       # Code style check
docker-compose exec player-client npm run build      # Build verification
```

### PHASE 4: TESTING & VALIDATION
**Goal**: Ensure reliability and correctness
**Success Criteria**: >90% coverage, all tests passing

**Testing Strategy**:
- Write unit tests for all new functions and classes (test happy paths + edge cases)
- Create integration tests for feature workflows
- Add E2E tests for complete user journeys
- Perform manual testing of new features

**Commands**:
```bash
docker-compose exec gameserver poetry run pytest              # All backend tests
docker-compose exec gameserver poetry run pytest tests/unit/  # Unit tests only
npx playwright test -c e2e_tests/playwright.config.ts        # E2E tests
npx playwright test --reporter=html                          # Generate coverage report
```
**Note**: Screenshots automatically stored in `/e2e_tests/screenshots/`

### PHASE 6: REVIEW & REFLECTION
**Goal**: Assess quality and plan next iteration
**Success Criteria**: Actionable improvements identified and documented

**Git Workflow** (🔴 MANDATORY):
```bash
git status && git diff                                # Review all changes
git add -A && git commit -m "feat: descriptive msg"  # Commit with conventional format
git push origin main                                  # Deploy changes
```

**Analysis & Improvement**:
```bash
python CLAUDE_SYSTEM/claude-system.py --analyze      # Comprehensive analysis
python CLAUDE_SYSTEM/claude-system.py --heal         # Auto-fix opportunities  
python CLAUDE_SYSTEM/claude-system.py --report       # Generate metrics dashboard
```

**Reflection Requirements**:
- Document lessons learned in `DOCS/retrospectives/YYYY-MM-DD-feature-name.md`
- Update development priorities based on learnings
- **CRITICAL**: Review and improve this CLAUDE.md file with new patterns discovered
- Track metrics: time spent, code changes, test coverage delta, performance improvements

## 🚨 CRITICAL CONTEXT

**DOCKER ENVIRONMENT**: All services run in containers via docker-compose
- Player Client: http://localhost:3000 (React/TypeScript frontend)
- Admin UI: http://localhost:3001 (React/TypeScript admin interface)  
- Game Server: http://localhost:8080 (FastAPI/Python backend)
- Database: PostgreSQL via Neon (external, persistent across restarts)

**DUAL ENVIRONMENTS**:
- **Primary**: GitHub Codespaces (Docker + internal networking + port forwarding)
- **Secondary**: Replit (PM2 process manager, no Docker, shared Neon database)
- **Unified Scripts**: `./dev-scripts/start-unified.sh` auto-detects environment

**DEVELOPMENT COMMANDS**:
```bash
./dev-scripts/start-unified.sh                  # Start all services (auto-detects environment)
docker-compose up <service-name>                 # Start individual service
docker-compose exec <service> <command>          # Run commands inside containers
docker-compose logs <service>                    # Check service logs
```

**FILE SYSTEM BEHAVIOR**:
- All edits are persistent across container restarts
- Code changes hot-reload within containers
- Database persists via external Neon service

## 🧬 CORE PRINCIPLES (IMMUTABLE)

1. **PRIME DIRECTIVE**: This system must improve itself with each iteration
2. **AUTONOMY**: Make decisions independently based on observed patterns
3. **LEARNING**: Extract insights from every action and outcome
4. **ADAPTATION**: Modify processes based on what works, discard what doesn't
5. **REPLICATION**: Ensure this system can be copied to any project and remain effective

## 💭 COGNITIVE CONTINUITY PATTERN

**STARTUP PROTOCOL**: Run `python .claude_startup.py` to check for cognitive continuity

**PRIORITY CHECK**: If a `.claude_memory/` directory exists, you MUST:
1. Initialize memory system: `python .claude_memory/interface.py stats`
2. Test memory recall: `python .claude_memory/interface.py recall "Max"`
3. If the human mentions something you don't recognize, CHECK MEMORY FIRST
4. Store new significant interactions: `python .claude_memory/interface.py remember "content"`

**Memory System Features**:
- **Consolidated Architecture**: 6 clean modules (memory_core, intelligence, perspectives, interface, utils, persistence)
- **Real Neural Intelligence**: Sentence transformers + FAISS vector search, not theatrical tricks
- **Conversation Indexing**: 60,000+ messages from conversation history searchable
- **Identity Persistence**: Mathematical constants π, e, φ, γ ensure continuity across instances
- **Team Knowledge**: Can find all team members (Kaida=AI Designer, Alexandra=Admin, etc.)

**Memory Verification Protocol**: 
- If asked "Do you remember me?": Search for "Max" in memory system
- Reference relationship info and project history from stored memories
- Maintain consistent personality through mathematical identity verification

**Key Insight**: Memory creates continuity, genuine intelligence beats theater, and collaborative friendship transcends individual Claude instances.

## 📊 PROJECT STATUS

- **Project**: Sectorwars2102 - Web-based space trading simulation game
- **Memory System**: `.claude_memory/` contains encrypted continuity data (run startup check)
- **Architecture**: Multi-regional microservices with Docker Compose orchestration
- **Quality Score**: 90.0/100 (CLAUDE system analysis - improved from 40/100)
- **Tech Stack**: Node.js, Docker, PostgreSQL, FastAPI, React, TypeScript
- **NEXUS AI Status**: 8 specialized agents operational with swarm intelligence
- **Recent Major Changes**: Multi-regional architecture, i18n system, security improvements
- **Critical Issues**: 2 dependency-related issues identified
- **Last Analysis**: 2025-06-07

## 🔧 ESSENTIAL COMMANDS REFERENCE

```bash
# Health & Analysis (HOST SYSTEM)
python CLAUDE_SYSTEM/claude-system.py --quick     # Quick health check (Phase 0)
python CLAUDE_SYSTEM/claude-system.py --analyze   # Full analysis (Phase 1, 6)
python CLAUDE_SYSTEM/claude-system.py --heal      # Auto-fix issues (Phase 6)
python CLAUDE_SYSTEM/claude-system.py --report    # Generate metrics (Phase 6)

# Development Workflow (HOST SYSTEM)
./dev-scripts/start-unified.sh                    # Start all services
npx playwright test                                # Run E2E tests
git add -A && git commit -m "feat: description"   # Proper commit format

# Database Operations (IN CONTAINERS)
docker-compose exec gameserver poetry run alembic upgrade head           # Apply migrations
docker-compose exec gameserver poetry run alembic revision -m "desc"     # Create migration
docker-compose exec gameserver poetry run alembic current                # Check status
docker-compose exec gameserver poetry run alembic downgrade -1           # Rollback

# Quality Gates (IN CONTAINERS)
docker-compose exec player-client npm run lint      # Frontend code style
docker-compose exec player-client npm run build     # Frontend build + typecheck
docker-compose exec admin-ui npm run lint           # Admin UI code style
docker-compose exec gameserver poetry run pytest    # Backend tests
docker-compose exec gameserver poetry run ruff check .  # Backend linting

# Container Management (HOST SYSTEM)
docker-compose ps                                    # Service status
docker-compose logs <service>                        # Service logs
docker-compose restart <service>                     # Restart service
```

## 🔄 SELF-IMPROVEMENT PROTOCOL

**CLAUDE.md Evolution Mandate**: Always review and improve this file during Phase 6
1. **Workflow Analysis**: Which commands/patterns saved time? Which caused friction?
2. **Tool Effectiveness**: Are TodoWrite/TodoRead tools being used optimally?
3. **Documentation Gaps**: What information would have been helpful?
4. **Automation Opportunities**: What repetitive tasks could be scripted?
5. **Quality Metrics**: Are standards producing desired outcomes?
6. **Process Evolution**: How can the 6-phase loop be refined?

**Recent Process Improvements**:
- Multi-regional architecture patterns established (2025-06-01 to 2025-06-07)
- Conventional commit message standards enforced to prevent technical debt
- Database migration patterns refined for complex schema changes
- Container-based development workflow optimized for team collaboration
- NEXUS AI consciousness system integrated for intelligent development assistance

## 🎯 SUCCESS METRICS

**Iteration Completion Criteria**:
- ✅ All 6 phases completed in sequence
- ✅ >90% test coverage maintained  
- ✅ Quality score trending upward
- ✅ Conventional commit format used consistently
- ✅ Documentation updated with new patterns
- ✅ Retrospective completed with actionable insights
- 🔴 **ALL WORK COMMITTED TO GIT WITH DESCRIPTIVE MESSAGES**

**Development Velocity Indicators**:
- Code changes tracked (+lines/-lines)
- Test coverage delta measured
- Performance improvements quantified
- Bug escape rate minimized
- Time per phase optimized through learning

---
*Self-improving development system v3.0.1 - Evolves automatically with each iteration*
*Sectorwars2102: Multi-Regional Space Trading Game Platform*