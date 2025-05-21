// This is a special configuration file for VS Code Test Explorer
import { defineConfig, devices } from '@playwright/test';
import path from 'path';
import dotenv from 'dotenv';

// Try to load environment variables from .env file
const envPath = path.resolve(process.cwd(), '.env');
dotenv.config({ path: envPath });

// Get URLs from environment variables or use defaults
const ADMIN_UI_URL = process.env.ADMIN_UI_URL || 'http://localhost:3001';
const PLAYER_UI_URL = process.env.PLAYER_UI_URL || 'http://localhost:3000';

console.log(`Test Explorer using Admin UI URL: ${ADMIN_UI_URL}`);
console.log(`Test Explorer using Player UI URL: ${PLAYER_UI_URL}`);

export default defineConfig({
  fullyParallel: true,
  reporter: 'list', // Use list reporter for VS Code Test Explorer integration
  use: {
    // Base config for all tests
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  // Global setup and teardown
  globalSetup: path.join(__dirname, 'global-setup.ts'),
  globalTeardown: path.join(__dirname, 'global-teardown.ts'),
  projects: [
    {
      name: 'admin-tests',
      testDir: './',
      testMatch: '**/admin/**/*.spec.ts',
      use: {
        ...devices['Desktop Chrome'],
        baseURL: ADMIN_UI_URL,
      },
    },
    {
      name: 'player-tests',
      testDir: './',
      testMatch: '**/player/**/*.spec.ts',
      use: {
        ...devices['Desktop Chrome'],
        baseURL: PLAYER_UI_URL,
      },
    },
  ],
});
