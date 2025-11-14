#!/bin/bash
# Startup Health Check Script for Sectorwars2102
# Run this script after Codespace boot to verify all services are healthy

set -e

echo "🏔️ Sectorwars2102 Startup Health Check"
echo "======================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SERVICES=(
    "gameserver"
    "player-client"
    "admin-ui"
    "database"
    "redis-cache"
    "nginx-gateway"
)

FAILED_SERVICES=()
UNHEALTHY_SERVICES=()

# Function to check if a service is running and healthy
check_service() {
    local service=$1
    local status=$(docker-compose ps | grep "$service" | awk '{for(i=4;i<=NF;i++) printf "%s ", $i; print ""}' | sed 's/ *$//')

    if [[ -z "$status" ]]; then
        echo -e "${RED}✗${NC} ${service}: Not running"
        FAILED_SERVICES+=("$service")
        return 1
    elif [[ "$status" == *"unhealthy"* ]]; then
        echo -e "${YELLOW}⚠${NC} ${service}: Running but unhealthy"
        UNHEALTHY_SERVICES+=("$service")
        return 2
    elif [[ "$status" == *"Up"* ]] && [[ "$status" == *"healthy"* || "$status" != *"health"* ]]; then
        echo -e "${GREEN}✓${NC} ${service}: Healthy"
        return 0
    else
        echo -e "${RED}✗${NC} ${service}: Unknown status: $status"
        FAILED_SERVICES+=("$service")
        return 1
    fi
}

# Check all services
echo "Checking service health..."
echo ""

for service in "${SERVICES[@]}"; do
    check_service "$service"
done

echo ""
echo "======================================="
echo ""

# Check API endpoints
echo "Checking API endpoints..."
echo ""

# Health endpoint
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/api/v1/status/health 2>/dev/null || echo "000")
if [ "$HEALTH_CHECK" == "200" ]; then
    echo -e "${GREEN}✓${NC} Gameserver health endpoint: OK"
else
    echo -e "${RED}✗${NC} Gameserver health endpoint: Failed (HTTP $HEALTH_CHECK)"
    FAILED_SERVICES+=("gameserver-api")
fi

# Database status
DB_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/api/v1/status/database 2>/dev/null || echo "000")
if [ "$DB_CHECK" == "200" ]; then
    echo -e "${GREEN}✓${NC} Database connection: OK"
else
    echo -e "${RED}✗${NC} Database connection: Failed (HTTP $DB_CHECK)"
    FAILED_SERVICES+=("database-connection")
fi

# Admin UI accessibility
ADMIN_UI_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3001 2>/dev/null || echo "000")
if [ "$ADMIN_UI_CHECK" == "200" ]; then
    echo -e "${GREEN}✓${NC} Admin UI: Accessible"
else
    echo -e "${YELLOW}⚠${NC} Admin UI: Not accessible (HTTP $ADMIN_UI_CHECK)"
fi

# Player Client accessibility
PLAYER_CLIENT_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "000")
if [ "$PLAYER_CLIENT_CHECK" == "200" ]; then
    echo -e "${GREEN}✓${NC} Player Client: Accessible"
else
    echo -e "${YELLOW}⚠${NC} Player Client: Not accessible (HTTP $PLAYER_CLIENT_CHECK)"
fi

echo ""
echo "======================================="
echo ""

# Summary
if [ ${#FAILED_SERVICES[@]} -eq 0 ] && [ ${#UNHEALTHY_SERVICES[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ All systems operational!${NC}"
    echo ""
    echo "Admin Panel: http://localhost:3001"
    echo "Player Client: http://localhost:3000"
    echo "API Docs: http://localhost:8080/docs"
    exit 0
elif [ ${#FAILED_SERVICES[@]} -gt 0 ]; then
    echo -e "${RED}✗ Critical failures detected!${NC}"
    echo ""
    echo "Failed services:"
    for service in "${FAILED_SERVICES[@]}"; do
        echo "  - $service"
    done
    echo ""
    echo "Recommended action: Check logs with 'docker-compose logs <service>'"
    exit 1
else
    echo -e "${YELLOW}⚠ Some services are unhealthy${NC}"
    echo ""
    echo "Unhealthy services:"
    for service in "${UNHEALTHY_SERVICES[@]}"; do
        echo "  - $service"
    done
    echo ""
    echo "These services may need to be restarted:"
    echo "  docker-compose restart <service>"
    echo ""
    echo "Or check logs:"
    echo "  docker-compose logs <service>"
    exit 2
fi
