#!/bin/bash

# Replit-specific startup script for non-Docker environments
echo "Starting Sector Wars 2102 in Replit (non-Docker mode)..."

# Environment setup
export ENVIRONMENT=replit
export NODE_ENV=development
export PYTHONUNBUFFERED=1

# Create data directories if they don't exist
mkdir -p /tmp/sectorwars/data

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

# Start Game API Server
echo "Starting Game API Server..."
cd /home/runner/Sectorwars2102/services/gameserver
python -m uvicorn src.main:app --host 0.0.0.0 --port 5000 --reload > /tmp/gameserver.log 2>&1 &

# Install Node.js dependencies if needed and start frontends
echo "Setting up frontends..."
cd /home/runner/Sectorwars2102
npm install -g npm@latest

# Player Client
cd /home/runner/Sectorwars2102/services/player-client
npm install
npm run dev -- --host 0.0.0.0 --port 3000 > /tmp/player-client.log 2>&1 &

# Admin UI
cd /home/runner/Sectorwars2102/services/admin-ui
npm install
npm run dev -- --host 0.0.0.0 --port 3001 > /tmp/admin-ui.log 2>&1 &

# Display access information
echo ""
echo "Services started in background:"
echo "Game API Server: http://localhost:5000 (logs: /tmp/gameserver.log)"
echo "Player Client: http://localhost:3000 (logs: /tmp/player-client.log)"
echo "Admin UI: http://localhost:3001 (logs: /tmp/admin-ui.log)"
echo ""
echo "Use 'tail -f /tmp/*.log' to view service logs"
echo "Services will continue running in background..."
echo ""

# Keep script alive to allow services to continue running
tail -f /dev/null