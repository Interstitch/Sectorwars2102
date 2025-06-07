#!/bin/bash
# Database backup script for SectorWars 2102
# Creates compressed backups with timestamp and retention management

set -e

# Configuration
DB_NAME="${POSTGRES_DB:-sectorwars_dev}"
DB_USER="${POSTGRES_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
BACKUP_DIR="${BACKUP_DIR:-/var/lib/postgresql/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/sectorwars_backup_${TIMESTAMP}.sql.gz"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" >&2
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Function to create backup directory
create_backup_dir() {
    if [ ! -d "$BACKUP_DIR" ]; then
        log "Creating backup directory: $BACKUP_DIR"
        mkdir -p "$BACKUP_DIR"
        chmod 750 "$BACKUP_DIR"
    fi
}

# Function to check disk space
check_disk_space() {
    local available_space
    available_space=$(df "$BACKUP_DIR" | awk 'NR==2 {print $4}')
    local required_space=1048576  # 1GB in KB
    
    if [ "$available_space" -lt "$required_space" ]; then
        error "Insufficient disk space. Available: ${available_space}KB, Required: ${required_space}KB"
        return 1
    fi
    
    log "Disk space check passed. Available: ${available_space}KB"
}

# Function to test database connectivity
test_connection() {
    log "Testing database connection..."
    
    if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t 10; then
        log "Database connection successful"
        return 0
    else
        error "Cannot connect to database"
        return 1
    fi
}

# Function to create database backup
create_backup() {
    log "Starting backup of database: $DB_NAME"
    log "Backup file: $BACKUP_FILE"
    
    # Create backup with compression
    if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        --verbose \
        --clean \
        --if-exists \
        --create \
        --format=plain \
        --no-owner \
        --no-privileges | gzip > "$BACKUP_FILE"; then
        
        local backup_size
        backup_size=$(du -h "$BACKUP_FILE" | cut -f1)
        log "Backup completed successfully. Size: $backup_size"
        
        # Create checksum
        md5sum "$BACKUP_FILE" > "${BACKUP_FILE}.md5"
        log "Checksum created: ${BACKUP_FILE}.md5"
        
        return 0
    else
        error "Backup failed"
        # Remove failed backup file if it exists
        [ -f "$BACKUP_FILE" ] && rm -f "$BACKUP_FILE"
        return 1
    fi
}

# Function to verify backup integrity
verify_backup() {
    log "Verifying backup integrity..."
    
    if [ ! -f "$BACKUP_FILE" ]; then
        error "Backup file not found: $BACKUP_FILE"
        return 1
    fi
    
    # Check if file is valid gzip
    if ! gzip -t "$BACKUP_FILE" 2>/dev/null; then
        error "Backup file is not a valid gzip archive"
        return 1
    fi
    
    # Verify checksum if it exists
    if [ -f "${BACKUP_FILE}.md5" ]; then
        if md5sum -c "${BACKUP_FILE}.md5" >/dev/null 2>&1; then
            log "Backup integrity verified successfully"
        else
            error "Backup checksum verification failed"
            return 1
        fi
    fi
    
    log "Backup verification completed"
    return 0
}

# Function to clean old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days..."
    
    local deleted_count=0
    
    # Find and delete old backup files
    find "$BACKUP_DIR" -name "sectorwars_backup_*.sql.gz" -mtime +$RETENTION_DAYS -type f | while read -r old_backup; do
        log "Deleting old backup: $(basename "$old_backup")"
        rm -f "$old_backup"
        rm -f "${old_backup}.md5"  # Also remove checksum file
        deleted_count=$((deleted_count + 1))
    done
    
    if [ $deleted_count -eq 0 ]; then
        log "No old backups to clean up"
    else
        log "Cleaned up $deleted_count old backup(s)"
    fi
}

# Function to list recent backups
list_backups() {
    log "Recent backups in $BACKUP_DIR:"
    
    if ls -la "$BACKUP_DIR"/sectorwars_backup_*.sql.gz 2>/dev/null; then
        echo
        log "Backup summary:"
        find "$BACKUP_DIR" -name "sectorwars_backup_*.sql.gz" -type f -printf "%TY-%Tm-%Td %TH:%TM  %s bytes  %f\n" | sort -r | head -10
    else
        warn "No backup files found"
    fi
}

# Function to send notification (placeholder for future integration)
send_notification() {
    local status=$1
    local message=$2
    
    # This is a placeholder for notification integration
    # Could be extended to send emails, Slack messages, etc.
    if [ "$status" = "success" ]; then
        log "NOTIFICATION: Backup completed successfully - $message"
    else
        error "NOTIFICATION: Backup failed - $message"
    fi
}

# Main backup function
run_backup() {
    local start_time
    start_time=$(date +%s)
    
    log "=== SectorWars 2102 Database Backup Started ==="
    
    # Pre-backup checks
    create_backup_dir || return 1
    check_disk_space || return 1
    test_connection || return 1
    
    # Perform backup
    if create_backup && verify_backup; then
        cleanup_old_backups
        
        local end_time
        end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        log "=== Backup completed successfully in ${duration} seconds ==="
        send_notification "success" "Backup completed in ${duration}s"
        list_backups
        return 0
    else
        local end_time
        end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        error "=== Backup failed after ${duration} seconds ==="
        send_notification "failure" "Backup failed after ${duration}s"
        return 1
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  backup    Create a new backup (default)"
    echo "  list      List recent backups"
    echo "  cleanup   Clean up old backups only"
    echo "  test      Test database connection"
    echo "  help      Show this help message"
    echo
    echo "Environment variables:"
    echo "  DB_NAME         Database name (default: sectorwars_dev)"
    echo "  DB_USER         Database user (default: postgres)"
    echo "  DB_HOST         Database host (default: localhost)"
    echo "  DB_PORT         Database port (default: 5432)"
    echo "  BACKUP_DIR      Backup directory (default: /var/lib/postgresql/backups)"
    echo "  RETENTION_DAYS  Backup retention in days (default: 7)"
}

# Main script logic
case "${1:-backup}" in
    backup)
        run_backup
        ;;
    list)
        list_backups
        ;;
    cleanup)
        create_backup_dir
        cleanup_old_backups
        ;;
    test)
        test_connection
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac