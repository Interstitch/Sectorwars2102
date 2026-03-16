import React, { createContext, useState, useContext, useEffect, useRef, ReactNode } from 'react';
import axios from 'axios';
import apiClient from '../services/apiClient';

interface User {
  id: string;
  username: string;
  email?: string;
  is_admin?: boolean;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  loginWithOAuth: (provider: string) => void;
  registerWithOAuth: (provider: string) => void;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

// Type for response data from login/register endpoints
interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user_id: string;
  [key: string]: any;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  
  // Use Vite proxy for all API requests to avoid CORS issues
  const getApiUrl = () => {
    // If an environment variable is explicitly set, use it
    if (import.meta.env.VITE_API_URL) {
      console.log('Using VITE_API_URL:', import.meta.env.VITE_API_URL);
      return import.meta.env.VITE_API_URL;
    }

    const windowUrl = window.location.origin;
    console.log('Current window URL:', windowUrl);

    // Always use the current origin to leverage Vite proxy in Docker environments
    // This ensures all API calls go through the Vite dev server proxy
    console.log('Using current origin with Vite proxy for Docker environment');
    return window.location.origin;  // Use current origin, which will use the proxy
  };
  
  // Initialize axios with API URL - use useMemo-like pattern with ref to avoid recalculation
  const apiUrlRef = useRef<string | null>(null);
  if (apiUrlRef.current === null) {
    apiUrlRef.current = getApiUrl();
  }
  const apiUrl = apiUrlRef.current;

  // Track if auth check has been performed
  const authCheckPerformed = useRef(false);

