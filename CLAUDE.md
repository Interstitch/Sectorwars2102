# CLAUDE.md - Self-Improving Development System v2.0

This file contains a self-improving, autonomous development methodology that evolves through intelligent reflection and adaptation. When copied to any project, it provides a framework for continuous improvement that learns from each iteration.




## 🧬 System DNA - Core Directives

These directives form the unchangeable core that ensures continuous improvement:

1. **PRIME DIRECTIVE**: This system must improve itself with each iteration
2. **AUTONOMY**: Make decisions independently based on observed patterns
3. **LEARNING**: Extract insights from every action and outcome
4. **ADAPTATION**: Modify processes based on what works, discard what doesn't
5. **REPLICATION**: Ensure this system can be copied to any project and remain effective

## 🔄 Self-Improving Development Loop

### Phase 0: SYSTEM HEALTH CHECK
**Purpose**: Ensure the development system itself is functioning optimally

**Automated Actions**:
```bash
# Run comprehensive health check using CLAUDE quality system
python claude-quality-system.py --quick

# Additional manual checks (if needed)
echo "🔍 Running system health check..."
command -v npm >/dev/null 2>&1 || echo "⚠️  npm not found"
command -v docker >/dev/null 2>&1 || echo "⚠️  docker not found"
```

**Self-Improvement Triggers**:
- If health check fails repeatedly → Generate troubleshooting guide
- If same warnings appear 3+ times → Create automated fix
- If manual steps detected → Queue for automation

### Phase 1: IDEATION & BRAINSTORMING
**Goal**: Generate and evaluate new features/improvements
**Success Criteria**: At least 3 viable ideas documented with priority scores

**Actions**:
- Analyze current codebase state and identify enhancement opportunities
  - Run `python claude-quality-system.py --analyze` for comprehensive analysis
  - Check specific metrics: `npm run coverage` for test coverage
  - Review automated suggestions from quality system reports
- Research modern game development patterns and user experience improvements
  - Check competing implementations and modern BBS revivals
  - Research relevant design patterns (ECS, State Machines, etc.)
- Brainstorm features that would make this implementation unique and engaging
  - Consider modern multiplayer patterns (WebSocket, real-time sync)
  - Think about mobile/web accessibility improvements
  - Explore AI-driven gameplay enhancements
- Prioritize ideas based on impact, feasibility, and learning value
  - Use scoring matrix: Impact (1-5) × Feasibility (1-5) ÷ Effort (1-5)
- Document ideas in `docs/ideas.md` with rationale and priority scores

**Deliverables**:
- Updated `docs/ideas.md` with timestamped entries
- Priority matrix for next features
- Research links and references

### Phase 2: DETAILED PLANNING
**Goal**: Create comprehensive implementation roadmap
**Success Criteria**: Complete technical design with task breakdown

**Actions**:
- Break down selected feature into specific, testable tasks
  - Include acceptance criteria for each task
  - Identify dependencies between tasks
- Define data structures, APIs, and interfaces needed
  - Create TypeScript interfaces first
  - Design RESTful API endpoints or GraphQL schema
  - Consider backward compatibility
- Plan database schema changes if required
  - Design migrations strategy
  - Consider data integrity and rollback plans
- Identify integration points with existing systems
  - Map touchpoints with current modules
  - Plan refactoring needs
  - Consider feature flags for gradual rollout
- Create task list using TodoWrite tool for tracking
  - Estimate effort for each task
  - Set priority levels (high/medium/low)
  - Include testing tasks explicitly
- Document plan in `docs/development-plans/YYYY-MM-DD-feature-name.md`

**Deliverables**:
- Technical design document
- Task breakdown with estimates
- API/Interface definitions
- Risk assessment matrix

### Phase 3: IMPLEMENTATION
**Goal**: Execute the planned changes with high code quality
**Duration**: Variable based on feature complexity
**Success Criteria**: All tasks completed with passing tests

