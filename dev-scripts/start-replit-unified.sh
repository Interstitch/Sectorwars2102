#!/bin/bash

# Unified Replit startup script for Sector Wars 2102
# Supports both PM2 and direct process management with host-check toggle

# Parse command-line options
NO_HOST_CHECK=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-host-check)
      NO_HOST_CHECK=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--no-host-check]"
      exit 1
      ;;
  esac
done

# Environment setup
export ENVIRONMENT=replit
export NODE_ENV=development
export PYTHONUNBUFFERED=1
export PYTHONPATH="./services/gameserver:$PYTHONPATH"

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

# Function to check if a command exists
command_exists() {
  type "$1" &> /dev/null
}

# Ensure python user base is in PATH
PYTHON_USER_BASE=$(python3 -m site --user-base)
export PATH="$PYTHON_USER_BASE/bin:$PATH"

# Run one-time setup if needed
if [ ! -f "$REPO_ROOT/.replit_setup_done" ]; then
  echo "First-time setup needed. Running setup script..."
  bash "$REPO_ROOT/dev-scripts/setup.sh"
fi

# Check for port 8080 availability
check_port_8080() {
  echo "Checking if port 8080 is available..."

  # Try to bind to port 8080
  if python3 -c "import socket; s=socket.socket(); s.bind(('0.0.0.0', 8080)); s.close(); print('Port 8080 is available')" 2>/dev/null; then
    echo "✅ Port 8080 is available"
    return 0
  else
    echo "❌ Port 8080 is not available"
    return 1
  fi
}

check_port_8080 || echo "Warning: Port 8080 may be in use or restricted"

# Direct mode with no host checking
run_services_no_host_check() {
  echo "Starting services with host checking disabled..."
  
  # Run gameserver in background
  cd "$REPO_ROOT/services/gameserver"
  chmod +x simple_server.py
  ./simple_server.py > /tmp/gameserver.log 2>&1 &
  GAMESERVER_PID=$!
  echo "Game API Server (port 8080) started with PID: $GAMESERVER_PID"
  
  # Run player-client with host checking disabled
  cd "$REPO_ROOT/services/player-client"
  node disable-host-check.js > /tmp/player-client.log 2>&1 &
  PLAYER_CLIENT_PID=$!
  echo "Player Client (port 3000) started with PID: $PLAYER_CLIENT_PID"
  
  # Run admin-ui with host checking disabled
  cd "$REPO_ROOT/services/admin-ui"
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
}

# Run services directly (fallback method)
run_services_directly() {
  echo "Running services directly without PM2..."
  
  # Start Game API Server
  echo "Starting Game API Server..."
  cd "$REPO_ROOT/services/gameserver"
  
  # Determine which Python command to use
  if command_exists python3; then
    PYTHON_CMD="python3"
  elif command_exists python; then
    PYTHON_CMD="python"
  else
    echo "ERROR: No Python interpreter found. Cannot start Game API Server."
    return 1
  fi
  
  # Try to start the server with various methods

  # Method 1: Try the simple server first (most likely to work)
  if [ -f "simple_server.py" ]; then
    echo "Starting simple test server first (most reliable)..."
    $PYTHON_CMD simple_server.py > /tmp/gameserver.log 2>&1 &
    GAMESERVER_PID=$!
    echo "Simple test server started with PID: $GAMESERVER_PID"

    # Wait a short time to see if it stays running
    sleep 3
    if kill -0 $GAMESERVER_PID 2>/dev/null; then
      echo "✅ Simple test server is running on port 8080"
    else
      echo "❌ Simple test server failed to start or stay running, checking logs..."
      cat /tmp/gameserver.log
      return 1
    fi
  else
    # Method 2: Try the regular server with uvicorn module
    echo "Starting game server with $PYTHON_CMD -m uvicorn..."
    PYTHONPATH="$PYTHON_USER_SITE:$REPO_ROOT/services/gameserver" $PYTHON_CMD -m uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload > /tmp/gameserver.log 2>&1 &
    GAMESERVER_PID=$!
    echo "Game API Server started with PID: $GAMESERVER_PID"

    # Wait a short time to see if it stays running
    sleep 3
    if ! kill -0 $GAMESERVER_PID 2>/dev/null; then
      echo "❌ Game API Server failed to start or stay running, checking logs..."
      cat /tmp/gameserver.log
      return 1
    fi
  fi
  
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
  echo "Game API Server: http://localhost:8080 (logs: /tmp/gameserver.log)"
  echo "Player Client: http://localhost:3000 (logs: /tmp/player-client.log)"
  echo "Admin UI: http://localhost:3001 (logs: /tmp/admin-ui.log)"
  echo ""
  echo "Use 'tail -f /tmp/gameserver.log' to view the game server logs"
}

