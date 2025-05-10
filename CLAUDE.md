# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sector Wars 2102 is a web-based space trading simulation game built with a microservices architecture. Players navigate through different sectors, trade commodities, manage ships, and colonize planets.

## Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 16 via Neon (SQLAlchemy ORM)
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

All environments use the same Neon PostgreSQL database and Docker containerization for consistency.

## Development Commands

### Setup & Running

```bash
# Clone repository
git clone https://github.com/yourusername/Sectorwars2102.git
cd Sectorwars2102

# Set up environment variables (copy from example)
cp .env.example .env
# Edit .env with your Neon database URL and other settings

# Start all services (auto-detects environment)
./dev-scripts/start.sh

# Or manually with Docker Compose
docker-compose up
```

### Working with Individual Services

```bash
# Game API Server
cd services/gameserver
poetry install  # Install dependencies locally (optional)

# Player Client
cd services/player-client
npm install     # Install dependencies locally (optional)
npm run dev     # Run development server locally (optional)

# Admin UI
cd services/admin-ui
npm install     # Install dependencies locally (optional)
npm run dev     # Run development server locally (optional)
```

### Testing

```bash
# Run all backend tests
cd services/gameserver
pytest

# Run specific backend test module
pytest tests/unit/test_trading.py

# Run frontend E2E tests
cd services/player-client
npx cypress run

# Run specific frontend test
npx cypress run --spec "cypress/e2e/trading.cy.js"
```

### Linting & Type Checking

```bash
# Backend linting
cd services/gameserver
ruff check .

# Backend type checking
mypy .

# Frontend linting
cd services/player-client
npm run lint
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

## Documentation

- **AISPEC files** (`/DOCS/AISPEC/`): AI-centric documentation of system components
- **Feature Documentation** (`/DOCS/FEATURE_DOCS/`): Specific feature details
- **Development Journal** (`/DEV_JOURNAL/`): Progress and decision tracking

## Important Development Guidelines

1. **API-First Development**: The Game API Server should be the single source of truth for game logic
2. **Service Isolation**: Each service should function independently
3. **Environment Agnostic**: Code should run identically in all three environments
4. **Testing First**: New features require test coverage before merging
5. **Documentation**: Update AISPEC files when creating or modifying features
6. **Development Journal**: Document changes regularly in the DEV_JOURNAL/ folder (@DEV_JOURNAL/README.md)

## Common Issues & Solutions

1. **Database Connection**: If you encounter database connection issues, verify:
   - `.env` file contains correct Neon PostgreSQL URL
   - Network access to Neon is available
   - Database migrations have been applied

2. **Docker Compatibility**: If Docker has issues on Replit:
   - Use the Replit-specific compose file: `docker-compose -f docker-compose.yml -f docker-compose.replit.yml up`
   - Verify Replit container permissions are set correctly

3. **Testing Environment**: For isolated testing:
   - Use the test database URL from `.env.test`
   - Run tests in dedicated containers: `docker-compose -f docker-compose.test.yml up`

## Development Environment Memory

- The Docker setup needs to remain compatible between Codespace + VS Code, Replit, and local Cursor IDE + Docker Desktop.