/**
 * Authentication utility functions
 */

/**
 * Get authentication token from localStorage
 */
export const getAuthToken = (): string | null => {
  return localStorage.getItem('accessToken');
};

/**
 * Decode a JWT token to get payload without validation
 */
export const decodeToken = (token: string): any => {
  try {
    // Handle mock tokens for testing
    if (token.startsWith('mock-')) {
      console.log('Mock token detected, returning test payload');
      const now = Math.floor(Date.now() / 1000);
      return {
        sub: '67890',
        username: 'test_player',
        email: 'player@test.com',
        is_admin: false,
        exp: now + 3600, // 1 hour from now
        iat: now,
      };
    }
    
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Token decode error:', error);
    return null;
  }
};

/**
 * Check if token is expired
 */
export const isTokenExpired = (token: string): boolean => {
  const decodedToken = decodeToken(token);
  if (!decodedToken || !decodedToken.exp) {
    return true;
  }
  
  // Token expiration is in seconds, convert to milliseconds
  const expirationTime = decodedToken.exp * 1000;
  const currentTime = Date.now();
  
  return currentTime >= expirationTime;
};

/**
 * Get time until token expiration in seconds
 */
export const getTokenTimeRemaining = (token: string): number => {
  const decodedToken = decodeToken(token);
  if (!decodedToken || !decodedToken.exp) {
    return 0;
  }
  
  const expirationTime = decodedToken.exp * 1000;
  const currentTime = Date.now();
  const timeRemaining = expirationTime - currentTime;
  
  return Math.max(0, Math.floor(timeRemaining / 1000));
};