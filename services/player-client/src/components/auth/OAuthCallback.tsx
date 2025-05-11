import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';

const OAuthCallback: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [status, setStatus] = useState<string>('Processing authentication...');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleOAuthCallback = async () => {
      try {
        // Parse the URL search params
        const params = new URLSearchParams(location.search);
        const accessToken = params.get('access_token');
        const refreshToken = params.get('refresh_token');
        const userId = params.get('user_id');
        // Check for new user indicators either from query param or in session storage
        const isNewUser = params.get('is_new_user') === 'true' || sessionStorage.getItem('oauth_register') === 'true';

        if (!accessToken || !refreshToken || !userId) {
          throw new Error('Invalid OAuth callback parameters');
        }

        // Store tokens in localStorage
        localStorage.setItem('accessToken', accessToken);
        localStorage.setItem('refreshToken', refreshToken);
        localStorage.setItem('userId', userId);

        // Set default Authorization header for future requests
        axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;

        // Clear the oauth_register flag from session storage
        sessionStorage.removeItem('oauth_register');

        if (isNewUser) {
          setStatus('Registration successful! Setting up your account...');
        } else {
          setStatus('Login successful! Launching game...');
        }

        // Redirect to home after a brief delay
        setTimeout(() => {
          navigate('/', { replace: true });
        }, 1500);
      } catch (error) {
        console.error('OAuth callback error:', error);
        setError('Authentication failed. Please try again.');
      }
    };

    handleOAuthCallback();
  }, [location, navigate]);

  return (
    <div className="oauth-callback-container">
      {error ? (
        <div className="error-message">
          <h3>Authentication Error</h3>
          <p>{error}</p>
          <button 
            onClick={() => navigate('/')} 
            className="login-button"
          >
            Back to Login
          </button>
        </div>
      ) : (
        <>
          <div className="loading-spinner"></div>
          <p>{status}</p>
        </>
      )}
    </div>
  );
};

export default OAuthCallback;