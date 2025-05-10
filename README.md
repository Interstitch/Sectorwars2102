# Sector Wars 2102

A web-based space trading simulation game built with a microservices architecture and modern technology stack.

## Overview

Sector Wars 2102 is a turn-based space trading game where players navigate through different sectors, trade commodities, manage ships, and colonize planets. The game features a dynamic universe with interconnected sectors, a robust trading system, and planet colonization mechanics.

## Architecture

The project uses a microservices architecture with three main components:

1. **Game API Server**: Core backend service containing all game logic, database operations, and API endpoints
2. **Player Client**: Web interface for playing the game
3. **Admin UI**: Specialized interface for game administration and universe management

All services are containerized using Docker for consistent development and deployment across environments.

## Technical Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 16 via Neon
- **ORM**: SQLAlchemy
- **Authentication**: JWT-based
- **Frontend**: React with TypeScript
- **Visualization**: D3.js (Admin UI)
- **Testing**: Pytest (backend) and Cypress (frontend)
- **Containerization**: Docker with Docker Compose

## Multi-Environment Support

The project is designed to work seamlessly across three development environments:

1. **Local Development**: MacBook with Cursor IDE and Docker Desktop
2. **GitHub Codespaces**: Remote development with VS Code
3. **Replit**: iPad-compatible development environment

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Steps to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Sectorwars2102.git
   cd Sectorwars2102
   ```

2. Start the services:
   ```bash
   # This will detect your environment and start the appropriate services
   ./dev-scripts/start.sh
   ```

3. Access the services:
   - **Game API Server**: http://localhost:5000
   - **Player Client**: http://localhost:3000
   - **Admin UI**: http://localhost:3001

## Service Endpoints

### Game API Server
- **Base URL**: http://localhost:5000
- **Health Check**: GET /health
- **API Documentation**: GET /docs (Swagger UI)

### Player Client
- **URL**: http://localhost:3000

### Admin UI
- **URL**: http://localhost:3001

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

## Documentation

- **Developer Documentation**: See [CLAUDE.md](./CLAUDE.md) for development guide
- **AI Specification**: See [DOCS/AISPEC/](./DOCS/AISPEC/) for detailed architecture specifications
- **Development Journal**: See [DEV_JOURNAL/](./DEV_JOURNAL/) for project evolution history