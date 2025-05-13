import { test, expect } from '../fixtures/auth.fixtures';
import { loginAsAdmin } from '../utils/auth.utils';

test.describe('Admin Logout Functionality', () => {
  
  test.beforeEach(async ({ page, adminCredentials }) => {
    // Login as admin before each test
    await loginAsAdmin(page, adminCredentials.username, adminCredentials.password);
    
    // Verify we're on the dashboard
    await expect(page).toHaveURL(/.*dashboard/);
    await expect(page.locator('h2')).toContainText('Universe Administration');
  });

  test('should redirect to login page after logout from dashboard', async ({ page }) => {
    // Verify we're logged in (dashboard visible)
    await expect(page.locator('main')).toBeVisible();
    
    // Find and click the logout button in the sidebar
    const logoutButton = page.locator('aside').locator('.logout-button');
    await expect(logoutButton).toBeVisible();
    await logoutButton.click();
    
    // Verify redirect to login page
    await expect(page).toHaveURL(/.*login/);
    
    // Verify login form is displayed
    await expect(page.locator('.login-form')).toBeVisible();
    
    // Verify we cannot access protected routes after logout
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/.*login/); // Should redirect back to login
  });

  test('should logout successfully from any admin page', async ({ page }) => {
    // Navigate to Users page
    await page.getByText('Users').first().click();
    await expect(page).toHaveURL(/.*users/);
    
    // Click logout from sidebar
    await page.locator('aside').locator('.logout-button').click();
    
    // Verify redirect to login
    await expect(page).toHaveURL(/.*login/);
    await expect(page.locator('.login-form')).toBeVisible();
  });

  test('should clear authentication state after logout', async ({ page, adminCredentials }) => {
    // Logout
    await page.locator('aside').locator('.logout-button').click();
    await expect(page).toHaveURL(/.*login/);
    
    // Try to access protected route
    await page.goto('/users');
    
    // Should be redirected to login
    await expect(page).toHaveURL(/.*login/);
    
    // Log back in to verify we can authenticate again
    await page.fill('#username', adminCredentials.username);
    await page.fill('#password', adminCredentials.password);
    await page.click('.login-button');
    
    // Verify successful login
    await expect(page).toHaveURL(/.*dashboard/);
  });
  
  test('should prevent browser back navigation after logout', async ({ page }) => {
    // Capture current URL for later comparison
    const dashboardUrl = page.url();
    
    // Logout
    await page.locator('aside').locator('.logout-button').click();
    await expect(page).toHaveURL(/.*login/);
    
    // Try to navigate back using browser history
    await page.goBack();
    
    // We should not be allowed back to the dashboard
    // Either we stay at login or get redirected back to login
    await expect(page).not.toHaveURL(dashboardUrl);
    await expect(page.locator('.login-form')).toBeVisible();
  });
  
  test('should logout successfully using the button next to username', async ({ page }) => {
    // Verify we're logged in (dashboard visible)
    await expect(page.locator('main')).toBeVisible();
    
    // Find and click the logout button next to the username in the main header
    const headerLogoutButton = page.locator('main').locator('.logout-button');
    await expect(headerLogoutButton).toBeVisible();
    await headerLogoutButton.click();
    
    // Verify redirect to login page
    await expect(page).toHaveURL(/.*login/);
    
    // Verify login form is displayed
    await expect(page.locator('.login-form')).toBeVisible();
    
    // Verify we cannot access protected routes after logout
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/.*login/); // Should redirect back to login
  });
});
