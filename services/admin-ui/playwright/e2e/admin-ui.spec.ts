import { test, expect } from '@playwright/test';

test.describe('Admin UI', () => {
  test('should load the login page correctly', async ({ page }) => {
    // Navigate to the base URL
    await page.goto('/');
    
    // Since we're not authenticated, we should be redirected to login
    await expect(page).toHaveURL(/.*login/);
    
    // Check that the login form is visible
    await expect(page.locator('.login-form')).toBeVisible();
    
    // Check that the app title is displayed
    await expect(page.locator('.login-header h1')).toContainText('Sector Wars 2102');
    await expect(page.locator('.login-header .subtitle')).toContainText('Admin Portal');
  });
});
