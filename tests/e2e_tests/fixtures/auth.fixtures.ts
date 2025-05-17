import { test as base } from '@playwright/test';

// Define admin credentials type
export type AdminCredentials = {
  username: string;
  password: string;
};

// Define player credentials type
export type PlayerCredentials = {
  username: string;
  password: string;
};

// Extend the test with fixtures
export const test = base.extend<{
  adminCredentials: AdminCredentials;
  playerCredentials: PlayerCredentials;
}>({
  // Default admin credentials for testing
  adminCredentials: {
    username: 'admin',
    password: 'admin', // Changed from 'admin123'
  },

  // Default player credentials for testing
  playerCredentials: {
    username: 'test_player',
    password: 'test_player123',
  },
});

export { expect } from '@playwright/test';
