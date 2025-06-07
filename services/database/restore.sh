#!/bin/bash
# Database restore script for SectorWars 2102
# Restores database from compressed backup files with safety checks

set -e

# Configuration
DB_NAME="${POSTGRES_DB:-sectorwars_dev}"
DB_USER="${POSTGRES_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
BACKUP_DIR="${BACKUP_DIR:-/var/lib/postgresql/backups}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
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

# Function to list available backups
list_available_backups() {
    log "Available backups in $BACKUP_DIR:"
    
    if ls -la "$BACKUP_DIR"/sectorwars_backup_*.sql.gz 2>/dev/null | head -20; then
        echo
        info "Backup details:"
        find "$BACKUP_DIR" -name "sectorwars_backup_*.sql.gz" -type f -printf "%TY-%Tm-%Td %TH:%TM  %s bytes  %f\n" | sort -r | head -10
        return 0
    else
        error "No backup files found in $BACKUP_DIR"
        return 1
    fi
}

# Function to select backup file
select_backup_file() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        # Interactive mode - show available backups and let user choose
        echo
        log "No backup file specified. Available backups:"
        
        local backup_files=()
        while IFS= read -r -d '' file; do
            backup_files+=("$file")
        done < <(find "$BACKUP_DIR" -name "sectorwars_backup_*.sql.gz" -type f -print0 | sort -z -r)
        
        if [ ${#backup_files[@]} -eq 0 ]; then
            error "No backup files found"
            return 1
        fi
        
        echo
        for i in "${!backup_files[@]}"; do
            local file="${backup_files[$i]}"
            local basename_file=$(basename "$file")
            local file_size=$(du -h "$file" | cut -f1)
            local file_date=$(stat -c %y "$file" | cut -d' ' -f1-2 | cut -d'.' -f1)
            echo "  $((i+1)). $basename_file ($file_size, $file_date)"
        done
        
        echo
        read -p "Select backup file (1-${#backup_files[@]}): " selection
        
        if [[ "$selection" =~ ^[0-9]+$ ]] && [ "$selection" -ge 1 ] && [ "$selection" -le ${#backup_files[@]} ]; then
            backup_file="${backup_files[$((selection-1))]}"
        else
            error "Invalid selection"
            return 1
        fi
    else
        # Check if specified file exists
        if [ ! -f "$backup_file" ]; then
            # Try to find it in backup directory
            local full_path="$BACKUP_DIR/$backup_file"
            if [ -f "$full_path" ]; then
                backup_file="$full_path"
            else
                error "Backup file not found: $backup_file"
                return 1
            fi
        fi
    fi
    
    echo "$backup_file"
}

# Function to verify backup file integrity
verify_backup_file() {
    local backup_file="$1"
    
    log "Verifying backup file: $(basename "$backup_file")"
    
    # Check if file exists
    if [ ! -f "$backup_file" ]; then
        error "Backup file not found: $backup_file"
        return 1
    fi
    
    # Check if file is readable
    if [ ! -r "$backup_file" ]; then
        error "Backup file is not readable: $backup_file"
        return 1
    fi
    
    # Check if file is valid gzip
    if ! gzip -t "$backup_file" 2>/dev/null; then
        error "Backup file is not a valid gzip archive: $backup_file"
        return 1
    fi
    
    # Verify checksum if it exists
    local checksum_file="${backup_file}.md5"
    if [ -f "$checksum_file" ]; then
        log "Verifying checksum..."
        if md5sum -c "$checksum_file" >/dev/null 2>&1; then
            log "Checksum verification passed"
        else
            error "Checksum verification failed"
            return 1
        fi
    else
        warn "No checksum file found, skipping checksum verification"
    fi
    
    # Check file size (basic sanity check)
    local file_size
    file_size=$(stat -c%s "$backup_file")
    if [ "$file_size" -lt 1024 ]; then  # Less than 1KB
        error "Backup file seems too small (${file_size} bytes)"
        return 1
    fi
    
    log "Backup file verification completed successfully"
    return 0
}

# Function to create pre-restore backup
create_pre_restore_backup() {
    log "Creating pre-restore backup of current database..."
    
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local pre_restore_file="${BACKUP_DIR}/pre_restore_backup_${timestamp}.sql.gz"
    
    # Create backup directory if it doesn't exist
    mkdir -p "$BACKUP_DIR"
    
    # Create pre-restore backup
    if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        --verbose \
        --clean \
        --if-exists \
        --create \
        --format=plain \
        --no-owner \
        --no-privileges | gzip > "$pre_restore_file"; then
        
        local backup_size
        backup_size=$(du -h "$pre_restore_file" | cut -f1)
        log "Pre-restore backup created: $(basename "$pre_restore_file") ($backup_size)"
        
        # Create checksum
        md5sum "$pre_restore_file" > "${pre_restore_file}.md5"
        
        echo "$pre_restore_file"
        return 0
    else
        error "Failed to create pre-restore backup"
        return 1
    fi
}

# Function to confirm restore operation
confirm_restore() {
    local backup_file="$1"
    local force="$2"
    
    if [ "$force" = "true" ]; then
        return 0
    fi
    
    echo
    warn "=== DATABASE RESTORE WARNING ==="
    warn "This operation will COMPLETELY REPLACE the current database content!"
    warn "Database: $DB_NAME"
    warn "Backup file: $(basename "$backup_file")"
    warn "Backup size: $(du -h "$backup_file" | cut -f1)"
    warn "Backup date: $(stat -c %y "$backup_file" | cut -d'.' -f1)"
    echo
    
    read -p "Are you sure you want to proceed? (type 'yes' to confirm): " confirmation
    
    if [ "$confirmation" = "yes" ]; then
        return 0
    else
        log "Restore operation cancelled by user"
        return 1
    fi
}

# Function to restore database
restore_database() {
    local backup_file="$1"
    local skip_pre_backup="$2"
    
    log "Starting database restore..."
    log "Source: $(basename "$backup_file")"
    log "Target: $DB_NAME on $DB_HOST:$DB_PORT"
    
    # Create pre-restore backup unless skipped
    local pre_restore_file=""
    if [ "$skip_pre_backup" != "true" ]; then
        if ! pre_restore_file=$(create_pre_restore_backup); then
            error "Failed to create pre-restore backup. Aborting restore."
            return 1
        fi
    fi
    
    # Perform the restore
    log "Restoring database from backup..."
    if gunzip -c "$backup_file" | psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -v ON_ERROR_STOP=1; then
        log "Database restore completed successfully"
        
        # Verify the restore by checking if we can connect to the restored database
        if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t 5; then
            log "Restored database is accessible"
            
            # Display some basic statistics
            local table_count
            table_count=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null || echo "Unknown")
            log "Tables in restored database: $table_count"
            
            return 0
        else
            error "Restored database is not accessible"
            return 1
        fi
    else
        error "Database restore failed"
        
        # Offer to restore from pre-restore backup
        if [ -n "$pre_restore_file" ] && [ -f "$pre_restore_file" ]; then
            echo
            read -p "Restore failed. Do you want to restore from pre-restore backup? (y/n): " restore_pre
            if [ "$restore_pre" = "y" ] || [ "$restore_pre" = "Y" ]; then
                log "Restoring from pre-restore backup..."
                if gunzip -c "$pre_restore_file" | psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -v ON_ERROR_STOP=1; then
                    log "Successfully restored from pre-restore backup"
                else
                    error "Failed to restore from pre-restore backup"
                fi
            fi
        fi
        
        return 1
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [BACKUP_FILE]"
    echo
    echo "Restore SectorWars 2102 database from backup file"
    echo
    echo "Options:"
    echo "  -f, --force           Skip confirmation prompts"
    echo "  -l, --list            List available backup files"
    echo "  -s, --skip-backup     Skip creating pre-restore backup"
    echo "  -t, --test            Test database connection only"
    echo "  -h, --help            Show this help message"
    echo
    echo "Arguments:"
    echo "  BACKUP_FILE           Path to backup file (optional, interactive if not provided)"
    echo
    echo "Environment variables:"
    echo "  DB_NAME         Database name (default: sectorwars_dev)"
    echo "  DB_USER         Database user (default: postgres)"
    echo "  DB_HOST         Database host (default: localhost)"
    echo "  DB_PORT         Database port (default: 5432)"
    echo "  BACKUP_DIR      Backup directory (default: /var/lib/postgresql/backups)"
    echo
    echo "Examples:"
    echo "  $0                                    # Interactive restore"
    echo "  $0 backup_20231215_120000.sql.gz     # Restore specific file"
    echo "  $0 -f -s latest_backup.sql.gz        # Force restore without pre-backup"
    echo "  $0 -l                                 # List available backups"
}

# Main script logic
main() {
    local backup_file=""
    local force=false
    local skip_pre_backup=false
    local list_only=false
    local test_only=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -f|--force)
                force=true
                shift
                ;;
            -l|--list)
                list_only=true
                shift
                ;;
            -s|--skip-backup)
                skip_pre_backup=true
                shift
                ;;
            -t|--test)
                test_only=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            -*)
                error "Unknown option: $1"
                show_usage
                exit 1
                ;;
            *)
                backup_file="$1"
                shift
                ;;
        esac
    done
    
    # Handle different modes
    if [ "$list_only" = true ]; then
        list_available_backups
        return $?
    fi
    
    if [ "$test_only" = true ]; then
        test_connection
        return $?
    fi
    
    # Start restore process
    log "=== SectorWars 2102 Database Restore Started ==="
    
    # Test connection first
    if ! test_connection; then
        error "Cannot connect to database. Restore aborted."
        return 1
    fi
    
    # Select backup file
    if ! backup_file=$(select_backup_file "$backup_file"); then
        error "No valid backup file selected"
        return 1
    fi
    
    # Verify backup file
    if ! verify_backup_file "$backup_file"; then
        error "Backup file verification failed"
        return 1
    fi
    
    # Confirm restore operation
    if ! confirm_restore "$backup_file" "$force"; then
        log "Restore operation cancelled"
        return 1
    fi
    
    # Perform restore
    local start_time
    start_time=$(date +%s)
    
    if restore_database "$backup_file" "$skip_pre_backup"; then
        local end_time
        end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        log "=== Database restore completed successfully in ${duration} seconds ==="
        return 0
    else
        local end_time
        end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        error "=== Database restore failed after ${duration} seconds ==="
        return 1
    fi
}

# Run main function with all arguments
main "$@"