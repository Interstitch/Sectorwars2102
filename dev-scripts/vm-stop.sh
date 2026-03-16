#!/bin/bash
# Stop the sectorwars-dev GCP VM
set -e

echo "Stopping sectorwars-dev VM..."
gcloud compute instances stop sectorwars-dev --project=sectorwars2102 --zone=us-central1-a
echo "VM stopped. No more compute charges."
