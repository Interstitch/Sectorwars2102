import { defineConfig, devices } from '@playwright/test';
import * as path from 'node:path';

// Define process if it doesn't exist
declare const process: {
  env: {
    CI?: string;
  };
};

// Explicitly set the root directory for test discovery
const rootDir = path.resolve(__dirname);

export default defineConfig({
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  testDir: rootDir,
  testMatch: '**/*.spec.ts',
  outputDir: path.join(rootDir, '../test-results'),
  projects: [
    {
      name: 'admin-tests',
      testMatch: '**/admin/**/*.spec.ts',
      use: {
        ...devices['Desktop Chrome'],
        baseURL: 'http://localhost:3001',
        trace: 'on-first-retry',
        screenshot: 'only-on-failure',
        headless: true, // Ensure headless mode is always used
      },
    },
    {
      name: 'player-tests',
      testMatch: '**/player/**/*.spec.ts',
      use: {
        ...devices['Desktop Chrome'],
        baseURL: 'http://localhost:3000',
        trace: 'on-first-retry',
        screenshot: 'only-on-failure',
        headless: true, // Ensure headless mode is always used
      },
    },
  ],
});
