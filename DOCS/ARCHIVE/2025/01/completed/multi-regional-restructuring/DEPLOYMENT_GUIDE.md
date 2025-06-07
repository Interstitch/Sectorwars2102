# Multi-Regional System Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Multi-Regional System in production environments. The deployment includes Central Nexus services, regional territory management, and the complete multi-container architecture.

## Prerequisites

### System Requirements

#### Hardware Specifications
- **Minimum**: 16 vCPU, 32GB RAM, 500GB SSD
- **Recommended**: 64 vCPU, 64GB RAM, 1TB NVMe SSD
- **Storage**: PostgreSQL requires ~10GB per 1000 active players
- **Network**: 1Gbps bandwidth, low latency (<50ms to major regions)

#### Software Dependencies
- **Docker**: Version 24.0+ with Compose V2
- **PostgreSQL**: Version 14+ with JSONB support
- **Redis**: Version 7.0+ for caching and sessions
- **Node.js**: Version 20+ for admin UI and services
- **Python**: Version 3.12+ for game server
- **Nginx**: Version 1.24+ for reverse proxy

### Environment Setup

#### 1. Install Docker and Docker Compose

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose V2
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

#### 2. Clone Repository

```bash
git clone https://github.com/your-org/sectorwars2102.git
cd sectorwars2102
```

#### 3. Environment Configuration

```bash
# Copy environment templates
cp .env.example .env
cp services/gameserver/.env.example services/gameserver/.env
cp services/admin-ui/.env.example services/admin-ui/.env

# Generate secure secrets
openssl rand -hex 32  # For JWT_SECRET
openssl rand -hex 16  # For DATABASE_PASSWORD
```

## Configuration

### Environment Variables

#### Main Configuration (`.env`)

```bash
# Environment
ENVIRONMENT=production
NODE_ENV=production

# Database Configuration
DATABASE_URL=postgresql://sectorwars_user:SECURE_PASSWORD@postgres:5432/sectorwars
DATABASE_TEST_URL=postgresql://sectorwars_user:SECURE_PASSWORD@postgres:5432/sectorwars_test
POSTGRES_USER=sectorwars_user
POSTGRES_PASSWORD=SECURE_PASSWORD_HERE
POSTGRES_DB=sectorwars

# Redis Configuration
REDIS_URL=redis://redis:6379/0
REDIS_PASSWORD=REDIS_PASSWORD_HERE

# Application Secrets
JWT_SECRET=YOUR_JWT_SECRET_HERE
ADMIN_USERNAME=admin
ADMIN_PASSWORD=SECURE_ADMIN_PASSWORD

# API Configuration
API_V1_STR=/api/v1
CORS_ORIGINS=["https://yourdomain.com","https://admin.yourdomain.com"]

# PayPal Integration
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
PAYPAL_WEBHOOK_ID=your_webhook_id
PAYPAL_MODE=live  # or 'sandbox' for testing

# Regional Configuration
DEFAULT_REGIONAL_SUBSCRIPTION_PRICE=25.00
GALACTIC_CITIZENSHIP_PRICE=5.00
MAX_REGIONS_PER_CLUSTER=50

# Central Nexus Configuration
NEXUS_GENERATION_TIMEOUT=1200  # 20 minutes
NEXUS_BACKUP_INTERVAL=3600     # 1 hour
DISTRICT_REGENERATION_TIMEOUT=300  # 5 minutes

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ADMIN_PASSWORD=GRAFANA_PASSWORD_HERE
MONITORING_RETENTION_DAYS=30

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_RETENTION_DAYS=7

# Performance Tuning
SQLALCHEMY_POOL_SIZE=20
SQLALCHEMY_MAX_OVERFLOW=30
UVICORN_WORKERS=4
GUNICORN_WORKERS=4
```

#### Game Server Configuration (`services/gameserver/.env`)

```bash
# Inherit from main .env
DATABASE_URL=${DATABASE_URL}
REDIS_URL=${REDIS_URL}
JWT_SECRET=${JWT_SECRET}

# Game Server Specific
UVICORN_HOST=0.0.0.0
UVICORN_PORT=8080
UVICORN_WORKERS=4
UVICORN_LOG_LEVEL=info

# Regional Features
ENABLE_REGIONAL_GOVERNANCE=true
ENABLE_CENTRAL_NEXUS=true
ENABLE_DIPLOMATIC_SYSTEM=true

# Performance
ASYNC_DB_POOL_SIZE=20
CACHE_TTL_SECONDS=300
BACKGROUND_TASK_WORKERS=2

# Security
BCRYPT_ROUNDS=12
RATE_LIMIT_PER_MINUTE=1000
MAX_REQUEST_SIZE=10MB
```

