import { test, expect } from '../fixtures/auth.fixtures';
import { loginAsAdmin } from '../utils/auth.utils';

test.describe('Admin Dashboard', () => {
  // Common setup - login before each test
  test.beforeEach(async ({ page, adminCredentials }) => {
    await loginAsAdmin(page, adminCredentials.username, adminCredentials.password);
    // Verify we're on the dashboard
    await expect(page).toHaveURL(/.*dashboard/);
  });
  
  test('should display game server status correctly', async ({ page }) => {
    // Locate the status section
    const statusSection = page.locator('.status-section');
    await expect(statusSection).toBeVisible();
    
    // Check the heading
    await expect(statusSection.locator('h3')).toContainText('Game Server Status');
    
    // Check the connection status
    const statusIndicator = statusSection.locator('.status-indicator');
    await expect(statusIndicator).toBeVisible();
    
    // This might be either "Connected" or "Error connecting to API" depending on environment
    const statusText = statusIndicator.locator('.status-text');
    await expect(statusText).toBeVisible();
    
    // If connected, verify API info is shown
    if (await statusText.textContent() === 'Connected') {
      const apiInfo = statusSection.locator('.api-info');
      await expect(apiInfo).toBeVisible();
      await expect(apiInfo).toContainText('Message:');
      await expect(apiInfo).toContainText('Environment:');
    }
  });
  
  test('should navigate to User Management and display users', async ({ page }) => {
    // Click on the Users card/link in the dashboard
    await page.getByText('Users').first().click();
    
    // Verify we navigated to the User Management page
    await expect(page).toHaveURL(/.*users/);
    
    // Give the page a moment to load if necessary
    await page.waitForTimeout(1000);
    
    // Check if the user management container exists
    const usersContainer = page.locator('.users-manager-container');
    await expect(usersContainer).toBeVisible();
    
    // Check for the header
    await expect(usersContainer.locator('h2')).toContainText('User Management');
    
    // Verify the users grid is visible
    const usersGrid = page.locator('.users-grid');
    if (await usersGrid.isVisible()) {
      // Check for column headers
      await expect(usersGrid.locator('.users-grid-header')).toBeVisible();
      
      // Look for the username column
      await expect(usersGrid.locator('.grid-cell').first()).toContainText('Username');
    }
  });
});
