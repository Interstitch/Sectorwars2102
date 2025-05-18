import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import dns from 'dns'

// This is critical: configure DNS to use IPv4 instead of IPv6
dns.setDefaultResultOrder('ipv4first')

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // Listen on all addresses
    port: 3001, // Restored to original port
    strictPort: true,

    // Completely disable host checking in development mode
    hmr: {
      clientPort: 3001,
      host: 'localhost'
    },

    // Direct configuration to allow any host
    cors: true,

    // Add explicit wildcard for all hosts - most important setting
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      '.replit.dev',
      '.repl.co',
      '0.0.0.0',
      '*', // Wildcard to allow everything
      'all' // Another way to allow everything
    ],

    // Don't check origin at all
    origin: '*',

    // Add proxy for API server to bypass CORS issues across all environments
    proxy: {
      '/api': {
        // Determine target dynamically based on environment
        target: process.env.API_URL ||
                (process.env.REPL_ID ? 'http://localhost:8080' : 'http://gameserver:8080'),
        // Do not rewrite all paths to /api/v1 - use paths as they are
        changeOrigin: true,
        secure: false,
        ws: true,
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('Sending Request to the Target:', req.method, req.url);
            console.log('Using API URL:', process.env.API_URL ||
                       (process.env.REPL_ID ? 'http://localhost:8080' : 'http://gameserver:8080'));

            // For GitHub Codespaces, we need to handle the 443 port correctly
            if (process.env.CODESPACE_NAME || process.env.GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN) {
              console.log('GitHub Codespaces environment detected, preserving host header');
              // Preserve the original host from the request
              if (req.headers.host) {
                proxyReq.setHeader('host', req.headers.host);
              }
            }
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
          });
        },
      }
    },

    watch: {
      usePolling: true,
    },

    // Disable FS restriction
    fs: {
      strict: false,
      allow: ['..'],
    },
  },
})