#### Admin UI Configuration (`services/admin-ui/.env`)

```bash
# API Endpoints
VITE_API_URL=https://api.yourdomain.com/api/v1
VITE_WS_URL=wss://api.yourdomain.com/ws

# Feature Flags
VITE_ENABLE_REGIONAL_GOVERNANCE=true
VITE_ENABLE_CENTRAL_NEXUS=true
VITE_ENABLE_REAL_TIME_UPDATES=true

# UI Configuration
VITE_APP_TITLE="SectorWars 2102 - Regional Administration"
VITE_DEFAULT_THEME=corporate
VITE_ENABLE_DARK_MODE=true

# Build Configuration
VITE_BUILD_VERSION=${GITHUB_SHA:-local}
VITE_BUILD_DATE=${BUILD_DATE:-$(date -u +%Y-%m-%dT%H:%M:%SZ)}
```

### Docker Compose Configuration

#### Production Deployment (`docker-compose.prod.yml`)

```yaml
version: '3.8'

services:
  # Nginx Gateway
  nginx:
    image: nginx:1.24-alpine
    container_name: sectorwars_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - nginx_cache:/var/cache/nginx
    depends_on:
      - gameserver
      - admin-ui
    networks:
      - frontend
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Game Server
  gameserver:
    build:
      context: ./services/gameserver
      dockerfile: Dockerfile
      target: production
    container_name: sectorwars_gameserver
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET=${JWT_SECRET}
    volumes:
      - gameserver_data:/app/data
      - gameserver_logs:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  # Admin UI
  admin-ui:
    build:
      context: ./services/admin-ui
      dockerfile: Dockerfile
      target: production
    container_name: sectorwars_admin_ui
    environment:
      - VITE_API_URL=https://api.yourdomain.com/api/v1
      - VITE_WS_URL=wss://api.yourdomain.com/ws
    networks:
      - frontend
    restart: unless-stopped

  # PostgreSQL Database
  postgres:
    image: postgres:14-alpine
    container_name: sectorwars_postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --lc-collate=C --lc-ctype=C"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d:ro
      - postgres_backups:/var/backups
    networks:
      - backend
    restart: unless-stopped
    command: |
      postgres 
      -c max_connections=200
      -c shared_buffers=256MB
      -c effective_cache_size=1GB
      -c maintenance_work_mem=64MB
      -c checkpoint_completion_target=0.9
      -c wal_buffers=16MB
      -c default_statistics_target=100
      -c random_page_cost=1.1
      -c effective_io_concurrency=200
      -c work_mem=4MB
      -c min_wal_size=1GB
      -c max_wal_size=4GB
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 30s
      timeout: 10s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: sectorwars_redis
    command: redis-server --requirepass ${REDIS_PASSWORD} --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    networks:
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Region Manager
  region-manager:
    build:
      context: ./services/region-manager
      dockerfile: Dockerfile
    container_name: sectorwars_region_manager
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - region_configs:/app/configs
    depends_on:
      - postgres
      - redis
    networks:
      - backend
      - management
    restart: unless-stopped

  # Monitoring Stack
  prometheus:
    image: prom/prometheus:latest
    container_name: sectorwars_prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
      - '--storage.tsdb.retention.time=30d'
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    networks:
      - monitoring
      - backend
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: sectorwars_grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources:ro
    networks:
      - monitoring
      - frontend
    restart: unless-stopped
    depends_on:
      - prometheus

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true
  management:
    driver: bridge
    internal: true
  monitoring:
    driver: bridge

volumes:
  postgres_data:
  postgres_backups:
  redis_data:
  gameserver_data:
  gameserver_logs:
  region_configs:
  prometheus_data:
  grafana_data:
  nginx_cache:
```

### Nginx Configuration

