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

## Port Configuration

We've switched from port 5000 to port 8080 for the Game API Server due to potential restrictions in the Replit environment.

### Testing Port Connectivity

To test if the Game API Server can bind to port 8080:

1. First, check if the port is available:
   ```bash
   /run test-port
   ```
   (This tries to bind to port 8080 and reports if it's available)

2. Try the simple test server:
   ```bash
   /run simple-server
   ```
   (This runs a minimal FastAPI server on port 8080)

3. If those tests work but the main API server doesn't, try:
   ```bash
   /run direct-start
   ```
   (Directly starts the uvicorn server without PM2)

4. If port 8080 still doesn't work, you may need to restart Replit or refresh your browser window

### Why We Switched from Port 5000

Port 5000 appears to be restricted in the Replit environment for several potential reasons:
- Port 5000 is commonly used by development servers and may be reserved
- It may conflict with Replit's internal services
- Some cloud providers give special treatment to well-known ports

Our diagnostics showed that while Python could bind to port 5000 at a low level, the service couldn't be properly exposed through Replit's proxy system.

### Checking Port Status

You can check the status of any port with a simple Python script:

```python
import socket
s = socket.socket()
try:
    s.bind(("0.0.0.0", 8080))  # Change port as needed
    print("Port is available")
    s.close()
except Exception as e:
    print(f"Port is not available: {e}")
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

3. Verify Python module imports with the verification script:
   ```bash
   cd services/gameserver
   python3 verify_imports.py
   ```

4. If modules are not found, install them with specific versions:
   ```bash
   pip3 install --user uvicorn==0.23.2 fastapi==0.103.1 pydantic==1.10.8 starlette==0.27.0
   ```

5. Try running the simple test server directly:
   ```bash
   cd services/gameserver
   python3 simple_server.py
   ```

6. If pip modules aren't in your PATH, run:
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

7. Check and fix Python path settings:
   ```bash
   # Display Python path configuration
   python3 -m site

   # Get user site-packages directory
   PYTHON_USER_SITE=$(python3 -m site --user-site)

   # Set PYTHONPATH to include user site-packages and app directory
   export PYTHONPATH="$PYTHON_USER_SITE:/home/runner/Sectorwars2102/services/gameserver:$PYTHONPATH"

   # Create a .pth file to permanently add your project path
   echo "/home/runner/Sectorwars2102/services/gameserver" > "$PYTHON_USER_SITE/sectorwars.pth"
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

### Problem: "Game API Server not running on port 8080"

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

3. Try the simple server first (most likely to work):
   ```bash
   cd services/gameserver
   python3 simple_server.py
   ```

4. If you see "ELF syntax error" in the PM2 logs, try direct execution instead:
   ```bash
   cd services/gameserver
   chmod +x simple_server.py
   ./simple_server.py
   ```

5. Start with PM2 using the simple server configuration:
   ```bash
   pm2 start pm2.replit.config.js --only simple-test-server
   ```

6. If it works directly, the issue might be with PM2. Restart the full application:
   ```bash
   /run start
   ```

### PM2 "ELF" Syntax Errors

If you see errors like this in the PM2 logs:
```
ELF
^
SyntaxError: invalid syntax
```

This means PM2 is trying to execute the Python binary as a script rather than using it as an interpreter. To fix:

1. Use the direct approach by setting the script to the Python file and using a proper interpreter:
   ```javascript
   // In pm2.replit.config.js
   {
     script: './simple_server.py',
     interpreter: '/usr/bin/env',
     interpreter_args: 'python3',
   }
   ```

2. Make your Python scripts executable:
   ```bash
   chmod +x services/gameserver/simple_server.py
   chmod +x services/gameserver/src/main.py
   ```

3. Ensure your Python scripts have the proper shebang line:
   ```python
   #!/usr/bin/env python3
   ```

4. If all else fails, bypass PM2 entirely using:
   ```bash
   cp .replit.direct .replit
   ```
   This configuration runs services directly without PM2.

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