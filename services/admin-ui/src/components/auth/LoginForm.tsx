import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';

interface LoginFormProps {
  onLoginSuccess?: () => void;
}

const LoginForm: React.FC<LoginFormProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [debug, setDebug] = useState<string>('');
  
  const { login } = useAuth();
  
  // Add debug information about the API connection
  useEffect(() => {
    // Use API_URL from environment or relative URL via proxy
    const apiUrl = import.meta.env.VITE_API_URL || '';
    setDebug(`Using API at ${apiUrl || 'via proxy'}\nDefault credentials: admin/admin`);
  }, []);
  
  // Function to make a direct login request to test the API
  const testDirectLogin = async () => {
    setIsSubmitting(true);
    setError(null);
    
    try {
      // Use API URL from environment or default to relative URL
      const apiUrl = import.meta.env.VITE_API_URL || '';
      setDebug(`Testing direct API at ${apiUrl || 'via proxy'}/api/v1/auth/login/direct...`);
      
      const response = await fetch(`${apiUrl}/api/v1/auth/login/direct`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          username: 'admin',
          password: 'admin'
        })
      });
      
      // Get response text first to debug any parsing issues
      const responseText = await response.text();
      setDebug(`Raw API response: ${responseText}`);
      
      try {
        // Now parse the JSON
        const data = JSON.parse(responseText);
        setDebug(`API test results:\nStatus: ${response.status}\nResponse: ${JSON.stringify(data, null, 2)}`);
        
        if (response.ok) {
          if (data.access_token && data.refresh_token) {
            // Store tokens manually
            localStorage.setItem('accessToken', data.access_token);
            localStorage.setItem('refreshToken', data.refresh_token);
            
            setDebug(`Login successful! 
AccessToken: ${data.access_token?.substring(0, 15)}...
RefreshToken: ${data.refresh_token?.substring(0, 15)}...
Redirecting to dashboard...`);
            
            // Reload the page to apply tokens
            setTimeout(() => {
              window.location.href = '/';
            }, 2000);
          } else {
            setError(`API response missing tokens. Access token: ${data.access_token ? 'Yes' : 'No'}, Refresh token: ${data.refresh_token ? 'Yes' : 'No'}`);
          }
        } else {
          setError(`API test failed with status ${response.status}: ${data.detail || 'Unknown error'}`);
        }
      } catch (jsonError) {
        setError(`Failed to parse JSON response: ${jsonError instanceof Error ? jsonError.message : 'Unknown error'}`);
      }
    } catch (err: any) {
      console.error('API test failed:', err);
      setError(`API test failed: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!username || !password) {
      setError('Please enter both username and password');
      return;
    }
    
    setError(null);
    setIsSubmitting(true);
    
    try {
      await login(username, password);
      
      if (onLoginSuccess) {
        onLoginSuccess();
      }
    } catch (err: any) {
      console.error('Login failed:', err);
      
      // Display appropriate error message
      if (err.response?.status === 401) {
        setError('Invalid username or password');
      } else if (err.response?.status === 400) {
        setError('Invalid login request. Please check your input.');
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else if (err.message) {
        setError(`Login error: ${err.message}`);
      } else {
        setError('An unknown error occurred. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // No environment check needed - OAuth works properly
  
  return (
    <div className="login-form-container">
      <form className="login-form" onSubmit={handleSubmit}>
        <h2>Admin Login</h2>
        
        {error && <div className="error-message">{error}</div>}
        
        <div className="form-group">
          <label htmlFor="username">Username</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={isSubmitting}
            autoComplete="username"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={isSubmitting}
            autoComplete="current-password"
          />
        </div>
        
        <div className="button-group">
          <button 
            type="submit" 
            className="login-button" 
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Logging in...' : 'Login'}
          </button>
          
          <button 
            type="button"
            className="direct-login-button"
            onClick={testDirectLogin}
            disabled={isSubmitting}
          >
            Test Direct API
          </button>
        </div>
        
        {debug && <div className="debug-info">{debug}</div>}
      </form>
      
      <style>{`
        .button-group {
          display: flex;
          gap: 10px;
          margin-bottom: 15px;
        }
        
        .direct-login-button {
          background-color: #606060;
          color: white;
          border: none;
          padding: 10px 15px;
          border-radius: 4px;
          cursor: pointer;
        }
        
        .notice-message {
          margin-bottom: 20px;
          padding: 10px;
          background-color: #fff8e6;
          border: 1px solid #f5c400;
          border-radius: 4px;
          color: #5a4500;
          font-size: 14px;
          line-height: 1.5;
        }
        
        .debug-info {
          margin-top: 20px;
          padding: 10px;
          background-color: #f5f5f5;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-family: monospace;
          white-space: pre-wrap;
          font-size: 12px;
        }
      `}</style>
    </div>
  );
};

export default LoginForm;