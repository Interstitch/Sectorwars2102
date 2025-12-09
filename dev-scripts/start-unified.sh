#!/bin/bash

# Unified startup script for Sector Wars 2102
# Starts services using Docker Compose

# Parse command-line options
USE_PRODUCTION_DB=false
ENV_TYPE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
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
      echo "Usage: $0 [--production-db] [development|production|test]"
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
fi

# Check which docker compose command is available
if command -v docker-compose &>/dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif command -v docker &>/dev/null && docker compose version &>/dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    echo "ERROR: Docker Compose is not available."
    echo "Please ensure Docker is properly installed and try again."
    exit 1
fi

# Set database environment variable if using production database
if [ "$USE_PRODUCTION_DB" = true ]; then
  echo "USING PRODUCTION DATABASE"
  export ENVIRONMENT=production
  echo "🚨 IMPORTANT: Running with PRODUCTION database 🚨"
else
  export ENVIRONMENT=${ENVIRONMENT:-development}
  echo "Using development database"
fi

# Detect if running in GitHub Codespaces
if [ -n "$CODESPACE_NAME" ] || [ -n "$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN" ]; then
  echo "Detected GitHub Codespaces environment"

  # Get the Codespace name
  if [ -n "$CODESPACE_NAME" ]; then
    CODESPACE_HOSTNAME="$CODESPACE_NAME"
  else
    CODESPACE_HOSTNAME=$(echo $GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN | cut -d'.' -f1)
  fi

  # Set the environment variables
  export DEV_ENVIRONMENT="codespaces"
  export API_BASE_URL="https://${CODESPACE_HOSTNAME}-8080.app.github.dev"
  export FRONTEND_URL="https://${CODESPACE_HOSTNAME}-3000.app.github.dev"

  echo "Environment variables set:"
  echo "  DEV_ENVIRONMENT=$DEV_ENVIRONMENT"
  echo "  API_BASE_URL=$API_BASE_URL"
  echo "  FRONTEND_URL=$FRONTEND_URL"
else
  echo "Running in local environment"
  export DEV_ENVIRONMENT="local"
fi

export NODE_ENV=development

echo "Starting services with Docker Compose..."
$DOCKER_COMPOSE_CMD up
