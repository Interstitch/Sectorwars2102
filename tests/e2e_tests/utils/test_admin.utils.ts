import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

/**
 * Creates a temporary admin account for testing purposes
 * @returns {Promise<{username: string, password: string}>} credentials for the created admin
 */
export async function createTestAdmin(): Promise<{username: string, password: string}> {
  // Generate unique username to avoid conflicts
  const randomSuffix = uuidv4().substring(0, 8);
  const username = `test_admin_${randomSuffix}`;
  const password = `testpass_${randomSuffix}`;
  const email = `${username}@test.com`;

  try {
    // Use the test API to create an admin account
    const response = await axios.post(
      'http://localhost:8080/api/v1/test/create-admin',
      {
        username,
        password,
        email
      },
      { validateStatus: () => true }
    );

    if (response.status !== 201 && response.status !== 200) {
      console.error('Failed to create test admin:', response.data);
      throw new Error(`Failed to create test admin: ${response.status} ${JSON.stringify(response.data)}`);
    }

    console.log(`Created test admin: ${username}`);
    return { username, password };
  } catch (error) {
    console.error('Error creating test admin:', error);
    throw error;
  }
}

/**
 * Deletes a test admin account after testing
 * @param {string} username - The username of the admin to delete
 */
export async function deleteTestAdmin(username: string): Promise<void> {
  try {
    // First get the admin user ID
    const usersResponse = await axios.get(
      `http://localhost:8080/api/v1/users?username=${username}`,
      {
        headers: {
          // Use the default admin account to authenticate this request
          Authorization: 'Bearer dummy-token-for-admin' // This will be replaced with a real token in a production environment
        },
        validateStatus: () => true
      }
    );

    // Check if the response has data and it's an array with items
    if (
      usersResponse.status !== 200 || 
      !usersResponse.data || 
      !Array.isArray(usersResponse.data) || 
      usersResponse.data.length === 0
    ) {
      console.log(`Admin ${username} not found or already deleted`);
      return;
    }

    const userId = usersResponse.data[0].id;

    // Delete the admin
    await axios.delete(
      `http://localhost:8080/api/v1/users/${userId}`,
      {
        headers: {
          Authorization: 'Bearer dummy-token-for-admin' // This will be replaced with a real token in a production environment
        },
        validateStatus: () => true
      }
    );

    console.log(`Deleted test admin: ${username}`);
  } catch (error) {
    console.error(`Error deleting test admin ${username}:`, error);
    // Don't rethrow - we don't want test cleanup to cause test failures
  }
} 