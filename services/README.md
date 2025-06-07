# Services

Microservices and backend components for the Sectorwars2102 game platform.

## Overview

This directory contains a multi-regional, containerized microservices architecture that powers the Sectorwars2102 space trading and combat game. The services are designed to scale across multiple regions while maintaining data consistency and real-time gameplay.

## Architecture

The services follow a distributed microservices pattern with:
- **Regional Distribution**: Services can be deployed across multiple geographic regions
- **Containerization**: All services run in Docker containers via docker-compose
- **Real-time Communication**: WebSocket connections for live gameplay
- **Multi-language Support**: Self-contained internationalization (i18n) in each frontend service
- **AI Integration**: Intelligent trading systems and player behavior analysis

## Services

### Core Services

#### `gameserver/`
**Main game backend service** - FastAPI-based Python service
- RESTful API endpoints for all game functionality
- Real-time WebSocket connections for live gameplay
- Database models for players, ships, sectors, planets, and economy
- Authentication and authorization (JWT + OAuth)
- AI trading intelligence and market prediction
- Multi-factor authentication (MFA) support
- Comprehensive admin tools and analytics

#### `database/`
**PostgreSQL database service**
- Primary data store for all game data
- Automated migrations via Alembic
- Database initialization scripts
- Backup and restore capabilities
- Multi-regional data replication support

### User Interfaces

#### `admin-ui/`
**Administrative dashboard** - React/TypeScript SPA
- Universe management and editing tools
- Player administration and moderation
- Real-time analytics and monitoring
- AI trading system controls
- Multi-regional governance tools
- Comprehensive reporting and audit logs
- Self-contained internationalization system

#### `player-client/`
**Player game interface** - React/TypeScript SPA
- Main game interface for players
- Real-time ship movement and trading
- Combat systems and fleet management
- Planetary colonization interface
- Team and alliance management
- Mobile-responsive design
- Self-contained internationalization system

### Infrastructure Services

#### `nginx-gateway/`
**Reverse proxy and load balancer**
- Routes traffic to appropriate services
- SSL termination and security headers
- Rate limiting and DDoS protection
- Static file serving

#### `region-manager/`
**Multi-regional orchestration service** - Python service
- Manages deployment across multiple regions
- Regional health monitoring
- Cross-region data synchronization
- Dynamic scaling and load balancing

## Technology Stack

- **Backend**: Python 3.11+ with FastAPI
- **Frontend**: React 18+ with TypeScript and Vite (Self-contained services with independent i18n)
- **Database**: PostgreSQL 15+ with Alembic migrations (Primary data store)
- **Cache & Messaging**: Redis 7+ (Real-time events, sessions, cross-regional communication)
- **Real-time**: WebSocket connections + Redis pub/sub
- **Authentication**: JWT tokens with OAuth integration
- **Containerization**: Docker and Docker Compose
- **Monitoring**: Built-in health checks and metrics
- **AI/ML**: Integrated trading intelligence and analytics

## Hybrid Architecture

The system uses a **PostgreSQL + Redis hybrid approach** for optimal performance:

### **PostgreSQL (Primary Data Store)**
- Player accounts and subscription management
- Regional governance and policy configuration
- Ship ownership and sector data
- Trade transactions and economic history
- Long-term analytics and reporting
- ACID compliance for financial operations

### **Redis (Real-time Layer)**
- Live player movement notifications
- Cross-regional messaging and events
- Session data and temporary state
- Market price broadcasting
- Service discovery for regional containers
- Real-time gameplay event streaming

## Getting Started

1. **Prerequisites**: Docker and Docker Compose installed
2. **Environment Setup**: Copy environment templates and configure
3. **Database**: Initialize with `docker-compose up database`
4. **Services**: Start all services with `docker-compose up`
5. **Access**: 
   - Player Client: http://localhost:3000
   - Admin UI: http://localhost:3001
   - Game API: http://localhost:8080
   - Region Manager: http://localhost:8081

## Development

Each service contains its own README with specific development instructions:
- See `gameserver/README.md` for backend development
- See `admin-ui/package.json` scripts for frontend development
- See `player-client/package.json` scripts for client development

## Regional Deployment

The system supports multi-regional deployment for global scalability:
- Central Nexus: Primary coordination region
- Regional Nodes: Geographic distribution points
- Data Replication: Automated cross-region synchronization
- Load Balancing: Intelligent request routing

---

*This documentation is maintained as part of the CLAUDE.md self-improving development system*
