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

# Try to upgrade Node.js using NVM if available
upgrade_node() {
  echo "Checking for Node.js upgrade possibilities..."
  
  if [ -f "$REPO_ROOT/nvm/nvm.sh" ]; then
    echo "NVM found, attempting to upgrade Node.js..."
    
    # Source NVM
    source "$REPO_ROOT/nvm/nvm.sh"
    
    # Get current version
    CURRENT_NODE_VERSION=$(node -v)
    echo "Current Node.js version: $CURRENT_NODE_VERSION"
    
    # Install Node.js 18 LTS (more recent but stable)
    echo "Installing Node.js 18 LTS..."
    nvm install 18 || echo "Failed to install Node.js 18, continuing with current version"
    
    # If installation succeeded, use it
    if nvm list | grep -q "v18"; then
      echo "Setting Node.js 18 as default..."
      nvm use 18
      nvm alias default 18
      
      # Verify the new version
      NEW_NODE_VERSION=$(node -v)
      echo "Upgraded Node.js version: $NEW_NODE_VERSION"
      
      # Set environment path to include the new Node.js version
      export PATH="$(dirname $(which node)):$PATH"
      
      # Report npm version
      echo "NPM version: $(npm -v)"
      
      return 0
    fi
  else
    echo "NVM not found, skipping Node.js upgrade"
  fi
  
  return 1
}

# Update npm to a compatible version in user space
update_npm() {
  echo "Updating npm to compatible version..."
  
  # Get current node version to determine compatible npm version
  if command_exists node; then
    NODE_VERSION=$(node -v | cut -d 'v' -f 2 | cut -d '.' -f 1)
    
    # Choose npm version based on Node.js version
    if [ "$NODE_VERSION" -ge 18 ]; then
      NPM_VERSION="latest"
    elif [ "$NODE_VERSION" -ge 16 ]; then
      NPM_VERSION="10.2.4"
    else
      NPM_VERSION="8.19.4"  # Last version for Node.js 14
    fi
    
    echo "Installing npm $NPM_VERSION for Node.js v$NODE_VERSION..."
  else
    # Default to a conservative version if node not found
    NPM_VERSION="10.2.4"
    echo "Node.js version not detected, installing npm $NPM_VERSION..."
  fi
  
  # Use local installation to avoid permission issues
  npm install -g npm@$NPM_VERSION --prefix=$HOME/.local || echo "Warning: Could not update npm"
  export PATH="$HOME/.local/bin:$PATH"
}

# Install PM2 if not available
install_pm2() {
  if ! command_exists pm2; then
    echo "Installing PM2 process manager..."
    
    # Try local installation to avoid permission issues
    mkdir -p "$HOME/.local/bin"
    npm install pm2 --prefix=$HOME/.local || echo "WARNING: Could not install PM2 locally"
    export PATH="$HOME/.local/bin:$PATH"
    
    # Create symlink to make pm2 available
    if [ -f "$HOME/.local/node_modules/.bin/pm2" ]; then
      ln -sf "$HOME/.local/node_modules/.bin/pm2" "$HOME/.local/bin/pm2"
    fi
    
    # If still not found, try project-level installation
    if ! command_exists pm2; then
      cd "$REPO_ROOT"
      npm install pm2
      export PATH="$REPO_ROOT/node_modules/.bin:$PATH"
    fi
  fi
}

# Install dependencies if needed
install_dependencies() {
  echo "Installing basic dependencies..."
  
  # Try to upgrade Node.js if possible
  upgrade_node
  
  # Update npm to compatible version
  update_npm
  
  # Try to install Python if not available
  if ! command_exists python3; then
    echo "Python not found, installing..."
    apt-get update && apt-get install -y python3 python3-pip || true
  fi
  
  # Try to install Node.js if not available and upgrade failed
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

# Check Python setup
setup_python() {
  # Check if pip3 exists, otherwise try pip
  if command_exists pip3; then
    PIP_CMD="pip3"
  elif command_exists pip; then
    PIP_CMD="pip"
  else
    echo "WARNING: pip not found."
    # Try to install pip if python is available
    if command_exists python3; then
      echo "Attempting to install pip..."
      python3 -m ensurepip || python3 -m ensurepip --user || echo "Could not install pip"
      if command_exists pip3; then
        PIP_CMD="pip3"
      elif command_exists pip; then
        PIP_CMD="pip"
      fi
    else
      echo "Python not found. Cannot proceed with pip installation."
    fi
  fi

  # If we have pip, use it
  if [ -n "$PIP_CMD" ]; then
    echo "Using $PIP_CMD to install Python packages..."
    cd "$REPO_ROOT/services/gameserver"
    $PIP_CMD install --user --upgrade pip
    $PIP_CMD install --user -r requirements.txt
  else
    echo "WARNING: Skipping Python dependencies installation due to missing pip."
  fi
}

# Install dependencies if needed
install_dependencies

# Setup Python
setup_python

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd "$REPO_ROOT/services/player-client"
npm install

cd "$REPO_ROOT/services/admin-ui"
npm install

# Go back to root directory
cd "$REPO_ROOT"

# Run services directly (fallback method) if PM2 is not available
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
  
  # Start the server
  $PYTHON_CMD -m uvicorn src.main:app --host 0.0.0.0 --port 5000 --reload > /tmp/gameserver.log 2>&1 &
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
  
  # Keep script alive to allow services to continue running
  echo "Press Ctrl+C to stop all services"
  tail -f /dev/null
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

# Check if PM2 is available in any location
if check_for_pm2; then
  echo "PM2 found at: $(which pm2)"
  
  # Kill existing PM2 processes if any
  pm2 kill || true
  
  # Start all services using PM2
  echo "Starting all services with PM2..."
  pm2 start "$REPO_ROOT/pm2.replit.config.js"
  
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
  run_services_directly
fi