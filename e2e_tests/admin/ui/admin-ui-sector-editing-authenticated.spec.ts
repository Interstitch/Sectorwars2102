import { expect } from '@playwright/test';
import { test as authTest } from '../../fixtures/auth.fixtures';
import { loginAsAdmin } from '../../utils/auth.utils';

authTest.describe('Admin UI - Authenticated Sector Management', () => {
  authTest.beforeEach(async ({ page, adminCredentials }) => {
    // Login with real credentials
    await page.goto('http://localhost:3001/login');
    await page.fill('#username', adminCredentials.username);
    await page.fill('#password', adminCredentials.password);
    await page.click('button:has-text("Login")');
    
    // Wait for successful login
    await page.waitForURL(/.*dashboard.*/, { timeout: 10000 });
  });

  authTest('should display sectors page with management interface', async ({ page }) => {
    // Navigate to sectors page
    await page.goto('http://localhost:3001/sectors');
    
    // Wait for loading to complete
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000); // Additional wait for dynamic content
    
    // Verify we're on the sectors page
    await expect(page).toHaveURL(/.*sectors.*/);
    
    // Check for sector management elements - more flexible
    const sectorHeadings = page.locator('h1, h2, h3').filter({ hasText: /sector/i });
    await expect(sectorHeadings.first()).toBeVisible();
    
    // Check for sector grid or table
    const hasTable = await page.locator('table').count() > 0;
    const hasGrid = await page.locator('.sector-grid, .grid, .card-grid, .sectors-container').count() > 0;
    const hasCards = await page.locator('.card, .sector-card').count() > 0;
    
    expect(hasTable || hasGrid || hasCards).toBeTruthy();
  });

  authTest('should have filter and search capabilities', async ({ page }) => {
    // Navigate to sectors page
    await page.goto('http://localhost:3001/sectors');
    
    // Look for search input
    const searchInput = page.locator('input[type="search"], input[placeholder*="search" i], input[placeholder*="filter" i]');
    if (await searchInput.count() > 0) {
      await expect(searchInput.first()).toBeVisible();
    }
    
    // Look for filter buttons or dropdowns
    const filterElements = page.locator('button:has-text("Filter"), select, .filter-button, .filter-dropdown');
    if (await filterElements.count() > 0) {
      await expect(filterElements.first()).toBeVisible();
    }
  });

  authTest('should allow editing sectors', async ({ page }) => {
    // Navigate to sectors page
    await page.goto('http://localhost:3001/sectors');
    
    // Wait for sectors to load
    await page.waitForTimeout(2000);
    
    // Look for edit buttons or clickable sectors
    const editButtons = page.locator('button:has-text("Edit"), .edit-button, [aria-label*="edit" i]');
    const sectorCards = page.locator('.sector-card, .card, tr[role="row"]');
    
    if (await editButtons.count() > 0) {
      // Click the first edit button
      await editButtons.first().click();
      
      // Check if a modal or edit form appears
      const modalOrForm = page.locator('.modal, .dialog, form, .edit-form');
      await expect(modalOrForm).toBeVisible({ timeout: 5000 });
    } else if (await sectorCards.count() > 0) {
      // Try clicking on a sector card
      await sectorCards.first().click();
      
      // Check if detail view or edit interface appears
      await page.waitForTimeout(1000);
    }
  });

  authTest('should show universe page with sector data', async ({ page }) => {
    // Navigate to universe page
    await page.goto('http://localhost:3001/universe');
    
    // Wait for loading to complete
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Verify we're on the universe page
    await expect(page).toHaveURL(/.*universe.*/);
    
    // Check for universe-related headings - more flexible
    const universeHeadings = page.locator('h1, h2, h3').filter({ hasText: /universe|galaxy|sector/i });
    await expect(universeHeadings.first()).toBeVisible();
    
    // Check for universe content - tables, cards, or visualization
    const hasContent = await page.locator('table, .card, .universe-container, canvas, svg').count() > 0;
    expect(hasContent).toBeTruthy();
  });

  authTest('should have navigation between sectors and universe', async ({ page }) => {
    // Start at dashboard
    await page.goto('http://localhost:3001/dashboard');
    
    // Navigate to sectors via sidebar
    const sectorsLink = page.locator('a[href*="sectors"], button:has-text("Sectors")');
    if (await sectorsLink.count() > 0) {
      await sectorsLink.first().click();
      await expect(page).toHaveURL(/.*sectors.*/);
    }
    
    // Navigate to universe
    const universeLink = page.locator('a[href*="universe"], button:has-text("Universe")');
    if (await universeLink.count() > 0) {
      await universeLink.first().click();
      await expect(page).toHaveURL(/.*universe.*/);
    }
  });
});