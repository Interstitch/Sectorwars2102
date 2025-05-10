#!/bin/bash

# One-time setup script for Replit environment
echo "Setting up Sector Wars 2102 in Replit environment..."

# Create necessary directories
mkdir -p ~/.config

# Install basic dependencies if not available
pip install --upgrade pip

# Install Python development dependencies
echo "Installing Python dependencies..."
cd /home/runner/Sectorwars2102/services/gameserver
pip install -r requirements.txt

# Install Node.js development dependencies
echo "Installing Node.js dependencies..."
npm install -g typescript@latest vite@latest

# Setup environment config
echo "Setting up environment configuration..."
cp /home/runner/Sectorwars2102/.env.example /home/runner/Sectorwars2102/.env
sed -i 's/DATABASE_URL=.*/DATABASE_URL=postgresql:\/\/postgres:postgres@db.example.com:5432\/sectorwars/' /home/runner/Sectorwars2102/.env

# Give execution permission to scripts
chmod +x /home/runner/Sectorwars2102/dev-scripts/*.sh

echo "Setup complete! Run './dev-scripts/start.sh' to start the application."