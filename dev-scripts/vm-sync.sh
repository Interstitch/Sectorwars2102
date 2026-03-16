#!/bin/bash
# Sync code to the remote VM via git push + pull
# Uses the 'dev' branch for development iteration
set -e

REMOTE="mrathbone@100.64.208.28"
REMOTE_PATH="/home/mrathbone/sectorwars2102"

# Check we're on dev branch
BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "dev" ]; then
  echo "WARNING: Not on dev branch (currently on '$BRANCH')"
  echo "Switch to dev first: git checkout dev"
  exit 1
fi

# Check for uncommitted changes
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "You have uncommitted changes. Commit them first."
  echo ""
  git status --short
  exit 1
fi

# Push to remote
echo "Pushing dev branch to origin..."
git push origin dev

# Pull on VM
echo "Pulling on VM..."
ssh "$REMOTE" "cd $REMOTE_PATH && git pull origin dev"

echo ""
echo "Sync complete. Services will hot-reload automatically."
echo "If you need to rebuild containers: ssh $REMOTE 'cd $REMOTE_PATH && docker compose --profile development up -d --build'"
