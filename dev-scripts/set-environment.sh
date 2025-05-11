#!/bin/bash
# Script to set the application environment (development or production)

# Default to development if no argument is provided
ENV="${1:-development}"

# Convert to lowercase
ENV=$(echo "$ENV" | tr '[:upper:]' '[:lower:]')

# Validate the environment value
if [[ "$ENV" != "development" && "$ENV" != "production" && "$ENV" != "test" ]]; then
  echo "Error: Invalid environment. Use 'development', 'production', or 'test'."
  exit 1
fi

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$REPO_ROOT/.env"

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
  echo "Error: .env file not found at $ENV_FILE"
  exit 1
fi

# Update the ENVIRONMENT value in the .env file
if grep -q "^ENVIRONMENT=" "$ENV_FILE"; then
  sed -i "s/^ENVIRONMENT=.*/ENVIRONMENT=$ENV/" "$ENV_FILE"
else
  # If ENVIRONMENT line doesn't exist, add it after API Server section
  sed -i "/# API Server/a ENVIRONMENT=$ENV" "$ENV_FILE"
fi

# Update DEBUG value based on environment
if [ "$ENV" == "production" ]; then
  sed -i "s/^DEBUG=.*/DEBUG=false/" "$ENV_FILE"
else
  sed -i "s/^DEBUG=.*/DEBUG=true/" "$ENV_FILE"
fi

# Update the NODE_ENV value for frontend
if grep -q "^NODE_ENV=" "$ENV_FILE"; then
  sed -i "s/^NODE_ENV=.*/NODE_ENV=$ENV/" "$ENV_FILE"
fi

echo "Environment set to $ENV"

# Set appropriate security settings for production
if [ "$ENV" == "production" ]; then
  echo "Configuring production security settings..."
  
  # Set secure cookies to true for production
  if grep -q "^SECURE_COOKIES=" "$ENV_FILE"; then
    sed -i "s/^SECURE_COOKIES=.*/SECURE_COOKIES=true/" "$ENV_FILE"
  else
    echo "SECURE_COOKIES=true" >> "$ENV_FILE"
  fi
  
  # Remind about JWT secret
  echo "REMINDER: For production, make sure to set a strong JWT_SECRET in the .env file"
else
  # Set secure cookies to false for non-production environments
  if grep -q "^SECURE_COOKIES=" "$ENV_FILE"; then
    sed -i "s/^SECURE_COOKIES=.*/SECURE_COOKIES=false/" "$ENV_FILE"
  else
    echo "SECURE_COOKIES=false" >> "$ENV_FILE"
  fi
fi

echo "Configuration complete."