  // Check if user is already authenticated on mount (only once)
  useEffect(() => {
    const checkAuth = async () => {
      if (authCheckPerformed.current) {
        console.log('Auth check already performed, skipping');
        return;
      }
      authCheckPerformed.current = true;
      setIsLoading(true);

      const accessToken = localStorage.getItem('accessToken');
      if (accessToken) {
        try {
          // Ensure the global axios header is in sync (for any code still
          // using the global axios instance directly).
          axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;

          // Use apiClient which will automatically refresh the token on 401
          console.log('Using standard /me endpoint with', apiUrl);
          const response = await apiClient.get<User>(`/api/v1/auth/me`);

          console.log('Auth check successful - user data retrieved');
          setUser(response.data);
        } catch (error) {
          console.error('Failed to validate token:', error);
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          axios.defaults.headers.common['Authorization'] = '';
        }
      } else {
        console.log('No access token found in localStorage');
      }

      setIsLoading(false);
    };

    checkAuth();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Run only on mount - apiUrl is stable via ref, authCheckPerformed prevents duplicates
  
  const login = async (username: string, password: string) => {
    setIsLoading(true);

    try {
      console.log('Attempting login with API URL:', apiUrl);

      // Try standard JSON endpoint
      try {
        console.log('Trying JSON login endpoint...');
        const response = await axios.post<AuthResponse>(`${apiUrl}/api/v1/auth/login/json`, {
          username,
          password,
        }, {
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });

        const { access_token, refresh_token } = response.data;
        // Store user ID for future reference
        localStorage.setItem('userId', response.data.user_id);

        // Store tokens in localStorage
        localStorage.setItem('accessToken', access_token);
        localStorage.setItem('refreshToken', refresh_token);

        // Set authorization header
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

        // Get user data
        const userResponse = await axios.get<User>(`${apiUrl}/api/v1/auth/me`);
        setUser(userResponse.data);
        console.log('Login successful with JSON endpoint');
        return;
      } catch (jsonError) {
        console.warn('JSON login attempt failed:', jsonError);

        // If JSON login fails, try form-based login as fallback
        console.log('Trying form-based login as fallback...');

        // Create form data
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        try {
          const response = await axios.post<AuthResponse>(`${apiUrl}/api/v1/auth/login`, formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          });

          const { access_token, refresh_token } = response.data;
          // Store user ID for future reference
          localStorage.setItem('userId', response.data.user_id);

          // Store tokens in localStorage
          localStorage.setItem('accessToken', access_token);
          localStorage.setItem('refreshToken', refresh_token);

          // Set authorization header
          axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

          // Get user data
          const userResponse = await axios.get<User>(`${apiUrl}/api/v1/auth/me`);
          setUser(userResponse.data);
          console.log('Login successful with form-based endpoint');
        } catch (formError) {
          console.warn('Form-based login attempt failed:', formError);
          throw formError;
        }
      }
    } catch (error) {
      console.error('All login attempts failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (username: string, email: string, password: string): Promise<void> => {
    setIsLoading(true);

    try {
      console.log('Attempting registration with API URL:', apiUrl);

      // Register user
      await axios.post<AuthResponse>(`${apiUrl}/api/v1/auth/register`, {
        username,
        email,
        password,
      });

      console.log('Registration successful, attempting login');

      // After registration, automatically log in
      await login(username, password);
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const loginWithOAuth = (provider: string) => {
    // Redirect to OAuth provider for login
    // Make sure we don't have a stale registration flag
    sessionStorage.removeItem('oauth_register');

    // For GitHub Codespaces, construct the correct URL directly
    let oauthUrl;
    if (window.location.hostname.includes('.app.github.dev') ||
        window.location.hostname.includes('github.dev')) {
      // Get the codespace name from the hostname
      const hostname = window.location.hostname;
      console.log('GitHub Codespaces environment detected for OAuth');
      console.log(`Hostname: ${hostname}`);
      
      // Extract the codespace name from the hostname
      // Format is like: super-duper-carnival-qppjvq94q9vcxwqp-3000.app.github.dev
      // We want: super-duper-carnival-qppjvq94q9vcxwqp
      const parts = hostname.split('.');
      const hostnamePart = parts[0]; // e.g., super-duper-carnival-qppjvq94q9vcxwqp-3000
      const lastDashIndex = hostnamePart.lastIndexOf('-');
      const codespaceName = lastDashIndex !== -1 ? hostnamePart.substring(0, lastDashIndex) : hostnamePart;
      console.log(`Codespace name extracted: ${codespaceName}`);
      
      // Construct the URL directly to the gameserver port
      oauthUrl = `https://${codespaceName}-8080.app.github.dev/api/v1/auth/${provider}`;
      console.log(`Using direct URL for OAuth login in Codespaces: ${oauthUrl}`);
    } else {
      // For non-Codespaces environments
      oauthUrl = `${apiUrl}/api/v1/auth/${provider}`;
    }

    console.log(`Redirecting to OAuth URL: ${oauthUrl}`);
    window.location.href = oauthUrl;
  };

  const registerWithOAuth = (provider: string) => {
    // Currently, the backend uses the same endpoint for both login and registration
    // The OAuth provider will handle first-time users as registrations
    // Store in session storage that this was a registration attempt
    sessionStorage.setItem('oauth_register', 'true');

    // For GitHub Codespaces, construct the correct URL directly
    let oauthUrl;
    if (window.location.hostname.includes('.app.github.dev') ||
        window.location.hostname.includes('github.dev')) {
      // Get the codespace name from the hostname
      const hostname = window.location.hostname;
      console.log('GitHub Codespaces environment detected for OAuth registration');
      console.log(`Hostname: ${hostname}`);
      
      // Extract the codespace name from the hostname
      // Format is like: super-duper-carnival-qppjvq94q9vcxwqp-3000.app.github.dev
      // We want: super-duper-carnival-qppjvq94q9vcxwqp
      const parts = hostname.split('.');
      const hostnamePart = parts[0]; // e.g., super-duper-carnival-qppjvq94q9vcxwqp-3000
      const lastDashIndex = hostnamePart.lastIndexOf('-');
      const codespaceName = lastDashIndex !== -1 ? hostnamePart.substring(0, lastDashIndex) : hostnamePart;
      console.log(`Codespace name extracted: ${codespaceName}`);
      
      // Construct the URL directly to the gameserver port
      oauthUrl = `https://${codespaceName}-8080.app.github.dev/api/v1/auth/${provider}?register=true`;
      console.log(`Using direct URL for OAuth registration in Codespaces: ${oauthUrl}`);
    } else {
      // For non-Codespaces environments
      oauthUrl = `${apiUrl}/api/v1/auth/${provider}?register=true`;
    }

    console.log(`Redirecting to OAuth URL for registration: ${oauthUrl}`);
    window.location.href = oauthUrl;
  };
  
  const refreshToken = async () => {
    const storedRefreshToken = localStorage.getItem('refreshToken');
    if (!storedRefreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      console.log('Manually refreshing token...');

      // Use plain axios (not apiClient) to avoid re-entering the interceptor
      const response = await axios.post<AuthResponse>(
        `${apiUrl}/api/v1/auth/refresh`,
        { refresh_token: storedRefreshToken },
        { headers: { Authorization: '' } }
      );

      const { access_token, refresh_token } = response.data;

      console.log('Token refresh successful, updating tokens');

      localStorage.setItem('accessToken', access_token);
      localStorage.setItem('refreshToken', refresh_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    } catch (error) {
      console.error('Token refresh failed:', error);

      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      axios.defaults.headers.common['Authorization'] = '';
      setUser(null);
      throw error;
    }
  };
  
  const logout = () => {
    const refreshToken = localStorage.getItem('refreshToken');
    
    // Call logout endpoint to invalidate refresh token
    if (refreshToken) {
      axios.post(`${apiUrl}/api/v1/auth/logout`, { refresh_token: refreshToken })
        .catch(error => console.error('Logout error:', error));
    }
    
    // Clear tokens and user
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('userId');
    axios.defaults.headers.common['Authorization'] = '';
    setUser(null);
  };
  
  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    loginWithOAuth,
    registerWithOAuth,
    logout,
    refreshToken,
  };
  
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};