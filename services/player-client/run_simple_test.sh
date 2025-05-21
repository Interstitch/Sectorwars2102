#!/bin/bash
# Run the simple API connectivity test and generate results

# Navigate to project directory
cd "$(dirname "$0")"

# Check if we're in a Docker container
if [ -f /.dockerenv ]; then
  echo "Running inside Docker container..."
  
  # Run the Node.js test to check connectivity
  echo "Running Node.js connectivity test..."
  node public/simple-test.js
  
  echo "Test results generated at public/simple-test-results.html"
  echo "Open this page in your browser to view comprehensive test results"
else
  echo "This script should be run inside the Docker container."
  echo "You can run it with: docker-compose exec player-client ./run_simple_test.sh"
fi