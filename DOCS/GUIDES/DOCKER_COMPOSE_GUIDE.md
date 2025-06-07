# Docker Compose Unified Setup Guide

This project now uses a single `docker-compose.yml` file that supports multiple deployment scenarios through Docker Compose profiles.

## Quick Start

### Development Mode (Default)
```bash
# Start basic development environment
docker-compose up

# Or explicitly use development profile
docker-compose --profile development up
```

### Multi-Regional Production
```bash
# Full multi-regional setup with all services
docker-compose --profile multi-regional up
```

### Security-Hardened Production
```bash
# Production environment with security hardening
docker-compose --profile production up
```

### Monitoring Stack
```bash
# Add monitoring services (Prometheus + Grafana)
docker-compose --profile monitoring up
```

## Environment Configuration

All configuration is handled through the `.env` file. Key variables:

### Profile Selection
```env
COMPOSE_PROFILES=development  # Options: development, multi-regional, production, monitoring
```

### Build Configuration
```env
BUILD_TARGET=development     # Options: development, production
ENVIRONMENT=development      # Options: development, production
```

### Service Ports
```env
GAMESERVER_PORT=8080
PLAYER_CLIENT_PORT=3000
ADMIN_UI_PORT=3001
```

## Available Profiles

### `development` (Default)
**Services**: database, gameserver, player-client, admin-ui
- Local PostgreSQL database
- Development builds with hot reload
- Basic networking
- Suitable for local development

### `multi-regional`
**Services**: central-nexus-db, redis-nexus, central-nexus-server, player-client, admin-ui, nginx-gateway, region-manager
- Multi-regional architecture
- Redis for cross-region communication
- Nginx reverse proxy
- Regional management capabilities

### `production`
**Services**: central-nexus-db, redis-nexus, central-nexus-server, player-client, admin-ui, nginx-gateway
- Production-optimized builds
- Security hardening
- Resource limits
- Health checks

### `monitoring`
**Services**: prometheus, grafana
- Prometheus metrics collection
- Grafana dashboards
- Can be combined with other profiles

### `regional-template`
**Services**: regional-db-template, regional-server-template
- Templates for dynamic regional scaling
- Used by region-manager for creating new regions

## Combining Profiles

You can run multiple profiles together:

```bash
# Production with monitoring
docker-compose --profile production --profile monitoring up

# Multi-regional with monitoring
docker-compose --profile multi-regional --profile monitoring up
```

## Environment-Specific Configurations

### GitHub Codespaces
Your `.env` is already configured for Codespaces:
```env
DEV_ENVIRONMENT=codespaces
API_BASE_URL=https://super-duper-carnival-qppjvq94q9vcxwqp-8080.app.github.dev
FRONTEND_URL=https://super-duper-carnival-qppjvq94q9vcxwqp-3000.app.github.dev
```

### Local Development
For local development, update these in `.env`:
```env
DEV_ENVIRONMENT=local
API_BASE_URL=http://localhost:8080
FRONTEND_URL=http://localhost:3000
```

### Production Deployment
For production, ensure all sensitive variables are set:
```env
ENVIRONMENT=production
JWT_SECRET=<your-secure-jwt-secret>
PAYPAL_CLIENT_ID=<your-paypal-client-id>
PAYPAL_CLIENT_SECRET=<your-paypal-client-secret>
# ... other production secrets
```

## Security Notes

- All sensitive values are stored in `.env` (not checked into git)
- Production profile includes security hardening
- No default secrets in production mode
- Resource limits applied in production

## Migration from Old Files

The old separate files have been consolidated:
- `docker-compose.yml` → Now the unified file
- `docker-compose.multi-regional.yml` → Use `--profile multi-regional`
- `docker-compose.prod.yml` → Use `--profile production`

## Troubleshooting

### Port Conflicts
Update port mappings in `.env`:
```env
GAMESERVER_PORT=8081  # If 8080 is in use
PLAYER_CLIENT_PORT=3001  # If 3000 is in use
```

### Profile Not Found
Ensure you're using the correct profile name:
```bash
docker-compose config --profile development  # Validate profile
```

### Environment Variables
Check that all required variables are set:
```bash
docker-compose config  # Show resolved configuration
```