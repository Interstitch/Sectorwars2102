#!/bin/bash

# One-time setup script for Replit environment with PM2
echo "Setting up Sector Wars 2102 in Replit environment..."

# Get the correct path for the repository root
if [ -d "/home/runner/Sectorwars2102" ]; then
  REPO_ROOT="/home/runner/Sectorwars2102"
else
  REPO_ROOT=$(pwd)
fi

# Create necessary directories
mkdir -p ~/.config
mkdir -p /tmp/sectorwars/data

# Make all scripts executable
chmod +x "$REPO_ROOT/dev-scripts/"*.sh

# Function to check if a command exists
command_exists() {
  type "$1" &> /dev/null
}

# Install basic dependencies
echo "Installing basic dependencies..."

# Install Python dependencies
echo "Installing Python dependencies..."
cd "$REPO_ROOT/services/gameserver"
pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
cd "$REPO_ROOT"
npm install -g typescript@latest vite@latest

# Install PM2 for process management
if ! command_exists pm2; then
  echo "Installing PM2 globally..."
  npm install -g pm2
  
  # Install locally as fallback
  cd "$REPO_ROOT"
  npm install pm2 --save-dev
fi

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd "$REPO_ROOT/services/player-client"
npm install

cd "$REPO_ROOT/services/admin-ui"
npm install

# Setup environment config
echo "Setting up environment configuration..."
if [ ! -f "$REPO_ROOT/.env" ] && [ -f "$REPO_ROOT/.env.example" ]; then
  cp "$REPO_ROOT/.env.example" "$REPO_ROOT/.env"
  
  # Configure database URL if provided
  if [ -n "$DATABASE_URL" ]; then
    sed -i "s#DATABASE_URL=.*#DATABASE_URL=$DATABASE_URL#" "$REPO_ROOT/.env"
  else
    sed -i 's#DATABASE_URL=.*#DATABASE_URL=postgresql://postgres:postgres@db.example.com:5432/sectorwars#' "$REPO_ROOT/.env"
  fi
  
  echo "Created .env file. Please update the database connection if needed."
fi

echo "Setup complete! Run './dev-scripts/start-replit.sh' to start the application."