# Setting Up GitHub OAuth for Sector Wars 2102

This guide explains how to set up GitHub OAuth authentication for the Sector Wars 2102 project, with a focus on making it work across all development environments (local, GitHub Codespaces, and Replit).

## Prerequisites

- GitHub account with owner/admin access to the repository
- Access to GitHub Developer Settings to create OAuth applications

## Step 1: Create a GitHub OAuth Application

1. Go to your GitHub account settings
2. Navigate to **Settings > Developer settings > OAuth Apps**
3. Click **New OAuth App**
4. Fill in the application details:
   - **Application name**: `Sector Wars 2102`
   - **Homepage URL**: Use your repository URL (e.g., `https://github.com/yourusername/Sectorwars2102`)
   - **Application description**: `Web-based space trading simulation game`
   - **Authorization callback URL**: See the next section

## Step 2: Configure Authorization Callback URLs

GitHub OAuth requires callback URLs to be pre-registered. To support all environments, you'll need to register multiple URLs.

### For GitHub Codespaces

For Codespaces, you'll need to use a pattern that works with dynamic Codespace URLs:

1. If your Codespace name is predictable and stays the same:
   ```
   https://your-codespace-name.app.github.dev/api/auth/github/callback
   ```

2. If your repository uses multiple/changing Codespace instances:
   - You'll need to update the callback URL each time you create a new Codespace, or
   - Register multiple callback URLs for different Codespace instances

**Important**:
- GitHub OAuth doesn't support wildcards in callback URLs, so you can't use patterns like `*.app.github.dev/...`
- Do NOT include port numbers (like `-8080`) in the callback URL for Codespaces - GitHub Codespaces routes all traffic through port 443

### For Local Development

Add a localhost URL:
```
http://localhost:8080/api/auth/github/callback
```

### For Replit

Add your Replit URL:
```
https://sectorwars2102.yourusername.repl.co/api/auth/github/callback
```

**Note**: You can add multiple callback URLs in the GitHub OAuth App settings by adding them in separate lines.

## Step 3: Get OAuth Credentials

After creating the OAuth App, GitHub will generate:

- **Client ID**: Public identifier for your app
- **Client Secret**: Private key that should be kept secure

Copy these values to use in the next step.

## Step 4: Set Up Environment Variables

### Using Codespaces Secrets (Recommended for Codespaces)

1. Go to your repository on GitHub
2. Navigate to **Settings > Secrets and variables > Codespaces**
3. Add the following secrets:
   - Name: `CLIENT_ID_GITHUB`, Value: your OAuth app client ID
   - Name: `CLIENT_SECRET_GITHUB`, Value: your OAuth app client secret

   **Note**: GitHub doesn't allow secret names that begin with "GITHUB_", which is why we use the "CLIENT_ID_" prefix instead.

### Using .env File (Local Development)

1. Open or create the `.env` file in the project root
2. Add the following lines:
   ```
   CLIENT_ID_GITHUB=your_client_id
   CLIENT_SECRET_GITHUB=your_client_secret
   ```

   **Note**: While the application supports both `GITHUB_CLIENT_ID` and `CLIENT_ID_GITHUB` formats for backward compatibility, we recommend using the `CLIENT_ID_GITHUB` format for consistency.

### Using Replit Secrets

1. In your Replit project, go to the **Secrets** tool (lock icon)
2. Add the same secrets as above with the `CLIENT_ID_GITHUB` format

## Step 5: Test the Authentication

### To Test in Codespaces:

1. Start the services using Docker Compose:
   ```bash
   ./dev-scripts/start-unified.sh
   ```

2. Open the player client in your browser using the forwarded port URL (usually `https://your-codespace-name.app.github.dev`)

3. Click the "Login with GitHub" button and verify that:
   - You are redirected to GitHub's authorization page
   - After authorizing, you're redirected back to the application
   - You're properly logged in

## Troubleshooting

### Common Issues

1. **404 Not Found on Callback URL**:
   - Ensure the callback URL in your OAuth app exactly matches the URL used by your application
   - Check that your API server is running on port 8080
   - Verify that the Codespace port is forwarded and publicly accessible

2. **Redirect Errors**:
   - Check console logs for API base URL detection issues
   - Ensure environment variables are properly loaded

3. **Authentication Not Working in Codespaces**:
   - Ensure the ports are correctly forwarded and set to "Public" visibility
   - Verify the CLIENT_ID_GITHUB and CLIENT_SECRET_GITHUB are available as environment variables
   - Check that the variables have been loaded correctly using `echo $CLIENT_ID_GITHUB` in the terminal
   - Be aware of URL construction issues with Codespaces port forwarding - avoid having port numbers in both hostname and explicit port (e.g., `hostname-8080.app.github.dev:8080` is incorrect)
   - The frontend will automatically detect Codespaces environments and construct proper OAuth URLs

4. **Internal Server Error During OAuth Callback**:
   - Check if the `deleted` field exists in the `OAuthAccount` model
   - Verify that your database schema is up-to-date by running the alembic migrations
   - Inspect the server logs for specific error details: `docker logs sectorwars2102-gameserver-1`

5. **GitHub pf-signin Error or "Not Found" errors**:
   - This is an issue with GitHub Codespaces handling of OAuth redirects
   - Make sure you're not using port numbers in your callback URLs for Codespaces
   - Ensure the frontend is using proxy-based URLs for OAuth in Codespaces
   - Check that both environment scripts and config files don't include port numbers
   - For detailed troubleshooting, see the `DOCS/AISPEC/GitHubOAuthCodespaces.md` file
   - Restart the player-client container after making changes: `docker-compose restart player-client`

### Debugging Tips

1. Enable debug logging in your application by setting:
   ```
   DEBUG=true
   ```

2. Check the server logs for OAuth redirect and callback URLs:
   ```
   GitHub OAuth redirect URI: https://...
   Environment detected: codespaces
   GitHub Client ID: ...
   ```

3. Inspect network requests in the browser developer tools to see the full redirect flow

## Security Considerations

1. Never commit OAuth secrets to the repository
2. Use environment variables or secrets management systems
3. Consider implementing additional security measures like CSRF protection and state validation
4. For production, set `SECURE_COOKIES=true` and use a strong `JWT_SECRET`

## Additional Resources

- [GitHub OAuth Documentation](https://docs.github.com/en/developers/apps/building-oauth-apps/authorizing-oauth-apps)
- [GitHub Codespaces Documentation](https://docs.github.com/en/codespaces)
- [OAuth 2.0 Security Best Practices](https://oauth.net/2/security-best-practices/)