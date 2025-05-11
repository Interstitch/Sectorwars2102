import React from 'react';
import { useNavigate } from 'react-router-dom';
import LoginForm from '../auth/LoginForm';
import { useAuth } from '../../contexts/AuthContext';
import './pages.css';

interface LoginPageProps {
  apiStatus: string;
}

const LoginPage: React.FC<LoginPageProps> = ({ apiStatus }) => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  
  // If already authenticated, redirect to dashboard
  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);
  
  const handleLoginSuccess = () => {
    navigate('/dashboard');
  };
  
  return (
    <div className="login-page">
      <div className="login-page-content">
        <h1>Welcome to Sector Wars 2102</h1>
        <p className="login-description">Log in to continue your adventure in space</p>
        
        {apiStatus.includes('Error') && (
          <div className="api-error-notice">
            <span className="api-error-icon">⚠️</span>
            <div className="api-error-message">
              <strong>Server Connection Issue</strong>
              <p>The game server appears to be offline. Login functionality may be limited.</p>
            </div>
          </div>
        )}
        
        <LoginForm onLoginSuccess={handleLoginSuccess} />
      </div>
    </div>
  );
};

export default LoginPage;