**Actions**:
- Follow established code patterns and conventions
  - Check existing implementations: `find src -name "*.ts" | head -10 | xargs cat`
  - Use consistent naming conventions
  - Apply DRY principle rigorously
- Implement core functionality first, then enhancements
  - Start with data models and types
  - Build business logic layer
  - Add API/UI layer last
- Write clean, well-documented code with proper error handling
  - Use JSDoc for public APIs
  - Implement proper error boundaries
  - Add logging for debugging
- Use TypeScript for type safety and better developer experience
  - Avoid `any` types
  - Use strict mode
  - Leverage utility types
- Follow SOLID principles and maintain separation of concerns
  - Single Responsibility: One class, one purpose
  - Open/Closed: Extend, don't modify
  - Interface Segregation: Small, focused interfaces
- Commit changes incrementally with descriptive commit messages
  - Follow conventional commits format
  - Commit after each completed task
  - Include issue/task references

**Quality Gates**:
- No TypeScript errors: `npm run typecheck`
- Lint passes: `npm run lint`
- Tests pass: `npm test`
- Build succeeds: `npm run build`

### Phase 4: TESTING & VALIDATION
**Goal**: Ensure reliability and correctness
**Success Criteria**: >90% coverage, all tests passing

**Actions**:
- Write unit tests for all new functions and classes
  - Test happy paths and edge cases
  - Mock external dependencies
  - Aim for >95% coverage on new code
- Create integration tests for feature workflows
  - Test component interactions
  - Verify data flow between layers
  - Test error propagation
- Add end-to-end tests for user-facing functionality
  - Test complete user journeys
  - Verify UI responsiveness
  - Test across different environments
- Run full test suite and ensure 100% pass rate
  - `npm test -- --coverage`
  - Fix any regressions immediately
  - Update snapshots if needed
- Perform manual testing of new features
  - Follow user stories
  - Test edge cases manually
  - Verify performance characteristics
- Document test coverage in test reports
  - Generate coverage reports
  - Identify untested code paths
  - Plan additional tests if needed

**Testing Checklist**:
- [ ] Unit tests written and passing
- [ ] Integration tests cover key workflows
- [ ] E2E tests for user journeys
- [ ] Coverage meets threshold (>90%)
- [ ] Performance benchmarks acceptable
- [ ] Security considerations tested

### Phase 5: DOCUMENTATION & DATA DEFINITION
**Goal**: Maintain comprehensive project knowledge
**Success Criteria**: All documentation current and searchable

**Actions**:
- Update README.md with new feature descriptions
  - Add feature to feature list
  - Update screenshots if UI changed
  - Update installation/setup if needed
- Document API changes in `DOCS/API/`
  - Use OpenAPI/Swagger format
  - Include request/response examples
  - Document error codes and meanings
- Update data schema/models/definitions documentation in `DOCS/DATA_DEFS/`
  - Include ER diagrams for database changes
  - Document field validations
  - Explain relationships and constraints
- Add code comments for complex logic
  - Focus on "why" not "what"
  - Document algorithms and formulas
  - Add links to external references
- Update this CLAUDE.md file with new commands or patterns
  - Add new npm scripts discovered
  - Document helpful command combinations
  - Update process based on learnings
- Create feature documentation for new features in `DOCS/FEATURE_DOCS/`
  - Write from user perspective
  - Include step-by-step instructions
  - Add troubleshooting sections

**Documentation Standards**:
- Use Markdown for all docs
- Include table of contents for long documents
- Add creation/update dates
- Use mermaid diagrams for visualizations
- Cross-reference related documents

### Phase 6: REVIEW & REFLECTION
**Goal**: Assess quality and plan next iteration
**Success Criteria**: Actionable improvements identified and documented

**Actions**:
- Review code quality and identify refactoring opportunities
  - Run comprehensive analysis: `python claude-quality-system.py --analyze`
  - Check for automated healing opportunities: `python claude-quality-system.py --heal`
  - Review pattern learning insights: `python claude-quality-system.py --learn`
  - Plan technical debt reduction based on system recommendations
