import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import axios from 'axios';

export interface User {
  id: string;
  username: string;
  email: string;
  is_admin: boolean;
  is_active: boolean;
  last_login: string | null;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
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
  const [token, setToken] = useState<string | null>(null);
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
    // This works in Docker, Replit, and local development because Vite is 
    // configured to proxy /api requests to the gameserver
    console.log('Using Vite proxy through relative URL');
    return '';
  };

  // Initialize API URL
  const apiUrl = getApiUrl();
  
  console.log('Initialized API URL:', apiUrl);
  
  // Helper function to clear auth data
  const clearAuthData = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    axios.defaults.headers.common['Authorization'] = '';
    setUser(null);
    setToken(null);
  };
  
  // Refresh token function
  const refreshToken = async (): Promise<void> => {
    const refreshTokenStr = localStorage.getItem('refreshToken');
    if (!refreshTokenStr) {
      console.error('No refresh token available in localStorage');
      throw new Error('No refresh token available');
    }
    
    try {
      console.log('Attempting to refresh token with refresh_token:', refreshTokenStr.substring(0, 5) + '...');
      
      // Use API URL from environment or default to relative URL
      const directApiUrl = import.meta.env.VITE_API_URL || '';
      
      const response = await fetch(
        `${directApiUrl}/api/v1/auth/refresh`,
        { 
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({ refresh_token: refreshTokenStr })
        }
      );
      
      // Check if the response is successful first
      if (!response.ok) {
        // If we get an error response, throw an error with the status code
        throw new Error(`Server returned status ${response.status}`);
      }
      
      // Get response text for debugging
      const responseText = await response.text();
      console.log('Raw refresh token response:', responseText);
      
      if (!responseText || responseText.trim() === '') {
        console.error('Empty response from refresh endpoint');
        throw new Error('Empty response from server');
      }
      
      // Parse the response manually
      let data;
      try {
        data = JSON.parse(responseText);
        console.log('Parsed refresh token data:', data);
      } catch (parseError) {
        console.error('Failed to parse refresh token response:', parseError);
        throw new Error(`Invalid JSON response: ${responseText.substring(0, 50)}...`);
      }
      
      // Destructure with default empty values to prevent undefined errors
      const { access_token = '', refresh_token = '' } = data || {};
      
      if (!access_token || !refresh_token) {
        console.error('Missing tokens in refresh response:', data);
        throw new Error(
          `Incomplete token data: Access token=${!!access_token}, Refresh token=${!!refresh_token}`
        );
      }
      
      // Store new tokens
      localStorage.setItem('accessToken', access_token);
      localStorage.setItem('refreshToken', refresh_token);
      setToken(access_token);
      
      // Update auth header for axios requests
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
        setToken(accessToken);
        
        // Try to get user profile
        const response = await axios.get<User>(`${apiUrl}/api/v1/auth/me`);
        setUser(response.data);
        console.log('Auth successful - user loaded:', response.data);
      } catch (error) {
        console.error('Initial auth check failed:', error);
        
        // Try token refresh if initial check fails
        try {
          await refreshToken();
          const userResponse = await axios.get<User>(`${apiUrl}/api/v1/auth/me`);
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
      
      // Use API URL from environment or default to relative URL
      const directApiUrl = import.meta.env.VITE_API_URL || '';
      console.log('Using API URL:', directApiUrl || 'via proxy');
      
      try {
        console.log('Attempting direct login call to gameserver API');
        
        // Use fetch API instead of axios for better control
        const directResponse = await fetch(`${directApiUrl}/api/v1/auth/login/direct`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: JSON.stringify({
            username,
            password,
          })
        });
        
        // Check if the response is successful
        if (!directResponse.ok) {
          // Handle HTTP error status
          if (directResponse.status === 401) {
            throw new Error('Invalid username or password');
          } else {
            const errorText = await directResponse.text();
            throw new Error(`Server error (${directResponse.status}): ${errorText}`);
          }
        }
        
        // Get response text first for debugging
        const responseText = await directResponse.text();
        console.log('Raw API response:', responseText);
        
        if (!responseText || responseText.trim() === '') {
          throw new Error('Empty response from server');
        }
        
        // Parse the response manually
        let data;
        try {
          data = JSON.parse(responseText);
          console.log('Parsed login data:', data);
        } catch (parseError) {
          console.error('Failed to parse login response:', parseError);
          throw new Error(`Invalid JSON response: ${responseText.substring(0, 50)}...`);
        }
        
        // Destructure with default empty values to prevent undefined errors
        const { access_token = '', refresh_token = '', user_id = '' } = data || {};

        if (!access_token || !refresh_token) {
          console.error('Missing tokens in login response:', data);
          throw new Error(
            `Incomplete token data: Access token=${!!access_token}, Refresh token=${!!refresh_token}`
          );
        }

        // Store tokens in localStorage
        localStorage.setItem('accessToken', access_token);
        localStorage.setItem('refreshToken', refresh_token);
        setToken(access_token);

        // Set authorization header for future axios requests
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

        // Get user data
        console.log('Fetching user data from /api/v1/auth/me');
        try {
          const userResponse = await fetch(`${directApiUrl}/api/v1/auth/me`, {
            headers: {
              'Authorization': `Bearer ${access_token}`,
              'Content-Type': 'application/json',
            }
          });
          
          if (!userResponse.ok) {
            console.warn(`User data fetch failed with status ${userResponse.status}`);
            throw new Error(`Failed to fetch user data: ${userResponse.status}`);
          }
          
          const userData = await userResponse.json();
          setUser(userData);
          console.log('Login successful with direct login endpoint');
        } catch (userError) {
          console.error('Failed to fetch user data, but login was successful:', userError);
          // Fetch user data failed, but login succeeded
          // We could still try to extract user_id from the token if needed
          if (user_id) {
            setUser({
              id: user_id,
              username: username,
              email: '',
              is_admin: false,
              is_active: true,
              last_login: null
            });
          }
        }
        return;
      } catch (error) {
        console.error('Login attempt failed:', error);
        throw error;
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
    token,
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