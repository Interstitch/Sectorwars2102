// Advanced network diagnostic script to troubleshoot Docker connectivity issues
const http = require('http');
const https = require('https');
const dns = require('dns');
const os = require('os');
const { exec } = require('child_process');

// Store diagnostic results
const results = {
  environment: {},
  dns: {},
  ping: {},
  http: {},
  docker: {}
};

// Environment info
function getEnvironmentInfo() {
  console.log('Gathering environment information...');
  
  results.environment = {
    hostname: os.hostname(),
    platform: os.platform(),
    release: os.release(),
    nodeVersion: process.version,
    networkInterfaces: os.networkInterfaces(),
    env: {
      NODE_ENV: process.env.NODE_ENV,
      API_URL: process.env.API_URL,
      CODESPACE_NAME: process.env.CODESPACE_NAME
    }
  };
}

// DNS resolution tests
async function testDnsResolution() {
  console.log('Testing DNS resolution...');
  
  const domains = [
    'www.google.com',
    'github.com',
    'gameserver',
    'player-client'
  ];
  
  for (const domain of domains) {
    try {
      console.log(`Resolving ${domain}...`);
      const addresses = await new Promise((resolve, reject) => {
        dns.lookup(domain, { all: true }, (err, addresses) => {
          if (err) reject(err);
          else resolve(addresses);
        });
      });
      
      results.dns[domain] = {
        success: true,
        addresses: addresses
      };
      console.log(`✅ Successfully resolved ${domain}: ${JSON.stringify(addresses)}`);
    } catch (err) {
      results.dns[domain] = {
        success: false,
        error: err.message
      };
      console.log(`❌ Failed to resolve ${domain}: ${err.message}`);
    }
  }
  
  // Also try dns.resolveAny for more info
  for (const domain of ['www.google.com', 'github.com']) {
    try {
      const records = await new Promise((resolve, reject) => {
        dns.resolveAny(domain, (err, records) => {
          if (err) reject(err);
          else resolve(records);
        });
      });
      
      results.dns[`${domain}_records`] = {
        success: true,
        records: records
      };
    } catch (err) {
      results.dns[`${domain}_records`] = {
        success: false,
        error: err.message
      };
    }
  }
}

// Run basic ping tests using child_process
async function runPingTests() {
  console.log('Running ping tests...');
  
  const hosts = [
    'www.google.com',
    'github.com',
    'gameserver',
    '8.8.8.8' // Google DNS
  ];
  
  for (const host of hosts) {
    try {
      console.log(`Pinging ${host}...`);
      const output = await new Promise((resolve, reject) => {
        // Use -c 2 to just send 2 packets
        exec(`ping -c 2 ${host}`, (err, stdout, stderr) => {
          if (err) reject(err);
          else resolve(stdout);
        });
      });
      
      results.ping[host] = {
        success: true,
        output: output
      };
      console.log(`✅ Successfully pinged ${host}`);
    } catch (err) {
      results.ping[host] = {
        success: false,
        error: err.message,
        code: err.code
      };
      console.log(`❌ Failed to ping ${host}: ${err.message}`);
    }
  }
}

// Run HTTP/HTTPS tests
async function runHttpTests() {
  console.log('Running HTTP/HTTPS tests...');
  
  const urls = [
    { name: 'Google', url: 'https://www.google.com' },
    { name: 'GitHub', url: 'https://github.com' },
    { name: 'Gameserver container', url: 'http://gameserver:8080/api/v1/status' },
    { name: 'Docker gateway', url: 'http://172.18.0.1:8080/api/v1/status' },
    { name: 'DNS server', url: 'https://8.8.8.8' } // Google DNS HTTPS
  ];
  
  for (const { name, url } of urls) {
    try {
      console.log(`Testing HTTP request to ${name} (${url})...`);
      
      const isHttps = url.startsWith('https://');
      const httpModule = isHttps ? https : http;
      
      const response = await new Promise((resolve, reject) => {
        const req = httpModule.get(url, {
          timeout: 5000,
          headers: {
            'User-Agent': 'Node.js Network Diagnostic'
          }
        }, (res) => {
          let data = '';
          res.on('data', (chunk) => { data += chunk; });
          res.on('end', () => {
            resolve({
              statusCode: res.statusCode,
              headers: res.headers,
              data: data.substring(0, 500) // Limit response data
            });
          });
        });
        
        req.on('error', reject);
        req.on('timeout', () => reject(new Error('Request timed out')));
      });
      
      results.http[name] = {
        success: true,
        statusCode: response.statusCode,
        headers: response.headers,
        data: response.data
      };
      console.log(`✅ Successfully connected to ${name}: Status ${response.statusCode}`);
    } catch (err) {
      results.http[name] = {
        success: false,
        error: err.message
      };
      console.log(`❌ Failed to connect to ${name}: ${err.message}`);
    }
  }
}