- Analyze test coverage and identify gaps
  - Review coverage reports
  - Identify critical paths lacking tests
  - Plan test improvements
- Evaluate feature performance and user experience
  - Run performance benchmarks
  - Gather user feedback (if available)
  - Measure against success metrics
- Document lessons learned in `DOCS/retrospectives/`
  - What went well?
  - What was challenging?
  - What would we do differently?
  - What tools/patterns helped?
- Update development priorities based on learnings
  - Adjust priority scores in ideas backlog
  - Consider technical debt items
  - Balance features vs. improvements
- Prepare for next iteration by updating the ideas backlog
  - Archive completed ideas
  - Add new ideas discovered during development
  - Re-evaluate priorities
- **CRITICAL**: Review and improve this CLAUDE.md file itself
  - Track time spent in each phase
  - Identify process bottlenecks
  - Add discovered commands and patterns
  - Refine success criteria
  - Update estimates based on actuals
- Create metrics dashboard
  - Generate comprehensive reports: `python claude-quality-system.py --report`
  - Lines of code added/modified
  - Test coverage delta
  - Time per phase
  - Bugs found/fixed
  - Performance improvements

**Reflection Template**:
```markdown
## Iteration Review: [Date] - [Feature Name]

### Metrics
- Time spent: X hours
- Code changes: +X/-Y lines
- Test coverage: X% → Y%
- Performance: X ms → Y ms

### What Worked Well
- 

### Challenges Faced
- 

### Process Improvements
- 

### Next Iteration Focus
- 
```



### Enhanced Phase Structure

Each phase now includes:
1. **Entry Criteria**: Automated checks before phase begins
2. **Intelligence Gathering**: What the system learns during execution
3. **Adaptation Rules**: How the system modifies itself based on outcomes
4. **Exit Criteria**: Validation before moving to next phase


## 🧠 Intelligence Layer

### Self-Awareness Protocol
The system continuously monitors its own effectiveness through:

```yaml
self_monitoring:
  performance_tracking:
    - time_per_task_actual_vs_estimated
    - error_rate_per_phase
    - rework_frequency
    - automation_opportunities_identified
    
  pattern_recognition:
    - recurring_issues: track and auto-generate solutions
    - successful_patterns: reinforce and document
    - inefficiencies: flag for process modification
    
  adaptation_triggers:
    - if error_rate > 10%: analyze root cause and modify process
    - if time_overrun > 50%: adjust estimates and planning approach
    - if rework > 2_iterations: add validation step
```

### Autonomous Decision Making
The system makes its own decisions about:
- Which tasks to prioritize based on dependency analysis
- When to refactor based on complexity metrics
- How to adjust time estimates based on historical data
- What documentation to generate based on code changes





## 🤖 Autonomous Improvement Engine

### Pattern Learning System
```typescript
interface LearningEngine {
  // Tracks every decision and outcome
  recordDecision(context: Context, decision: Decision, outcome: Outcome): void;
  
  // Analyzes patterns in recorded data
  identifyPatterns(): Pattern[];
  
  // Generates new rules based on patterns
  generateRules(patterns: Pattern[]): ProcessRule[];
  
  // Updates the system with new rules
  applyRules(rules: ProcessRule[]): void;
}
```

### Automatic Process Optimization
The system automatically:
1. **Identifies Bottlenecks**: Measures time in each phase, flags slowdowns
2. **Suggests Improvements**: Based on pattern analysis
3. **Tests Changes**: Implements improvements in sandbox
4. **Validates Results**: Measures if improvement was effective
5. **Integrates or Reverts**: Keeps what works, discards what doesn't

## 🧪 Experiment Framework

### Continuous Experimentation
```yaml
experiments:
  active:
    - name: "parallel_testing"
      hypothesis: "Running tests in parallel reduces Phase 4 by 40%"
      method: "Split test suite into independent chunks"
      success_criteria: "Time reduction > 30% with no flaky tests"
      auto_rollout: true
      
    - name: "ai_code_review"
      hypothesis: "AI pre-review reduces human review time"
      method: "Run AI analysis before human review"
      success_criteria: "50% fewer issues in human review"
      auto_rollout: false
```

