import { Page } from '@playwright/test';

/**
 * Helper functions for handling authentication in tests
 */
export async function loginAsAdmin(page: Page, username: string, password: string): Promise<void> {
  await page.goto('/login');
  await page.fill('#username', username);
  await page.fill('#password', password);
  await page.click('.login-button');
  
  // Wait for navigation to complete
  await page.waitForURL(/.*dashboard/);
}

export async function logout(page: Page): Promise<void> {
  // Find and click the logout button
  await page.click('.logout-button');
  
  // Wait for navigation to login page
  await page.waitForURL(/.*login/);
}
