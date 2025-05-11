import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import './auth.css';

interface LoginFormProps {
  onLoginSuccess?: () => void;
  switchToRegister?: () => void;
  onClose?: () => void;
}

const LoginForm: React.FC<LoginFormProps> = ({ onLoginSuccess, switchToRegister, onClose }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { login, loginWithOAuth } = useAuth();

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
    } catch (err) {
      console.error('Login failed:', err);
      setError('Invalid username or password');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOAuthLogin = (provider: string) => {
    loginWithOAuth(provider);
  };

  return (
    <div className="login-form-container">
      <form className="login-form" onSubmit={handleSubmit}>
        {onClose && (
          <button type="button" className="close-button" onClick={onClose}>
            ✕
          </button>
        )}
        <h2>Access Your Universe</h2>

        {error && <div className="error-message">{error}</div>}

        <div className="form-group">
          <label htmlFor="username">Commander ID</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={isSubmitting}
            autoComplete="username"
            placeholder="Enter your commander name"
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">Security Code</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={isSubmitting}
            autoComplete="current-password"
            placeholder="Enter your password"
          />
        </div>

        <button
          type="submit"
          className="login-button"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Launching...' : 'Play Now'}
        </button>

        <div className="register-link">
          New to Sector Wars? <button type="button" onClick={switchToRegister} className="text-button">Create Account</button>
        </div>

        <div className="oauth-divider">
          <span>Or Sign In With</span>
        </div>

        <div className="oauth-buttons">
          <button
            type="button"
            onClick={() => handleOAuthLogin('steam')}
            className="oauth-button steam-button"
          >
            Steam
          </button>
          <button
            type="button"
            onClick={() => handleOAuthLogin('github')}
            className="oauth-button github-button"
          >
            GitHub
          </button>
          <button
            type="button"
            onClick={() => handleOAuthLogin('google')}
            className="oauth-button google-button"
          >
            Google
          </button>
        </div>
      </form>
    </div>
  );
};

export default LoginForm;