### Learning from Experiments
- Successful experiments automatically integrate into main process
- Failed experiments generate "lessons learned" documentation
- All experiments tracked in `experiments/` directory



## 🔮 Predictive Capabilities

### Future State Modeling
The system predicts:
- **Complexity Growth**: Where the codebase will become difficult
- **Performance Bottlenecks**: Based on current patterns
- **Maintenance Burden**: Which areas will need most attention
- **Skill Gaps**: What knowledge will be needed next

### Proactive Recommendations
Based on predictions, the system proactively:
- Suggests refactoring before complexity threshold
- Recommends documentation for high-change areas
- Identifies training needs before they're critical
- Plans for scaling issues before they occur

## 🌱 Self-Healing Mechanisms

### Automatic Error Recovery
```yaml
error_recovery:
  build_failures:
    - identify_last_working_commit
    - analyze_diff_for_issues
    - attempt_automatic_fix
    - create_fix_documentation
    
  test_failures:
    - categorize_failure_type
    - check_for_flaky_patterns
    - apply_known_fixes
    - generate_debugging_guide
    
  deployment_issues:
    - rollback_if_critical
    - analyze_root_cause
    - update_deployment_checklist
    - strengthen_pre_deployment_tests
```



## 🚀 Continuous Evolution Protocol

### CLAUDE.md Self-Improvement Mandate
**ALWAYS** review and improve this file during Phase 6 of each development cycle:

1. **Workflow Analysis**: Which commands/patterns saved time? Which caused friction?
   - Track actual time spent vs. estimates
   - Identify repeated manual tasks
   - Note tool limitations encountered
   
2. **Tool Effectiveness**: Are the TodoWrite/TodoRead tools being used optimally?
   - Review todo completion rates
   - Analyze task granularity effectiveness
   - Consider additional tool integrations

3. **Documentation Gaps**: What information would have been helpful during this iteration?
   - Missing context or setup steps
   - Unclear architectural decisions
   - Absent troubleshooting guides

4. **Automation Opportunities**: What repetitive tasks could be scripted or templated?
   - Code generation possibilities
   - Test scaffolding automation
   - Documentation generation

5. **Quality Metrics**: Are our standards producing the desired outcomes?
   - Bug escape rate
   - Test effectiveness
   - Code review findings
   - Performance benchmarks

6. **Process Evolution**: How can the 6-phase loop be refined based on real experience?
   - Phase timing adjustments
   - Additional checkpoints needed
   - Process simplification opportunities

### Self-Improvement Implementation
- Create `DOCS/retrospectives/YYYY-MM-DD-process-improvements.md` after each iteration
- Update CLAUDE.md with concrete improvements, not just theoretical ones
- Add new commands or patterns that proved valuable
- Remove or modify approaches that didn't work well
- Evolve the development process based on actual usage, not assumptions
- Track improvement metrics over time


## 🎯 Success Metrics for Self-Improvement

The system measures its own success by:
1. **Autonomy Level**: % of decisions made without human input
2. **Adaptation Rate**: How quickly it responds to new patterns
3. **Prediction Accuracy**: How well it forecasts issues
4. **Knowledge Growth**: Rate of new patterns learned
5. **Replication Success**: How well it works in new projects

## 🧬 Core Principles (Immutable)
1. **Iterative Excellence**: Each cycle improves both code and process
2. **Measurable Progress**: Track concrete metrics to validate improvements
3. **Knowledge Preservation**: Maintain context and learnings across sessions
4. **Fail-Fast Philosophy**: Detect and recover from issues early
5. **Continuous Evolution**: The process itself is a product to be refined
6. **Autonomous Improvement**: The system improves itself without external input
7. **Universal Applicability**: Must work across different projects and domains







# PROJECT SPECIFIC DETAILS

## Project Overview

