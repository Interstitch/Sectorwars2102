#!/bin/bash

# Replit-specific startup script avoiding Nix dependencies
echo "Starting Sector Wars 2102 in Replit (simple mode)..."

# Environment setup
export ENVIRONMENT=replit
export NODE_ENV=development
export PYTHONUNBUFFERED=1

# Get the correct path for the repository root
if [ -d "/home/runner/Sectorwars2102" ]; then
  REPO_ROOT="/home/runner/Sectorwars2102"
else
  REPO_ROOT=$(pwd)
fi

# Create data directories if they don't exist
mkdir -p /tmp/sectorwars/data

# Check if .env file exists, create from example if not
if [ ! -f "$REPO_ROOT/.env" ] && [ -f "$REPO_ROOT/.env.example" ]; then
  echo "Creating .env file from example..."
  cp "$REPO_ROOT/.env.example" "$REPO_ROOT/.env"
  echo "Created .env file from example. Please review the settings."
fi

# Function to check if a command exists without relying on command -v
# which may not be available in all environments
command_exists() {
  type "$1" &> /dev/null
}

# Install Python and Node.js using system package manager if not available
install_dependencies() {
  echo "Installing basic dependencies..."
  
  # Try to install Python if not available
  if ! command_exists python3; then
    echo "Python not found, installing..."
    apt-get update && apt-get install -y python3 python3-pip || true
  fi
  
  # Try to install Node.js if not available
  if ! command_exists node; then
    echo "Node.js not found, installing..."
    # Use NVM if available
    if [ -f "$REPO_ROOT/nvm/nvm.sh" ]; then
      echo "Using NVM to install Node.js..."
      source "$REPO_ROOT/nvm/nvm.sh"
      nvm install 16 || true
      nvm use 16 || true
    fi
  fi
  
  # Check if we now have the basics
  if ! command_exists python3; then
    echo "WARNING: Could not install Python."
  else
    echo "Python installed: $(python3 --version)"
  fi
  
  if ! command_exists node; then
    echo "WARNING: Could not install Node.js."
  else
    echo "Node installed: $(node --version)"
    echo "NPM installed: $(npm --version)"
  fi
}

# Install dependencies if needed
install_dependencies

# Install Python dependencies for Game API Server
echo "Installing Python dependencies..."
cd "$REPO_ROOT/services/gameserver"
python3 -m pip install -r requirements.txt

# Start Game API Server
echo "Starting Game API Server..."
cd "$REPO_ROOT/services/gameserver"
python3 -m uvicorn src.main:app --host 0.0.0.0 --port 5000 --reload > /tmp/gameserver.log 2>&1 &
GAMESERVER_PID=$!
echo "Game API Server started with PID: $GAMESERVER_PID"

# Player Client
echo "Setting up Player Client..."
cd "$REPO_ROOT/services/player-client"
npm install
npm run dev -- --host 0.0.0.0 --port 3000 > /tmp/player-client.log 2>&1 &
PLAYER_CLIENT_PID=$!
echo "Player Client started with PID: $PLAYER_CLIENT_PID"

# Admin UI
echo "Setting up Admin UI..."
cd "$REPO_ROOT/services/admin-ui"
npm install
npm run dev -- --host 0.0.0.0 --port 3001 > /tmp/admin-ui.log 2>&1 &
ADMIN_UI_PID=$!
echo "Admin UI started with PID: $ADMIN_UI_PID"

# Save PIDs for cleanup
echo "$GAMESERVER_PID $PLAYER_CLIENT_PID $ADMIN_UI_PID" > /tmp/sectorwars-pids.txt

# Display access information
echo ""
echo "Services started in background:"
echo "Game API Server: http://localhost:5000 (logs: /tmp/gameserver.log)"
echo "Player Client: http://localhost:3000 (logs: /tmp/player-client.log)"
echo "Admin UI: http://localhost:3001 (logs: /tmp/admin-ui.log)"
echo ""
echo "Use 'tail -f /tmp/gameserver.log' to view the game server logs"
echo "Services will continue running in background..."
echo ""

# Register cleanup handler
cleanup() {
  echo "Stopping services..."
  if [ -f /tmp/sectorwars-pids.txt ]; then
    cat /tmp/sectorwars-pids.txt | xargs kill -15 2>/dev/null || true
    rm /tmp/sectorwars-pids.txt
  fi
  echo "Services stopped"
  exit 0
}

trap cleanup INT TERM

# Keep script alive to allow services to continue running
echo "Press Ctrl+C to stop all services"
tail -f /dev/null