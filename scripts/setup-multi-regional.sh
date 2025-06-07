#!/bin/bash

# Multi-Regional SectorWars Setup Script
# This script sets up the complete multi-regional platform infrastructure

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="${ENVIRONMENT:-production}"
DOMAIN="${DOMAIN:-sectorwars.local}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    
    # Check available disk space (minimum 50GB recommended)
    AVAILABLE_SPACE=$(df / | awk 'NR==2 {print $4}')
    REQUIRED_SPACE=$((50 * 1024 * 1024)) # 50GB in KB
    
    if [ "$AVAILABLE_SPACE" -lt "$REQUIRED_SPACE" ]; then
        log_warning "Less than 50GB available disk space. Multi-regional platform may need more space."
    fi
    
    # Check available memory (minimum 16GB recommended)
    AVAILABLE_MEMORY=$(free -m | awk 'NR==2{print $7}')
    REQUIRED_MEMORY=16384 # 16GB in MB
    
    if [ "$AVAILABLE_MEMORY" -lt "$REQUIRED_MEMORY" ]; then
        log_warning "Less than 16GB available memory. Performance may be affected."
    fi
    
    log_success "Prerequisites check completed"
}

# Create directory structure
create_directories() {
    log_info "Creating directory structure..."
    
    # Create data directories
    sudo mkdir -p /var/lib/sectorwars/{central-nexus,regions,monitoring,backups}
    sudo mkdir -p /var/lib/sectorwars/central-nexus/{database,redis,logs,assets}
    sudo mkdir -p /var/lib/sectorwars/monitoring/{prometheus,grafana,alertmanager}
    sudo mkdir -p /var/lib/sectorwars/backups/{central-nexus,regions}
    
    # Create log directories
    sudo mkdir -p /var/log/sectorwars/{central-nexus,region-manager,nginx}
    
    # Create SSL directory
    sudo mkdir -p /etc/sectorwars/ssl
    
    # Set appropriate permissions
    sudo chown -R $USER:$USER /var/lib/sectorwars
    sudo chown -R $USER:$USER /var/log/sectorwars
    sudo chown -R $USER:$USER /etc/sectorwars
    
    log_success "Directory structure created"
}

# Generate SSL certificates (self-signed for development)
generate_ssl_certificates() {
    log_info "Generating SSL certificates..."
    
    SSL_DIR="/etc/sectorwars/ssl"
    
    if [ ! -f "$SSL_DIR/cert.pem" ] || [ ! -f "$SSL_DIR/key.pem" ]; then
        # Generate self-signed certificate
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "$SSL_DIR/key.pem" \
            -out "$SSL_DIR/cert.pem" \
            -subj "/C=US/ST=State/L=City/O=SectorWars/CN=$DOMAIN"
        
        log_success "SSL certificates generated"
    else
        log_info "SSL certificates already exist"
    fi
}

# Setup environment files
setup_environment() {
    log_info "Setting up environment configuration..."
    
    ENV_FILE="$PROJECT_ROOT/.env.multi-regional"
    
    if [ ! -f "$ENV_FILE" ]; then
        cat > "$ENV_FILE" << EOF
# Multi-Regional SectorWars Environment Configuration

# Environment
ENVIRONMENT=$ENVIRONMENT
DOMAIN=$DOMAIN

# Database Configuration
NEXUS_DB_PASSWORD=$(openssl rand -base64 32)
REGION_DB_PASSWORD=$(openssl rand -base64 32)
DB_SUPERUSER_PASSWORD=$(openssl rand -base64 32)

# Redis Configuration
REDIS_PASSWORD=$(openssl rand -base64 32)

# JWT Configuration
JWT_SECRET=$(openssl rand -base64 64)

# PayPal Configuration (Set these with your actual PayPal credentials)
PAYPAL_CLIENT_ID=
PAYPAL_CLIENT_SECRET=
PAYPAL_GALACTIC_CITIZEN_PLAN_ID=
PAYPAL_REGIONAL_OWNER_PLAN_ID=
PAYPAL_NEXUS_PREMIUM_PLAN_ID=
PAYPAL_WEBHOOK_ID=

# Monitoring Configuration
GRAFANA_PASSWORD=$(openssl rand -base64 16)

# Regional Configuration
MAX_REGIONS_PER_USER=5
MAX_TOTAL_REGIONS=100
DEFAULT_CPU_CORES=2.0
DEFAULT_MEMORY_GB=4
DEFAULT_DISK_GB=20

# Auto-scaling Configuration
AUTO_SCALING_ENABLED=true
SCALE_UP_CPU_THRESHOLD=80.0
SCALE_UP_MEMORY_THRESHOLD=85.0
SCALE_DOWN_CPU_THRESHOLD=20.0
SCALE_DOWN_MEMORY_THRESHOLD=30.0

# Security
REGION_API_KEY=$(openssl rand -base64 32)
NEXUS_API_KEY=$(openssl rand -base64 32)
EOF

        log_success "Environment file created: $ENV_FILE"
        log_warning "Please update PayPal credentials in $ENV_FILE before starting services"
    else
        log_info "Environment file already exists: $ENV_FILE"
    fi
}

# Initialize databases
initialize_databases() {
    log_info "Initializing databases..."
    
    # Copy SQL initialization scripts
    cp "$PROJECT_ROOT/services/gameserver/sql/"*.sql /tmp/
    
    log_success "Database initialization scripts prepared"
}