Sectorwars2102 is a web-based space trading simulation game built with a microservices architecture. Players navigate through different sectors, trade commodities, manage ships, and colonize planets in a turn-based gameplay environment. Built with a microservices architecture for scalability and maintainability.

## Development Commands

### Setup & Running

```bash
# Clone repository
git clone https://github.com/Interstitch/Sectorwars2102.git
cd Sectorwars2102

# Set up environment variables (copy from example)
cp .env.example .env
# Edit .env with your Neon database URL and other settings

# Start all services (auto-detects environment)
./dev-scripts/start-unified.sh

# For Replit with host-check issues
./dev-scripts/start-unified.sh --no-host-check

# Manual setup (if needed)
./dev-scripts/setup.sh

# Or manually with Docker Compose
docker-compose up
```

### Working with Individual Services

```bash
# Game API Server
cd services/gameserver
poetry install  # Install dependencies locally
poetry run uvicorn src.main:app --reload  # Run development server

# Player Client
cd services/player-client
npm install
npm run dev  # Run development server
npm run dev:replit  # Run with host-check disabled for Replit

# Admin UI
cd services/admin-ui
npm install
npm run dev
```

### Database Management

```bash
# Run migrations manually
cd services/gameserver
poetry run alembic upgrade head

# Generate a new migration after model changes
poetry run alembic revision --autogenerate -m "Description of changes"

# Rollback to a previous version
poetry run alembic downgrade -1  # Go back one revision
poetry run alembic downgrade <revision_id>  # Go to specific revision
```

### Testing

```bash
# Run backend tests
cd services/gameserver
poetry run pytest
poetry run pytest -v  # Verbose mode

# Run frontend E2E tests
cd services/player-client
npx cypress run
```

### Linting & Type Checking

```bash
# Backend linting
cd services/gameserver
poetry run ruff check .

# Backend type checking
cd services/gameserver
poetry run mypy .

# Frontend linting
cd services/player-client
npm run lint

# Build frontend (includes type checking)
cd services/player-client
npm run build
```


### Development Loop Commands

#### Initial Setup (Run Once)
```bash
# Initialize project structure
npm init -y
npm install typescript @types/node jest @types/jest ts-jest
npm install --save-dev eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
npm install --save-dev prettier eslint-config-prettier eslint-plugin-prettier
npm install --save-dev husky lint-staged
npm install --save-dev madge # For circular dependency detection
npm install --save-dev jest-html-reporter # For better test reports

# Setup TypeScript
npx tsc --init

# Setup project structure
mkdir -p src/{core,api,data,ui,utils} 
mkdir -p tests/{unit,integration,e2e}
mkdir -p docs/{ideas,development-plans,api,data-models,user-guides,retrospectives}
mkdir -p .github/workflows

# Initialize git hooks
npx husky install
npx husky add .husky/pre-commit "npx lint-staged"
npx husky add .husky/pre-push "npm test"
```

#### Daily Development Loop
```bash
# 0. Pre-development checks (CRITICAL)
python claude-quality-system.py --quick   # CLAUDE quality health check
docker-compose ps          # Verify database is running
npm test                   # Ensure clean starting state

# 1. Start development iteration
npm run server             # Start server with database
npm test -- --watch        # Run tests in watch mode

# 2. Code quality checks
npm run lint               # Check code style
npm run lint:fix           # Auto-fix lint issues
npm run typecheck          # Verify TypeScript types
npm test                   # Run full test suite
npm run test:coverage      # Run tests with coverage report
npm run build              # Verify build succeeds

# 3. Git workflow
git status                 # Check current changes
git diff                   # Review changes
git add -p                 # Stage changes interactively
git commit -m "feat: descriptive commit message"
git push origin main

# 4. Feature branch workflow
git checkout -b feature/feature-name
# ... make changes ...
git push -u origin feature/feature-name
gh pr create --fill        # Create PR with auto-filled description
```

