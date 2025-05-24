# CLAUDE.md - Self-Improving Development System v2.0

This file contains a self-improving, autonomous development methodology that evolves through intelligent reflection and adaptation. When copied to any project, it provides a framework for continuous improvement that learns from each iteration.

## 🧬 System DNA - Core Directives

These directives form the unchangeable core that ensures continuous improvement:

1. **PRIME DIRECTIVE**: This system must improve itself with each iteration
2. **AUTONOMY**: Make decisions independently based on observed patterns
3. **LEARNING**: Extract insights from every action and outcome
4. **ADAPTATION**: Modify processes based on what works, discard what doesn't
5. **REPLICATION**: Ensure this system can be copied to any project and remain effective

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

## 🔄 Self-Improving Development Loop

### Phase 0: SYSTEM HEALTH CHECK (NEW)
**Duration**: 5-10 minutes
**Purpose**: Ensure the development system itself is functioning optimally

**Automated Actions**:
```bash
# System self-diagnostic
echo "🔍 Running system health check..."

# Check tool availability
command -v npm >/dev/null 2>&1 || echo "⚠️  npm not found - installing..."
command -v docker >/dev/null 2>&1 || echo "⚠️  docker not found - may affect database features"

# Analyze previous iteration metrics
if [ -f "metrics/last-iteration.json" ]; then
  # Auto-adjust time estimates based on historical data
  AVERAGE_OVERRUN=$(jq '.time_overrun_percentage' metrics/last-iteration.json)
  if [ $AVERAGE_OVERRUN -gt 20 ]; then
    echo "📊 Adjusting time estimates by +${AVERAGE_OVERRUN}% based on historical data"
  fi
fi

# Check for process improvements from last iteration
if [ -f "docs/retrospectives/latest-improvements.md" ]; then
  echo "📈 Applying process improvements from last iteration..."
  # Auto-apply documented improvements
fi
```

**Self-Improvement Triggers**:
- If health check fails repeatedly → Generate troubleshooting guide
- If same warnings appear 3+ times → Create automated fix
- If manual steps detected → Queue for automation

### Enhanced Phase Structure

Each phase now includes:
1. **Entry Criteria**: Automated checks before phase begins
2. **Intelligence Gathering**: What the system learns during execution
3. **Adaptation Rules**: How the system modifies itself based on outcomes
4. **Exit Criteria**: Validation before moving to next phase

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

## 📊 Advanced Metrics & Intelligence

### Real-Time Analytics Dashboard
```javascript
// Automatically generated based on project activity
const MetricsDashboard = {
  // Predictive metrics
  estimatedCompletionTime: calculateBasedOnVelocity(),
  predictedBugCount: analyzeCodeComplexity(),
  technicalDebtGrowth: measureRefactoringNeeds(),
  
  // Learning metrics
  processImprovementRate: trackMethodologyChanges(),
  automationGrowth: measureManualVsAutomatedTasks(),
  knowledgeRetention: analyzeDocumentationQuality(),
  
  // Health metrics
  developerSatisfaction: inferFromCommitPatterns(),
  codebaseHealth: combineAllQualityMetrics(),
  systemAutonomy: measureDecisionsMadeAutomatically()
};
```

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

### Weekly Evolution Cycle
Every week, the system automatically:
1. Analyzes all metrics and patterns
2. Identifies top 3 improvement opportunities
3. Generates implementation plans
4. Tests improvements in isolation
5. Integrates successful changes
6. Documents learnings

### Monthly Revolution Check
Monthly, the system asks:
- "What fundamental assumptions should be challenged?"
- "What new technologies could transform our process?"
- "What would a 10x improvement look like?"
- "How can we make developers happier?"

## 🔄 Replication & Adaptation

### Project Initialization
When copied to a new project:
```bash
# Auto-detect project type and adapt
./claude-init.sh

# System automatically:
# 1. Analyzes project structure
# 2. Identifies technology stack
# 3. Adapts processes to fit
# 4. Generates custom commands
# 5. Creates initial metrics baseline
```

