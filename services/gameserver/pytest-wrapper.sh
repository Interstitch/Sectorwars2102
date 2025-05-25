#!/bin/bash
# Wrapper script to run pytest in Docker container for VS Code Test Explorer

# Change to the workspace directory (parent of gameserver)
cd "$(dirname "$0")/.."

# Run pytest in the gameserver container
docker-compose exec -T gameserver poetry run pytest "$@"