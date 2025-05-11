#!/bin/bash

# Unified startup script for Sector Wars 2102
# Automatically detects environment and starts services accordingly

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
USE_PRODUCTION_DB=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-host-check)
      NO_HOST_CHECK=true
      shift
      ;;
    --production-db)
      USE_PRODUCTION_DB=true
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--no-host-check] [--production-db]"
      exit 1
      ;;
  esac
done

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

# Run one-time setup if needed
if [ ! -f "$REPO_ROOT/.env" ] || [ ! -f "$REPO_ROOT/.replit_setup_done" ] && [ "$DEV_ENVIRONMENT" = "replit" ]; then
  echo "First-time setup needed. Running setup script..."
  bash "$REPO_ROOT/dev-scripts/setup.sh"
fi

# Check which docker compose command is available
if command -v docker-compose &>/dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif command -v docker &>/dev/null && docker compose version &>/dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    DOCKER_COMPOSE_CMD=""
fi

# Set database environment variable if using production database
if [ "$USE_PRODUCTION_DB" = true ]; then
  echo "USING PRODUCTION DATABASE"
  export ENVIRONMENT=production
  echo "🚨 IMPORTANT: Running with PRODUCTION database 🚨"
else
  export ENVIRONMENT=development
  echo "Using development database"
fi

# Set environment variables based on detected environment
case "$DEV_ENVIRONMENT" in
  "replit")
    echo "Starting services in Replit environment..."
    export NODE_ENV=development

    # Check if Docker is available in Replit environment
    if [ -n "$DOCKER_COMPOSE_CMD" ] && command -v docker &> /dev/null; then
      echo "Docker available in Replit. Using Docker Compose..."
      $DOCKER_COMPOSE_CMD -f docker-compose.yml up
    else
      # Pass the flags if they were provided
      FLAGS=""
      if [ "$NO_HOST_CHECK" = true ]; then
        FLAGS="$FLAGS --no-host-check"
      fi
      if [ "$USE_PRODUCTION_DB" = true ]; then
        FLAGS="$FLAGS --production-db"
      fi

      bash "$REPO_ROOT/dev-scripts/start-replit-unified.sh" $FLAGS
    fi
    ;;

  "codespaces")
    echo "Starting services in GitHub Codespaces environment..."
    export NODE_ENV=development

    # Set up Codespaces environment variables
    source "$(dirname "$0")/set-codespaces-env.sh"

    # Make sure Docker is available
    if [ -z "$DOCKER_COMPOSE_CMD" ]; then
      echo "ERROR: Docker Compose is not available in Codespaces environment."
      echo "Please ensure Docker is properly installed and try again."
      exit 1
    fi

    # Start services with standard configuration
    $DOCKER_COMPOSE_CMD up
    ;;

  "local")
    echo "Starting services in local environment..."
    export NODE_ENV=development

    # Make sure Docker is available
    if [ -z "$DOCKER_COMPOSE_CMD" ]; then
      echo "ERROR: Docker Compose is not available in local environment."
      echo "Please ensure Docker is properly installed and try again."
      exit 1
    fi

    # Start services with standard configuration
    $DOCKER_COMPOSE_CMD up
    ;;

  *)
    echo "Unknown environment: $DEV_ENVIRONMENT"
    echo "Please set DEV_ENVIRONMENT to 'local', 'codespaces', or 'replit'"
    exit 1
    ;;
esac