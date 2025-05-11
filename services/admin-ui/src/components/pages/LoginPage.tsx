import React from 'react';
import { useNavigate } from 'react-router-dom';
import LoginForm from '../auth/LoginForm';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  
  const handleLoginSuccess = () => {
    navigate('/dashboard');
  };
  
  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <h1>Sector Wars 2102</h1>
          <p className="subtitle">Admin Portal</p>
        </div>
        
        <LoginForm onLoginSuccess={handleLoginSuccess} />
        
        <div className="login-footer">
          <p>Sector Wars 2102 - Admin UI v0.1.0</p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;