import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';

const OAuthCallback: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [status, setStatus] = useState<string>('Processing authentication...');
  const [error, setError] = useState<string | null>(null);
  const [userInfo, setUserInfo] = useState<any>(null);
  const [playerInfo, setPlayerInfo] = useState<any>(null);
  const { refreshToken: authRefreshToken } = useAuth();

  useEffect(() => {
    const handleOAuthCallback = async () => {
      try {
        // Parse the URL search params
        const params = new URLSearchParams(location.search);
        console.log('OAuth callback URL search params:', location.search);
        console.log('Raw params:', Object.fromEntries(params.entries()));
        
        const accessToken = params.get('access_token');
        const refreshToken = params.get('refresh_token');
        const userId = params.get('user_id');
        // Check for new user indicators either from query param or in session storage
        const isNewUser = params.get('is_new_user') === 'true' || sessionStorage.getItem('oauth_register') === 'true';

        console.log('OAuth callback parameters:', { 
          accessToken: accessToken ? 'present' : 'missing',
          refreshToken: refreshToken ? 'present' : 'missing',
          userId: userId ? 'present' : 'missing',
          isNewUser
        });

        if (!accessToken || !refreshToken || !userId) {
          throw new Error(`Invalid OAuth callback parameters: accessToken=${Boolean(accessToken)}, refreshToken=${Boolean(refreshToken)}, userId=${Boolean(userId)}`);
        }

        console.log('OAuth callback received tokens:', { 
          accessToken: accessToken.substring(0, 5) + '...',
          refreshToken: refreshToken.substring(0, 5) + '...',
          userId
        });

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

        // NOTE: Removed API calls from OAuth callback due to GitHub Codespaces authentication requirements
        // The main app will fetch user/player info after redirect using proper authentication context
        setStatus(`Login successful! Launching game...`);

        // Force a reload of authentication state in the AuthContext
        try {
          console.log('Attempting to refresh token through AuthContext...');
          await authRefreshToken();
          console.log('AuthContext refresh token succeeded');
        } catch (refreshError) {
          console.error('Failed to refresh token through AuthContext:', refreshError);
          // Continue anyway, as we'll do a full page reload
        }
        
        // Let's check what happens with the auth tokens
        console.log('Stored tokens for debug:');
        console.log('Access token (substring):', localStorage.getItem('accessToken')?.substring(0, 20) + '...');
        console.log('Refresh token (substring):', localStorage.getItem('refreshToken')?.substring(0, 10) + '...');
        console.log('User ID:', localStorage.getItem('userId'));
        
        // Set a sessionStorage flag to track the redirect
        sessionStorage.setItem('oauth_redirect_completed', 'true');
        
        // Create a function to directly navigate to the dashboard with the token
        const navigateWithToken = () => {
          try {
            // First, make sure the token is correctly set in localStorage
            console.log('Verifying token data is correctly stored in localStorage...');
            if (localStorage.getItem('accessToken') !== accessToken) {
              console.log('Token mismatch! Resetting localStorage values...');
              localStorage.setItem('accessToken', accessToken);
              localStorage.setItem('refreshToken', refreshToken);
              localStorage.setItem('userId', userId);
              
              // Set axios defaults for current session
              axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
            }
            
            // No need to use URL parameters - instead direct to game page
            console.log('Directly navigating to game dashboard...');
            window.location.href = '/game';
          } catch (err) {
            console.error('Error during navigation:', err);
            // Fallback to simple navigation
            window.location.href = '/';
          }
        };
        
        // Redirect after a brief delay
        setTimeout(navigateWithToken, 1500);
      } catch (error) {
        console.error('OAuth callback error:', error);
        setError('Authentication failed. Please try again.');
      }
    };

    handleOAuthCallback();
  }, [location, navigate, authRefreshToken]);

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
          <div style={{marginTop: '20px', padding: '10px', border: '1px solid #ccc', borderRadius: '5px'}}>
            <h4>Authentication Status:</h4>
            <p>✅ GitHub OAuth successful</p>
            <p>✅ Access token stored</p>
            <p>⏳ Redirecting to game dashboard...</p>
            <p><small>Player data will be loaded in the main application</small></p>
          </div>
        </>
      )}
    </div>
  );
};

export default OAuthCallback;