// Check Docker network info
async function checkDockerNetwork() {
  console.log('Checking Docker network...');
  
  try {
    const output = await new Promise((resolve, reject) => {
      exec('cat /etc/resolv.conf', (err, stdout, stderr) => {
        if (err) reject(err);
        else resolve(stdout);
      });
    });
    
    results.docker.resolvConf = output;
    console.log('✅ Successfully read resolv.conf');
  } catch (err) {
    results.docker.resolvConf = {
      success: false,
      error: err.message
    };
    console.log(`❌ Failed to read resolv.conf: ${err.message}`);
  }
  
  // Try to get Docker container info if available
  try {
    const output = await new Promise((resolve, reject) => {
      exec('cat /etc/hosts', (err, stdout, stderr) => {
        if (err) reject(err);
        else resolve(stdout);
      });
    });
    
    results.docker.hostsFile = output;
    console.log('✅ Successfully read hosts file');
  } catch (err) {
    results.docker.hostsFile = {
      success: false,
      error: err.message
    };
    console.log(`❌ Failed to read hosts file: ${err.message}`);
  }
}

// Run all diagnostic tests and save results
async function runDiagnostics() {
  console.log('Starting network diagnostics...');
  
  try {
    // Get basic environment info
    getEnvironmentInfo();
    
    // Run tests
    await testDnsResolution();
    await runPingTests();
    await runHttpTests();
    await checkDockerNetwork();
    
    // Save results to file
    const fs = require('fs');
    fs.writeFileSync('/app/public/network-diagnostic-results.json', JSON.stringify(results, null, 2));
    
    // Generate HTML report
    generateHtmlReport();
    
    console.log('Diagnostics complete! Results saved to /app/public/network-diagnostic-results.json and /app/public/network-diagnostic-results.html');
  } catch (err) {
    console.error('Error running diagnostics:', err);
  }
}

