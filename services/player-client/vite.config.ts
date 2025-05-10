import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    watch: {
      usePolling: true,
    },
    // Allow connections from any hostname in Replit
    hmr: {
      clientPort: process.env.REPL_SLUG ? 443 : 3000,
      // Allow connections from any host for HMR
      host: '0.0.0.0',
    },
    // Explicitly allow all hosts to solve blocked request issue
    cors: true,
    strictPort: true,
    allowedHosts: 'all',
    // Remove origin check to prevent CORS issues
    origin: 'http://localhost:3000',
    fs: {
      strict: false,
    },
  },
})