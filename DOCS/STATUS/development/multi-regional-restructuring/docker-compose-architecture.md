# Docker Compose Architecture for Multi-Regional Platform

*Created: June 1, 2025*  
*Status: SPECIFICATION*  
*Scope: Docker container orchestration for single-server deployment*

## 🏗️ Container Architecture Overview

The multi-regional platform runs entirely on Docker containers on a single 64 vCPU/64GB server, providing isolation between regions while maximizing resource efficiency.

## 🐳 Core Docker Compose Configuration

### Master Docker Compose Structure

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Reverse Proxy & Load Balancer
  nginx:
    image: nginx:alpine
    container_name: sectorwars_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx:/etc/nginx/conf.d
      - ./ssl:/etc/ssl/certs
      - ./assets:/var/www/html/static
    depends_on:
      - nexus-api
      - region-1-api
      - region-2-api
    restart: unless-stopped

  # Central Nexus Services
  nexus-api:
    build: ./services/gameserver
    container_name: sectorwars_nexus
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://nexus_user:nexus_pass@nexus-db:5432/nexus_db
      - REDIS_URL=redis://redis:6379/0
      - REGION_TYPE=nexus
    depends_on:
      - nexus-db
      - redis
    restart: unless-stopped

  nexus-db:
    image: postgres:15-alpine
    container_name: sectorwars_nexus_db
    ports:
      - "5435:5432"
    environment:
      - POSTGRES_DB=nexus_db
      - POSTGRES_USER=nexus_user
      - POSTGRES_PASSWORD=nexus_pass
    volumes:
      - nexus_db_data:/var/lib/postgresql/data
      - ./database/nexus-init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

  # Region 1 (Default Galaxy)
  region-1-api:
    build: ./services/gameserver
    container_name: sectorwars_region_1
    ports:
      - "8001:8000"
    environment:
      - DATABASE_URL=postgresql://region1_user:region1_pass@region-1-db:5432/region1_db
      - REDIS_URL=redis://redis:6379/1
      - REGION_ID=default-region-uuid
      - REGION_TYPE=default
    depends_on:
      - region-1-db
      - redis
    restart: unless-stopped

  region-1-db:
    image: postgres:15-alpine
    container_name: sectorwars_region_1_db
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=region1_db
      - POSTGRES_USER=region1_user
      - POSTGRES_PASSWORD=region1_pass
    volumes:
      - region1_db_data:/var/lib/postgresql/data
      - ./database/region-init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

  # Shared Services
  redis:
    image: redis:7-alpine
    container_name: sectorwars_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --maxmemory 8gb --maxmemory-policy allkeys-lru
    restart: unless-stopped

  # Admin UI
  admin-ui:
    build: ./services/admin-ui
    container_name: sectorwars_admin
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost/api
    restart: unless-stopped

  # Player UI
  player-ui:
    build: ./services/player-client
    container_name: sectorwars_player
    ports:
      - "3001:3000"
    environment:
      - REACT_APP_API_URL=http://localhost/api
    restart: unless-stopped

  # PayPal Integration Service
  paypal-service:
    build: ./services/paypal-service
    container_name: sectorwars_paypal
    ports:
      - "8080:8080"
    environment:
      - PAYPAL_CLIENT_ID=${PAYPAL_CLIENT_ID}
      - PAYPAL_CLIENT_SECRET=${PAYPAL_CLIENT_SECRET}
      - PAYPAL_ENVIRONMENT=sandbox  # Change to live for production
    restart: unless-stopped

volumes:
  nexus_db_data:
    driver: local
  region1_db_data:
    driver: local
  redis_data:
    driver: local

networks:
  default:
    driver: bridge
```

## 🚀 Dynamic Region Creation

### Region Container Generator

```bash
#!/bin/bash
# scripts/create-region.sh

REGION_ID=$1
REGION_NAME=$2
DB_PORT=$((5436 + REGION_ID))
API_PORT=$((8001 + REGION_ID))

cat > docker-compose.region-${REGION_ID}.yml << EOF
version: '3.8'

services:
  region-${REGION_ID}-api:
    build: ./services/gameserver
    container_name: sectorwars_region_${REGION_ID}
    ports:
      - "${API_PORT}:8000"
    environment:
      - DATABASE_URL=postgresql://region${REGION_ID}_user:region${REGION_ID}_pass@region-${REGION_ID}-db:5432/region${REGION_ID}_db
      - REDIS_URL=redis://redis:6379/${REGION_ID}
      - REGION_ID=${REGION_ID}
      - REGION_NAME=${REGION_NAME}
      - REGION_TYPE=player_owned
    depends_on:
      - region-${REGION_ID}-db
    restart: unless-stopped
    networks:
      - default

  region-${REGION_ID}-db:
    image: postgres:15-alpine
    container_name: sectorwars_region_${REGION_ID}_db
    ports:
      - "${DB_PORT}:5432"
    environment:
      - POSTGRES_DB=region${REGION_ID}_db
      - POSTGRES_USER=region${REGION_ID}_user
      - POSTGRES_PASSWORD=region${REGION_ID}_pass
    volumes:
      - region${REGION_ID}_db_data:/var/lib/postgresql/data
      - ./database/region-init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped
    networks:
      - default

volumes:
  region${REGION_ID}_db_data:
    driver: local

networks:
  default:
    external:
      name: sectorwars_default
EOF

# Start the new region
docker-compose -f docker-compose.region-${REGION_ID}.yml up -d

# Update nginx configuration
./scripts/update-nginx-config.sh ${REGION_ID} ${API_PORT}