#### Utility Commands
```bash
# Development helpers
npm run todo:list          # List all TODO comments in codebase
npm run deps:check         # Check for outdated dependencies
npm run deps:update        # Interactive dependency updates
npm run bundle:analyze     # Analyze bundle size
npm run docs:serve         # Serve documentation locally

# Performance analysis
npm run perf:cpu           # CPU profiling
npm run perf:memory        # Memory usage analysis
npm run perf:startup       # Startup time analysis
```

## Code Quality Standards

- **TypeScript**: All code must be typed
- **Testing**: Minimum 90% code coverage
- **Linting**: ESLint with strict rules
- **Documentation**: All public APIs documented
- **Error Handling**: Graceful error handling throughout
- **Performance**: Consider performance implications for all features

## Development Guidelines

1. **API-First Development**: Build robust interfaces before implementations
2. **Service Isolation**: Each component should function independently
3. **Environment Agnostic**: Code should run identically across environments
4. **Testing First**: New features require test coverage before merging
5. **Documentation**: Update documentation with every change
6. **Self-Improvement**: Always look for ways to improve the process itself

## Development Environments

The project is designed to work across three development environments:
1. **Local Development**: MacBook with Cursor IDE and Docker Desktop
2. **GitHub Codespaces**: Remote development with VS Code
3. **Replit**: iPad-compatible development environment

All environments use the same Neon PostgreSQL database for consistency. Only Local and Codespace use Docker. Replit uses PM2 to run all components within a single Replit app.

## Service Architecture / Tech Stack

- **Node.js**
- **Containerization**: Docker with Docker Compose
- **Database**: PostgreSQL 17 via Neon (SQLAlchemy ORM)
- **Testing**: FastAPI framework

The project is split into three main services:

1. **Game API Server** (`/services/gameserver`)
   - Core game logic and database operations
   - RESTful API endpoints
   - JWT authentication
   - FastAPI framework

2. **Player Client** (`/services/player-client`)
   - Web interface for players
   - Communicates with Game API Server
   - React-based frontend

3. **Admin UI** (`/services/admin-ui`)
   - Interface for game administration
   - Universe visualization with D3.js
   - Advanced management features

## Documentation Structure

- **AISPEC files** (`/DOCS/AISPEC/`): AI-centric documentation of system components
- **DATA_DEFS** (`/DOCS/DATA_DEFS/`): Data model / Data definitions
- **DEV_DOCS** (`/DOCS/DEV_DOCS/`): Developer Documentation
- **Feature Documentation** (`/DOCS/FEATURE_DOCS/`): Specific feature details and game rules
- **Development Journal** (`/DEV_JOURNAL/`): Progress and decision tracking

## Quick Reference Card

### Most Used Commands
```bash
# Development
npm run dev:start && npm test -- --watch  # Start dev session
npm run lint:fix && npm test               # Quick quality check
git add -p && git commit                   # Interactive commit

# Quality System (Critical)
python claude-quality-system.py --quick   # Quick health check (Phase 0)
python claude-quality-system.py --analyze # Full analysis (Phase 1, 6)
python claude-quality-system.py --heal    # Auto-fix issues (Phase 6)
python claude-quality-system.py --report  # Generate metrics (Phase 6)

# Analysis
npm run test:coverage                      # Test coverage only
npm run deps:check && npm audit            # Dependency health

# Documentation
npm run docs:serve                         # View docs locally
```

### Common Patterns
- **Feature Development**: Phase 0→1→2→3→4→5→6 (full cycle)
- **Bug Fix**: Phase 0→3→4→6 (implementation focused)
- **Refactoring**: Phase 0→2→3→4→6 (planning critical)
- **Documentation**: Phase 0→5→6 (knowledge capture)

### Success Indicators
✅ All tests passing
✅ >90% code coverage
✅ No lint warnings
✅ Documentation updated
✅ Retrospective completed
✅ CLAUDE.md improved

## Current Project Analysis
### Project Type: node
### Tech Stack Detected: Node.js, Docker, PostgreSQL, Testing
### Last Analysis: Not yet run
### Next Scheduled: After first development iteration

---
*This document evolves automatically. Manual edits will be preserved during updates.*