#### Main Configuration (`nginx/nginx.conf`)

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    
    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 10M;
    
    # Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
    limit_req_zone $binary_remote_addr zone=admin:10m rate=60r/m;
    
    # Upstream servers
    upstream gameserver {
        server gameserver:8080;
        keepalive 32;
    }
    
    upstream admin_ui {
        server admin-ui:3000;
        keepalive 16;
    }
    
    upstream grafana {
        server grafana:3000;
        keepalive 8;
    }
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # Main API Server
    server {
        listen 443 ssl http2;
        server_name api.yourdomain.com;
        
        ssl_certificate /etc/nginx/ssl/api.yourdomain.com.crt;
        ssl_certificate_key /etc/nginx/ssl/api.yourdomain.com.key;
        
        # API Endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://gameserver;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 5s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
            
            # Buffering
            proxy_buffering on;
            proxy_buffer_size 8k;
            proxy_buffers 16 8k;
        }
        
        # WebSocket Support
        location /ws {
            proxy_pass http://gameserver;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket timeouts
            proxy_read_timeout 3600s;
            proxy_send_timeout 3600s;
        }
        
        # Health check
        location /health {
            proxy_pass http://gameserver/api/v1/health;
            access_log off;
        }
    }
    
    # Admin UI Server
    server {
        listen 443 ssl http2;
        server_name admin.yourdomain.com;
        
        ssl_certificate /etc/nginx/ssl/admin.yourdomain.com.crt;
        ssl_certificate_key /etc/nginx/ssl/admin.yourdomain.com.key;
        
        # Admin Interface
        location / {
            limit_req zone=admin burst=10 nodelay;
            
            proxy_pass http://admin_ui;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Static file caching
            location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
                expires 1y;
                add_header Cache-Control "public, immutable";
            }
        }
    }
    
    # Monitoring Dashboard
    server {
        listen 443 ssl http2;
        server_name monitoring.yourdomain.com;
        
        ssl_certificate /etc/nginx/ssl/monitoring.yourdomain.com.crt;
        ssl_certificate_key /etc/nginx/ssl/monitoring.yourdomain.com.key;
        
        # Grafana Dashboard
        location / {
            auth_basic "Monitoring Dashboard";
            auth_basic_user_file /etc/nginx/.htpasswd;
            
            proxy_pass http://grafana;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    
    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name api.yourdomain.com admin.yourdomain.com monitoring.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }
}
```

## Deployment Process

### 1. Pre-Deployment Validation

```bash
# Validate configuration files
docker compose -f docker-compose.prod.yml config

# Check environment variables
docker compose -f docker-compose.prod.yml config | grep -E "(DATABASE_URL|JWT_SECRET|PAYPAL_)"

# Validate SSL certificates
openssl x509 -in nginx/ssl/api.yourdomain.com.crt -text -noout
openssl x509 -in nginx/ssl/admin.yourdomain.com.crt -text -noout

# Test database connectivity
docker run --rm postgres:14-alpine \
  psql "${DATABASE_URL}" -c "SELECT version();"
```

### 2. Database Migration

```bash
# Run database migrations
docker compose -f docker-compose.prod.yml run --rm gameserver \
  python -m alembic upgrade head

# Verify migration status
docker compose -f docker-compose.prod.yml run --rm gameserver \
  python -m alembic current

# Create admin user
docker compose -f docker-compose.prod.yml run --rm gameserver \
  python -c "from src.auth.admin import create_default_admin; create_default_admin()"
```

### 3. Initial Deployment

```bash
# Pull latest images
docker compose -f docker-compose.prod.yml pull

# Start infrastructure services
docker compose -f docker-compose.prod.yml up -d postgres redis

# Wait for database to be ready
docker compose -f docker-compose.prod.yml exec postgres \
  pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}

# Start application services
docker compose -f docker-compose.prod.yml up -d gameserver admin-ui

# Start reverse proxy
docker compose -f docker-compose.prod.yml up -d nginx

# Start monitoring
docker compose -f docker-compose.prod.yml up -d prometheus grafana

# Verify all services are running
docker compose -f docker-compose.prod.yml ps
```

### 4. Post-Deployment Verification

```bash
# Health checks
curl -f https://api.yourdomain.com/health
curl -f https://admin.yourdomain.com/
curl -f https://monitoring.yourdomain.com/api/health

# API functionality test
curl -X POST https://api.yourdomain.com/api/v1/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_admin_password"}'

# Central Nexus status
curl -H "Authorization: Bearer <token>" \
  https://api.yourdomain.com/api/v1/nexus/status

