#!/usr/bin/env node

/**
 * Script to run Playwright tests against Docker container
 * and ensure the process exits cleanly after showing the report
 */

const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// Paths
const reportDir = path.join(__dirname, '..', 'playwright-report');
const configPath = path.join(__dirname, '..', 'playwright.docker.config.ts');

console.log('Running e2e tests against Docker container...');

try {
  // Run Playwright tests
  execSync(`npx playwright test --config="${configPath}" --reporter=line --project=chromium`, {
    stdio: 'inherit'
  });
  
  // Check if the report directory exists
  if (fs.existsSync(reportDir)) {
    console.log('\n📊 Test report is ready. Opening report...');
    
    // Determine port for report server
    const port = process.env.PORT || 9323;
    
    // Show the report for a fixed amount of time, then exit
    const baseUrl = `http://localhost:${port}`;
    
    // Use a background process with a timeout to show the report briefly then exit
    execSync(`
      npx playwright show-report --port=${port} > /dev/null 2>&1 & 
      PID=$!
      echo "📊 Test report available at: ${baseUrl}"
      echo "   Report will be available for 10 seconds."
      
      # Wait for 10 seconds
      sleep 10
      
      # Kill the report server and exit
      kill $PID 2>/dev/null || true
      echo "⏱️ Report server stopped."
      exit 0
    `, { 
      stdio: 'inherit',
      shell: true
    });
  } else {
    console.log('No test report generated.');
    process.exit(0);
  }
} catch (error) {
  console.error('Error running tests:', error.message);
  process.exit(1);
}