// Generate HTML report
function generateHtmlReport() {
  const fs = require('fs');
  
  const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Docker Network Diagnostic Results</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      max-width: 1000px;
      margin: 0 auto;
      padding: 20px;
      line-height: 1.6;
    }
    h1, h2, h3 { color: #0366d6; }
    .section {
      margin-bottom: 30px;
      padding: 20px;
      border-radius: 5px;
      background-color: #f6f8fa;
    }
    .success { color: #28a745; }
    .error { color: #dc3545; }
    pre {
      background-color: #f0f0f0;
      padding: 15px;
      border-radius: 5px;
      overflow-x: auto;
      max-height: 300px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
    }
    th, td {
      padding: 8px;
      text-align: left;
      border-bottom: 1px solid #ddd;
    }
    th {
      background-color: #f2f2f2;
    }
    .recommendations {
      margin-top: 40px;
      padding: 20px;
      background-color: #f1f8ff;
      border-left: 5px solid #0366d6;
      border-radius: 0 5px 5px 0;
    }
  </style>
</head>
<body>
  <h1>Docker Network Diagnostic Results</h1>
  <p>This report shows diagnostic results for troubleshooting network connectivity issues in Docker containers.</p>
  
  <div class="section">
    <h2>Environment Information</h2>
    <pre>${JSON.stringify(results.environment, null, 2)}</pre>
  </div>
  
  <div class="section">
    <h2>DNS Resolution Tests</h2>
    <table>
      <tr>
        <th>Domain</th>
        <th>Status</th>
        <th>Results</th>
      </tr>
      ${Object.entries(results.dns).map(([domain, result]) => `
        <tr>
          <td>${domain}</td>
          <td class="${result.success ? 'success' : 'error'}">${result.success ? '✅ Success' : '❌ Failed'}</td>
          <td>
            ${result.success 
              ? (result.addresses 
                ? JSON.stringify(result.addresses) 
                : JSON.stringify(result.records))
              : result.error}
          </td>
        </tr>
      `).join('')}
    </table>
  </div>
  
  <div class="section">
    <h2>Ping Tests</h2>
    <table>
      <tr>
        <th>Host</th>
        <th>Status</th>
        <th>Details</th>
      </tr>
      ${Object.entries(results.ping).map(([host, result]) => `
        <tr>
          <td>${host}</td>
          <td class="${result.success ? 'success' : 'error'}">${result.success ? '✅ Success' : '❌ Failed'}</td>
          <td>${result.success ? 'Ping successful' : result.error}</td>
        </tr>
      `).join('')}
    </table>
    
    ${Object.entries(results.ping)
      .filter(([host, result]) => result.success)
      .map(([host, result]) => `
        <h3>Ping output for ${host}</h3>
        <pre>${result.output}</pre>
      `).join('')}
  </div>
  
  <div class="section">
    <h2>HTTP/HTTPS Tests</h2>
    <table>
      <tr>
        <th>Endpoint</th>
        <th>Status</th>
        <th>Details</th>
      </tr>
      ${Object.entries(results.http).map(([name, result]) => `
        <tr>
          <td>${name}</td>
          <td class="${result.success ? 'success' : 'error'}">${result.success ? `✅ Success (${result.statusCode})` : '❌ Failed'}</td>
          <td>${result.success ? `Status: ${result.statusCode}` : result.error}</td>
        </tr>
      `).join('')}
    </table>
  </div>
  
  <div class="section">
    <h2>Docker Network Configuration</h2>
    
    <h3>DNS Configuration (/etc/resolv.conf)</h3>
    <pre>${typeof results.docker.resolvConf === 'string' ? results.docker.resolvConf : JSON.stringify(results.docker.resolvConf, null, 2)}</pre>
    
    <h3>Hosts File (/etc/hosts)</h3>
    <pre>${typeof results.docker.hostsFile === 'string' ? results.docker.hostsFile : JSON.stringify(results.docker.hostsFile, null, 2)}</pre>
  </div>
  
  <div class="recommendations">
    <h2>Recommendations</h2>
    
    <h3>DNS Resolution</h3>
    ${Object.values(results.dns).some(result => !result.success)
      ? `<p>❌ Some DNS resolution tests failed. This may indicate DNS configuration issues in the Docker container.</p>
         <ul>
           <li>Check that the Docker container has proper DNS configuration in /etc/resolv.conf</li>
           <li>Verify that the Docker daemon's DNS settings are correct</li>
           <li>Try adding custom DNS servers in your docker-compose.yml file</li>
         </ul>`
      : `<p>✅ All DNS resolution tests passed successfully.</p>`
    }
    
    <h3>Network Connectivity</h3>
    ${Object.values(results.http).some(result => !result.success)
      ? `<p>❌ Some HTTP connectivity tests failed. This may indicate network connectivity issues.</p>
         <ul>
           <li>Check Docker network settings and firewall rules</li>
           <li>Verify that outbound connections are allowed from the container</li>
           <li>Check that the container has proper network access</li>
         </ul>`
      : `<p>✅ All HTTP connectivity tests passed successfully.</p>`
    }
    
    <h3>Container Communication</h3>
    ${results.http['Gameserver container']?.success
      ? `<p>✅ Communication with the gameserver container is working correctly.</p>`
      : `<p>❌ Communication with the gameserver container failed. Check Docker network configuration and container health.</p>`
    }
    
    <h3>External Connectivity</h3>
    ${(results.http['Google']?.success || results.http['GitHub']?.success)
      ? `<p>✅ External internet connectivity is working.</p>`
      : `<p>❌ External internet connectivity is not working. This container cannot reach the internet.</p>
         <ul>
           <li>Check Docker network settings to ensure outbound internet access</li>
           <li>Verify DNS settings in the container</li>
           <li>Check if there are proxy settings needed for internet access</li>
         </ul>`
    }
  </div>
  
  <p style="text-align: center; margin-top: 30px; color: #666;">
    Diagnostic run at: ${new Date().toISOString()}
  </p>
</body>
</html>
  `;
  
  fs.writeFileSync('/app/public/network-diagnostic-results.html', htmlContent);
}

// Run all diagnostics
runDiagnostics();