# Check logs for errors
docker compose -f docker-compose.prod.yml logs gameserver | grep -i error
docker compose -f docker-compose.prod.yml logs admin-ui | grep -i error
docker compose -f docker-compose.prod.yml logs nginx | grep -i error
```

## Monitoring & Observability

### Prometheus Metrics

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'gameserver'
    static_configs:
      - targets: ['gameserver:8080']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:9113']
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
    scrape_interval: 30s

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 30s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### Grafana Dashboards

Key dashboards to configure:

1. **System Overview**
   - CPU, Memory, Disk usage
   - Network I/O
   - Docker container status

2. **Application Metrics**
   - API response times
   - Request rates
   - Error rates
   - Active users

3. **Database Performance**
   - Connection pool usage
   - Query performance
   - Lock wait times
   - Cache hit ratios

4. **Regional System Metrics**
   - Active regions
   - Policy voting activity
   - Election participation
   - Inter-regional travel

5. **Central Nexus Metrics**
   - Generation status
   - District performance
   - Player distribution
   - Traffic patterns

### Log Management

```bash
# Centralized logging with Docker
docker compose -f docker-compose.prod.yml logs -f --tail=100

# Application-specific logs
docker compose -f docker-compose.prod.yml logs gameserver
docker compose -f docker-compose.prod.yml logs admin-ui
docker compose -f docker-compose.prod.yml logs nginx

# Log rotation configuration
# Add to docker-compose.prod.yml for each service:
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## Backup & Recovery

### Database Backup

```bash
#!/bin/bash
# scripts/backup-database.sh

BACKUP_DIR="/var/backups/sectorwars"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="sectorwars_backup_${TIMESTAMP}.sql"

# Create backup directory
mkdir -p ${BACKUP_DIR}

# Perform backup
docker compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U ${POSTGRES_USER} -d ${POSTGRES_DB} \
  --clean --if-exists --create > ${BACKUP_DIR}/${BACKUP_FILE}

# Compress backup
gzip ${BACKUP_DIR}/${BACKUP_FILE}

# Clean old backups (keep 30 days)
find ${BACKUP_DIR} -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

### Application Data Backup

```bash
#!/bin/bash
# scripts/backup-volumes.sh

BACKUP_DIR="/var/backups/sectorwars/volumes"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p ${BACKUP_DIR}

# Backup Docker volumes
docker run --rm \
  -v sectorwars_gameserver_data:/source:ro \
  -v ${BACKUP_DIR}:/backup \
  alpine tar czf /backup/gameserver_data_${TIMESTAMP}.tar.gz -C /source .

docker run --rm \
  -v sectorwars_region_configs:/source:ro \
  -v ${BACKUP_DIR}:/backup \
  alpine tar czf /backup/region_configs_${TIMESTAMP}.tar.gz -C /source .

echo "Volume backups completed"
```

### Disaster Recovery

```bash
#!/bin/bash
# scripts/restore-system.sh

BACKUP_DIR="/var/backups/sectorwars"
RESTORE_DATE=${1:-latest}

echo "Starting system restore for date: ${RESTORE_DATE}"

# Stop services
docker compose -f docker-compose.prod.yml down

# Restore database
BACKUP_FILE=$(ls -t ${BACKUP_DIR}/sectorwars_backup_*.sql.gz | head -1)
echo "Restoring database from: ${BACKUP_FILE}"

gunzip -c ${BACKUP_FILE} | \
  docker compose -f docker-compose.prod.yml exec -T postgres \
  psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}

# Restore volumes
docker run --rm \
  -v sectorwars_gameserver_data:/target \
  -v ${BACKUP_DIR}/volumes:/backup:ro \
  alpine tar xzf /backup/gameserver_data_${RESTORE_DATE}.tar.gz -C /target

# Start services
docker compose -f docker-compose.prod.yml up -d

echo "System restore completed"
```

## Security Hardening

### SSL/TLS Configuration

```bash
# Generate SSL certificates (using Let's Encrypt)
certbot certonly --standalone \
  -d api.yourdomain.com \
  -d admin.yourdomain.com \
  -d monitoring.yourdomain.com

# Copy certificates to nginx directory
cp /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem nginx/ssl/api.yourdomain.com.crt
cp /etc/letsencrypt/live/api.yourdomain.com/privkey.pem nginx/ssl/api.yourdomain.com.key

