import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import axios from 'axios';

interface User {
  id: string;
  username: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  
  // Get API URL based on environment
  const getApiUrl = () => {
    // If an environment variable is explicitly set, use it
    if (import.meta.env.VITE_API_URL) {
      return import.meta.env.VITE_API_URL;
    }

    const windowUrl = window.location.origin;
    console.log('Current window URL:', windowUrl);

    // In all environments, use relative URLs that go through the Vite proxy
    // This works in Docker, Replit, and local development
    return '';
  };

  // Initialize API URL
  const apiUrl = getApiUrl();
  
  // Helper function to clear auth data
  const clearAuthData = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    axios.defaults.headers.common['Authorization'] = '';
    setUser(null);
  };
  
  // Refresh token function
  const refreshToken = async (): Promise<void> => {
    const refreshTokenStr = localStorage.getItem('refreshToken');
    if (!refreshTokenStr) {
      throw new Error('No refresh token available');
    }
    
    try {
      const response = await axios.post(
        `${apiUrl}/api/v1/auth/refresh`,
        { refresh_token: refreshTokenStr },
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
      clearAuthData();
      throw error;
    }
  };
  
  // Setup authentication check and interceptor
  useEffect(() => {
    // Set up timeout to prevent infinite loading state
    const authTimeout = setTimeout(() => {
      console.warn('Authentication check timed out');
      clearAuthData();
      setIsLoading(false);
    }, 5000);
    
    // Set up axios interceptor for authentication
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
            clearAuthData();
            return Promise.reject(refreshError);
          }
        }
        
        return Promise.reject(error);
      }
    );
    
    // Check if user is already authenticated
    const checkAuth = async () => {
      const accessToken = localStorage.getItem('accessToken');
      if (!accessToken) {
        clearAuthData();
        setIsLoading(false);
        clearTimeout(authTimeout);
        return;
      }
      
      try {
        // Add token to default headers
        axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
        
        // Try to get user profile
        const response = await axios.get(`${apiUrl}/api/v1/auth/me`);
        setUser(response.data);
        console.log('Auth successful - user loaded:', response.data);
      } catch (error) {
        console.error('Initial auth check failed:', error);
        
        // Try token refresh if initial check fails
        try {
          await refreshToken();
          const userResponse = await axios.get(`${apiUrl}/api/v1/auth/me`);
          setUser(userResponse.data);
          console.log('Auth successful after refresh');
        } catch (refreshError) {
          console.error('Refresh token failed:', refreshError);
          clearAuthData();
        }
      } finally {
        clearTimeout(authTimeout);
        setIsLoading(false);
      }
    };
    
    // Start auth check
    checkAuth();
    
    // Clean up
    return () => {
      clearTimeout(authTimeout);
      axios.interceptors.response.eject(interceptor);
    };
  }, []);
  
  // Login function
  const login = async (username: string, password: string) => {
    setIsLoading(true);
    
    try {
      console.log('Attempting login with username:', username);
      
      // Try direct login with credentials as plain parameters
      try {
        console.log('Attempting direct login call to /api/v1/auth/login/direct');
        console.log('API URL:', apiUrl);
        const directResponse = await axios.post(`${apiUrl}/api/v1/auth/login/direct`, {
          username,
          password,
        });

        console.log('Direct login response:', directResponse.status, directResponse.statusText);
        const { access_token, refresh_token } = directResponse.data;

        // Store tokens in localStorage
        localStorage.setItem('accessToken', access_token);
        localStorage.setItem('refreshToken', refresh_token);

        // Set authorization header
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

        // Get user data
        console.log('Fetching user data from /api/v1/auth/me');
        const userResponse = await axios.get(`${apiUrl}/api/v1/auth/me`);
        setUser(userResponse.data);
        console.log('Login successful with direct login endpoint');
        return;
      } catch (directError) {
        console.warn('Direct login attempt failed:', directError);

        // If direct login fails, try JSON login
        try {
          console.log('Trying JSON login endpoint at /api/v1/auth/login/json');
          const response = await axios.post(`${apiUrl}/api/v1/auth/login/json`, {
            username,
            password,
          }, {
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            }
          });

          console.log('JSON login response:', response.status, response.statusText);
          const { access_token, refresh_token } = response.data;

          // Store tokens in localStorage
          localStorage.setItem('accessToken', access_token);
          localStorage.setItem('refreshToken', refresh_token);

          // Set authorization header
          axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

          // Get user data
          const userResponse = await axios.get(`${apiUrl}/api/v1/auth/me`);
          setUser(userResponse.data);
          console.log('Login successful with JSON endpoint');
          return;
        } catch (jsonError) {
          console.warn('JSON login attempt failed:', jsonError);

          // If JSON login fails, try form-based login as fallback
          console.log('Trying form-based login as fallback at /api/v1/auth/login');

          // Create form data
          const formData = new FormData();
          formData.append('username', username);
          formData.append('password', password);

          const response = await axios.post(`${apiUrl}/api/v1/auth/login`, formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          });

          console.log('Form login response:', response.status, response.statusText);
          const { access_token, refresh_token } = response.data;

          // Store tokens in localStorage
          localStorage.setItem('accessToken', access_token);
          localStorage.setItem('refreshToken', refresh_token);

          // Set authorization header
          axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

          // Get user data
          const userResponse = await axios.get(`${apiUrl}/api/v1/auth/me`);
          setUser(userResponse.data);
          console.log('Login successful with form-based endpoint');
        }
      }
    } catch (error) {
      console.error('All login attempts failed:', error);
      clearAuthData();
      throw error;
    } finally {
      setIsLoading(false);
    }
  };
  
  // Logout function
  const logout = () => {
    const refreshTokenStr = localStorage.getItem('refreshToken');

    // Clear tokens and user immediately
    clearAuthData();

    // Call logout endpoint to invalidate refresh token, but don't wait for it
    if (refreshTokenStr) {
      // Set a short timeout to avoid CORS issues during page navigation
      axios.post(`${apiUrl}/api/v1/auth/logout`, { refresh_token: refreshTokenStr }, {
        timeout: 1000 // 1 second timeout
      }).catch(() => {
        // Just log the error, don't block logout
        console.log('Logout token invalidation skipped');
      });
    }

    // Redirect to login page
    window.location.href = '/login';
  };
  
  // Context value
  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
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