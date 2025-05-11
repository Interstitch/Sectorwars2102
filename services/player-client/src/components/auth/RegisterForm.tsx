import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import './auth.css';

interface RegisterFormProps {
  onRegisterSuccess?: () => void;
  switchToLogin?: () => void;
  onClose?: () => void;
}

const RegisterForm: React.FC<RegisterFormProps> = ({ onRegisterSuccess, switchToLogin, onClose }) => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { register, registerWithOAuth } = useAuth();
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic validation
    if (!username || !email || !password || !confirmPassword) {
      setError('Please fill in all fields');
      return;
    }
    
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }
    
    setError(null);
    setIsSubmitting(true);
    
    try {
      await register(username, email, password);
      if (onRegisterSuccess) {
        onRegisterSuccess();
      }
    } catch (err: any) {
      console.error('Registration failed:', err);
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Registration failed. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleOAuthRegister = (provider: string) => {
    registerWithOAuth(provider);
  };
  
  return (
    <div className="register-form-container">
      <form className="register-form" onSubmit={handleSubmit}>
        {onClose && (
          <button type="button" className="close-button" onClick={onClose}>
            ✕
          </button>
        )}
        <h2>Create Your Account</h2>

        {error && <div className="error-message">{error}</div>}
        
        <div className="form-group">
          <label htmlFor="username">Commander Name</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={isSubmitting}
            autoComplete="username"
            placeholder="Choose a unique commander name"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={isSubmitting}
            autoComplete="email"
            placeholder="Your email address"
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
            autoComplete="new-password"
            placeholder="At least 8 characters"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="confirm-password">Confirm Password</label>
          <input
            type="password"
            id="confirm-password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            disabled={isSubmitting}
            autoComplete="new-password"
            placeholder="Repeat your password"
          />
        </div>
        
        <button 
          type="submit" 
          className="register-button" 
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Creating Account...' : 'Register to Play'}
        </button>

        <div className="login-link">
          Already have an account? <button type="button" onClick={switchToLogin} className="text-button">Sign In</button>
        </div>

        <div className="oauth-divider">
          <span>Or Register With</span>
        </div>

        <div className="oauth-buttons">
          <button 
            type="button"
            onClick={() => handleOAuthRegister('steam')}
            className="oauth-button steam-button"
          >
            Steam
          </button>
          <button 
            type="button"
            onClick={() => handleOAuthRegister('github')}
            className="oauth-button github-button"
          >
            GitHub
          </button>
          <button 
            type="button"
            onClick={() => handleOAuthRegister('google')}
            className="oauth-button google-button"
          >
            Google
          </button>
        </div>
      </form>
    </div>
  );
};

export default RegisterForm;