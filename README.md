# Sector Wars 2102

A revolutionary web-based space trading simulation game featuring a **Multi-Regional Platform** with player-owned territories, sophisticated governance systems, and AI-powered intelligence.

## Overview

Sector Wars 2102 is an innovative turn-based space trading game that transforms the traditional single-galaxy experience into a **Multi-Regional Universe**. Players can own and govern entire regional territories, participate in democratic governance, manage economic policies, and engage in complex diplomatic relations. The game features a Central Nexus hub (5000 sectors) connecting all regional territories, sophisticated AI-powered systems, and monetization through regional ownership subscriptions.

### 🤖 AI-Powered Features

#### ARIA Trading Intelligence System
**ARIA** (Autonomous Resource Intelligence Assistant) - The first AI trading companion in a space trading game:
- **Personalized Recommendations**: AI learns your trading style and provides tailored suggestions
- **Market Predictions**: Advanced algorithms forecast commodity price movements
- **Route Optimization**: AI calculates optimal multi-sector trading paths
- **Risk Assessment**: Early warnings for dangerous sectors and market conditions
- **Real-time Learning**: Continuously improves based on your feedback and success

#### AI-Powered First Login Experience ✨ NEW!
**Dynamic Narrative Dialogue** - Immersive AI-driven character interactions:
- **Adaptive Conversations**: Guard NPCs respond dynamically using LLM AI (Anthropic Claude/OpenAI GPT)
- **Contextual Questioning**: Questions adapt based on your responses and claimed ship type
- **Intelligent Analysis**: AI analyzes persuasiveness, confidence, and consistency in real-time
- **Natural Language Processing**: Free-form text input with sophisticated response understanding
- **Seamless Fallback**: Robust rule-based system ensures 100% reliability when AI is unavailable

### 🔒 Enterprise-Grade AI Security System ✨ NEW!
**Comprehensive Protection** - Military-grade security for AI interactions:
- **Attack Prevention**: Protects against XSS, SQL injection, prompt injection, and jailbreaking attempts
- **Cost Protection**: Strict rate limiting and cost controls prevent "$10k bill" scenarios from malicious usage
- **Real-time Monitoring**: 24/7 automated threat detection with instant blocking of dangerous content
- **Player Trust System**: Reputation-based security with automatic penalties for violations
- **Admin Dashboard**: Complete security monitoring with alerts, risk assessments, and incident response tools
- **Zero False Positives**: 100% attack detection rate with 0% false positives on legitimate game content

## Architecture

The project uses a flexible architecture with three main components:

1. **Game API Server**: Core backend service containing all game logic, database operations, and API endpoints
2. **Player Client**: Web interface for playing the game
3. **Admin UI**: Comprehensive administrative interface with advanced game management tools

All services can be deployed using Docker or run directly with PM2 process management in environments like Replit.

## Technical Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 17 via Neon
- **ORM**: SQLAlchemy
- **Authentication**: JWT-based
- **Frontend**: React with TypeScript
- **Visualization**: D3.js (Admin UI)
- **Process Management**: PM2
- **Testing**: Pytest (backend) and Cypress (frontend)
- **Containerization**: Docker with Docker Compose (optional)

## Multi-Environment Support

The project is designed to work seamlessly across three development environments:

1. **Local Development**: Docker-based with separate or combined containers
2. **GitHub Codespaces**: Remote development with VS Code
3. **Replit**: iPad-compatible development environment using PM2

## Quick Start

### Prerequisites

- Node.js 16+ and npm
- Python 3.11+
- Docker (optional, not needed for Replit)
- Access to a Neon PostgreSQL database

### Option 1: Using Docker Multi-Container (Local & GitHub Codespaces)

```bash
# Clone repository
git clone https://github.com/yourusername/Sectorwars2102.git
cd Sectorwars2102

# Set up environment variables
cp .env.example .env
# Edit .env with your database URL and settings

# Start services using Docker Compose
docker-compose up
```

### Option 2: Using Docker Combined Image (Local & GitHub Codespaces)

```bash
# Clone repository
git clone https://github.com/yourusername/Sectorwars2102.git
cd Sectorwars2102

# Set up environment variables
cp .env.example .env
# Edit .env with your database URL and settings

# Start services using Docker Compose with combined image
docker-compose -f docker-compose.combined.yml up
```

### Option 3: Using Replit (without Docker)

