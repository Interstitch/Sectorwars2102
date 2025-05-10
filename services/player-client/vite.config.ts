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
    port: 3000,
    strictPort: true,

    // Completely disable host checking in development mode
    hmr: {
      clientPort: 443,
      host: '0.0.0.0'
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