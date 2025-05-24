# API Connectivity Test Guide

This document explains how to use the API connectivity tests to diagnose and fix issues with accessing the API server.

## Available Tests

1. **Browser Test (`simple-test.html`)**
   - Tests API connectivity directly from your browser
   - Detects your environment (Codespaces, local, etc.)
   - Tests different URL patterns to find what works
   - Subject to browser CORS restrictions

2. **Server-Side Test**
   - Runs inside the Docker container, not subject to browser restrictions
   - Tests multiple URL patterns including internal Docker networking
   - Generates comprehensive HTML report

3. **Comprehensive Browser Test (`browser-test.html`)**
   - Advanced browser-based testing with more detailed diagnostics
   - Compares server-side and browser-side results

## How to Use the Tests

### Browser Test

1. Navigate to `/simple-test.html` in your browser
2. The test automatically detects your environment
3. Click the test buttons to try different URL patterns
4. The recommended approach is to use the proxy URL (`/api/v1/status`)

### Server-Side Test

1. Inside the player-client container, run:
   ```
   ./run_simple_test.sh
   ```
2. OR from your host machine:
   ```
   docker-compose exec player-client ./run_simple_test.sh
   ```
3. View the results at `/simple-test-results.html` in your browser

### Comprehensive Browser Test

1. Navigate to `/browser-test.html` in your browser
2. This page shows both server-side and browser-side test results
3. It helps identify if issues are with Docker networking or browser security

## Common Issues and Solutions

### 1. CORS Errors

If you see errors like "Access to fetch at X from origin Y has been blocked by CORS policy":

- Use the proxy URL (`/api/v1/status`) which avoids CORS issues
- Check that the CORS middleware is properly configured in the API server
- In development, ensure the Vite proxy is correctly set up

### 2. GitHub Codespaces Port Doubling

GitHub Codespaces has a known issue with port forwarding where URLs can get an extra port appended:
- Correct: `https://codespace-name-8080.app.github.dev/api/v1/status`
- Incorrect: `https://codespace-name-8080.app.github.dev:8080/api/v1/status`

Our frontend code has special handling to fix this. If you're seeing issues:
- Use the `/api/v1/status` relative URL with the proxy
- Check that port forwarding is publicly accessible

### 3. Docker Network Issues

If server-side tests work but browser tests don't:
- This indicates a network or CORS issue, not an API problem
- Use the proxy URL from your browser
- From server-side code, use `http://gameserver:8080` for direct access

## Correct URL Patterns

| Environment | Browser URL          | Server-to-Server URL     |
|-------------|--------------------|--------------------------|
| Local Dev   | `/api/v1/status`   | `http://gameserver:8080` |
| Codespaces  | `/api/v1/status`   | `http://gameserver:8080` |
| Replit      | `/api/v1/status`   | `http://localhost:8080`  |

## Need Help?

If you continue to experience issues:
1. Run all tests and collect the results
2. Check that all services are running correctly
3. Verify that port forwarding is configured properly in Codespaces