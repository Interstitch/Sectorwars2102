# SectorWars 2102 Database Service

Local PostgreSQL database service for SectorWars 2102 development environment.

## Overview

This service provides a containerized PostgreSQL 15 database with:
- Optimized configuration for development
- Automated initialization and seeding
- Security best practices
- Backup and restore capabilities
- Health monitoring

## Quick Start

### Starting the Database

```bash
# Start database service only
docker-compose up database

# Start all services (includes database)
docker-compose up
```

### Accessing the Database

```bash
# From host machine (external access)
psql -h localhost -p 5433 -U sectorwars_app -d sectorwars_dev

# From within Docker network
psql -h database -p 5432 -U sectorwars_app -d sectorwars_dev

# Using the postgres superuser
psql -h localhost -p 5433 -U postgres -d sectorwars_dev
```

### Database Credentials

| User | Password | Privileges |
|------|----------|------------|
| `postgres` | `postgres_dev_password_123` | Superuser |
| `sectorwars_app` | `sectorwars_app_password_123` | Application user |
| `sectorwars_readonly` | `sectorwars_readonly_password_123` | Read-only access |
| `sectorwars_backup` | `sectorwars_backup_password_123` | Backup operations |
| `sectorwars_monitor` | `sectorwars_monitor_password_123` | Monitoring access |

## Directory Structure

```
services/database/
├── Dockerfile                 # Database container definition
├── README.md                 # This file
├── backup.sh                 # Backup script
├── restore.sh                # Restore script
├── healthcheck.sh            # Health check script
├── config/                   # PostgreSQL configuration
│   ├── postgresql.conf       # Main PostgreSQL config
│   └── pg_hba.conf          # Client authentication
├── init/                     # Initialization scripts
│   ├── 01-init-database.sql  # Database and user creation
│   ├── 02-create-users.sql   # Additional users and security
│   └── 03-seed-data.sql      # Essential seed data
├── migrations/               # Database migrations (linked to gameserver/alembic)
└── backups/                  # Backup storage (Docker volume)
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_DB` | `sectorwars_dev` | Database name |
| `POSTGRES_USER` | `postgres` | Superuser name |
| `POSTGRES_PASSWORD` | `postgres_dev_password_123` | Superuser password |
| `DB_PASSWORD` | `postgres_dev_password_123` | Database password |

### PostgreSQL Configuration

The database uses optimized settings for development:
- **Memory**: 128MB shared_buffers, 4MB work_mem
- **Connections**: 100 max connections
- **Logging**: Connection logging enabled, query logging for slow queries (>1s)
- **Security**: SCRAM-SHA-256 password encryption
- **Performance**: Optimized for development workload

## Database Management

### Backup Operations

```bash
# Create backup
./services/database/backup.sh

# List available backups
./services/database/backup.sh list

# Clean up old backups
./services/database/backup.sh cleanup

# Test database connection
./services/database/backup.sh test
```

### Restore Operations

```bash
# Interactive restore (choose from available backups)
./services/database/restore.sh

# Restore specific backup
./services/database/restore.sh backup_20231215_120000.sql.gz

# Force restore without confirmation
./services/database/restore.sh -f backup_file.sql.gz

# List available backups
./services/database/restore.sh -l
```

### Schema Migrations

The database uses Alembic for schema migrations:

```bash
# Run migrations from gameserver
cd services/gameserver
alembic upgrade head

# Generate new migration
alembic revision --autogenerate -m "Description"

# Check current migration status
alembic current
```

## Security Features

### User Management
- **Application User**: Limited privileges for application operations
- **Read-only User**: For analytics and reporting
- **Backup User**: For automated backup operations
- **Monitor User**: For database monitoring tools

### Security Policies
- Row-level security preparation
- Audit logging for sensitive operations
- Password strength validation
- Secure password hashing (bcrypt)

### Network Security
- Database isolated within Docker network
- External access limited to development tools
- Client authentication via md5/scram-sha-256

## Monitoring and Health Checks

### Health Check

The database includes a comprehensive health check that verifies:
- Database connectivity
- Table accessibility
- Basic performance
- Essential table existence

```bash
# Manual health check
docker exec sectorwars-database /usr/local/bin/healthcheck.sh
```

### Database Statistics

```sql
-- Check database status
SELECT * FROM database_initialization_status;

-- View seed data statistics
SELECT * FROM get_seed_data_stats();

-- Check database version
SELECT * FROM get_database_version();
```

## Troubleshooting

### Common Issues

#### Database Won't Start
```bash
# Check container logs
docker logs sectorwars-database

# Check disk space
df -h

# Verify permissions
ls -la services/database/
```

#### Connection Refused
```bash
# Verify container is running
docker ps | grep database

# Check health status
docker inspect sectorwars-database | grep Health -A 10

# Test connectivity
pg_isready -h localhost -p 5433 -U postgres
```

#### Slow Performance
```bash
# Check database statistics
psql -h localhost -p 5433 -U postgres -d sectorwars_dev -c "
SELECT 
    schemaname,
    tablename,
    n_tup_ins,
    n_tup_upd,
    n_tup_del,
    n_live_tup,
    n_dead_tup
FROM pg_stat_user_tables;
"

# Run VACUUM if needed
psql -h localhost -p 5433 -U postgres -d sectorwars_dev -c "VACUUM ANALYZE;"
```

### Data Recovery

#### Restore from Backup
```bash
# List available backups
./services/database/restore.sh -l

# Restore latest backup
./services/database/restore.sh
```

#### Reset Database
```bash
# Stop database
docker-compose stop database

# Remove database volume (WARNING: Data loss!)
docker volume rm sectorwars2102_postgres_data

# Restart database (will reinitialize)
docker-compose up database
```

## Development Guidelines

### Making Schema Changes
1. Create Alembic migration in gameserver
2. Test migration on development database
3. Update seed data if needed
4. Document changes in migration message

### Adding Seed Data
1. Add data to `init/03-seed-data.sql`
2. Use `_pending_seed_data` table for new data
3. Update `apply_pending_seed_data()` function if needed
4. Test with fresh database initialization

### Database Testing
1. Always create backups before major changes
2. Use read-only user for analytics queries
3. Test with realistic data volumes
4. Validate performance impact of changes

## Production Considerations

When deploying to production:

1. **Security Hardening**
   - Change all default passwords
   - Restrict network access
   - Enable SSL/TLS connections
   - Use stronger authentication methods

2. **Performance Tuning**
   - Adjust memory settings for production load
   - Configure appropriate connection pooling
   - Set up monitoring and alerting
   - Plan for backup and disaster recovery

3. **Data Management**
   - Implement automated backup strategy
   - Set up log rotation and archiving
   - Plan for data retention policies
   - Configure high availability if needed

## Support

For issues with the database service:

1. Check container logs: `docker logs sectorwars-database`
2. Verify health status: Health check endpoint or manual script
3. Review PostgreSQL logs in container
4. Consult PostgreSQL documentation for configuration issues

---

*This database service is optimized for development. Production deployments require additional security and performance considerations.*