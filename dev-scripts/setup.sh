#!/bin/bash

# Setup script for Sector Wars 2102
# For use with Docker-based development (GitHub Codespaces or local)

REPO_ROOT=$(pwd)

echo "Setting up Sector Wars 2102 development environment..."

# Make all scripts executable
chmod +x "$REPO_ROOT/dev-scripts/"*.sh 2>/dev/null || true

# Setup environment config
setup_env() {
  echo "Setting up environment configuration..."
  if [ ! -f "$REPO_ROOT/.env" ] && [ -f "$REPO_ROOT/.env.example" ]; then
    cp "$REPO_ROOT/.env.example" "$REPO_ROOT/.env"
    echo "Created .env file from .env.example"
    echo "Please update database connection settings if needed."
  elif [ -f "$REPO_ROOT/.env" ]; then
    echo ".env file already exists"
  else
    echo "WARNING: No .env.example found. Please create .env manually."
  fi
}

# Detect environment
if [ -n "$CODESPACE_NAME" ] || [ -n "$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN" ]; then
  echo "Detected GitHub Codespaces environment"
  export DEV_ENVIRONMENT="codespaces"
else
  echo "Detected local environment"
  export DEV_ENVIRONMENT="local"
fi

# Run setup
setup_env

# Check Docker availability
if command -v docker-compose &>/dev/null || (command -v docker &>/dev/null && docker compose version &>/dev/null); then
  echo "✅ Docker Compose is available"
else
  echo "❌ Docker Compose not found. Please install Docker."
  exit 1
fi

echo ""
echo "Setup complete!"
echo "Run './dev-scripts/start-unified.sh' to start the application."
echo ""
echo "Services will be available at:"
echo "  - Player Client: http://localhost:3000"
echo "  - Admin UI: http://localhost:3001"
echo "  - Game Server API: http://localhost:8080"
