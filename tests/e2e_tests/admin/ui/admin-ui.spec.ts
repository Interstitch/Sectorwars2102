import { test, expect } from '@playwright/test';
import { test as authTest } from '../../fixtures/auth.fixtures';
import { loginAsAdmin, logout } from '../../utils/auth.utils';

test.describe('Admin UI - Login', () => {
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
  
  authTest('should login successfully with valid credentials', async ({ page, adminCredentials }) => {
    // Use the helper function to log in
    await loginAsAdmin(page, adminCredentials);
    
    // Verify we're on the dashboard
    await expect(page.url()).toContain('/dashboard');
    
    // The page title is in a PageHeader component, not a .page-title element
    await expect(page.locator('h1')).toContainText('Dashboard');
  });
  
  test('should show error with invalid credentials', async ({ page }) => {
    await page.goto('/login');
    
    // Enter invalid credentials
    await page.fill('#username', 'wronguser');
    await page.fill('#password', 'wrongpass');
    await page.click('.login-button');
    
    // Verify error message is displayed
    await expect(page.locator('.error-message')).toBeVisible();
    await expect(page.locator('.error-message')).toContainText('Login error');
    
    // Verify we're still on the login page
    await expect(page.url()).toContain('/login');
  });
});

test.describe('Admin UI - Dashboard', () => {
  authTest.beforeEach(async ({ page, adminCredentials }) => {
    // Log in before each test in this suite
    await loginAsAdmin(page, adminCredentials);
  });
  
  authTest('should display galaxy overview section', async ({ page }) => {
    // Verify the welcome section is present with expected title
    await expect(page.locator('.welcome-section h2')).toContainText('Galaxy Administration');
  });
  
  authTest('should display quick access cards', async ({ page }) => {
    // Verify quick access cards are present
    await expect(page.locator('.admin-cards h3')).toContainText('Quick Access');
    await expect(page.locator('.card-grid')).toBeVisible();
    
    // Verify there are 4 quick access cards
    await expect(page.locator('.admin-card')).toHaveCount(4);
  });
  
  authTest('should logout successfully', async ({ page }) => {
    // Use the helper function to log out
    await logout(page);
    
    // Verify we're back at the login page
    await expect(page.url()).toContain('/login');
  });
});
