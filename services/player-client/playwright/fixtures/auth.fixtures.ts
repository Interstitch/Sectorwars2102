import { test as base } from '@playwright/test';

/**
 * Player credentials for testing
 */
export type PlayerCredentials = {
  username: string;
  password: string;
};

/**
 * GitHub OAuth credentials for testing
 */
export type GitHubCredentials = {
  username: string;
  email: string;
  mockToken: string;
};

/**
 * Extend the base test fixture with player credentials
 */
export const test = base.extend<{
  playerCredentials: PlayerCredentials;
  githubCredentials: GitHubCredentials;
}>({
  // Default player credentials for testing
  playerCredentials: {
    username: 'testplayer',
    password: 'password123',
  },
  
  // Default GitHub OAuth credentials for testing
  githubCredentials: {
    username: 'github-user',
    email: 'github-user@example.com',
    mockToken: 'mock-github-token',
  },
});

export { expect } from '@playwright/test';
