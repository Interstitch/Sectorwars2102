import { defineConfig, devices } from '@playwright/test';
import path from 'path';
import { TEST_ACCOUNTS, createTestAdmin, createTestPlayer, cleanupAllTestAccounts, initTestAccountManager } from './utils/test_account_manager';

/**
 * Global setup - runs once before all tests
 * Creates test accounts for the test run
 */
async function globalSetup() {
  console.log('=== Global Setup: Creating test accounts for this test run ===');
  try {
    // Initialize the test account manager
    initTestAccountManager();
    
    // Create test admin account
    const admin = createTestAdmin();
    console.log(`Test admin account created: ${admin.username}`);
    
    // Create test player account
    const player = createTestPlayer();
    console.log(`Test player account created: ${player.username}`);
    
    console.log('=== Test accounts created successfully ===');
  } catch (error) {
    console.error('Failed to create test accounts:', error);
    throw error;
  }
}

/**
 * Global teardown - runs once after all tests complete
 * Cleans up test accounts created during setup
 */
async function globalTeardown() {
  console.log('=== Global Teardown: Cleaning up test accounts ===');
  try {
    cleanupAllTestAccounts();
    console.log('=== Test accounts cleaned up ===');
  } catch (error) {
    console.error('Failed to clean up test accounts:', error);
    // Don't throw error during teardown to avoid masking test failures
  }
}

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
    timeout: 10000,
  },
  
  // Don't fail the test run if some tests are retries
  retries: 1,
  
  // Limit the number of failures before stopping the run
  maxFailures: 5,
  
  // Reporter to use
  reporter: [
    ['html', { outputFolder: './playwright-reports', open: 'never' }],
    ['list']
  ],
  
  // Shared settings for all projects
  use: {
    // Base URL for navigation
    baseURL: 'http://localhost:3001',
    
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
        // Storage state is no longer needed as we now use direct auth
      },
      testMatch: '**/admin/**/*.spec.ts',
      testIgnore: /.*\.demo\.spec\.ts$/
    },
    {
      name: 'player-tests',
      use: { 
        ...devices['Desktop Chrome'],
        // Storage state is no longer needed as we now use direct auth
      },
      testMatch: '**/player/**/*.spec.ts',
      testIgnore: /.*\.demo\.spec\.ts$/
    },
  ],
});
