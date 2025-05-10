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

# Check if running in Replit environment
if [ "$DEV_ENVIRONMENT" = "replit" ]; then
  # Handle Replit-specific paths
  REPO_ROOT="/home/runner/Sectorwars2102"
  
  # If we're in Replit and Docker is not available, use non-Docker mode
  if ! command -v docker &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo "Docker not available in Replit. Using non-Docker fallback mode."
    
    # Check if we're in the correct path
    if [ -f "./dev-scripts/start-replit.sh" ]; then
      bash ./dev-scripts/start-replit.sh
    elif [ -f "$REPO_ROOT/dev-scripts/start-replit.sh" ]; then
      bash "$REPO_ROOT/dev-scripts/start-replit.sh"
    else
      echo "Error: Cannot find start-replit.sh script."
      exit 1
    fi
    exit $?
  fi
else
  REPO_ROOT="$(pwd)"
fi

# Check if .env file exists, create from example if not
if [ ! -f .env ] && [ -f .env.example ]; then
  echo "Creating .env file from example..."
  cp .env.example .env
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