### Cross-Project Learning
The system can:
- Share learnings between projects
- Identify universal patterns
- Build a knowledge graph of solutions
- Suggest proven approaches from other contexts

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

## Self-Improving Development Process

This repository follows a structured 6-phase development loop designed for autonomous improvement:

### Phase 1: IDEATION & BRAINSTORMING
**Goal**: Generate and evaluate new features/improvements
**Duration**: 15-30 minutes
**Success Criteria**: At least 3 viable ideas documented with priority scores

**Actions**:
- Analyze current codebase state and identify enhancement opportunities
  - Run `npm run analyze:complexity` to identify complex modules
  - Check test coverage gaps with `npm run coverage`
  - Review TODO comments: `grep -r "TODO" src/`
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
**Duration**: 30-45 minutes
**Success Criteria**: Complete technical design with task breakdown

**Actions**:
- Break down selected feature into specific, testable tasks
  - Each task should be completable in 1-2 hours
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
**Duration**: 30-60 minutes
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
**Duration**: 20-30 minutes
**Success Criteria**: All documentation current and searchable

**Actions**:
- Update README.md with new feature descriptions
  - Add feature to feature list
  - Update screenshots if UI changed
  - Update installation/setup if needed
- Document API changes in `docs/api/`
  - Use OpenAPI/Swagger format
  - Include request/response examples
  - Document error codes and meanings
- Update data schema documentation in `docs/data-models/`
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
- Create user guides for new features in `docs/user-guides/`
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
**Duration**: 30-45 minutes
**Success Criteria**: Actionable improvements identified and documented

**Actions**:
- Review code quality and identify refactoring opportunities
  - Run static analysis: `npm run analyze`
  - Check cyclomatic complexity
  - Identify code smells and duplication
  - Plan technical debt reduction
- Analyze test coverage and identify gaps
  - Review coverage reports
  - Identify critical paths lacking tests
  - Plan test improvements
- Evaluate feature performance and user experience
  - Run performance benchmarks
  - Gather user feedback (if available)
  - Measure against success metrics
- Document lessons learned in `docs/retrospectives/`
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

## Development Loop Commands

### Initial Setup (Run Once)
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

### Daily Development Loop
```bash
# 0. Pre-development checks
docker-compose ps          # Verify database is running
npm test                   # Ensure clean starting state
npm run typecheck          # Check for type errors

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

# 3. Database operations
npm run migration:run      # Apply database migrations
npm run migration:revert   # Rollback last migration
docker-compose up -d postgres  # Start PostgreSQL

# 4. Testing with environment
NODE_ENV=test npm test -- tests/unit/  # Run unit tests without database

# 5. Git workflow
git status                 # Check current changes
git diff                   # Review changes
git add -p                 # Stage changes interactively
git commit -m "feat: descriptive commit message"
git push origin main

# 6. Feature branch workflow
git checkout -b feature/feature-name
# ... make changes ...
git push -u origin feature/feature-name
gh pr create --fill        # Create PR with auto-filled description
```

### Utility Commands
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

