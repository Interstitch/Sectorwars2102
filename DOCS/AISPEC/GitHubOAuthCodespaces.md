# GitHub OAuth in Codespaces

This document describes how GitHub OAuth is implemented in Codespaces environments and the fixes applied to make it work properly.

## Problem

GitHub Codespaces routes all traffic through port 443 (HTTPS), but our application was using explicit port numbers in URLs:
- Backend API: Port 8080
- Frontend: Port 3000

This created an issue with OAuth callbacks, as GitHub would attempt to redirect to TCP 8080, but the application was actually listening on TCP 443 in Codespaces, resulting in "Not Found" errors during OAuth authentication.

## Solution

The following changes were made to fix GitHub OAuth in Codespaces:

### 1. Remove Port Numbers from Codespaces URLs

- Updated `src/core/config.py` to generate Codespaces URLs without port numbers
- Modified environment scripts to set URLs without ports for Codespaces

### 2. Improved Codespaces Environment Detection

- Enhanced GitHub OAuth callback function to properly detect Codespaces
- Used request headers to determine the actual host being used
- Added additional logging for debugging OAuth issues

### 3. Frontend Proxy Configuration

- Updated Vite proxy configuration to preserve host headers in GitHub Codespaces
- Added special handling for proxy requests in Codespaces environment
- Ensured frontend auth redirects use the correct proxy URLs

### 4. AuthContext Updates

- Modified frontend OAuth handling to use proper URLs in Codespaces
- Added additional logging to help diagnose issues
- Ensured consistent URL handling across login and registration flows

## Testing

To test GitHub OAuth in Codespaces:

1. Start all services using `./dev-scripts/start-unified.sh`
2. Navigate to the player client frontend
3. Click "Login with GitHub" or "Register with GitHub"
4. The OAuth flow should complete successfully without "Not Found" errors
5. Check the server logs for debugging information if issues persist

## Environment Variables

For GitHub OAuth to work in Codespaces, ensure these environment variables are set correctly:

- `CODESPACE_NAME`: Should be auto-detected in GitHub Codespaces
- `CLIENT_ID_GITHUB`: Your GitHub OAuth Application Client ID
- `CLIENT_SECRET_GITHUB`: Your GitHub OAuth Application Client Secret

You can set these in Codespaces Secrets or directly in your development environment.

## Common Issues

- If you see "Not Found" errors, check that the callback URL doesn't contain port numbers
- If GitHub OAuth redirects fail, verify that frontend proxy configuration is correct
- For other authentication issues, check the server logs for detailed debugging information