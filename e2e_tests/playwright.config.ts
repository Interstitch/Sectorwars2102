import { defineConfig, devices } from '@playwright/test';
import path from 'path';
import dotenv from 'dotenv';

// Try to load environment variables from .env file
const envPath = path.resolve(process.cwd(), '.env');
dotenv.config({ path: envPath });

// Get URLs from environment variables or use defaults
const ADMIN_UI_URL = process.env.ADMIN_UI_URL || 'http://localhost:3001';
const PLAYER_UI_URL = process.env.PLAYER_UI_URL || 'http://localhost:3000';
const API_URL = process.env.API_URL || 'http://localhost:8080';

console.log(`Playwright config using Admin UI URL: ${ADMIN_UI_URL}`);
console.log(`Playwright config using Player UI URL: ${PLAYER_UI_URL}`);
console.log(`Playwright config using API URL: ${API_URL}`);

/**
 * Playwright configuration
 * See https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  // Global setup and teardown
  globalSetup: path.join(__dirname, 'global-setup.ts'),
  globalTeardown: path.join(__dirname, 'global-teardown.ts'),
  
  // Test directory contains all the tests
  testDir: './',
  
  // Maximum time one test can run for
  timeout: 30 * 1000,
  
  // Expect timeout
  expect: {
    timeout: 15000, // Increased timeout for more reliable tests
  },
  
  // Don't fail the test run if some tests are retries
  retries: 2, // Increased retries for more reliable test runs
  
  // Limit the number of failures before stopping the run
  maxFailures: 5,
  
  // Reporter to use
  reporter: [
    ['html', { outputFolder: './playwright-reports', open: 'never' }],
    ['list']
  ],
  
  // Shared settings for all projects
  use: {
    // Base URL for navigation will be overridden in projects
    baseURL: ADMIN_UI_URL,
    
    // Collect trace & screenshots when test fails
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    
    // Browser default settings
    viewport: { width: 1280, height: 720 },
    launchOptions: {
      slowMo: 100,
    },
  },
  
  // Configure projects for different environments
  projects: [
    {
      name: 'admin-tests',
      use: { 
        ...devices['Desktop Chrome'],
        baseURL: ADMIN_UI_URL,
      },
      testMatch: '**/admin/**/*.spec.ts',
      testIgnore: /.*\.demo\.spec\.ts$/
    },
    {
      name: 'player-tests',
      use: { 
        ...devices['Desktop Chrome'],
        baseURL: PLAYER_UI_URL,
      },
      testMatch: '**/player/**/*.spec.ts',
      testIgnore: /.*\.demo\.spec\.ts$/
    },
  ],
});
