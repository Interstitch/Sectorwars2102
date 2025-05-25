#!/bin/bash
# Run player-client e2e tests directly

cd /workspaces/Sectorwars2102/services/player-client
npx playwright test --project=chromium
