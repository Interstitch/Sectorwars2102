# Date: 2023-05-10
# Topic: Process Management and Replit Compatibility

## Context
While our Docker-based approach works well for local development and GitHub Codespaces, Replit environments do not consistently support Docker. Since Replit is a critical development platform for iPad compatibility, we needed to create a solution that provides consistent application behavior across all environments.

## Decisions
1. Implement PM2 process manager to coordinate all services
2. Create two deployment models that work with identical codebase:
   - Docker-based with traditional microservices or combined container
   - Process-based using PM2 directly on the host (for Replit)
3. Maintain environment detection for automatic configuration
4. Keep external Neon PostgreSQL database as the single source of truth

## Implementation
1. Created PM2 configuration files for both environments:
   - `pm2.config.js` for Docker combined container
   - `pm2.replit.config.js` for direct Replit execution
2. Developed a combined Dockerfile that contains all three services
3. Updated startup scripts to handle both deployment models:
   - `start.sh` for environment detection and routing
   - `start-replit.sh` for PM2-based process management
4. Created setup scripts with Nix fallback mechanisms:
   - `replit-setup.sh` for standard setup
   - `replit-setup-simple.sh` for simplified setup without Nix
5. Added proper process lifecycle management with cleanup hooks
6. Updated documentation in AISPEC files to reflect the new architecture

## Challenges
1. Nix environment in Replit is not always reliable
2. Managing inter-service communication without Docker networking
3. Ensuring consistent port assignments across environments
4. Handling process lifecycles properly in Replit
5. Providing graceful fallbacks for all critical components

## Solutions
1. Created a tiered fallback system in start scripts:
   - Try Docker first
   - Fall back to PM2 if Docker not available
   - Fall back to direct process management if PM2 fails
2. Changed inter-service communication to use localhost in Replit
3. Standardized port assignments across all environments
4. Implemented proper process tracking and cleanup
5. Added comprehensive error handling and diagnostics

## Lessons
1. Process management is a viable alternative to containerization
2. Hybrid approaches can bridge capability gaps across environments
3. Automatic environment detection improves developer experience
4. Well-designed fallback mechanisms enhance reliability
5. PM2 provides many containerization benefits without requiring Docker

## Next Steps
1. Test the solution across all three environments
2. Monitor performance differences between deployment models
3. Consider adding health checks to verify service availability
4. Explore database connection pooling to improve efficiency
5. Document the new architecture for future team members