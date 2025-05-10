#!/bin/bash

# Environment detection script for Sector Wars 2102
# Automatically detects the current environment and starts the appropriate services

# Function to detect environment
detect_environment() {
  if [ -n "$REPL_ID" ] || [ -n "$REPL_SLUG" ]; then
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

# Check if .env file exists, create from example if not
if [ ! -f .env ]; then
  echo "Creating .env file from example..."
  cp .env.example .env
  echo "Created .env file from example. Please review the settings."
fi

# Set environment variables based on detected environment
case "$DEV_ENVIRONMENT" in
  "replit")
    echo "Starting services in Replit environment..."
    export ENVIRONMENT=replit
    export NODE_ENV=development
    
    # Start services with Replit-specific configuration
    docker-compose -f docker-compose.yml -f docker-compose.replit.yml up
    ;;
    
  "codespaces")
    echo "Starting services in GitHub Codespaces environment..."
    export ENVIRONMENT=development
    export NODE_ENV=development
    
    # Start services with standard configuration
    docker-compose up
    ;;
    
  "local")
    echo "Starting services in local environment..."
    export ENVIRONMENT=development
    export NODE_ENV=development
    
    # Start services with standard configuration
    docker-compose up
    ;;
    
  *)
    echo "Unknown environment: $DEV_ENVIRONMENT"
    echo "Please set DEV_ENVIRONMENT to 'local', 'codespaces', or 'replit'"
    exit 1
    ;;
esac