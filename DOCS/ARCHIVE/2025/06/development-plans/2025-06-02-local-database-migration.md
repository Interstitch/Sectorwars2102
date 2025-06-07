# Local Database Migration Plan - June 2, 2025

## Overview
Migration from remote Neon PostgreSQL to local Docker-based PostgreSQL service to improve development experience, reduce external dependencies, and enhance data control.

## Current Architecture Analysis

### Existing Setup
- **Database**: Remote Neon PostgreSQL 
- **Connection**: Via `DATABASE_URL` environment variable
- **Services**: gameserver, admin-ui, player-client, region-manager
- **Limitations**: 
  - Network dependency for database access
  - Limited control over database configuration
  - Potential latency issues in development
  - External service dependency

### Multi-Regional Reference
The `docker-compose.multi-regional.yml` already includes:
- PostgreSQL 15 Alpine containers
- Proper volume mounting for data persistence
- Health checks and initialization scripts
- Network isolation and security

## Target Architecture

### New Local Database Service Structure
```
services/
├── database/
│   ├── Dockerfile
│   ├── docker-compose.override.yml
│   ├── init/
│   │   ├── 01-init-database.sql
│   │   ├── 02-create-users.sql
│   │   └── 03-seed-data.sql
│   ├── migrations/
│   │   └── (linked to gameserver/alembic)
│   ├── backups/
│   │   └── .gitkeep
│   ├── config/
│   │   ├── postgresql.conf
│   │   └── pg_hba.conf
│   └── README.md
```

### Service Configuration
- **Image**: PostgreSQL 15 Alpine (lightweight, secure)
- **Port**: 5432 (internal), 5433 (external for tools)
- **Database**: `sectorwars_dev`
- **Users**: 
  - `postgres` (superuser)
  - `sectorwars_app` (application user)
  - `sectorwars_readonly` (read-only user for analytics)

### Data Management
- **Persistence**: Docker volumes for data and backups
- **Initialization**: Automated schema creation and seeding
- **Migration**: Alembic integration for schema changes
- **Backup**: Automated backup scripts and restoration

## Implementation Tasks

### Phase 1: Database Service Creation
1. **Create Database Service Directory**
   - `/services/database/` structure
   - Dockerfile based on postgres:15-alpine
   - Configuration files for PostgreSQL

2. **Database Initialization Scripts**
   - Database and user creation
   - Schema initialization from existing alembic migrations
   - Essential seed data (languages, namespaces, admin users)

3. **Security Configuration**
   - Proper user privileges and access control
   - Network isolation within Docker
   - Environment variable management for credentials

### Phase 2: Docker Compose Integration
1. **Update Main docker-compose.yml**
   - Add PostgreSQL service definition
   - Configure service dependencies
   - Set up networking and volumes

2. **Environment Variable Migration**
   - Update DATABASE_URL to point to local service
   - Add database credentials management
   - Maintain backward compatibility options

3. **Service Dependencies**
   - Update gameserver depends_on configuration
   - Add health checks for database readiness
   - Configure proper startup order

### Phase 3: Data Migration and Testing
1. **Data Export from Neon**
   - Export existing schema and data
   - Transform for local database format
   - Create migration validation scripts

2. **Migration Scripts**
   - Automated migration from Neon to local
   - Rollback procedures if needed
   - Data integrity validation

3. **Testing and Validation**
   - Unit tests for database connectivity
   - Integration tests for all services
   - Performance benchmarking

## Technical Specifications

### PostgreSQL Configuration
```sql
-- Database: sectorwars_dev
-- Extensions: uuid-ossp, pgcrypto
-- Collation: en_US.UTF-8
-- Timezone: UTC
```

### Docker Service Definition
```yaml
database:
  image: postgres:15-alpine
  container_name: sectorwars-database
  environment:
    POSTGRES_DB: sectorwars_dev
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: ${DB_PASSWORD}
  volumes:
    - postgres_data:/var/lib/postgresql/data
    - ./services/database/init:/docker-entrypoint-initdb.d
    - ./services/database/config:/etc/postgresql
  ports:
    - "5433:5432"
  networks:
    - sectorwars-network
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U postgres -d sectorwars_dev"]
    interval: 10s
    timeout: 5s
    retries: 5
  restart: unless-stopped
```

### Application Configuration Updates
```python
# Local database URL
DATABASE_URL = "postgresql://sectorwars_app:${APP_DB_PASSWORD}@database:5432/sectorwars_dev"

# Connection pool settings for local development
SQLALCHEMY_POOL_SIZE = 5
SQLALCHEMY_MAX_OVERFLOW = 10
SQLALCHEMY_POOL_TIMEOUT = 30
```

