import { test, expect } from '@playwright/test';
import { loginAsAdmin } from '../../utils/auth.utils';
import { AdminCredentials } from '../../fixtures/auth.fixtures';

test.describe('Admin UI - Sector Editing', () => {
  test.beforeEach(async ({ page }) => {
    // Log in as admin
    await loginAsAdmin(page, AdminCredentials);
    
    // Navigate to sectors management
    await page.goto('http://localhost:3001/sectors');
    await page.waitForLoadState('networkidle');
  });

  test('should open sector edit modal when clicking Edit button', async ({ page }) => {
    // Wait for sectors to load
    await page.waitForSelector('.sectors-grid-row', { timeout: 10000 });
    
    // Click the first Edit button
    const firstEditButton = page.locator('.edit-button').first();
    await firstEditButton.click();
    
    // Verify modal opens
    await expect(page.locator('.sector-edit-modal')).toBeVisible();
    await expect(page.locator('.modal-header h2')).toContainText('Edit Sector:');
  });

  test('should display tabbed interface with all tabs', async ({ page }) => {
    // Open edit modal
    await page.waitForSelector('.sectors-grid-row', { timeout: 10000 });
    await page.locator('.edit-button').first().click();
    
    await expect(page.locator('.sector-edit-modal')).toBeVisible();
    
    // Check all tabs are present
    await expect(page.locator('.tab-button').filter({ hasText: 'Basic Info' })).toBeVisible();
    await expect(page.locator('.tab-button').filter({ hasText: 'Physical Properties' })).toBeVisible();
    await expect(page.locator('.tab-button').filter({ hasText: 'Discovery' })).toBeVisible();
    await expect(page.locator('.tab-button').filter({ hasText: 'Control' })).toBeVisible();
  });

  test('should allow editing basic sector information', async ({ page }) => {
    // Open edit modal
    await page.waitForSelector('.sectors-grid-row', { timeout: 10000 });
    await page.locator('.edit-button').first().click();
    
    await expect(page.locator('.sector-edit-modal')).toBeVisible();
    
    // Edit sector name
    const nameInput = page.locator('#sector-name');
    await nameInput.clear();
    await nameInput.fill('Test Sector Updated');
    
    // Change sector type
    await page.locator('#sector-type').selectOption('NEBULA');
    
    // Add description
    await page.locator('#sector-description').fill('This is a test sector for E2E testing');
    
    // Verify Save button becomes enabled
    await expect(page.locator('.save-button')).toBeEnabled();
  });

  test('should switch between tabs correctly', async ({ page }) => {
    // Open edit modal
    await page.waitForSelector('.sectors-grid-row', { timeout: 10000 });
    await page.locator('.edit-button').first().click();
    
    await expect(page.locator('.sector-edit-modal')).toBeVisible();
    
    // Click Physical Properties tab
    await page.locator('.tab-button').filter({ hasText: 'Physical Properties' }).click();
    await expect(page.locator('#radiation-level')).toBeVisible();
    await expect(page.locator('#hazard-level')).toBeVisible();
    
    // Click Discovery tab
    await page.locator('.tab-button').filter({ hasText: 'Discovery' }).click();
    await expect(page.locator('input[type="checkbox"]')).toBeVisible();
    
    // Click Control tab
    await page.locator('.tab-button').filter({ hasText: 'Control' }).click();
    await expect(page.locator('#controlling-faction')).toBeVisible();
  });

  test('should handle physical properties sliders', async ({ page }) => {
    // Open edit modal
    await page.waitForSelector('.sectors-grid-row', { timeout: 10000 });
    await page.locator('.edit-button').first().click();
    
    await expect(page.locator('.sector-edit-modal')).toBeVisible();
    
    // Switch to Physical Properties tab
    await page.locator('.tab-button').filter({ hasText: 'Physical Properties' }).click();
    
    // Test radiation level slider
    const radiationSlider = page.locator('#radiation-level');
    await radiationSlider.fill('5.5');
    
    // Test hazard level slider
    const hazardSlider = page.locator('#hazard-level');
    await hazardSlider.fill('7');
    
    // Test resource regeneration slider
    const regenSlider = page.locator('#resource-regen');
    await regenSlider.fill('2.50');
    
    // Verify Save button becomes enabled
    await expect(page.locator('.save-button')).toBeEnabled();
  });

  test('should handle coordinate editing', async ({ page }) => {
    // Open edit modal
    await page.waitForSelector('.sectors-grid-row', { timeout: 10000 });
    await page.locator('.edit-button').first().click();
    
    await expect(page.locator('.sector-edit-modal')).toBeVisible();
    
    // Edit coordinates
    await page.locator('#x-coord').fill('100');
    await page.locator('#y-coord').fill('200');
    await page.locator('#z-coord').fill('50');
    
    // Verify Save button becomes enabled
    await expect(page.locator('.save-button')).toBeEnabled();
  });

  test('should show unsaved changes warning when closing', async ({ page }) => {
    // Open edit modal
    await page.waitForSelector('.sectors-grid-row', { timeout: 10000 });
    await page.locator('.edit-button').first().click();
    
    await expect(page.locator('.sector-edit-modal')).toBeVisible();
    
    // Make a change
    await page.locator('#sector-name').fill('Modified Name');
    
    // Try to close modal
    await page.locator('.close-button').click();
    
    // Should show confirmation dialog
    page.on('dialog', async dialog => {
      expect(dialog.message()).toContain('unsaved changes');
      await dialog.dismiss();
    });
  });

  test('should close modal without warning when no changes made', async ({ page }) => {
    // Open edit modal
    await page.waitForSelector('.sectors-grid-row', { timeout: 10000 });
    await page.locator('.edit-button').first().click();
    
    await expect(page.locator('.sector-edit-modal')).toBeVisible();
    
    // Close without making changes
    await page.locator('.close-button').click();
    
    // Modal should close immediately
    await expect(page.locator('.sector-edit-modal')).not.toBeVisible();
  });

  test('should handle discovery settings', async ({ page }) => {
    // Open edit modal
    await page.waitForSelector('.sectors-grid-row', { timeout: 10000 });
    await page.locator('.edit-button').first().click();
    
    await expect(page.locator('.sector-edit-modal')).toBeVisible();
    
    // Switch to Discovery tab
    await page.locator('.tab-button').filter({ hasText: 'Discovery' }).click();
    
    // Toggle discovery status
    const discoveryCheckbox = page.locator('input[type="checkbox"]');
    await discoveryCheckbox.click();
    
    // Add discovered by ID
    await page.locator('#discovered-by').fill('00000000-0000-0000-0000-000000000001');
    
    // Verify Save button becomes enabled
    await expect(page.locator('.save-button')).toBeEnabled();
  });

  test('should handle control settings', async ({ page }) => {
    // Open edit modal
    await page.waitForSelector('.sectors-grid-row', { timeout: 10000 });
    await page.locator('.edit-button').first().click();
    
    await expect(page.locator('.sector-edit-modal')).toBeVisible();
    
    // Switch to Control tab
    await page.locator('.tab-button').filter({ hasText: 'Control' }).click();
    
    // Set controlling faction
    await page.locator('#controlling-faction').fill('Test Faction');
    
    // Set controlling team
    await page.locator('#controlling-team').fill('00000000-0000-0000-0000-000000000002');
    
    // Verify Save button becomes enabled
    await expect(page.locator('.save-button')).toBeEnabled();
  });

  test('should handle form validation errors', async ({ page }) => {
    // Open edit modal
    await page.waitForSelector('.sectors-grid-row', { timeout: 10000 });
    await page.locator('.edit-button').first().click();
    
    await expect(page.locator('.sector-edit-modal')).toBeVisible();
    
    // Clear required field
    await page.locator('#sector-name').clear();
    
    // Try to save
    await page.locator('.save-button').click();
    
    // Should show error message
    await expect(page.locator('.error-message')).toBeVisible();
  });

  test('should disable Save button when no changes made', async ({ page }) => {
    // Open edit modal
    await page.waitForSelector('.sectors-grid-row', { timeout: 10000 });
    await page.locator('.edit-button').first().click();
    
    await expect(page.locator('.sector-edit-modal')).toBeVisible();
    
    // Save button should be disabled initially
    await expect(page.locator('.save-button')).toBeDisabled();
  });
});