# Setup monitoring configuration
setup_monitoring() {
    log_info "Setting up monitoring configuration..."
    
    # Copy monitoring configs to appropriate locations
    cp -r "$PROJECT_ROOT/monitoring/"* /var/lib/sectorwars/monitoring/
    
    # Create Grafana provisioning directories
    mkdir -p /var/lib/sectorwars/monitoring/grafana/{dashboards,datasources}
    
    # Create default Grafana datasource
    cat > /var/lib/sectorwars/monitoring/grafana/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF

    log_success "Monitoring configuration setup completed"
}

# Pull required Docker images
pull_images() {
    log_info "Pulling required Docker images..."
    
    docker pull postgres:15-alpine
    docker pull redis:7-alpine
    docker pull nginx:alpine
    docker pull prom/prometheus:latest
    docker pull grafana/grafana:latest
    docker pull python:3.11-slim
    
    log_success "Docker images pulled"
}

# Build custom images
build_images() {
    log_info "Building custom Docker images..."
    
    cd "$PROJECT_ROOT"
    
    # Build gameserver image
    log_info "Building gameserver image..."
    docker build -t sectorwars/gameserver:latest -f services/gameserver/Dockerfile services/gameserver/
    
    # Build region manager image
    log_info "Building region manager image..."
    docker build -t sectorwars/region-manager:latest -f services/region-manager/Dockerfile services/region-manager/
    
    # Build admin UI image
    log_info "Building admin UI image..."
    docker build -t sectorwars/admin-ui:latest -f services/admin-ui/Dockerfile services/admin-ui/
    
    # Build player client image
    log_info "Building player client image..."
    docker build -t sectorwars/player-client:latest -f services/player-client/Dockerfile services/player-client/
    
    log_success "Custom images built"
}

# Create Docker networks
create_networks() {
    log_info "Creating Docker networks..."
    
    # Create networks if they don't exist
    docker network create nexus-network --subnet=172.20.0.0/16 2>/dev/null || true
    docker network create regional-network --subnet=172.21.0.0/16 2>/dev/null || true
    
    log_success "Docker networks created"
}

# Start core services
start_core_services() {
    log_info "Starting core services..."
    
    cd "$PROJECT_ROOT"
    
    # Use the environment file
    export $(cat .env.multi-regional | grep -v '^#' | xargs)
    
    # Start core infrastructure
    docker-compose -f docker-compose.multi-regional.yml up -d \
        central-nexus-db \
        redis-nexus \
        prometheus \
        grafana
    
    log_info "Waiting for databases to be ready..."
    sleep 30
    
    # Start application services
    docker-compose -f docker-compose.multi-regional.yml up -d \
        central-nexus-server \
        region-manager \
        admin-ui \
        player-client \
        nginx-gateway
    
    log_success "Core services started"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    # Wait for central nexus server to be ready
    sleep 30
    
    # Run Alembic migrations
    docker-compose -f docker-compose.multi-regional.yml exec central-nexus-server \
        alembic upgrade head
    
    log_success "Database migrations completed"
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check service health
    SERVICES=(
        "central-nexus-db:5433"
        "redis-nexus:6379"
        "central-nexus-server:8080"
        "region-manager:8081"
        "nginx-gateway:80"
    )
    
    for service in "${SERVICES[@]}"; do
        IFS=':' read -r name port <<< "$service"
        if nc -z localhost "$port" 2>/dev/null; then
            log_success "$name is running"
        else
            log_error "$name is not responding on port $port"
        fi
    done
    
    # Test API endpoints
    log_info "Testing API endpoints..."
    
    if curl -s -f http://localhost/api/v1/status/health > /dev/null; then
        log_success "Central Nexus API is responding"
    else
        log_error "Central Nexus API is not responding"
    fi
    
    if curl -s -f http://localhost/admin > /dev/null; then
        log_success "Admin UI is accessible"
    else
        log_error "Admin UI is not accessible"
    fi
    
    log_success "Deployment verification completed"
}

# Display access information
display_access_info() {
    log_success "Multi-Regional SectorWars Platform Setup Complete!"
    
    echo
    echo "=== Access Information ==="
    echo "Player Client:    https://$DOMAIN/"
    echo "Admin UI:         https://$DOMAIN/admin/"
    echo "Central Nexus API: https://$DOMAIN/api/v1/"
    echo "Grafana:          http://localhost:3002/ (admin/$(grep GRAFANA_PASSWORD .env.multi-regional | cut -d'=' -f2))"
    echo "Prometheus:       http://localhost:9090/"
    echo
    echo "=== Next Steps ==="
    echo "1. Update PayPal credentials in .env.multi-regional"
    echo "2. Create your first region via the Admin UI"
    echo "3. Set up proper SSL certificates for production"
    echo "4. Configure domain DNS to point to this server"
    echo "5. Review monitoring dashboards in Grafana"
    echo
    echo "=== Useful Commands ==="
    echo "View logs:        docker-compose -f docker-compose.multi-regional.yml logs -f [service]"
    echo "Restart service:  docker-compose -f docker-compose.multi-regional.yml restart [service]"
    echo "Scale service:    docker-compose -f docker-compose.multi-regional.yml up -d --scale [service]=N"
    echo "Stop all:         docker-compose -f docker-compose.multi-regional.yml down"
    echo
}

# Main execution
main() {
    log_info "Starting Multi-Regional SectorWars Platform Setup"
    
    check_prerequisites
    create_directories
    generate_ssl_certificates
    setup_environment
    initialize_databases
    setup_monitoring
    pull_images
    build_images
    create_networks
    start_core_services
    run_migrations
    verify_deployment
    display_access_info
    
    log_success "Setup completed successfully!"
}

# Run main function
main "$@"