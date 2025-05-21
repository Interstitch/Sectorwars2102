// Simple test to verify Docker network connectivity and proxy configuration
const http = require('http');
const https = require('https');

// Log test results
const results = [];

// Detect environment
const isCodespaces = process.env.CODESPACE_NAME !== undefined;
const codespaceUrl = isCodespaces ? `https://${process.env.CODESPACE_NAME}-8080.app.github.dev` : null;

// Test a URL and return a promise with the result
function testUrl(name, url) {
  return new Promise((resolve) => {
    console.log(`Testing ${name}: ${url}`);
    
    // Skip non-absolute URLs for server-side testing
    if (url.startsWith('/')) {
      console.log(`Skipping relative URL ${url} in server-side test`);
      resolve({
        name,
        url,
        success: false,
        error: 'Relative URLs cannot be tested server-side, only in browser'
      });
      return;
    }
    
    // Parse the URL to determine protocol
    const isHttps = url.startsWith('https://');
    const httpModule = isHttps ? https : http;
    
    const req = httpModule.get(url, {
      timeout: 5000, // 5 second timeout
      headers: {
        'User-Agent': 'Node.js Simple Test'
      }
    }, (res) => {
      console.log(`Status for ${name}: ${res.statusCode}`);
      
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        // Try to parse as JSON, otherwise truncate text
        let result;
        try {
          result = JSON.parse(data);
        } catch (e) {
          result = data.length > 200 ? data.substring(0, 200) + '...' : data;
        }
        
        resolve({
          name,
          url,
          success: true,
          statusCode: res.statusCode,
          data: result,
          headers: res.headers
        });
      });
    });
    
    req.on('error', (err) => {
      console.error(`Error for ${name}: ${err.message}`);
      resolve({
        name,
        url,
        success: false,
        error: err.message
      });
    });
    
    // Set a timeout handler
    req.on('timeout', () => {
      req.abort();
      console.error(`Timeout for ${name}`);
      resolve({
        name,
        url,
        success: false,
        error: 'Request timed out after 5 seconds'
      });
    });
  });
}

// URLs to test - multiple alternatives to ensure at least one works
const urlsToTest = [
  // From inside Docker container
  { name: 'API via container name', url: 'http://gameserver:8080/api/v1/status' },
  { name: 'API via Docker gateway', url: 'http://172.18.0.1:8080/api/v1/status' },
  { name: 'API via localhost', url: 'http://localhost:8080/api/v1/status' },
  // Note: relative URLs are skipped in server-side tests
  { name: 'API via proxy (relative URL)', url: '/api/v1/status' },
  // External sites
  { name: 'External site (Google)', url: 'https://www.google.com' }
];

// Add Codespaces URL if detected
if (isCodespaces && codespaceUrl) {
  urlsToTest.push({ 
    name: 'API via Codespaces public URL', 
    url: `${codespaceUrl}/api/v1/status` 
  });
}