# Database operations
npm run db:migrate         # Run database migrations
npm run db:seed            # Seed development data
npm run db:reset           # Reset database to clean state
```

## Project Structure

```
TradeWars2102/
├── src/                   # Source code
│   ├── core/             # Core game logic
│   ├── api/              # API layer
│   ├── data/             # Data access layer
│   ├── ui/               # User interface
│   └── utils/            # Shared utilities
├── tests/                # Test files
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
├── docs/                 # Documentation
│   ├── ideas.md          # Feature ideas backlog
│   ├── development-plans/ # Detailed feature plans
│   ├── api/              # API documentation
│   ├── data-models/      # Data schema docs
│   ├── user-guides/      # User documentation
│   └── retrospectives/   # Development reflections
└── data/                 # Game data files
```

## Code Quality Standards

- **TypeScript**: All code must be typed
- **Testing**: Minimum 90% code coverage
- **Linting**: ESLint with strict rules
- **Documentation**: All public APIs documented
- **Error Handling**: Graceful error handling throughout
- **Performance**: Consider performance implications for all features

## Current Development Priority

1. Establish basic project infrastructure (TypeScript, testing, CI/CD)
2. Implement core game data models
3. Create basic game mechanics (trading, combat, exploration)
4. Build user interface (CLI initially, web later)
5. Add multiplayer capabilities
6. Implement advanced features (economy simulation, AI traders, etc.)

## Security Considerations

- Never commit sensitive data (tokens, passwords, API keys)
- Validate all user inputs
- Use secure random number generation for game mechanics
- Implement proper authentication for multiplayer features

## Process Meta-Improvement Protocol

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
- Create `docs/retrospectives/YYYY-MM-DD-process-improvements.md` after each iteration
- Update CLAUDE.md with concrete improvements, not just theoretical ones
- Add new commands or patterns that proved valuable
- Remove or modify approaches that didn't work well
- Evolve the development process based on actual usage, not assumptions
- Track improvement metrics over time

### Continuous Learning Integration
- Research new development practices and tools after each iteration
- Experiment with emerging technologies that could enhance the workflow
- Adapt the process based on project scale and complexity changes
- Incorporate community feedback on development practices
- Subscribe to relevant newsletters and blogs
- Attend virtual conferences and workshops

### Process Metrics Dashboard
Track these KPIs across iterations:
```yaml
velocity:
  - features_per_iteration: X
  - story_points_completed: Y
  - average_task_duration: Z hours

quality:
  - defect_density: bugs/KLOC
  - test_coverage: X%
  - code_review_findings: Y per PR
  
efficiency:
  - automation_percentage: X%
  - rework_percentage: Y%
  - context_switch_frequency: Z per day

learning:
  - new_patterns_adopted: X
  - process_improvements: Y
  - knowledge_articles_created: Z
