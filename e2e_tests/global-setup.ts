import path from 'path';
import { createTestAdmin, createTestPlayer, initTestAccountManager } from './utils/test_account_manager';
import * as dotenv from 'dotenv';

/**
 * Global setup function that runs before all tests
 */
async function globalSetup() {
  console.log('=== Global Setup: Creating test accounts for this test run ===');
  
  try {
    // Load environment variables from .env file if available
    const envPath = path.resolve(process.cwd(), '.env');
    console.log(`Looking for .env file at: ${envPath}`);
    
    if (dotenv.config({ path: envPath }).parsed) {
      console.log('Loaded environment variables from .env file');
    } else {
      console.log('No .env file found or it was empty, using existing environment variables');
    }
    
    // Initialize the test account manager
    console.log('Initializing test account manager...');
    initTestAccountManager();
    
    // Create test admin account
    console.log('Creating test admin account...');
    const admin = createTestAdmin();
    console.log(`Test admin account created: ${admin.username}`);
    
    // Create test player account
    console.log('Creating test player account...');
    const player = createTestPlayer();
    console.log(`Test player account created: ${player.username}`);
    
    console.log('=== Test accounts created successfully ===');
  } catch (error) {
    console.error('Failed to create test accounts:', error);
    console.error(error instanceof Error ? error.stack : 'Unknown error');
    throw error;
  }
}

export default globalSetup;