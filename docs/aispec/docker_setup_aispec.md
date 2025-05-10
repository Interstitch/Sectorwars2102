# AI Spec: Sector Wars 2102 - Docker Setup (Iteration 1)

**Source Document:** `docs/devops_setup/docker_setup.md`
**Date:** May 10, 2025

## Docker Environment Components (Orchestrated by `docker-compose.yml`):
1.  **PHP Application Service (`app`):**
    *   Base: `php:8.3-fpm`.
    *   Extensions: `pdo_pgsql`, common web app extensions.
    *   Code: Mounted from host.
    *   Composer: For PHP dependencies.

2.  **Web Server Service (`web` or `nginx`):**
    *   Base: `nginx:latest`.
    *   Config: Custom Nginx config for PHP-FPM & static assets.
    *   Ports: Exposes 80/443.

3.  **PostgreSQL Database Service (`db`):**
    *   Base: `postgres:16`.
    *   Env Vars: User, password, DB name.
    *   Persistence: Docker volume (`pgdata`).

## Key Files (Conceptual Content Outlined in Source Document):
*   **`Dockerfile` (for `app` service):**
    *   FROM `php:8.3-fpm`.
    *   Installs system dependencies & PHP extensions (`pdo_pgsql`).
    *   Installs Composer.
*   **`docker-compose.yml`:**
    *   Defines `app`, `web`, `db` services.
    *   `app`: Builds from `Dockerfile`, mounts app code, depends on `db`.
    *   `web`: Uses `nginx` image, mounts Nginx config, depends on `app`, exposes port (e.g., 8080:80).
    *   `db`: Uses `postgres` image, sets env vars for credentials, mounts `pgdata` volume.
    *   Defines `pgdata` volume and `sectorwars_network` bridge network.
*   **Nginx Configuration (`docker/nginx/default.conf`):**
    *   Listens on port 80.
    *   Sets document root (e.g., `/var/www/html/public`).
    *   Configures `location /` to try files or pass to `index.php`.
    *   Configures `location ~ \.php$` to pass requests to PHP-FPM (`app:9000`).

## Next Steps (DevOps Iteration 2):
- Create actual `Dockerfile`, `docker-compose.yml`, Nginx config.
- Test setup.
- Document Docker commands.
- Consider adding Adminer/pgAdmin.
