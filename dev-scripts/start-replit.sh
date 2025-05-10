#!/bin/bash

# Replit-specific startup script for non-Docker environments
echo "Starting Sector Wars 2102 in Replit (non-Docker mode)..."

# Environment setup
export ENVIRONMENT=replit
export NODE_ENV=development
export PYTHONUNBUFFERED=1

# Check if .env file exists, create from example if not
if [ ! -f .env ]; then
  echo "Creating .env file from example..."
  cp .env.example .env
  echo "Created .env file from example. Please review the settings."
fi

# Install Python dependencies for Game API Server
echo "Installing Python dependencies..."
cd /home/runner/Sectorwars2102/services/gameserver
pip install -r requirements.txt

# Set up Game API Server in background
echo "Starting Game API Server..."
cd /home/runner/Sectorwars2102/services/gameserver
uvicorn src.main:app --host 0.0.0.0 --port 5000 --reload &
GAME_SERVER_PID=$!

# Wait for Game API Server to start
echo "Waiting for Game API Server to start..."
sleep 5

# Install Node.js dependencies for both frontends if not already installed
echo "Installing Node.js dependencies for frontends..."
if [ ! -d "/home/runner/Sectorwars2102/services/player-client/node_modules" ]; then
  cd /home/runner/Sectorwars2102/services/player-client
  npm install
fi

if [ ! -d "/home/runner/Sectorwars2102/services/admin-ui/node_modules" ]; then
  cd /home/runner/Sectorwars2102/services/admin-ui
  npm install
fi

# Start Player Client (port 3000)
echo "Starting Player Client..."
cd /home/runner/Sectorwars2102/services/player-client
npm run dev -- --host 0.0.0.0 --port 3000 &
PLAYER_CLIENT_PID=$!

# Start Admin UI (port 3001)
echo "Starting Admin UI..."
cd /home/runner/Sectorwars2102/services/admin-ui
npm run dev -- --host 0.0.0.0 --port 3001 &
ADMIN_UI_PID=$!

# Display URLs for services
echo ""
echo "Services started successfully!"
echo "Game API Server: http://localhost:5000"
echo "Player Client: http://localhost:3000"
echo "Admin UI: http://localhost:3001"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for all processes to complete (or until user interrupts)
wait $GAME_SERVER_PID $PLAYER_CLIENT_PID $ADMIN_UI_PID

# Clean up on exit
trap "kill $GAME_SERVER_PID $PLAYER_CLIENT_PID $ADMIN_UI_PID 2>/dev/null" EXIT