## Security Considerations

### Database Security
- **User Isolation**: Separate application and admin users
- **Network Security**: Database only accessible within Docker network
- **Password Management**: Strong passwords via environment variables
- **Backup Encryption**: Encrypted backup storage

### Development vs Production
- **Development**: Simplified configuration, debug logging
- **Production**: Enhanced security, monitoring, backup automation
- **Environment Separation**: Clear distinction between local and production configs

## Benefits

### Development Experience
- **Faster Development**: No network latency to external database
- **Offline Development**: Work without internet connection
- **Data Control**: Full control over test data and schema changes
- **Debugging**: Direct access to database for troubleshooting

### Operational Benefits
- **Cost Reduction**: No external database costs for development
- **Data Privacy**: Sensitive development data stays local
- **Testing Flexibility**: Easy database resets and test data management
- **Version Control**: Database configuration tracked in Git

### Performance
- **Latency**: Eliminated network round-trips to external service
- **Throughput**: Local disk I/O typically faster than network
- **Reliability**: No dependency on external service availability

## Migration Strategy

### Phase A: Preparation (30 minutes)
1. Create database service structure
2. Configure PostgreSQL settings
3. Update docker-compose.yml

### Phase B: Data Migration (15 minutes)
1. Export data from Neon database
2. Initialize local database with schema
3. Import data to local database

### Phase C: Service Integration (15 minutes)
1. Update gameserver configuration
2. Test service connectivity
3. Validate application functionality

### Phase D: Validation (15 minutes)
1. Run full test suite
2. Verify data integrity
3. Test backup and restore procedures

## Rollback Plan

### If Migration Fails
1. **Immediate Rollback**: Revert DATABASE_URL to Neon
2. **Service Restart**: Restart all services with original configuration
3. **Data Validation**: Verify Neon database integrity
4. **Issue Analysis**: Document and analyze failure points

### Backup Procedures
- **Pre-migration Backup**: Full Neon database export
- **Configuration Backup**: Git commit of all configuration changes
- **Documentation**: Step-by-step rollback procedures

## Success Metrics

### Technical Metrics
- **Database Response Time**: < 5ms for local queries
- **Service Startup Time**: < 30 seconds for full stack
- **Data Integrity**: 100% data consistency validation
- **Test Coverage**: All existing tests pass with local database

### Operational Metrics
- **Development Speed**: Reduced database-related development delays
- **Reliability**: 99.9% uptime for local development environment
- **Backup Success**: Automated daily backups with validation
- **Migration Time**: Complete migration in < 90 minutes

## Future Enhancements

### Phase 2 Features
- **Database Monitoring**: Grafana dashboards for database metrics
- **Automated Backups**: Scheduled backups with retention policies
- **Read Replicas**: Read-only replicas for analytics and reporting
- **Connection Pooling**: PgBouncer integration for connection management

### Phase 3 Features
- **Multi-Database Support**: Separate databases for different environments
- **Schema Versioning**: Advanced migration and rollback capabilities
- **Performance Tuning**: Automated performance optimization
- **Disaster Recovery**: Automated disaster recovery procedures

## Implementation Timeline

### Day 1: Foundation (2 hours)
- Create database service structure
- Configure PostgreSQL settings
- Update docker-compose.yml
- Test basic connectivity

### Day 1: Migration (1 hour)
- Export Neon database
- Initialize local database
- Import data and validate
- Update service configurations

### Day 1: Validation (30 minutes)
- Run full test suite
- Verify functionality
- Document any issues
- Create backup procedures

**Total Estimated Time**: 3.5 hours

## Risk Assessment

### High Risk
- **Data Loss**: Mitigated by comprehensive backups
- **Service Downtime**: Mitigated by quick rollback procedures
- **Configuration Errors**: Mitigated by testing and validation

### Medium Risk
- **Performance Issues**: Mitigated by benchmarking and tuning
- **Compatibility Problems**: Mitigated by version matching
- **Network Issues**: Mitigated by Docker network configuration

### Low Risk
- **Volume Management**: Mitigated by Docker best practices
- **Backup Failures**: Mitigated by multiple backup strategies
- **Documentation Gaps**: Mitigated by comprehensive documentation

## Conclusion

This migration plan provides a comprehensive roadmap for transitioning from the remote Neon PostgreSQL database to a local Docker-based PostgreSQL service. The approach prioritizes data safety, service reliability, and development experience while maintaining the ability to rollback if issues arise.

The implementation follows CLAUDE.md principles with clear phases, measurable outcomes, and continuous improvement opportunities.

---

*Migration plan created following CLAUDE.md Phase 2 methodology*