# Set proper permissions
chmod 644 nginx/ssl/*.crt
chmod 600 nginx/ssl/*.key
```

### Firewall Configuration

```bash
# UFW firewall rules
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw enable

# Fail2ban for intrusion prevention
apt-get install fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

### Docker Security

```bash
# Run containers as non-root users
# Add to Dockerfiles:
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup
USER appuser

# Enable Docker content trust
export DOCKER_CONTENT_TRUST=1

# Scan images for vulnerabilities
docker scout quickview
docker scout cves
```

## Performance Optimization

### Database Tuning

```sql
-- PostgreSQL configuration optimizations
-- Add to postgresql.conf

# Memory
shared_buffers = 512MB                 # 25% of RAM
effective_cache_size = 1536MB          # 75% of RAM
work_mem = 8MB                         # Per operation
maintenance_work_mem = 128MB

# Checkpoint
wal_buffers = 16MB
checkpoint_completion_target = 0.9
checkpoint_timeout = 15min

# Planner
random_page_cost = 1.1                 # For SSD
effective_io_concurrency = 200         # For SSD
default_statistics_target = 100

# Logging
log_min_duration_statement = 1000      # Log slow queries
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
```

### Application Tuning

```bash
# services/gameserver/.env production settings
UVICORN_WORKERS=4
SQLALCHEMY_POOL_SIZE=20
SQLALCHEMY_MAX_OVERFLOW=30
CACHE_TTL_SECONDS=300
BACKGROUND_TASK_WORKERS=2

# services/admin-ui/.env production settings
VITE_BUILD_OPTIMIZATION=true
VITE_BUNDLE_ANALYZER=false
VITE_SOURCEMAP=false
```

### Redis Optimization

```bash
# Redis configuration for caching
maxmemory 512mb
maxmemory-policy allkeys-lru
save ""  # Disable disk persistence for cache
tcp-keepalive 300
timeout 0
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues

```bash
# Check database status
docker compose -f docker-compose.prod.yml exec postgres pg_isready

# Check connection from gameserver
docker compose -f docker-compose.prod.yml exec gameserver \
  python -c "from src.core.database import engine; print(engine.execute('SELECT 1').scalar())"

# Check connection pool status
docker compose -f docker-compose.prod.yml exec gameserver \
  python -c "from src.core.database import engine; print(engine.pool.status())"
```

#### 2. High Memory Usage

```bash
# Check container memory usage
docker stats

# Check PostgreSQL memory usage
docker compose -f docker-compose.prod.yml exec postgres \
  psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} \
  -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"

# Optimize database connections
docker compose -f docker-compose.prod.yml exec postgres \
  psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} \
  -c "ALTER SYSTEM SET max_connections = '100';"
```

#### 3. API Performance Issues

```bash
# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s https://api.yourdomain.com/api/v1/health

# Check application logs
docker compose -f docker-compose.prod.yml logs gameserver | grep -E "(ERROR|WARN|slow)"

# Monitor active requests
docker compose -f docker-compose.prod.yml exec gameserver \
  ps aux | grep uvicorn
```

### Log Analysis

```bash
# Error analysis
docker compose -f docker-compose.prod.yml logs gameserver 2>&1 | \
  grep -E "(ERROR|Exception|Traceback)" | \
  tail -20

# Performance analysis
docker compose -f docker-compose.prod.yml logs nginx | \
  awk '$9 >= 400 {print $0}' | \
  tail -20

# API endpoint analysis
docker compose -f docker-compose.prod.yml logs nginx | \
  awk '{print $7}' | sort | uniq -c | sort -nr | head -10
```

## Maintenance

### Regular Maintenance Tasks

```bash
#!/bin/bash
# scripts/maintenance.sh

echo "Starting maintenance tasks..."

# Update system packages
apt-get update && apt-get upgrade -y

# Clean Docker resources
docker system prune -f
docker volume prune -f

# Backup database
./scripts/backup-database.sh

# Backup volumes
./scripts/backup-volumes.sh

# Analyze database performance
docker compose -f docker-compose.prod.yml exec postgres \
  psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "ANALYZE;"

# Update container images
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d

# Check SSL certificate expiration
openssl x509 -in nginx/ssl/api.yourdomain.com.crt -noout -dates

echo "Maintenance tasks completed"
```

### Health Monitoring

```bash
#!/bin/bash
# scripts/health-check.sh

ENDPOINTS=(
  "https://api.yourdomain.com/health"
  "https://admin.yourdomain.com/"
  "https://monitoring.yourdomain.com/api/health"
)

for endpoint in "${ENDPOINTS[@]}"; do
  if curl -f -s --max-time 10 "$endpoint" > /dev/null; then
    echo "✅ $endpoint - OK"
  else
    echo "❌ $endpoint - FAILED"
    # Send alert notification
    # curl -X POST "$SLACK_WEBHOOK" -d "{\"text\":\"Health check failed for $endpoint\"}"
  fi
done

# Check container health
docker compose -f docker-compose.prod.yml ps --format "table {{.Service}}\t{{.Status}}\t{{.Health}}"
```

---

**Deployment Guide Version:** 2.0.0  
**Last Updated:** June 1, 2025  
**Target Environment:** Production  
**Infrastructure:** Docker Compose with monitoring  