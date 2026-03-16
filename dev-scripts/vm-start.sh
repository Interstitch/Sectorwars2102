#!/bin/bash
# Start the sectorwars-dev GCP VM and wait for Tailscale
set -e

echo "Starting sectorwars-dev VM..."
gcloud compute instances start sectorwars-dev --project=sectorwars2102 --zone=us-central1-a

echo "Waiting for Tailscale to come online..."
for i in {1..30}; do
  if tailscale ping 100.64.208.28 --timeout=2s &>/dev/null; then
    echo "VM is reachable via Tailscale at 100.64.208.28"
    echo ""
    echo "Services will be at:"
    echo "  Player Client: http://100.64.208.28:3000"
    echo "  Admin UI:      http://100.64.208.28:3001"
    echo "  Game Server:   http://100.64.208.28:8080"
    echo ""
    echo "SSH: ssh mrathbone@100.64.208.28"
    exit 0
  fi
  sleep 2
done

echo "Warning: VM started but Tailscale not responding yet. Try again in a minute."