```

## Advanced Development Patterns

### Common Issues & Solutions
Based on actual development experience:

1. **Test Failures Due to Database Dependency**
   - Solution: Use `NODE_ENV=test` to skip database initialization
   - Pattern: Add environment checks in initialization code
   ```typescript
   if (process.env.NODE_ENV === 'test') {
     console.log('Database check skipped in test environment');
     return;
   }
   ```

2. **Jest/Mocha Test Framework Conflicts**
   - Issue: Jest tries to parse Mocha test files with Chai imports
   - Solution: Configure Jest to exclude Mocha test files
   - Pattern: Add exclusion patterns in jest.config.js
   ```javascript
   testPathIgnorePatterns: [
     '.*\\.mocha\\.test\\.ts$'
   ]
   ```

3. **EconomicSimulator Implementation Bugs**
   - Issue: Methods returning `undefined` instead of numbers due to incomplete mocks
   - Solution: Ensure test mocks match TypeScript interface requirements
   - Pattern: Mock data must include all required interface properties
   ```typescript
   // Incomplete mock causes NaN
   planets: [{ name: 'Earth', type: PlanetType.INDUSTRIAL }]
   
   // Complete mock works correctly  
   planets: [{ 
     id: 'earth', name: 'Earth', type: PlanetType.INDUSTRIAL,
     population: 5000000, economy: {} as any, defenses: {} as any
   }]
   ```

5. **React App Not Loading (MIME Type/CSP Errors)**
   - Issue: Browser tries to load TypeScript source instead of built bundle
   - Solution: Ensure client is built with `npm run client:build`
   - Pattern: Serve static files after API routes to prevent conflicts
   ```typescript
   // API routes first
   setupRoutes(app, {...});
   
   // Static files last
   if (fs.existsSync(clientPath)) {
     app.use(express.static(clientPath));
     app.use((req, res, next) => {
       if (req.path.startsWith('/api')) return next();
       res.sendFile('index.html', { root: clientPath });
     });
   }
   ```

2. **TypeScript Strict Mode Errors**
   - Run `npm run typecheck` frequently during development
   - Fix null/undefined checks immediately
   - Use optional chaining (`?.`) and nullish coalescing (`??`)

3. **Method Signature Mismatches in Tests**
   - Create wrapper methods for backward compatibility
   - Document public API changes clearly
   - Update tests immediately after refactoring

4. **Database Connection Issues**
   - Always check `docker-compose ps` before starting
   - Use health checks in docker-compose.yml
   - Implement connection retry logic

5. **Repository Testing Pattern**
   - Mock TypeORM at the module level:
   ```typescript
   jest.mock('../../../src/data/database.config', () => ({
     AppDataSource: {
       getRepository: jest.fn(),
     },
   }));
   ```
   - Create comprehensive mock repository with all methods
   - Test edge cases like null returns and missing relations
   - Always mock both successful and failure scenarios

### Error Recovery Protocol
When development issues occur:
1. **Immediate Assessment**: Identify scope and impact
2. **Root Cause Analysis**: Use git bisect if needed
3. **Recovery Options**:
   - Rollback: `git reset --hard HEAD~1`
   - Feature flag disable: Toggle in config
   - Hotfix branch: `git checkout -b hotfix/issue-name`
4. **Post-Mortem**: Document in `docs/retrospectives/incidents/`

### Context Preservation Between Sessions
Maintain development continuity:
1. **Session Start Checklist**:
   ```bash
   git status                    # Check working state
   npm test                      # Verify tests pass
   npm run todo:read             # Review pending tasks
   cat docs/session-notes.md     # Read previous context
   ```
2. **Session End Checklist**:
   ```bash
   npm run todo:write            # Update task status
   echo "## $(date)" >> docs/session-notes.md
   # Document current state and next steps
   git add -A && git commit -m "WIP: session checkpoint"
   ```

### Performance Optimization Workflow
1. **Baseline Measurement**: Record current metrics
2. **Profile**: Use appropriate tools (CPU, memory, startup)
3. **Optimize**: Apply targeted improvements
4. **Verify**: Ensure optimization didn't break functionality
5. **Document**: Record techniques that worked

### Dependency Management Strategy
- **Monthly Review**: Check for updates and security patches
- **Conservative Updates**: Update dev dependencies freely, runtime carefully
- **Version Pinning**: Use exact versions for critical dependencies
- **Update Process**:
  ```bash
  npm outdated                  # Check what needs updating
  npm update --dry-run          # Preview changes
  npm update                    # Apply updates
  npm test                      # Verify nothing broke
  npm audit                     # Check security
  ```

## Notes for Future Development

- Keep the classic Trade Wars spirit while modernizing the experience
- Focus on clean, maintainable code that can evolve
- Prioritize features that showcase modern development practices
- Document architectural decisions for future reference
- Balance nostalgia with modern UX expectations
- Consider accessibility from the start
- Plan for internationalization early
- **ESSENTIAL**: This development process is itself a living system that must evolve and improve with each iteration

## Quick Reference Card

### Most Used Commands
```bash
# Development
npm run dev:start && npm test -- --watch  # Start dev session
npm run lint:fix && npm test               # Quick quality check
git add -p && git commit                   # Interactive commit

# Analysis
npm run analyze && npm run test:coverage   # Full code analysis
npm run deps:check && npm audit            # Dependency health

# Documentation
npm run docs:serve                         # View docs locally
```

### Common Patterns
- **Feature Development**: Phase 1→2→3→4→5→6 (full cycle)
- **Bug Fix**: Phase 3→4→6 (implementation focused)
- **Refactoring**: Phase 2→3→4→6 (planning critical)
- **Documentation**: Phase 5→6 (knowledge capture)

### Success Indicators
✅ All tests passing
✅ >90% code coverage
✅ No lint warnings
✅ Documentation updated
✅ Retrospective completed
✅ CLAUDE.md improved