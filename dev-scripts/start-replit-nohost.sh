#!/bin/bash

# This script starts all services with host checking completely disabled
# Use this as a last resort when regular start-replit.sh has host blocking issues

echo "Starting Sector Wars 2102 in Replit with host checking disabled..."

# Run gameserver in background
cd /home/runner/Sectorwars2102/services/gameserver
chmod +x simple_server.py
./simple_server.py > /tmp/gameserver.log 2>&1 &
GAMESERVER_PID=$!
echo "Game API Server (port 8080) started with PID: $GAMESERVER_PID"

# Run player-client with host checking disabled
cd /home/runner/Sectorwars2102/services/player-client
node disable-host-check.js > /tmp/player-client.log 2>&1 &
PLAYER_CLIENT_PID=$!
echo "Player Client (port 3000) started with PID: $PLAYER_CLIENT_PID"

# Run admin-ui with host checking disabled
cd /home/runner/Sectorwars2102/services/admin-ui
node disable-host-check.js > /tmp/admin-ui.log 2>&1 &
ADMIN_UI_PID=$!
echo "Admin UI (port 3001) started with PID: $ADMIN_UI_PID"

# Save PIDs for cleanup
echo "$GAMESERVER_PID $PLAYER_CLIENT_PID $ADMIN_UI_PID" > /tmp/sectorwars-pids.txt

# Display access information
echo ""
echo "Services started in background with host checking disabled:"
echo "Game API Server: http://localhost:8080 (logs: /tmp/gameserver.log)"
echo "Player Client: http://localhost:3000 (logs: /tmp/player-client.log)"
echo "Admin UI: http://localhost:3001 (logs: /tmp/admin-ui.log)"
echo ""
echo "Use 'tail -f /tmp/gameserver.log' to view the game server logs"

# Register cleanup handler
cleanup_direct() {
  echo "Stopping services..."
  if [ -f /tmp/sectorwars-pids.txt ]; then
    cat /tmp/sectorwars-pids.txt | xargs kill -15 2>/dev/null || true
    rm /tmp/sectorwars-pids.txt
  fi
  echo "Services stopped"
  exit 0
}

trap cleanup_direct INT TERM

# Keep script alive
echo "Press Ctrl+C to stop all services"
tail -f /dev/null