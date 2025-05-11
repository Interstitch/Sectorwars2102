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
ENV_TYPE=""

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
    development|production|test)
      ENV_TYPE="$1"
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--no-host-check] [--production-db] [development|production|test]"
      exit 1
      ;;
  esac
done

# Handle environment type setting if specified
if [ -n "$ENV_TYPE" ]; then
  case "$ENV_TYPE" in
    development)
      export ENVIRONMENT="development"
      export DEBUG="true"
      export SECURE_COOKIES="false"
      echo "Environment set to DEVELOPMENT"
      ;;
    production)
      export ENVIRONMENT="production"
      export DEBUG="false"
      export SECURE_COOKIES="true"
      echo "Environment set to PRODUCTION"
      echo "WARNING: Make sure you have set a strong JWT_SECRET for production!"
      ;;
    test)
      export ENVIRONMENT="test"
      export DEBUG="true"
      export SECURE_COOKIES="false"
      echo "Environment set to TEST"
      ;;
  esac

  # Update the .env file if it exists
  if [ -f "$(dirname "$0")/../.env" ]; then
    ENV_FILE="$(dirname "$0")/../.env"
    # Create a new .env file with the updated environment
    grep -v "^ENVIRONMENT=" "$ENV_FILE" > "$ENV_FILE.tmp" || true
    echo "ENVIRONMENT=$ENVIRONMENT" >> "$ENV_FILE.tmp"

    grep -v "^DEBUG=" "$ENV_FILE.tmp" > "$ENV_FILE.tmp2" || true
    echo "DEBUG=$DEBUG" >> "$ENV_FILE.tmp2"

    grep -v "^SECURE_COOKIES=" "$ENV_FILE.tmp2" > "$ENV_FILE.tmp" || true
    echo "SECURE_COOKIES=$SECURE_COOKIES" >> "$ENV_FILE.tmp"

    mv "$ENV_FILE.tmp" "$ENV_FILE"
    rm -f "$ENV_FILE.tmp2"

    echo "Updated .env file with $ENV_TYPE environment settings"
  fi
fi

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

    # Setup Codespaces environment variables
    if [ -n "$CODESPACE_NAME" ] || [ -n "$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN" ]; then
      echo "Setting up environment variables for GitHub Codespaces..."

      # Get the Codespace name
      if [ -n "$CODESPACE_NAME" ]; then
        CODESPACE_HOSTNAME="$CODESPACE_NAME"
      else
        CODESPACE_HOSTNAME=$(echo $GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN | cut -d'.' -f1)
      fi

      # Set the environment variables
      export DEV_ENVIRONMENT="codespaces"
      # Include port numbers in the hostnames for Codespaces URLs
      export API_BASE_URL="https://${CODESPACE_HOSTNAME}-8080.app.github.dev"
      export FRONTEND_URL="https://${CODESPACE_HOSTNAME}-3000.app.github.dev"

      echo "Environment variables set:"
      echo "DEV_ENVIRONMENT=$DEV_ENVIRONMENT"
      echo "API_BASE_URL=$API_BASE_URL"
      echo "FRONTEND_URL=$FRONTEND_URL"

      # Check for GitHub OAuth credentials
      if [ -n "$CLIENT_ID_GITHUB" ] && [ -n "$CLIENT_SECRET_GITHUB" ]; then
        echo "Using real GitHub OAuth credentials"
      else
        echo "WARNING: GitHub OAuth credentials not found!"
        echo "Using mock credentials instead. Set CLIENT_ID_GITHUB and CLIENT_SECRET_GITHUB"
        echo "in your Codespaces secrets to use real GitHub OAuth."
      fi
    fi

    # Make sure Docker is available
    if [ -z "$DOCKER_COMPOSE_CMD" ]; then
      echo "ERROR: Docker Compose is not available in Codespaces environment."
      echo "Please ensure Docker is properly installed and try again."
      exit 1
    fi

    # For Codespaces, we need to ensure the environment variables are set correctly
    # Update the main .env file

    # Create .env file if it doesn't exist
    if [ ! -f "$REPO_ROOT/.env" ]; then
      touch "$REPO_ROOT/.env"
    fi

    # Update environment variables in the .env file
    echo "# Sector Wars 2102 environment configuration" > "$REPO_ROOT/.env"
    echo "DEV_ENVIRONMENT=codespaces" >> "$REPO_ROOT/.env"
    echo "API_BASE_URL=$API_BASE_URL" >> "$REPO_ROOT/.env"
    echo "FRONTEND_URL=$FRONTEND_URL" >> "$REPO_ROOT/.env"
    echo "CODESPACE_NAME=$CODESPACE_NAME" >> "$REPO_ROOT/.env"
    echo "ENVIRONMENT=${ENVIRONMENT:-development}" >> "$REPO_ROOT/.env"
    echo "DEBUG=${DEBUG:-true}" >> "$REPO_ROOT/.env"

    # Add GitHub OAuth credentials if available
    if [ -n "$CLIENT_ID_GITHUB" ] && [ -n "$CLIENT_SECRET_GITHUB" ]; then
      echo "CLIENT_ID_GITHUB=$CLIENT_ID_GITHUB" >> "$REPO_ROOT/.env"
      echo "CLIENT_SECRET_GITHUB=$CLIENT_SECRET_GITHUB" >> "$REPO_ROOT/.env"
    fi

    echo "✅ Updated .env file with Codespaces configuration"

    # Start services with the updated environment
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