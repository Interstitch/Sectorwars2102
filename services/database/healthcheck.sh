#!/bin/bash
# Health check script for SectorWars 2102 PostgreSQL database
# This script verifies database connectivity and basic functionality

set -e

# Configuration
DB_NAME="${POSTGRES_DB:-sectorwars_dev}"
DB_USER="${POSTGRES_USER:-postgres}"
TIMEOUT=5

# Function to log messages
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [HEALTHCHECK] $1"
}

# Function to check if PostgreSQL is accepting connections
check_connection() {
    log "Checking PostgreSQL connection..."
    
    if pg_isready -h localhost -p 5432 -U "$DB_USER" -d "$DB_NAME" -t "$TIMEOUT"; then
        log "PostgreSQL is accepting connections"
        return 0
    else
        log "PostgreSQL is not accepting connections"
        return 1
    fi
}

# Function to check if database exists and is accessible
check_database() {
    log "Checking database accessibility..."
    
    if psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
        log "Database $DB_NAME is accessible"
        return 0
    else
        log "Database $DB_NAME is not accessible"
        return 1
    fi
}

# Function to check if essential tables exist
check_tables() {
    log "Checking essential tables..."
    
    # Check if the users table exists (should be created by alembic)
    if psql -h localhost -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT 1 FROM information_schema.tables WHERE table_name = 'users';" | grep -q 1; then
        log "Essential tables exist"
        return 0
    else
        log "Essential tables missing (database may be initializing)"
        return 1
    fi
}

# Function to check database performance
check_performance() {
    log "Checking database performance..."
    
    # Simple performance test - should complete in reasonable time
    start_time=$(date +%s%N)
    psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c "SELECT COUNT(*) FROM information_schema.tables;" > /dev/null 2>&1
    end_time=$(date +%s%N)
    
    duration=$(( (end_time - start_time) / 1000000 )) # Convert to milliseconds
    
    if [ $duration -lt 1000 ]; then # Less than 1 second
        log "Database performance is good (${duration}ms)"
        return 0
    else
        log "Database performance is slow (${duration}ms)"
        return 1
    fi
}

# Main health check function
main() {
    log "Starting health check for SectorWars 2102 database..."
    
    # Basic connectivity check
    if ! check_connection; then
        log "Health check FAILED: Connection check failed"
        exit 1
    fi
    
    # Database accessibility check
    if ! check_database; then
        log "Health check FAILED: Database accessibility check failed"
        exit 1
    fi
    
    # Table existence check (optional - may fail during initialization)
    if ! check_tables; then
        log "Health check WARNING: Essential tables check failed (may be initializing)"
        # Don't exit here as this is expected during first startup
    fi
    
    # Performance check
    if ! check_performance; then
        log "Health check WARNING: Performance check failed"
        # Don't exit here as this might be temporary
    fi
    
    log "Health check PASSED: Database is healthy"
    exit 0
}

# Trap signals and cleanup
trap 'log "Health check interrupted"; exit 1' INT TERM

# Run main function
main "$@"