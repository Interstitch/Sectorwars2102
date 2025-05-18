import { test as base, expect } from '@playwright/test';
import { TEST_ACCOUNTS, TestAccount } from '../utils/test_account_manager';

// Export account types for backward compatibility
export type AdminCredentials = {
  username: string;
  password: string;
};

export type PlayerCredentials = {
  username: string;
  password: string;
};

// Extend the test with fixtures
export const test = base.extend<{
  adminCredentials: AdminCredentials;
  playerCredentials: PlayerCredentials;
  testAccounts: { admin: TestAccount | null; player: TestAccount | null };
}>({
  // Use the shared admin account created during global setup
  adminCredentials: async ({}, use) => {
    // Fall back to default credentials if no test account exists
    if (!TEST_ACCOUNTS.admin) {
      console.warn('No test admin account exists! Using default credentials');
      await use({
        username: 'admin',
        password: 'admin',
      });
      return;
    }
    
    await use({
      username: TEST_ACCOUNTS.admin.username,
      password: TEST_ACCOUNTS.admin.password,
    });
  },

  // Use the shared player account created during global setup
  playerCredentials: async ({}, use) => {
    // Fall back to default credentials if no test account exists
    if (!TEST_ACCOUNTS.player) {
      console.warn('No test player account exists! Using default credentials');
      await use({
        username: 'test_player',
        password: 'test_player123',
      });
      return;
    }
    
    await use({
      username: TEST_ACCOUNTS.player.username,
      password: TEST_ACCOUNTS.player.password,
    });
  },
  
  // Provide access to all test accounts
  testAccounts: async ({}, use) => {
    await use(TEST_ACCOUNTS);
  },
});

// Configure retries for flaky tests
test.describe.configure({ retries: 2 });

export { expect };
