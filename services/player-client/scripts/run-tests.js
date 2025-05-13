#!/usr/bin/env node

/**
 * Custom script to run Playwright tests and handle environment detection
 */

const { execSync } = require('child_process');
const os = require('os');

// Get the hostname and check environment
const getBaseUrl = () => {
  // Check for Codespaces environment
  if (process.env.CODESPACE_NAME) {
    return `https://${process.env.CODESPACE_NAME}-9323.${process.env.GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}`;
  }
  
  // Check for Replit environment
  if (process.env.REPL_ID || process.env.REPL_SLUG) {
    try {
      // Try to get Replit URL using webcontainer env vars
      const replitHostname = process.env.REPL_SLUG ? 
        `${process.env.REPL_SLUG}.${process.env.REPL_OWNER}.repl.co` : 
        `${process.env.REPL_ID}.id.repl.co`;
      return `https://${replitHostname}`;
    } catch (error) {
      console.error('Error getting Replit URL:', error);
    }
  }
  
  // Fallback to localhost (for local development)
  return 'http://localhost:9323';
};

try {
  console.log('Running Playwright tests...');
  
  // Run tests with line reporter and only in Chromium to avoid browser installation issues
  execSync('npx playwright test -c playwright.config.ts --reporter=line --project=chromium', { 
    stdio: 'inherit' 
  });
  
  // Generate HTML report and keep it running indefinitely
  const baseUrl = getBaseUrl();
  
  console.log(`\n📊 Test report is being generated...`);
  
  // !!!IMPORTANT!!! DO NOT MODIFY THIS SECTION !!!IMPORTANT!!!
  // This deliberately keeps the report server running indefinitely until manually terminated
  // DO NOT add any automatic termination, timeout, or Ctrl+C prompting here
  // Users should not need to press Ctrl+C to view the report
  console.log(`\n📊 Test report available at: ${baseUrl}`);
  execSync(`npx playwright show-report --port 9323`, { 
    stdio: 'inherit',
    shell: true 
  });
  
} catch (error) {
  console.error('Error running tests:', error.message);
  process.exit(1);
}
