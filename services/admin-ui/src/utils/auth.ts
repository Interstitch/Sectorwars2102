/**
 * Authentication utility functions
 */

import axios from 'axios';

// Create axios instance with default config
export const api = axios.create({
  baseURL: '', // Will use proxy
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Decode a JWT token to get payload without validation
 */
export const decodeToken = (token: string): any => {
  try {
    if (!token || typeof token !== 'string') {
      console.error('Invalid token format:', token);
      return null;
    }
    
    const parts = token.split('.');
    if (parts.length !== 3) {
      console.error('Token does not have 3 parts:', token);
      return null;
    }
    
    const base64Url = parts[1];
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
  if (!token) {
    console.error('No token provided to isTokenExpired');
    return true;
  }
  
  const decodedToken = decodeToken(token);
  if (!decodedToken || !decodedToken.exp) {
    console.error('Token invalid or missing expiration:', decodedToken);
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
  if (!token) {
    console.error('No token provided to getTokenTimeRemaining');
    return 0;
  }
  
  const decodedToken = decodeToken(token);
  if (!decodedToken || !decodedToken.exp) {
    console.error('Token invalid or missing expiration');
    return 0;
  }
  
  const expirationTime = decodedToken.exp * 1000;
  const currentTime = Date.now();
  const timeRemaining = expirationTime - currentTime;
  
  return Math.max(0, Math.floor(timeRemaining / 1000));
};