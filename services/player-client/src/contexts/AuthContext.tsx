import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import axios from 'axios';

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
  
  // Use direct URL for gameserver in Codespaces
  const getApiUrl = () => {
    // If an environment variable is explicitly set, use it
    if (import.meta.env.VITE_API_URL) {
      console.log('Using VITE_API_URL:', import.meta.env.VITE_API_URL);
      return import.meta.env.VITE_API_URL;
    }

    const windowUrl = window.location.origin;
    console.log('Current window URL:', windowUrl);

    // For GitHub Codespaces, use proxy to avoid authentication issues with external URLs
    if (windowUrl.includes('.app.github.dev')) {
      console.log('GitHub Codespaces detected - using proxy for API calls');
      return '';  // Use proxy through Vite dev server
    }

    // Local development - still use direct URL to avoid Docker network issues
    if (windowUrl.includes('localhost')) {
      console.log('Using direct localhost API URL');
      return 'http://localhost:8080';
    }

    // For other environments (Replit, etc.) - use proxy
    console.log('Using proxy API URL for', windowUrl);
    return '';  // Empty string means use relative URL with proxy
  };
  
  // Initialize axios with API URL
  const apiUrl = getApiUrl();
  
  // Setup axios interceptor for authentication
  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        
        // If error is 401 and not already retrying, attempt to refresh token
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            await refreshToken();
            
            // Re-attempt the original request with new token
            const accessToken = localStorage.getItem('accessToken');
            originalRequest.headers['Authorization'] = `Bearer ${accessToken}`;
            return axios(originalRequest);
          } catch (refreshError) {
            // If refresh token fails, logout
            logout();
            return Promise.reject(refreshError);
          }
        }
        
        return Promise.reject(error);
      }
    );
    
    // Check if user is already authenticated
    const checkAuth = async () => {
      setIsLoading(true);

      const accessToken = localStorage.getItem('accessToken');
      if (accessToken) {
        try {
          // Check if the token is already in headers - if not, add it
          if (axios.defaults.headers.common['Authorization'] !== `Bearer ${accessToken}`) {
            console.log('Setting axios authorization header');
            axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
          }

          // Standard approach - verify token by getting user profile
          console.log('Using standard /me endpoint with', apiUrl);
          const response = await axios.get<User>(`${apiUrl}/api/v1/auth/me`);
          
          // Successfully got user data - update state
          console.log('Auth check successful - user data retrieved');
          setUser(response.data);
        } catch (error) {
          console.error('Failed to validate token:', error);
          
          // Try token refresh before giving up
          try {
            await refreshToken();
            
            // If refresh succeeded, try again to get user data
            const response = await axios.get<User>(`${apiUrl}/api/v1/auth/me`);
            setUser(response.data);
            console.log('Auth successful after token refresh');
          } catch (refreshError) {
            console.error('Token refresh failed, clearing auth data:', refreshError);
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            axios.defaults.headers.common['Authorization'] = '';
          }
        }
      } else {
        console.log('No access token found in localStorage');
      }

      setIsLoading(false);
    };
    
    checkAuth();
    
    // Clean up interceptor
    return () => {
      axios.interceptors.response.eject(interceptor);
    };
  }, [apiUrl]);
  
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
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }
    
    try {
      const response = await axios.post<AuthResponse>(
        `${apiUrl}/api/v1/auth/refresh`,
        { refresh_token: refreshToken },
        { headers: { Authorization: '' } } // Don't send current auth header
      );
      
      const { access_token, refresh_token } = response.data;
      
      // Store new tokens
      localStorage.setItem('accessToken', access_token);
      localStorage.setItem('refreshToken', refresh_token);
      
      // Update auth header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    } catch (error) {
      console.error('Token refresh failed:', error);
      // Clear tokens and user on refresh failure
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