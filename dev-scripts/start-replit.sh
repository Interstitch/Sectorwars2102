#!/bin/bash

# Replit-specific startup script using PM2 for process management
echo "Starting Sector Wars 2102 in Replit using PM2..."

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
command_exists() {
  type "$1" &> /dev/null
}

# Install PM2 if not available
install_pm2() {
  if ! command_exists pm2; then
    echo "Installing PM2 process manager..."
    npm install -g pm2 || echo "WARNING: Could not install PM2 globally"
    
    # Try local installation if global fails
    if ! command_exists pm2; then
      cd "$REPO_ROOT"
      npm install pm2 || echo "WARNING: Could not install PM2 locally"
      export PATH="$PATH:$REPO_ROOT/node_modules/.bin"
    fi
  fi
}

# Install dependencies if needed
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
  
  # Install PM2
  install_pm2
}

# Install dependencies if needed
install_dependencies

# Install Python dependencies for Game API Server
echo "Installing Python dependencies..."
cd "$REPO_ROOT/services/gameserver"
python3 -m pip install -r requirements.txt

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd "$REPO_ROOT/services/player-client"
npm install

cd "$REPO_ROOT/services/admin-ui"
npm install

# Go back to root directory
cd "$REPO_ROOT"

# Check if PM2 is available
if command_exists pm2; then
  # Kill existing PM2 processes if any
  pm2 kill || true
  
  # Start all services using PM2
  echo "Starting all services with PM2..."
  pm2 start pm2.replit.config.js
  
  # Display PM2 status
  pm2 status
  
  # Display access information
  echo ""
  echo "Services started with PM2:"
  echo "Game API Server: http://localhost:5000"
  echo "Player Client: http://localhost:3000"
  echo "Admin UI: http://localhost:3001"
  echo ""
  echo "Use 'pm2 logs' to view all logs or 'pm2 logs [service-name]' for specific service logs"
  echo "Use 'pm2 monit' for a real-time dashboard"
  echo "Services will continue running in background..."
  echo ""
  
  # Keep script alive to keep PM2 processes running
  echo "Press Ctrl+C to exit (services will continue running)"
  
  # Register cleanup handler
  cleanup() {
    echo "Script terminated. PM2 processes continue to run."
    echo "Use 'pm2 kill' to stop all services if needed."
    exit 0
  }
  
  trap cleanup INT TERM
  
  # Wait indefinitely (PM2 processes will keep running)
  tail -f /dev/null
else
  echo "ERROR: PM2 is not available. Using fallback process management..."
  
  # Start Game API Server
  echo "Starting Game API Server..."
  cd "$REPO_ROOT/services/gameserver"
  python3 -m uvicorn src.main:app --host 0.0.0.0 --port 5000 --reload > /tmp/gameserver.log 2>&1 &
  GAMESERVER_PID=$!
  echo "Game API Server started with PID: $GAMESERVER_PID"
  
  # Player Client
  echo "Setting up Player Client..."
  cd "$REPO_ROOT/services/player-client"
  npm run dev -- --host 0.0.0.0 --port 3000 > /tmp/player-client.log 2>&1 &
  PLAYER_CLIENT_PID=$!
  echo "Player Client started with PID: $PLAYER_CLIENT_PID"
  
  # Admin UI
  echo "Setting up Admin UI..."
  cd "$REPO_ROOT/services/admin-ui"
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
fi