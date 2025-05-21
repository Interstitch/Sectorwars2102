# Docker Networking in GitHub Codespaces

This document explains networking behavior in Docker containers running in GitHub Codespaces, which may help diagnose and fix connectivity issues.

## Key Findings

After thorough diagnostics on the networking environment, we found:

1. **DNS Resolution Works**: The containers can properly resolve both internal container names (like `gameserver`) and external domains (like `google.com`).

2. **HTTP Connectivity Works**: HTTP/HTTPS requests to both internal services and external websites succeed.

3. **PING Does Not Work**: ICMP traffic (ping) fails from inside the containers. This is a common restriction in many container environments for security reasons.

4. **Container-to-Container Communication**: Works correctly using service names defined in docker-compose.yml.

## Recommended Connection Methods

Based on our tests, here are the most reliable ways to connect services:

### From Browser to API Server

Use the proxy configuration in Vite, which enables requests to go through the frontend server to the API server:

```javascript
// In your frontend code
fetch('/api/v1/status')  // Use relative URLs
```

This approach:
- Avoids CORS issues
- Works consistently across all environments
- Handles GitHub Codespaces port forwarding quirks
- Allows the proxy to manage connections

### From Container to Container

Inside a Docker container, use the service name to connect to other containers:

```
http://gameserver:8080/api/v1/status
```

This approach:
- Uses Docker's internal DNS resolution
- Works regardless of the external environment (local, Codespaces, Replit)
- Provides the most reliable container-to-container communication

### For Testing External Connectivity

If you need to test connectivity to external sites:

1. Use HTTP/HTTPS requests rather than ping
2. For browser tests, be aware of CORS restrictions 
3. For server-side tests, direct HTTP requests work well

## Common Issues and Solutions

### CORS Errors in Browser

If you see CORS errors when trying to access the API directly from the browser:
- Use the proxy approach with relative URLs
- Ensure your Vite proxy configuration is correct
- Don't try to access the API via its direct URL from browser code

### GitHub Codespaces Port Doubling

GitHub Codespaces has a known issue where redirected URLs can get an extra port appended:
- Correct: `https://codespace-name-8080.app.github.dev/api/v1/status`
- Incorrect: `https://codespace-name-8080.app.github.dev:8080/api/v1/status`

The Vite proxy and frontend code has special handling to fix this automatically.

### External Sites Accessible But PING Fails

This is expected behavior and not a problem:
- Many container environments block ICMP (ping) traffic but allow HTTP
- Use HTTP requests to test connectivity instead of ping
- The ping failure doesn't indicate an issue with your networking

## Technical Details

### Docker DNS Resolution

Docker uses an internal DNS resolver (usually at 127.0.0.11) that handles:
- Service name resolution for services in docker-compose.yml
- Forwarding external DNS requests to the host's DNS servers

### Network Topology

In our Docker Compose setup:
- Each container connects to a shared bridge network
- The gateway (172.18.0.1) provides access to the host and external networks
- Container-to-container communication happens directly within the bridge network

### Proxy Configuration

The Vite configuration includes a proxy that forwards requests from `/api/*` to the API server:

```javascript
proxy: {
  '/api': {
    target: 'http://gameserver:8080',
    changeOrigin: true,
    secure: false,
    ws: true,
    rewrite: (path) => path
  }
}
```

This is the most robust way to handle API requests from the frontend.