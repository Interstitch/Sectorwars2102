/**
 * This script starts the player client dev server with host checking disabled
 * It's a direct workaround for the "Blocked request" issue in Replit
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Path to the vite config file
const configFile = path.join(__dirname, 'vite.config.ts');

// Create a backup of the original vite config if it doesn't exist
const backupFile = path.join(__dirname, 'vite.config.backup.ts');
if (!fs.existsSync(backupFile)) {
  console.log('Creating backup of original vite.config.ts...');
  fs.copyFileSync(configFile, backupFile);
}

// Define a simplified config that completely disables host checking
const newConfig = `
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import dns from 'dns'

// Force IPv4 to avoid issues with IPv6
dns.setDefaultResultOrder('ipv4first')

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 3000,
    strictPort: true,
    hmr: {
      clientPort: 443,
      host: '0.0.0.0'
    },
    // Maximum permissiveness for hosts
    cors: true,
    allowedHosts: ['*', '.replit.dev', '.repl.co'],
    origin: '*',
    watch: {
      usePolling: true,
    },
    fs: {
      strict: false,
      allow: ['..'],
    },
  },
})
`;

// Write the new config
fs.writeFileSync(configFile, newConfig, 'utf8');
console.log('Temporary config written to disable host checking...');

try {
  // Run npm dev with VITE_ALLOW_ANY_HOST=true to disable host checking
  console.log('Starting dev server with host checking disabled...');
  execSync('VITE_ALLOW_ANY_HOST=true npm run dev -- --host 0.0.0.0 --port 3000', {
    stdio: 'inherit',
    env: {
      ...process.env,
      VITE_ALLOW_ANY_HOST: 'true',
      VITE_DISABLE_HOST_CHECK: 'true',
    }
  });
} catch (error) {
  console.error('Error starting dev server:', error);
} finally {
  // Restore the original config from backup
  console.log('Restoring original vite.config.ts...');
  fs.copyFileSync(backupFile, configFile);
}