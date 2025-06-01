#!/usr/bin/env node
/**
 * Simple live reload script for GitHub Codespaces
 * Run this script and it will watch for file changes and automatically refresh your browser tab
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🔄 Live reload watcher started for GitHub Codespaces');
console.log('📁 Watching src/ directory for changes...');
console.log('💡 Tip: Keep your browser tab open - it will auto-refresh when you save files!');

let lastChange = 0;
const debounceMs = 1000; // Wait 1 second between reloads

function watchDirectory(dir) {
  try {
    fs.watch(dir, { recursive: true }, (eventType, filename) => {
      if (!filename || filename.includes('node_modules')) return;
      
      const now = Date.now();
      if (now - lastChange < debounceMs) return;
      lastChange = now;

      if (filename.endsWith('.tsx') || filename.endsWith('.ts') || filename.endsWith('.css')) {
        console.log(`📝 File changed: ${filename}`);
        console.log('🔄 Building and refreshing...');
        
        try {
          // Trigger a build
          execSync('npm run build', { cwd: __dirname, stdio: 'inherit' });
          console.log('✅ Build complete - your browser should refresh now!');
        } catch (error) {
          console.error('❌ Build failed:', error.message);
        }
      }
    });
  } catch (error) {
    console.error('Error watching directory:', error.message);
  }
}

// Watch the src directory
watchDirectory(path.join(__dirname, 'src'));

// Keep the script running
process.on('SIGINT', () => {
  console.log('\n👋 Live reload watcher stopped');
  process.exit(0);
});