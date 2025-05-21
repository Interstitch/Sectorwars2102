/**
 * Script to initialize admin user in the database
 */

const axios = require('axios');

async function createAdminUser() {
  try {
    console.log('Creating admin user...');
    
    // Try to create the admin user via direct API call to gameserver
    const apiUrl = 'http://gameserver:8080';
    
    // 1. First try direct login to see if admin already exists
    try {
      const loginResponse = await axios.post(`${apiUrl}/api/v1/auth/login/direct`, {
        username: 'admin',
        password: 'admin'
      });
      
      console.log('Admin user already exists, login successful!');
      console.log(`Access token received: ${loginResponse.data.access_token?.substring(0, 10)}...`);
      console.log(`Refresh token received: ${loginResponse.data.refresh_token?.substring(0, 10)}...`);
      return;
    } catch (loginError) {
      console.log('Admin login failed, will try to create admin user:', loginError.message);
    }
    
    // 2. If login fails, we might need to create the admin user
    // Note: You would typically need admin credentials to create another admin
    // For initial setup, you might need to modify this to use a special API or command
    console.log('Cannot directly create admin user via API as it would require admin credentials');
    console.log('Please use the database initialization script on the gameserver side');
    
  } catch (error) {
    console.error('Error:', error.message);
  }
}

// Run the function
createAdminUser();