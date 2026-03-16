#!/bin/bash
# Sync local code to the remote VM via Tailscale
set -e

REMOTE="mrathbone@100.64.208.28"
REMOTE_PATH="/home/mrathbone/sectorwars2102/"
LOCAL_PATH="$(cd "$(dirname "$0")/.." && pwd)/"

echo "Syncing code to VM..."
rsync -avz --delete \
  --exclude 'node_modules' \
  --exclude '.git' \
  --exclude '__pycache__' \
  --exclude '.env' \
  --exclude 'postgres_data' \
  --exclude '.next' \
  --exclude 'dist' \
  --exclude 'build' \
  "$LOCAL_PATH" "$REMOTE:$REMOTE_PATH"

echo "Sync complete. SSH in and restart containers if needed:"
echo "  ssh $REMOTE"
echo "  cd sectorwars2102 && docker compose up -d"
