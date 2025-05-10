# Replit Troubleshooting Guide

This document provides solutions for common issues encountered when running Sector Wars 2102 in Replit environments.

## Quick Commands

Replit provides several predefined commands to help you manage the application:

```bash
# Start the application
/run start

# Run the setup script
/run setup 

# Update npm to the latest version compatible with Node.js 18
/run update-npm

# Install PM2 in user space
/run install-pm2

# Upgrade Node.js to version 18 (using NVM)
/run upgrade-node

# Set up Python and install requirements
/run python-setup

# Start Game API Server directly (emergency fallback)
/run direct-start

# Run a simple test API server
/run test-api

# Run a very basic socket server on port 5000
/run simple-api
```

## Port 5000 Issues

If port 5000 (Game API Server) isn't showing in the Replit interface:

1. First, check if any services can bind to port 5000:
   ```bash
   /run simple-api
   ```
   (This runs a basic socket server on port 5000)

2. If the simple-api works, try the test API server:
   ```bash
   /run test-api
   ```

3. If those tests work but the main API server doesn't, try:
   ```bash
   /run direct-start
   ```

4. Restart Replit or refresh your browser window
   
5. Make sure you don't have any other service using port 5000 in Replit

### Possible Port 5000 Restrictions

Some cloud providers (including Replit) may restrict or proxy port 5000 because:
- Port 5000 is commonly used by development servers
- It may conflict with Replit's internal services
- Some providers give special treatment to this port

If none of the above commands make port 5000 available, try modifying the Game API Server to use port 8080 instead:

1. Edit the PM2 config:
   ```bash
   vim pm2.replit.config.js
   ```
   And change the port to 8080 in the game-api-server section.

2. Edit the frontend services to point to port 8080 instead of 5000.

3. Add port 8080 in the .replit configuration.

## Node.js/NPM Version Issues

If you're experiencing issues with old Node.js or npm versions:

1. Try upgrading Node.js:
   ```bash
   /run upgrade-node
   ```

2. Restart your Replit shell to load the new Node.js version
   
3. After upgrading Node.js, update npm to a compatible version:
   ```bash
   /run update-npm
   ```

4. Verify the upgraded versions:
   ```bash
   node -v
   npm -v
   ```

## Python and Pip Issues

If you encounter Python-related errors:

1. Disable pip version checking to avoid errors:
   ```bash
   export PIP_DISABLE_PIP_VERSION_CHECK=1
   ```

2. Use the user-space install to avoid permission issues:
   ```bash
   /run python-setup
   ```

3. If pip modules aren't in your PATH, run:
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

4. If the Python path isn't properly set:
   ```bash
   export PYTHONPATH="./services/gameserver:$PYTHONPATH"
   ```

## Common Issues

### Problem: "Could not get Nix environment building"

If you encounter errors like:
```
couldn't get nix env building nix env: exit status 1: evaluating file '/nix/store/...'
```

**Solution:**
The application will automatically detect Nix issues and fall back to a simplified mode that doesn't require Nix. If you still have issues:

1. Run the setup script:
   ```bash
   /run setup
   ```

2. Refresh your Replit shell (close and reopen the shell or restart the Repl)

### Problem: "Blocked request. This host is not allowed"

If you see errors in the browser about blocked hosts:

**Solution:**
The Vite configuration has been updated to accept any Replit-generated hostname. If you still encounter this issue:

1. Restart the application:
   ```bash
   /run start
   ```

2. If it persists, check if any of the services failed to start properly in the logs.

### Problem: "Game API Server not running"

If the Game API Server isn't starting properly:

**Solution:**
1. Check the PM2 logs:
   ```bash
   pm2 logs game-api-server
   ```
   
2. Kill all running PM2 processes:
   ```bash
   pm2 kill
   ```

3. Try the test server:
   ```bash
   /run test-api
   ```

4. If it works directly, the issue might be with PM2. Restart the full application:
   ```bash
   /run start
   ```

## Manual Recovery

If you need to completely reset your Replit environment:

1. Kill all processes:
   ```bash
   pm2 kill
   ```
   
2. Upgrade Node.js first:
   ```bash
   /run upgrade-node
   ```

3. Run the setup script again:
   ```bash
   /run setup
   ```

4. Try starting each component individually:
   ```bash
   # Game server first - try the test server first
   /run test-api
   
   # If that works, try the regular server
   /run direct-start
   
   # In a separate shell tab, start player client
   cd services/player-client && npm run dev -- --host 0.0.0.0 --port 3000
   
   # In a third shell tab, start admin UI
   cd services/admin-ui && npm run dev -- --host 0.0.0.0 --port 3001
   ```

## Getting Help

If you continue experiencing issues:

1. Check the PM2 logs: `pm2 logs`
2. Monitor PM2 processes in real-time: `pm2 monit` 
3. Look at raw process logs in `/tmp/*.log` files
4. Try running services individually to isolate problems