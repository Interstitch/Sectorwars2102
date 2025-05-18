import { createTestAdmin, createTestPlayer, initTestAccountManager } from './utils/test_account_manager';

/**
 * Global setup function that runs before all tests
 */
async function globalSetup() {
  console.log('=== Global Setup: Creating test accounts for this test run ===');
  try {
    // Initialize the test account manager
    initTestAccountManager();
    
    // Create test admin account
    const admin = createTestAdmin();
    console.log(`Test admin account created: ${admin.username}`);
    
    // Create test player account
    const player = createTestPlayer();
    console.log(`Test player account created: ${player.username}`);
    
    console.log('=== Test accounts created successfully ===');
  } catch (error) {
    console.error('Failed to create test accounts:', error);
    throw error;
  }
}

export default globalSetup; 