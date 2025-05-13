import { test, expect } from '../fixtures/auth.fixtures';
import { loginAsAdmin } from '../utils/auth.utils';

test.describe('User Management', () => {
  // Define test user information
  const testUser = {
    username: `test-user-${Date.now()}`, // Unique username with timestamp
    email: `test-${Date.now()}@example.com`,
    password: 'Password123!',
    is_admin: false
  };
  
  // Modified test user information for edit test
  const modifiedUser = {
    username: `edited-${testUser.username}`,
    email: `edited-${testUser.email}`,
    is_active: false
  };
  
  test.beforeEach(async ({ page, adminCredentials }) => {
    // Login as admin before each test
    await loginAsAdmin(page, adminCredentials.username, adminCredentials.password);
    
    // Navigate to the User Management page
    await page.getByText('Users').first().click();
    await expect(page).toHaveURL(/.*users/);
    
    // Verify we're on the User Management page
    const usersContainer = page.locator('.users-manager-container');
    await expect(usersContainer).toBeVisible();
    await expect(usersContainer.locator('h2')).toContainText('User Management');
  });

  test('should create, edit, and delete a test user', async ({ page }) => {
    // -------------------------------------------------
    // Step 1: Create a new test user
    // -------------------------------------------------
    
    // Click on "Create User" button
    await page.click('.create-user-button');
    
    // Wait for the create user modal to appear
    const modal = page.locator('.modal-container');
    await expect(modal).toBeVisible();
    await expect(modal.locator('h3')).toContainText('Create New User');
    
    // Fill in the user creation form
    await modal.locator('#username').fill(testUser.username);
    await modal.locator('#email').fill(testUser.email);
    await modal.locator('#password').fill(testUser.password);
    
    // Set admin status if needed (default is false)
    if (testUser.is_admin) {
      await modal.locator('input[type="checkbox"]').check();
    }
    
    // Submit the form
    await modal.locator('button.primary-button').click();
    
    // Wait for the modal to close and the new user to appear in the grid
    await expect(modal).not.toBeVisible();
    
    // Verify the new user appears in the user grid
    const userRow = page.locator('.users-grid-row', { hasText: testUser.username });
    await expect(userRow).toBeVisible();
    await expect(userRow.locator('.grid-cell').nth(0)).toContainText(testUser.username);
    await expect(userRow.locator('.grid-cell').nth(1)).toContainText(testUser.email);
    
    // -------------------------------------------------
    // Step 2: Edit the test user
    // -------------------------------------------------
    
    // Click the edit button for the test user
    await userRow.locator('button', { hasText: 'Edit' }).click();
    
    // Wait for the edit modal to appear
    const editModal = page.locator('.modal-container');
    await expect(editModal).toBeVisible();
    await expect(editModal.locator('h3')).toContainText(`Edit User: ${testUser.username}`);
    
    // Update username
    await editModal.locator('#edit-username').clear();
    await editModal.locator('#edit-username').fill(modifiedUser.username);
    
    // Update email
    await editModal.locator('#edit-email').clear();
    await editModal.locator('#edit-email').fill(modifiedUser.email);
    
    // Toggle active status
    if (!modifiedUser.is_active) {
      await editModal.locator('input[type="checkbox"]').uncheck();
    }
    
    // Save changes
    await editModal.locator('button', { hasText: 'Save Changes' }).click();
    
    // Wait for the modal to close
    await expect(editModal).not.toBeVisible();
    
    // Verify the edited user appears in the user grid with updated values
    const editedUserRow = page.locator('.users-grid-row', { hasText: modifiedUser.username });
    await expect(editedUserRow).toBeVisible();
    await expect(editedUserRow.locator('.grid-cell').nth(0)).toContainText(modifiedUser.username);
    await expect(editedUserRow.locator('.grid-cell').nth(1)).toContainText(modifiedUser.email);
    
    // Verify status has changed - the status should now be "Inactive"
    const statusCell = editedUserRow.locator('.user-status');
    await expect(statusCell).toContainText('Inactive');
    
    // -------------------------------------------------
    // Step 3: Delete the test user
    // -------------------------------------------------
    
    // Click the delete button for the test user
    await editedUserRow.locator('button', { hasText: 'Delete' }).click();
    
    // Wait for the delete confirmation modal to appear
    const deleteModal = page.locator('.modal-container');
    await expect(deleteModal).toBeVisible();
    await expect(deleteModal.locator('h3')).toContainText('Delete User');
    
    // Enter the username to confirm
    await deleteModal.locator('.confirm-input').fill(modifiedUser.username);
    
    // Click the delete button
    await deleteModal.locator('button.delete-button').click();
    
    // Wait for the modal to close
    await expect(deleteModal).not.toBeVisible();
    
    // Verify the user has been removed from the grid
    await expect(page.locator('.users-grid-row', { hasText: modifiedUser.username })).not.toBeVisible();
  });
});
