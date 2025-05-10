#!/bin/bash

# Simple one-time setup script for Replit environment without Nix
echo "Setting up Sector Wars 2102 in Replit environment (simple mode)..."

# Get the correct path for the repository root
if [ -d "/home/runner/Sectorwars2102" ]; then
  REPO_ROOT="/home/runner/Sectorwars2102"
else
  REPO_ROOT=$(pwd)
fi

# Make all scripts executable
chmod +x "$REPO_ROOT/dev-scripts/"*.sh

# Create necessary directories
mkdir -p ~/.config
mkdir -p /tmp/sectorwars/data

# Function to check if a command exists
command_exists() {
  type "$1" &> /dev/null
}

# Function to install NVM if needed
setup_nvm() {
  if [ -f "$REPO_ROOT/nvm/nvm.sh" ]; then
    echo "NVM found, setting up..."
    source "$REPO_ROOT/nvm/nvm.sh"
    nvm install 16 || echo "Failed to install Node.js via NVM"
  else
    echo "NVM not found, skipping Node.js setup"
  fi
}

# Function to setup Python environment
setup_python() {
  echo "Setting up Python environment..."
  
  # Try to use system Python or fall back
  if command_exists python3; then
    echo "Python 3 found: $(python3 --version)"
    python3 -m pip install --upgrade pip
  else
    echo "WARNING: Python 3 not found and cannot be installed automatically."
    echo "Please install Python 3 manually or use a Replit with Python support."
  fi
}

# Function to setup Node.js environment
setup_nodejs() {
  echo "Setting up Node.js environment..."
  
  # Try to use system Node.js or fall back to NVM
  if command_exists node; then
    echo "Node.js found: $(node --version)"
    echo "NPM found: $(npm --version)"
  else
    echo "Node.js not found, trying to install via NVM..."
    setup_nvm
  fi
}

# Setup basic environments
setup_python
setup_nodejs

# Check if .env file exists, create from example if not
if [ ! -f "$REPO_ROOT/.env" ] && [ -f "$REPO_ROOT/.env.example" ]; then
  echo "Creating .env file from example..."
  cp "$REPO_ROOT/.env.example" "$REPO_ROOT/.env"
  echo "Created .env file from example. Please review the settings."
fi

# Install Python dependencies
echo "Installing Python dependencies..."
cd "$REPO_ROOT/services/gameserver"
python3 -m pip install -r requirements.txt || echo "WARNING: Failed to install Python dependencies"

# Install Node.js dependencies globally
echo "Installing global Node.js dependencies..."
npm install -g typescript vite || echo "WARNING: Failed to install global Node.js dependencies"

echo "Setup complete! Run './dev-scripts/start-replit.sh' to start the application."