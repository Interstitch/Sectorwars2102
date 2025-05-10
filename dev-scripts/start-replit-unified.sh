#!/bin/bash

# Unified Replit startup script for Sector Wars 2102
# Runs services with PM2 process management, with an option to disable host checking

# Source environment settings if available
if [ -d "$(dirname "$0")/../.env.d" ]; then
  for script in "$(dirname "$0")/../.env.d"/*.sh; do
    if [ -f "$script" ]; then
      source "$script"
      echo "Loaded environment settings from $script"
    fi
  done
fi

# Ensure local bin is in PATH, even if env scripts were not loaded
export PATH="$HOME/.local/bin:$PATH"

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

# No-host-check mode with PM2
run_with_no_host_check() {
  echo "Starting with PM2 and host-check disabled..."
  
  # Kill existing PM2 processes if any
  pm2 kill || true
  
  # Get config file based on host-check setting
  local CONFIG_FILE="$REPO_ROOT/pm2.replit-nohost.config.js"
  
  # If config file doesn't exist, create it
  if [ ! -f "$CONFIG_FILE" ]; then
    echo "Creating no-host-check PM2 config..."
    cat > "$CONFIG_FILE" << EOF
module.exports = {
  apps: [
    {
      name: 'simple-test-server',
      cwd: './services/gameserver',
      script: './simple_server.py',
      env: {
        PYTHONUNBUFFERED: 1,
        PATH: process.env.PATH || '',
        PYTHONPATH: '/home/runner/.local/lib/python3.10/site-packages:/home/runner/Sectorwars2102/services/gameserver',
        ENVIRONMENT: 'replit',
        DATABASE_URL: process.env.DATABASE_URL
      },
      watch: false,
      autorestart: true,
      max_restarts: 10,
      interpreter: '/usr/bin/env',
      interpreter_args: 'python3',
    },
    {
      name: 'player-client-nohost',
      cwd: './services/player-client',
      script: 'node',
      args: 'disable-host-check.js',
      env: {
        API_URL: 'http://localhost:8080',
        NODE_ENV: process.env.NODE_ENV || 'development',
      },
      autorestart: true,
      max_restarts: 5,
    },
    {
      name: 'admin-ui-nohost',
      cwd: './services/admin-ui',
      script: 'node',
      args: 'disable-host-check.js',
      env: {
        API_URL: 'http://localhost:8080',
        NODE_ENV: process.env.NODE_ENV || 'development',
      },
      autorestart: true,
      max_restarts: 5,
    },
  ],
};
EOF
  fi
  
  # Start services with PM2 and no-host-check config
  cd "$REPO_ROOT"
  pm2 start "$CONFIG_FILE"
  
  # Display PM2 status
  pm2 status
  
  # Display access information
  echo ""
  echo "Services started with PM2 (host-check disabled):"
  echo "Game API Server: http://localhost:8080"
  echo "Player Client: http://localhost:3000"
  echo "Admin UI: http://localhost:3001"
  echo ""
  echo "Use 'pm2 logs' to view all logs or 'pm2 logs [service-name]' for specific service logs"
  echo "Use 'pm2 monit' for a real-time dashboard"
  echo "Services will continue running in background..."
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

# Install PM2 if it's not available
install_pm2() {
  echo "PM2 not found. Installing PM2..."
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
  
  # Check if it's now available
  if command_exists pm2; then
    echo "PM2 installed successfully at: $(which pm2)"
    return 0
  else
    echo "ERROR: Failed to install PM2. Please install it manually."
    return 1
  fi
}

# Register cleanup handler
cleanup_pm2() {
  echo "Script terminated. PM2 processes continue to run."
  echo "Use 'pm2 kill' to stop all services if needed."
  exit 0
}

# Main execution logic
if ! check_for_pm2; then
  install_pm2 || { echo "Cannot continue without PM2."; exit 1; }
fi

echo "PM2 found at: $(which pm2)"

# Kill existing PM2 processes if any
pm2 kill || true

# Start services based on host-check setting
if [ "$NO_HOST_CHECK" = true ]; then
  run_with_no_host_check
else
  # Start all services using standard PM2 config
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
fi

# Register cleanup handler
trap cleanup_pm2 INT TERM

# Wait indefinitely (PM2 processes will keep running)
echo ""
echo "Press Ctrl+C to exit (services will continue running)"
tail -f /dev/null