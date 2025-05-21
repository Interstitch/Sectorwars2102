// This script runs on the server-side in the player-client container
// It tests direct connectivity to the gameserver container

const http = require('http');
const fs = require('fs');

// Test URLs
const urls = [
  { name: 'Gameserver container (internal)', url: 'http://gameserver:8080/api/v1/status' },
  { name: 'Gameserver via localhost', url: 'http://localhost:8080/api/v1/status' },
  { name: 'Gameserver via gateway', url: 'http://172.18.0.1:8080/api/v1/status' },
  { name: 'External site (Google)', url: 'https://www.google.com' }
];

// Function to test a URL
function testUrl(urlObj) {
  return new Promise((resolve) => {
    console.log(`Testing ${urlObj.name}: ${urlObj.url}`);
    
    // Parse the URL to determine if it's HTTP or HTTPS
    const isHttps = urlObj.url.startsWith('https://');
    let httpModule;
    
    if (isHttps) {
      httpModule = require('https');
    } else {
      httpModule = require('http');
    }
    
    const req = httpModule.get(urlObj.url, (res) => {
      console.log(`Status Code for ${urlObj.name}: ${res.statusCode}`);
      
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        let result;
        try {
          // Try to parse as JSON
          result = JSON.parse(data);
        } catch (e) {
          // If not JSON, truncate the data
          result = data.substring(0, 200) + (data.length > 200 ? '...' : '');
        }
        
        resolve({
          name: urlObj.name,
          url: urlObj.url,
          success: true,
          statusCode: res.statusCode,
          data: result
        });
      });
    });
    
    req.on('error', (err) => {
      console.error(`Error for ${urlObj.name}: ${err.message}`);
      resolve({
        name: urlObj.name,
        url: urlObj.url,
        success: false,
        error: err.message
      });
    });
    
    // Set a timeout of 5 seconds
    req.setTimeout(5000, () => {
      req.abort();
      console.error(`Timeout for ${urlObj.name}`);
      resolve({
        name: urlObj.name,
        url: urlObj.url,
        success: false,
        error: 'Request timed out after 5 seconds'
      });
    });
  });
}

// Test all URLs and write results to a file
async function runTests() {
  const results = [];
  
  for (const url of urls) {
    try {
      const result = await testUrl(url);
      results.push(result);
    } catch (error) {
      console.error(`Unexpected error testing ${url.name}:`, error);
      results.push({
        name: url.name,
        url: url.url,
        success: false,
        error: `Unexpected error: ${error.message}`
      });
    }
  }
  
  // Add environment information
  results.push({
    name: 'Environment Info',
    environment: {
      nodeVersion: process.version,
      platform: process.platform,
      hostname: require('os').hostname(),
      networkInterfaces: require('os').networkInterfaces()
    }
  });
  
  // Write results to a file
  fs.writeFileSync('/app/public/network-test-results.json', JSON.stringify(results, null, 2));
  console.log('Tests completed. Results written to /app/public/network-test-results.json');
}

// Run the tests
runTests();