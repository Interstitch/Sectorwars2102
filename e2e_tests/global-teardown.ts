import { cleanupAllTestAccounts } from './utils/test_account_manager';

/**
 * Global teardown function that runs after all tests
 */
async function globalTeardown() {
  console.log('=== Global Teardown: Cleaning up test accounts ===');
  try {
    cleanupAllTestAccounts();
    console.log('=== Test accounts cleaned up ===');
  } catch (error) {
    console.error('Failed to clean up test accounts:', error);
    // Don't throw error during teardown to avoid masking test failures
  }
}

export default globalTeardown; 