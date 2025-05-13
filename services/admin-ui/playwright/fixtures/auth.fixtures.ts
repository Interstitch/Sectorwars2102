import { test as base } from '@playwright/test';

// Define custom fixture types
type AuthFixtures = {
  adminCredentials: { username: string; password: string };
};

// Extend the base test fixtures with our custom ones
export const test = base.extend<AuthFixtures>({
  // Define adminCredentials fixture
  adminCredentials: async ({}, use) => {
    // You would typically load these from environment variables in real scenarios
    const credentials = {
      username: 'admin',
      password: 'admin'
    };
    
    await use(credentials);
  },
});

export { expect } from '@playwright/test';
