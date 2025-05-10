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
```

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

### Problem: PM2 Installation Issues

If PM2 fails to install with permission errors:

**Solution:**
Use the user-space installation command:
```bash
/run install-pm2
```

This installs PM2 in your home directory, avoiding permission issues with Nix store directories.

### Problem: "ERROR: No Python interpreter found"

If the Python interpreter cannot be found:

**Solution:**
1. Verify Python is installed:
   ```bash
   python3 --version
   ```

2. If not, run the Python setup:
   ```bash
   /run python-setup
   ```

### Problem: Services Fail to Start

If one or more services (Game API Server, Player Client, Admin UI) fail to start:

**Solution:**
1. Check the log files:
   ```bash
   pm2 logs
   # Or for specific service
   pm2 logs game-api-server
   ```

2. For Node.js services, try clearing npm cache:
   ```bash
   cd /services/player-client
   rm -rf node_modules
   npm cache clean --force
   npm install
   ```

3. Restart individual services:
   ```bash
   pm2 restart game-api-server
   pm2 restart player-client
   pm2 restart admin-ui
   ```

## Manual Recovery

If you need to completely reset your Replit environment:

1. Upgrade Node.js first:
   ```bash
   /run upgrade-node
   ```

2. Run the setup script again:
   ```bash
   /run setup
   ```

3. Kill any running PM2 processes:
   ```bash
   pm2 kill
   ```

4. Restart the application:
   ```bash
   /run start
   ```

## Getting Help

If you continue experiencing issues:

1. Check the PM2 logs: `pm2 logs`
2. Monitor PM2 processes in real-time: `pm2 monit` 
3. Look at raw process logs in `/tmp/*.log` files
4. Try running services individually to isolate problems