# Check for PM2 in all possible locations
check_for_pm2() {
  # Check in PATH
  if command_exists pm2; then
    return 0
  fi
  
  # Check in HOME/.local/bin
  if [ -f "$HOME/.local/bin/pm2" ]; then
    export PATH="$HOME/.local/bin:$PATH"
    return 0
  fi
  
  # Check in node_modules
  if [ -f "$HOME/.local/node_modules/.bin/pm2" ]; then
    export PATH="$HOME/.local/node_modules/.bin:$PATH"
    return 0
  fi
  
  # Check in project node_modules
  if [ -f "$REPO_ROOT/node_modules/.bin/pm2" ]; then
    export PATH="$REPO_ROOT/node_modules/.bin:$PATH"
    return 0
  fi
  
  return 1
}

# Register cleanup handler for direct mode
cleanup_direct() {
  echo "Stopping services..."
  if [ -f /tmp/sectorwars-pids.txt ]; then
    cat /tmp/sectorwars-pids.txt | xargs kill -15 2>/dev/null || true
    rm /tmp/sectorwars-pids.txt
  fi
  echo "Services stopped"
  exit 0
}

# Register cleanup handler for PM2 mode
cleanup_pm2() {
  echo "Script terminated. PM2 processes continue to run."
  echo "Use 'pm2 kill' to stop all services if needed."
  exit 0
}

# Main execution logic
if [ "$NO_HOST_CHECK" = true ]; then
  echo "Starting with host checks disabled (emergency mode)..."
  run_services_no_host_check
  trap cleanup_direct INT TERM
  # Keep script alive to allow services to continue running
  echo "Press Ctrl+C to stop all services"
  tail -f /dev/null
elif check_for_pm2; then
  echo "PM2 found at: $(which pm2)"
  
  # Kill existing PM2 processes if any
  pm2 kill || true
  
  # Start all services using PM2
  echo "Starting all services with PM2..."
  cd "$REPO_ROOT"
  pm2 start "$REPO_ROOT/pm2.replit.config.js"
  
  # Display PM2 status
  pm2 status
  
  # Display access information
  echo ""
  echo "Services started with PM2:"
  echo "Game API Server: http://localhost:8080"
  echo "Player Client: http://localhost:3000"
  echo "Admin UI: http://localhost:3001"
  echo ""
  echo "Use 'pm2 logs' to view all logs or 'pm2 logs [service-name]' for specific service logs"
  echo "Use 'pm2 monit' for a real-time dashboard"
  echo "Services will continue running in background..."
  echo ""
  
  # Register cleanup handler
  trap cleanup_pm2 INT TERM
  
  # Wait indefinitely (PM2 processes will keep running)
  echo "Press Ctrl+C to exit (services will continue running)"
  tail -f /dev/null
else
  echo "PM2 is not available. Using direct process management..."
  run_services_directly
  trap cleanup_direct INT TERM
  # Keep script alive to allow services to continue running
  echo "Press Ctrl+C to stop all services"
  tail -f /dev/null
fi