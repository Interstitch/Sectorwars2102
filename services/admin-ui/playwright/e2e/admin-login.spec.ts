import { test, expect } from '../fixtures/auth.fixtures';
import { loginAsAdmin } from '../utils/auth.utils';

test.describe('Admin Authentication', () => {
  test('should display the login page correctly', async ({ page }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Verify the login page elements are visible
    await expect(page.locator('.login-form')).toBeVisible();
    await expect(page.locator('h2')).toContainText('Admin Login');
    
    // Verify form fields are present
    await expect(page.locator('#username')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
    await expect(page.locator('.login-button')).toBeVisible();
  });

  test('should login successfully with admin credentials', async ({ page, adminCredentials }) => {
    // Navigate to login page
    await page.goto('/login');
    
    // Fill in the login form
    await page.fill('#username', adminCredentials.username);
    await page.fill('#password', adminCredentials.password);
    
    // Submit the form
    await page.click('.login-button');
    
    // Verify redirect to dashboard
    await expect(page).toHaveURL(/.*dashboard/);
    
    // Verify user info is displayed (adjust these selectors based on your actual UI)
    const userInfo = page.locator('.user-profile');
    await expect(userInfo).toBeVisible();
    await expect(userInfo.locator('.username')).toContainText(adminCredentials.username);
  });

  test('should logout successfully after login', async ({ page, adminCredentials }) => {
    // First login as admin
    await loginAsAdmin(page, adminCredentials.username, adminCredentials.password);
    
    // Verify we're on the dashboard
    await expect(page).toHaveURL(/.*dashboard/);
    
    // Find and click the logout button
    await page.click('.logout-button');
    
    // Verify redirect to login page
    await expect(page).toHaveURL(/.*login/);
    
    // Verify login form is displayed again
    await expect(page.locator('.login-form')).toBeVisible();
  });
});
