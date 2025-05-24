#!/bin/bash

echo "Restarting Docker services with updated configuration..."

# Stop and remove all containers
docker-compose down

# Start the services again
docker-compose up -d

echo "Services restarted. Player client should be available at: http://localhost:3000"
echo "New test pages available at:"
echo "- http://localhost:3000/proxy-test.html - Simple proxy test"
echo "- http://localhost:3000/browser-test.html - Comprehensive test dashboard"
echo ""
echo "To view logs, run: docker-compose logs -f player-client"