# Reload nginx
docker exec sectorwars_nginx nginx -s reload

echo "Region ${REGION_ID} (${REGION_NAME}) created successfully!"
echo "API available at: http://localhost:${API_PORT}"
echo "Database available at: localhost:${DB_PORT}"
```

## 📊 Resource Allocation Strategy

### Container Resource Limits

```yaml
# Resource limits for 64GB/64 vCPU server
services:
  nexus-api:
    deploy:
      resources:
        limits:
          cpus: '8'
          memory: 8G
        reservations:
          cpus: '4'
          memory: 4G

  nexus-db:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 16G
        reservations:
          cpus: '2'
          memory: 8G

  region-x-api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  region-x-db:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G

  redis:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G

  nginx:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '1'
          memory: 512M
```

### Scaling Calculation

```
Maximum Regions (Conservative):
- Available after core services: 40 vCPU, 32GB RAM
- Per region requirement: 4 vCPU, 6GB RAM
- Maximum regions: 5-6 active regions

Maximum Regions (Optimized):
- Per region requirement: 2 vCPU, 3GB RAM  
- Maximum regions: 10-12 active regions
```

## 🔧 Nginx Configuration

### Dynamic Region Routing

```nginx
# config/nginx/default.conf
upstream nexus_backend {
    server nexus-api:8000;
}

# Dynamic upstream generation
upstream region_1_backend {
    server region-1-api:8000;
}

# Main server block
server {
    listen 80;
    listen 443 ssl http2;
    server_name localhost;

    ssl_certificate /etc/ssl/certs/server.crt;
    ssl_certificate_key /etc/ssl/private/server.key;

    # Static assets
    location /static/ {
        root /var/www/html;
        expires 1y;
        add_header Cache-Control "public, immutable";
        gzip_static on;
    }

    # Central Nexus API
    location /api/nexus/ {
        proxy_pass http://nexus_backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Regional API routing
    location ~ ^/api/regions/([a-f0-9-]+)/ {
        set $region_id $1;
        
        # Route to appropriate region container
        # This requires dynamic configuration update
        proxy_pass http://region_${region_id}_backend$request_uri;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Region-ID $region_id;
    }

    # Default region (legacy compatibility)
    location /api/ {
        proxy_pass http://region_1_backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Admin UI
    location /admin/ {
        proxy_pass http://admin-ui:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Player UI (default)
    location / {
        proxy_pass http://player-ui:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 💾 Database Backup Strategy

### Automated Backup System

```bash
#!/bin/bash
# scripts/backup-all-regions.sh

BACKUP_DIR="/opt/backups/$(date +%Y-%m-%d)"
mkdir -p $BACKUP_DIR

# Backup Nexus database
docker exec sectorwars_nexus_db pg_dump -U nexus_user nexus_db | gzip > $BACKUP_DIR/nexus_db.sql.gz

# Backup all regional databases
for container in $(docker ps --format "table {{.Names}}" | grep "sectorwars_region_.*_db"); do
    region_id=$(echo $container | sed 's/sectorwars_region_\(.*\)_db/\1/')
    docker exec $container pg_dump -U region${region_id}_user region${region_id}_db | gzip > $BACKUP_DIR/region_${region_id}_db.sql.gz
done

# Backup Redis data
docker exec sectorwars_redis redis-cli BGSAVE
docker cp sectorwars_redis:/data/dump.rdb $BACKUP_DIR/redis_dump.rdb

# Clean up old backups (keep 30 days)
find /opt/backups -type d -mtime +30 -exec rm -rf {} +

echo "Backup completed: $BACKUP_DIR"
```

## 📈 Monitoring & Health Checks

### Docker Health Checks

```yaml
# Health check configuration
services:
  nexus-api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  nexus-db:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U nexus_user -d nexus_db"]
      interval: 30s
      timeout: 5s
      retries: 3

  redis:
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 3s
      retries: 3
```

### System Monitoring

```bash
#!/bin/bash
# scripts/monitor-system.sh

echo "=== Docker Container Status ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "=== Resource Usage ==="
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo ""
echo "=== Database Connections ==="
for db in nexus region_1; do
    echo "$db database connections:"
    docker exec sectorwars_${db}_db psql -U ${db}_user -d ${db}_db -c "SELECT count(*) FROM pg_stat_activity;" 2>/dev/null || echo "  Connection failed"
done

echo ""
echo "=== Disk Usage ==="
df -h /var/lib/docker
docker system df
```

## 🔄 Deployment Scripts

### Complete System Startup

```bash
#!/bin/bash
# scripts/start-all.sh

echo "Starting SectorWars Multi-Regional Platform..."

# Start core services
docker-compose up -d nginx redis nexus-api nexus-db

# Wait for core services
echo "Waiting for core services..."
sleep 30

# Start default region
docker-compose up -d region-1-api region-1-db

# Start UI services  
docker-compose up -d admin-ui player-ui paypal-service

# Start any additional regions
for region_file in docker-compose.region-*.yml; do
    if [ -f "$region_file" ]; then
        echo "Starting $(basename $region_file)..."
        docker-compose -f $region_file up -d
    fi
done

echo "All services started!"
echo "Access points:"
echo "  Player UI: http://localhost"
echo "  Admin UI: http://localhost/admin"
echo "  Nexus API: http://localhost:8000"
echo "  Region 1 API: http://localhost:8001"
```

---

*This Docker architecture provides a scalable, maintainable foundation for the multi-regional platform on a single powerful server.*