// Simple test script to check API connectivity
// Run this with Node.js to test the API directly

const https = require('https');

const apiUrl = 'https://super-duper-carnival-qppjvq94q9vcxwqp-8080.app.github.dev';

console.log('Testing API connectivity to:', apiUrl);

// Test 1: Status endpoint (no auth required)
console.log('\n1. Testing status endpoint...');
https.get(`${apiUrl}/api/v1/status`, (res) => {
  console.log('Status Code:', res.statusCode);
  console.log('Headers:', res.headers);
  
  let data = '';
  res.on('data', (chunk) => {
    data += chunk;
  });
  
  res.on('end', () => {
    console.log('Response:', data);
  });
}).on('error', (err) => {
  console.error('Error:', err.message);
});

// Test 2: Auth endpoint with fake token
console.log('\n2. Testing auth endpoint with Bearer token...');
const options = {
  hostname: 'super-duper-carnival-qppjvq94q9vcxwqp-8080.app.github.dev',
  path: '/api/v1/auth/me',
  method: 'GET',
  headers: {
    'Authorization': 'Bearer fake-token-for-testing',
    'Content-Type': 'application/json'
  }
};

const req = https.request(options, (res) => {
  console.log('Status Code:', res.statusCode);
  console.log('Headers:', res.headers);
  
  let data = '';
  res.on('data', (chunk) => {
    data += chunk;
  });
  
  res.on('end', () => {
    console.log('Response:', data);
  });
});

req.on('error', (err) => {
  console.error('Error:', err.message);
});

req.end();