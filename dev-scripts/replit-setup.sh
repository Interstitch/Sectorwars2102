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
mkdir -p "$HOME/.local/bin"

# Make all scripts executable
chmod +x "$REPO_ROOT/dev-scripts/"*.sh

# Function to check if a command exists
command_exists() {
  type "$1" &> /dev/null
}

# Update npm to a compatible version in user space
update_npm() {
  echo "Updating npm to compatible version..."
  # Use 10.2.4 which is compatible with Node.js 16
  npm install -g npm@10.2.4 --prefix=$HOME/.local || echo "Warning: Could not update npm"
  export PATH="$HOME/.local/bin:$PATH"
}

# Install PM2 in user space (avoiding permission issues)
install_pm2() {
  echo "Installing PM2 in user space..."
  # Install PM2 to user's home directory to avoid permission issues
  npm install pm2 --prefix=$HOME/.local || echo "WARNING: Could not install PM2 locally"
  
  # Create symlink to make pm2 available
  if [ -f "$HOME/.local/node_modules/.bin/pm2" ]; then
    ln -sf "$HOME/.local/node_modules/.bin/pm2" "$HOME/.local/bin/pm2"
    echo "PM2 installed at $HOME/.local/bin/pm2"
  else
    echo "Warning: PM2 installation incomplete"
  fi
  
  # Add to PATH for this session
  export PATH="$HOME/.local/bin:$PATH"
  
  # Add to PATH permanently
  grep -q 'export PATH="$HOME/.local/bin:$PATH"' ~/.bashrc || echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
}

# Install basic dependencies
echo "Installing basic dependencies..."

# Update npm
update_npm

# Install Python dependencies
echo "Installing Python dependencies..."
cd "$REPO_ROOT/services/gameserver"

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
  $PIP_CMD install --user --upgrade pip
  $PIP_CMD install --user -r requirements.txt
else
  echo "WARNING: Skipping Python dependencies installation due to missing pip."
fi

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
cd "$REPO_ROOT"
npm install typescript vite --prefix=$HOME/.local

# Install PM2 for process management
if ! command_exists pm2; then
  install_pm2
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
echo "Note: You may need to refresh your terminal session to access PM2."
echo "You can also use '/run start' to start the application."