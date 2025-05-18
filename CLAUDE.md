# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sector Wars 2102 is a web-based space trading simulation game built with a microservices architecture. Players navigate through different sectors, trade commodities, manage ships, and colonize planets in a turn-based gameplay environment.

## Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 17 via Neon (SQLAlchemy ORM)
- **Authentication**: JWT-based authentication
- **Web Server**: Uvicorn with Gunicorn
- **Frontend**: 
  - Player Client: React with TypeScript
  - Admin UI: React with TypeScript and D3.js for visualization
- **Testing**: 
  - Pytest for backend unit and integration tests
  - Cypress for E2E testing
- **Containerization**: Docker with Docker Compose
- **Code Quality**: 
  - Ruff for linting
  - MyPy for type checking

## Development Environments

The project is designed to work across three development environments:
1. **Local Development**: MacBook with Cursor IDE and Docker Desktop
2. **GitHub Codespaces**: Remote development with VS Code
3. **Replit**: iPad-compatible development environment

All environments use the same Neon PostgreSQL database for consistency. Only Local and Codespace use Docker. Replit uses PM2 to run all components within a single Replit app.

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

The gameserver automatically manages the database schema:

1. On startup, it checks if the database tables exist
2. If tables don't exist, it automatically runs Alembic migrations
3. After migrations, it creates initial data including default admin user

If you need to manually manage the database:

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

When connecting to a new database, no additional action is required - the system will automatically:
1. Detect the fresh database
2. Run migrations to create the schema
3. Create the default admin user (username: admin, password: admin)

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

## Service Architecture

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

## Game Mechanics

- **Ships**: Players start with a Light Freighter and can purchase larger ships
- **Trading**: Buy and sell commodities (Food, Tech, Ore, Fuel) with price variations by sector
- **Fighters**: Space fighters can be purchased for ship defense
- **Colonization**: Transport population to colonize planets by meeting population and credit requirements

## Documentation Structure

- **AISPEC files** (`/DOCS/AISPEC/`): AI-centric documentation of system components
- **Feature Documentation** (`/DOCS/FEATURE_DOCS/`): Specific feature details and game rules
- **Development Journal** (`/DEV_JOURNAL/`): Progress and decision tracking

## Important Development Guidelines

1. **API-First Development**: The Game API Server should be the single source of truth for game logic
2. **Service Isolation**: Each service should function independently
3. **Environment Agnostic**: Code should run identically in all three environments
4. **Testing First**: New features require test coverage before merging
5. **Documentation**: Update AISPEC files when creating or modifying features