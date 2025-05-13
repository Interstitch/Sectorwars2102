#!/usr/bin/env node

/**
 * Simplified custom script to run Playwright tests
 */

const { execSync } = require('child_process');

try {
  console.log('Running Playwright tests...');
  
  // Run tests with line reporter and only in Chromium to avoid browser installation issues
  execSync('npx playwright test -c playwright.config.ts --reporter=line --project=chromium', { 
    stdio: 'inherit' 
  });
  
  // Generate HTML report with the path
  console.log('\n📊 Test report generated.');
  console.log('   You can view the report with: npx playwright show-report');
  
} catch (error) {
  console.error('Error running tests:', error.message);
  process.exit(1);
}