// Run all tests and write results
async function runTests() {
  // Add environment info
  results.push({
    name: 'Environment',
    environment: {
      nodeVersion: process.version,
      platform: process.platform,
      isCodespaces: isCodespaces,
      codespaceUrl: codespaceUrl,
      hostname: require('os').hostname(),
      env: {
        NODE_ENV: process.env.NODE_ENV,
        API_URL: process.env.API_URL,
        CODESPACE_NAME: process.env.CODESPACE_NAME
      }
    }
  });
  
  // Run all URL tests
  for (const testCase of urlsToTest) {
    try {
      const result = await testUrl(testCase.name, testCase.url);
      results.push(result);
    } catch (error) {
      console.error(`Unexpected error in test "${testCase.name}":`, error);
      results.push({
        name: testCase.name,
        url: testCase.url,
        success: false,
        error: `Unexpected error: ${error.message}`
      });
    }
  }
  
  // Print a summary of the results
  console.log('\n===== TEST RESULTS SUMMARY =====');
  let successCount = 0;
  let skipCount = 0;
  results.forEach(result => {
    if (result.name === 'Environment') return;
    
    if (result.success) {
      successCount++;
      console.log(`✅ ${result.name}: Success (${result.statusCode})`);
    } else if (result.error.includes('Relative URLs cannot be tested')) {
      skipCount++;
      console.log(`⏭️ ${result.name}: Skipped - ${result.error}`);
    } else {
      console.log(`❌ ${result.name}: Failed - ${result.error}`);
    }
  });
  
  const testCount = urlsToTest.length - skipCount;
  console.log(`\nTests passed: ${successCount}/${testCount} (${skipCount} skipped)`);
  
  // Output all test results as HTML
  const htmlResults = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Simple API Test Results</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      max-width: 900px;
      margin: 0 auto;
      padding: 20px;
      line-height: 1.6;
    }
    h1, h2 { color: #0366d6; }
    .success { color: #28a745; }
    .error { color: #dc3545; }
    .skipped { color: #6c757d; }
    .test-result {
      margin-bottom: 20px;
      padding: 15px;
      border-radius: 5px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    .test-result.success { background-color: #f1f8e9; }
    .test-result.error { background-color: #fff8f8; }
    .test-result.skipped { background-color: #f8f9fa; }
    .test-info {
      margin-bottom: 10px;
      display: flex;
      justify-content: space-between;
    }
    pre {
      background-color: #f6f8fa;
      padding: 15px;
      border-radius: 4px;
      overflow: auto;
    }
    .env-info {
      background-color: #f0f7ff;
      padding: 15px;
      border-radius: 5px;
      margin-bottom: 20px;
    }
    .summary {
      margin-top: 30px;
      padding: 10px;
      background-color: #f6f8fa;
      border-radius: 5px;
      text-align: center;
    }
    .timestamp {
      color: #6c757d;
      font-size: 0.9em;
      text-align: center;
      margin-top: 20px;
    }
    .recommendations {
      background-color: #f1f8e9;
      padding: 15px;
      border-radius: 5px;
      margin-top: 30px;
    }
    .recommendations h3 {
      margin-top: 0;
    }
    .recommendations li {
      margin-bottom: 10px;
    }
  </style>
</head>
<body>
  <h1>Simple API Test Results</h1>
  
  <div class="env-info">
    <h2>Environment Information</h2>
    <pre>${JSON.stringify(results.find(r => r.name === 'Environment')?.environment || {}, null, 2)}</pre>
  </div>
  
  <h2>Test Results</h2>
  ${results.filter(r => r.name !== 'Environment').map(result => {
    const isSkipped = !result.success && result.error.includes('Relative URLs cannot be tested');
    
    return `
    <div class="test-result ${isSkipped ? 'skipped' : (result.success ? 'success' : 'error')}">
      <div class="test-info">
        <h3>${result.name}</h3>
        <span class="${isSkipped ? 'skipped' : (result.success ? 'success' : 'error')}">
          ${isSkipped ? 
            `⏭️ Skipped` : 
            (result.success ? 
              `✅ Success (${result.statusCode})` : 
              `❌ Failed`
            )
          }
        </span>
      </div>
      <div><strong>URL:</strong> ${result.url}</div>
      ${isSkipped ?
        `<div><strong>Note:</strong> ${result.error}</div>` :
        (result.success ? 
          `<div><strong>Status:</strong> ${result.statusCode}</div>
           <div><strong>Response:</strong></div>
           <pre>${typeof result.data === 'object' ? JSON.stringify(result.data, null, 2) : result.data}</pre>` : 
          `<div><strong>Error:</strong> ${result.error}</div>`
        )
      }
    </div>
  `}).join('')}
  
  <div class="summary">
    <h2>Summary</h2>
    <p>${successCount} of ${testCount} tests passed successfully (${skipCount} skipped).</p>
  </div>

  <div class="recommendations">
    <h3>Recommendations</h3>
    <p>Based on the test results, here are the recommended URL patterns for API requests:</p>
    <ul>
      ${results.filter(r => r.success && r.name !== 'Environment').map(r => 
        `<li><strong>${r.name}:</strong> ${r.url}</li>`
      ).join('')}
    </ul>
    <p><strong>For Docker environments:</strong></p>
    <ul>
      <li>Server-to-server communication: Use <code>http://gameserver:8080</code> for reliable communication within the Docker network</li>
      <li>Browser requests: Use relative URLs with the Vite proxy (e.g., <code>/api/v1/status</code>)</li>
    </ul>
    <p><strong>For GitHub Codespaces:</strong></p>
    <ul>
      <li>Server-to-server communication: Use <code>http://gameserver:8080</code> inside the Docker network</li>
      <li>Browser requests: Use relative URLs with the Vite proxy to avoid CORS and port-doubling issues</li>
    </ul>
    <p>Read the <a href="/API_TEST_README.md">API Testing Documentation</a> for more detailed information.</p>
  </div>
  
  <div class="timestamp">
    Test ran at: ${new Date().toISOString()}
  </div>
</body>
</html>
  `;
  
  // Write the HTML results to a file
  require('fs').writeFileSync('/app/public/simple-test-results.html', htmlResults);
  console.log('Test results written to /app/public/simple-test-results.html');
  
  // Also write JSON results
  require('fs').writeFileSync('/app/public/simple-test-results.json', JSON.stringify(results, null, 2));
  console.log('JSON results written to /app/public/simple-test-results.json');
}

// Run the tests
runTests();