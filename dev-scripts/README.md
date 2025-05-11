# Sector Wars 2102 Development Scripts

This directory contains scripts used to set up and run the Sector Wars 2102 application across different environments.

## Script Architecture

| Script                | Local | Codespaces | Replit | Description |
|-----------------------|:-----:|:----------:|:------:|-------------|
| `start-unified.sh`    |   ✅  |     ✅     |   ✅   | Universal entry point script that detects the environment, configures settings, and starts the application accordingly. Also supports switching between development, production, and test environments. |
| `setup.sh`            |   ✅  |     ✅     |   ✅   | Unified setup script that handles environment-specific configuration and dependency installation. |
| `start-replit-unified.sh` | ❌ |     ❌     |   ✅   | Replit-specific startup script that supports both PM2 and direct process management with a host-check toggle option. |

Legend:
- ✅ Fully supported and primary script for this environment
- ❌ Not intended for use in this environment

## Execution Flow

```
start-unified.sh [--no-host-check] [--production-db] [development|production|test]
  ├── [First run] -> setup.sh (environment-specific configuration)
  ├── [Local/Codespaces] -> docker-compose up
  └── [Replit] -> start-replit-unified.sh [--no-host-check]
                   ├── [Standard mode] -> PM2 with standard config
                   └── [--no-host-check] -> PM2 with host-check disabled
```

## Using the Scripts

### Normal Usage

To start the application in any environment:

```bash
./dev-scripts/start-unified.sh
```

The script will automatically detect your environment and use the appropriate startup method.

### Switching Environments

To switch between development, production, and test environments:

```bash
# Switch to development environment (uses development database)
./dev-scripts/start-unified.sh development

# Switch to production environment (uses production database)
./dev-scripts/start-unified.sh production

# Switch to test environment (uses test database)
./dev-scripts/start-unified.sh test

# Combine with other options
./dev-scripts/start-unified.sh production --production-db
```

This will update the environment settings in the .env file and adjust security settings accordingly.

### Replit with Host-Check Disabled

If you're experiencing host-check issues in Replit (blocked requests), use:

```bash
./dev-scripts/start-unified.sh --no-host-check
```

This will start the application in Replit with host checking completely disabled.

### Manual Setup

To manually run the setup process:

```bash
./dev-scripts/setup.sh
```

This will detect your environment and perform the appropriate setup.

## Environment-Specific Features

### Docker-based Environments (Local/Codespaces)
- Uses docker-compose for container orchestration
- Mounts volumes for live-reload development
- Consistent environment across development machines

### Replit Environment
- PM2-based process management
- Auto-install of PM2 if not found
- Node.js version management via NVM
- Python dependency management in user space
- Port availability diagnostics (8080)
- Host-checking bypass options

## Script Details

### start-unified.sh
The universal entry point that:
- Detects the environment automatically
- Handles command-line options (--no-host-check)
- Runs setup if needed
- Uses the appropriate startup method for the detected environment
- For Docker environments: Uses docker-compose
- For Replit: Uses start-replit-unified.sh

### setup.sh
Unified setup script that:
- Detects the environment automatically
- Sets up Node.js (with NVM when available)
- Updates npm to a compatible version
- Installs PM2 if needed (Replit)
- Sets up Python environment and dependencies
- Configures environment (.env file)
- Installs frontend dependencies

### start-replit-unified.sh
Replit-specific unified script that:
- Uses PM2 for process management (installs it if not found)
- Provides host-check disable option (--no-host-check)
- Creates a special PM2 config for no-host-check mode
- Tests port availability
- Runs setup if needed
- Starts all services appropriately for the Replit environment

