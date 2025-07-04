#!/usr/bin/env python3
"""Test authentication endpoints to debug OAuth issues"""

import requests
import sys

# Test if the OAuth callback created valid tokens
if len(sys.argv) < 2:
    print("Usage: python test_auth.py <access_token>")
    print("Get the access token from browser's localStorage after OAuth login")
    sys.exit(1)

access_token = sys.argv[1]
api_base = "http://localhost:8080/api/v1"

# Test 1: Check if token is valid
print("Testing /auth/me endpoint...")
response = requests.get(
    f"{api_base}/auth/me",
    headers={"Authorization": f"Bearer {access_token}"}
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    user_data = response.json()
    print(f"User: {user_data}")
    user_id = user_data.get('id')
else:
    print(f"Error: {response.text}")
    sys.exit(1)

# Test 2: Check player state
print("\nTesting /player/state endpoint...")
response = requests.get(
    f"{api_base}/player/state",
    headers={"Authorization": f"Bearer {access_token}"}
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    player_data = response.json()
    print(f"Player: {player_data}")
else:
    print(f"Error: {response.text}")

# Test 3: Check if player exists
print("\nTesting /player/current-ship endpoint...")
response = requests.get(
    f"{api_base}/player/current-ship",
    headers={"Authorization": f"Bearer {access_token}"}
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    ship_data = response.json()
    print(f"Ship: {ship_data}")
else:
    print(f"Error: {response.text}")