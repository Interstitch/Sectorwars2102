#!/bin/bash
# Script to test auth endpoints

# Set base URL
GAMESERVER_URL="http://localhost:8080"

# Test login endpoint
echo "Testing direct login endpoint..."
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' \
  -v \
  ${GAMESERVER_URL}/api/v1/auth/login/direct

echo -e "\n\nTesting JSON login endpoint..."
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"username":"admin","password":"admin"}' \
  -v \
  ${GAMESERVER_URL}/api/v1/auth/login/json

echo -e "\n\nTesting form-based login endpoint..."
curl -X POST \
  -F "username=admin" \
  -F "password=admin" \
  -v \
  ${GAMESERVER_URL}/api/v1/auth/login