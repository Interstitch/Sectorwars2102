#!/bin/bash

# Environment detection script for Sector Wars 2102
# Automatically detects the current environment and starts the appropriate services

# Function to detect environment
detect_environment() {
  if [ -n "$REPL_ID" ] || [ -n "$REPL_SLUG" ] || [ -d "/home/runner" ]; then
    echo "replit"
  elif [ -n "$CODESPACE_NAME" ] || [ -n "$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN" ]; then
    echo "codespaces"
  else
    echo "local"
  fi
}

# Set environment variable if not already set
export DEV_ENVIRONMENT=${DEV_ENVIRONMENT:-$(detect_environment)}
echo "Detected environment: $DEV_ENVIRONMENT"

# Get the correct path for the repository root
if [ "$DEV_ENVIRONMENT" = "replit" ] && [ -d "/home/runner/Sectorwars2102" ]; then
  REPO_ROOT="/home/runner/Sectorwars2102"
else
  REPO_ROOT=$(pwd)
fi

# Check if running in Replit environment
if [ "$DEV_ENVIRONMENT" = "replit" ]; then
  # If we're in Replit, check for Nix issues
  if [ -f "$REPO_ROOT/nix-env-error" ] || ! command -v nix-shell &>/dev/null; then
    # Nix environment is not working, use simplified mode
    echo "Nix environment not available in Replit. Using simplified mode."
    
    # Run one-time setup if needed
    if [ ! -f "$REPO_ROOT/.replit_simple_setup_done" ]; then
      echo "Running one-time simplified setup..."
      bash "$REPO_ROOT/dev-scripts/replit-setup-simple.sh"
      touch "$REPO_ROOT/.replit_simple_setup_done"
    fi
    
    # Launch simplified version
    bash "$REPO_ROOT/dev-scripts/start-replit.sh"
    exit $?
  fi
  
  # If Docker is not available, use non-Docker mode
  if ! command -v docker &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo "Docker not available in Replit. Using non-Docker fallback mode."
    
    # Launch non-Docker version
    bash "$REPO_ROOT/dev-scripts/start-replit.sh"
    exit $?
  fi
fi

# Check if .env file exists, create from example if not
if [ ! -f "$REPO_ROOT/.env" ] && [ -f "$REPO_ROOT/.env.example" ]; then
  echo "Creating .env file from example..."
  cp "$REPO_ROOT/.env.example" "$REPO_ROOT/.env"
  echo "Created .env file from example. Please review the settings."
fi

# Check which docker compose command is available
if command -v docker-compose &>/dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif command -v docker &>/dev/null && docker compose version &>/dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    echo "Neither docker-compose nor docker compose commands are available."
    
    if [ "$DEV_ENVIRONMENT" = "replit" ]; then
      echo "Using non-Docker fallback mode for Replit."
      bash "$REPO_ROOT/dev-scripts/start-replit.sh"
      exit $?
    else 
      echo "Please install Docker and Docker Compose for local or Codespaces environments."
      exit 1
    fi
fi

# Set environment variables based on detected environment
case "$DEV_ENVIRONMENT" in
  "replit")
    echo "Starting services in Replit environment using Docker..."
    export ENVIRONMENT=replit
    export NODE_ENV=development
    
    # Start services with Replit-specific configuration
    $DOCKER_COMPOSE_CMD -f docker-compose.yml -f docker-compose.replit.yml up
    ;;
    
  "codespaces")
    echo "Starting services in GitHub Codespaces environment..."
    export ENVIRONMENT=development
    export NODE_ENV=development
    
    # Start services with standard configuration
    $DOCKER_COMPOSE_CMD up
    ;;
    
  "local")
    echo "Starting services in local environment..."
    export ENVIRONMENT=development
    export NODE_ENV=development
    
    # Start services with standard configuration
    $DOCKER_COMPOSE_CMD up
    ;;
    
  *)
    echo "Unknown environment: $DEV_ENVIRONMENT"
    echo "Please set DEV_ENVIRONMENT to 'local', 'codespaces', or 'replit'"
    exit 1
    ;;
esac