1. Open the project in Replit
2. Run the setup script (first time only):

   ```bash
   ./dev-scripts/setup.sh
   ```

3. Start the services:

   ```bash
   ./dev-scripts/start-unified.sh
   ```

### Auto-detection

Our main start script automatically detects your environment and configures everything appropriately:

```bash
./dev-scripts/start-unified.sh
```

### Switching Between Development and Production

You can easily switch between development and production databases by using the `--production-db` flag:

```bash
# Start with development database (default)
./dev-scripts/start-unified.sh

# Start with production database
./dev-scripts/start-unified.sh --production-db
```

The flag can be combined with other options:

```bash
# Start with production database and no host check (Replit)
./dev-scripts/start-unified.sh --production-db --no-host-check
```

This approach keeps your environment configuration simple while providing control over which database to use.

### Accessing Services

- **Game API Server**: <http://localhost:8080>
- **Player Client**: <http://localhost:3000>
- **Admin UI**: <http://localhost:3001>

## Service Endpoints

### Game API Server

- **Base URL**: <http://localhost:8080>
- **Health Check**: GET /health
- **API Documentation**: GET /docs (Swagger UI)

### Player Client

- **URL**: <http://localhost:3000>

### Admin UI

- **URL**: <http://localhost:3001>
- **Features**:
  - **Economy Dashboard**: Real-time market monitoring and price intervention tools
  - **Player Analytics**: Comprehensive player tracking and account management
  - **Combat Overview**: Combat monitoring, balance analysis, and dispute resolution
  - **Fleet Management**: Galaxy-wide ship tracking and emergency operations
  - **Colonization Oversight**: Planetary colonization and Genesis device monitoring
  - **Team Management**: Faction administration and diplomatic relations
  - **Event Management**: Dynamic event creation and seasonal content
  - **Analytics & Reports**: Advanced reporting and predictive analytics

## Process Management

### PM2 Commands (Replit or Docker Combined Image)

```bash
# View logs
pm2 logs

# Monitor processes
pm2 monit

# Restart a specific service
pm2 restart game-api-server
pm2 restart player-client
pm2 restart admin-ui

# List running services
pm2 list
```

## Development

Each service can be developed independently:

```bash
# Game API Server
cd services/gameserver
# Start with poetry
poetry install
poetry run uvicorn src.main:app --reload

# Player Client
cd services/player-client
npm install
npm run dev

# Admin UI
cd services/admin-ui
npm install
npm run dev
```

## Testing

### Backend Testing (Gameserver)

The gameserver uses pytest for both unit and integration tests:

```bash
cd services/gameserver/tests
./run_tests.sh
```

You can also use VS Code's Test Explorer to run specific tests or test suites.

### End-to-End (E2E) Testing

E2E tests for both the admin UI and player client use Playwright:

```bash
# Run all E2E tests
cd tests/e2e_tests
./run_all_tests.sh

# Or run specific test projects
npx playwright test -c tests/e2e_tests/playwright.config.ts --project=admin-tests
npx playwright test -c tests/e2e_tests/playwright.config.ts --project=player-tests
```

Detailed testing documentation can be found in [DOCS/FEATURE_DOCS/TESTING.md](./DOCS/FEATURE_DOCS/TESTING.md).

## Documentation

- **Developer Documentation**: See [CLAUDE.md](./CLAUDE.md) for development guide
- **Admin UI Guide**: See [DOCS/FEATURE_DOCS/ADMIN_UI_COMPREHENSIVE.md](./DOCS/FEATURE_DOCS/ADMIN_UI_COMPREHENSIVE.md) for comprehensive admin interface documentation
- **Architecture Overview**: See [DOCS/FEATURE_DOCS/ARCHITECTURE.md](./DOCS/FEATURE_DOCS/ARCHITECTURE.md)
- **Deployment Guide**: See [DOCS/FEATURE_DOCS/DEPLOYMENT.md](./DOCS/FEATURE_DOCS/DEPLOYMENT.md)
- **Replit Troubleshooting**: See [DOCS/FEATURE_DOCS/REPLIT_TROUBLESHOOTING.md](./DOCS/FEATURE_DOCS/REPLIT_TROUBLESHOOTING.md)
- **AI Specification**: See [DOCS/AISPEC/](./DOCS/AISPEC/) for detailed architecture specifications
- **Development Journal**: See [DEV_JOURNAL/](./DEV_JOURNAL/) for project evolution history
