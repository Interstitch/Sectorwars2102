# Nginx Gateway Service

This service provides the main reverse proxy and load balancer for the Sectorwars multi-regional architecture.

## Features

- Load balancing across multiple backend services
- SSL termination
- Rate limiting and security headers
- Regional API routing
- WebSocket support for real-time features
- Static asset caching

## SSL Certificates

Place your SSL certificates in the `ssl/` directory:
- `cert.pem` - SSL certificate
- `key.pem` - Private key

For development, you can generate self-signed certificates:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem \
    -out ssl/cert.pem \
    -subj "/C=US/ST=Dev/L=Dev/O=Dev/CN=localhost"
```

## Configuration

The main configuration is in `nginx.conf` and includes:

- Central Nexus API routing (`/api/v1/`)
- Regional API routing (`/api/v1/regions/{region}/`)
- Admin UI routing (`/admin/`)
- Player client routing (`/`)
- WebSocket routing (`/ws/`)
- Health checks (`/health`)
- Monitoring endpoints (`/metrics`)

## Building

This service is built as part of the multi-regional docker-compose setup:

```bash
docker-compose -f docker-compose.multi-regional.yml build nginx-gateway
```