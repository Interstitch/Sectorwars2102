import { expect } from '@playwright/test';
import { test as authTest } from '../../fixtures/auth.fixtures';

authTest.describe('Admin UI - Sector Management', () => {
  // Test basic authentication and navigation
  authTest('should require authentication for sector pages', async ({ page }) => {
    // Try to access sectors page directly
    await page.goto('http://localhost:3001/sectors');
    
    // Should redirect to login page
    await expect(page).toHaveURL(/.*login.*/);
    await expect(page.locator('text=Admin Login')).toBeVisible();
  });

  authTest('should show login form with correct elements', async ({ page }) => {
    // Navigate to login page
    await page.goto('http://localhost:3001/login');
    
    // Verify login form elements
    await expect(page.locator('#username')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
    await expect(page.locator('button:has-text("Login")')).toBeVisible();
    
    // Check for additional UI elements
    await expect(page.locator('text=Admin Portal')).toBeVisible();
    await expect(page.locator('h1:has-text("Sector Wars 2102")')).toBeVisible();
  });

  authTest('should display error for invalid credentials', async ({ page }) => {
    // Navigate to login page
    await page.goto('http://localhost:3001/login');
    
    // Enter invalid credentials
    await page.fill('#username', 'wronguser');
    await page.fill('#password', 'wrongpass');
    await page.click('button:has-text("Login")');
    
    // Should show error message
    await expect(page.locator('.alert-error')).toBeVisible();
    await expect(page.locator('.alert-error')).toContainText(/invalid|error/i);
  });

  authTest('should have correct page structure on login page', async ({ page }) => {
    // Navigate to login page
    await page.goto('http://localhost:3001/login');
    
    // Check page structure
    await expect(page.locator('.login-container, .login-form, form')).toBeVisible();
    
    // Check for API info message
    const apiInfo = page.locator('text=Using API at');
    if (await apiInfo.count() > 0) {
      await expect(apiInfo).toBeVisible();
    }
    
    // Check for default credentials info
    const defaultCreds = page.locator('text=Default credentials');
    if (await defaultCreds.count() > 0) {
      await expect(defaultCreds).toBeVisible();
    }
  });

  authTest('universe page requires authentication', async ({ page }) => {
    // Try to access universe page directly
    await page.goto('http://localhost:3001/universe');
    
    // Should redirect to login page
    await expect(page).toHaveURL(/.*login.*/);
  });

  authTest('all admin routes are protected', async ({ page }) => {
    // Test multiple protected routes
    const protectedRoutes = [
      '/dashboard',
      '/universe',
      '/sectors',
      '/users',
      '/players',
      '/analytics'
    ];
    
    for (const route of protectedRoutes) {
      await page.goto(`http://localhost:3001${route}`);
      await expect(page).toHaveURL(/.*login.*/);
    }
  });

  authTest('login page has proper form validation', async ({ page }) => {
    // Navigate to login page
    await page.goto('http://localhost:3001/login');
    
    // Try to submit empty form
    await page.click('button:has-text("Login")');
    
    // Check if browser validation or custom validation appears
    // The form should not submit with empty fields
    await expect(page).toHaveURL(/.*login.*/);
  });

  authTest('test direct API button functionality', async ({ page }) => {
    // Navigate to login page
    await page.goto('http://localhost:3001/login');
    
    // Check if Test Direct API button exists
    const testApiButton = page.locator('button:has-text("Test Direct API")');
    const hasTestButton = await testApiButton.count() > 0;
    
    if (hasTestButton) {
      await expect(testApiButton).toBeVisible();
      // Click it to test API connectivity
      await testApiButton.click();
      
      // Wait a moment for any response
      await page.waitForTimeout(1000);
      
      // The page should still be on login (unless API test logs in)
      expect(page.url()).toContain('login');
    }
  });
});