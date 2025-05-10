# Sector Wars 2102 Development Scripts

This directory contains scripts used to set up and run the Sector Wars 2102 application across different environments.

## Script Architecture

| Script                | Local | Codespaces | Replit | Description |
|-----------------------|:-----:|:----------:|:------:|-------------|
| `start-unified.sh`    |   ✅  |     ✅     |   ✅   | Universal entry point script that detects the environment and starts the application accordingly with appropriate configuration. |
| `setup.sh`            |   ✅  |     ✅     |   ✅   | Unified setup script that handles environment-specific configuration and dependency installation. |
| `start-replit-unified.sh` | ❌ |     ❌     |   ✅   | Replit-specific startup script that supports both PM2 and direct process management with a host-check toggle option. |

Legend:
- ✅ Fully supported and primary script for this environment
- ❌ Not intended for use in this environment

## Execution Flow

```
start-unified.sh [--no-host-check]
  ├── [First run] -> setup.sh (environment-specific configuration)
  ├── [Local/Codespaces] -> docker-compose up
  └── [Replit] -> start-replit-unified.sh [--no-host-check]
                   ├── [PM2 available] -> PM2 process management
                   ├── [PM2 unavailable] -> Direct process management
                   └── [--no-host-check] -> Host-check disabled mode
```

## Using the Scripts

### Normal Usage

To start the application in any environment:

```bash
./dev-scripts/start-unified.sh
```

The script will automatically detect your environment and use the appropriate startup method.

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
- PM2-based process management (when available)
- Direct process management fallback
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
- Supports both PM2 and direct process management
- Provides host-check disable option (--no-host-check)
- Tests port availability
- Runs setup if needed
- Starts all services appropriately for the Replit environment