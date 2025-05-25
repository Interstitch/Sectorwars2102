import React from 'react';
import { useNavigate } from 'react-router-dom';
import LoginForm from '../auth/LoginForm';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  
  const handleLoginSuccess = () => {
    navigate('/dashboard');
  };
  
  return (
    <div className="min-h-screen bg-surface-primary flex items-center justify-center p-4">
      <div className="card max-w-md w-full">
        <div className="card-header text-center">
          <h1 className="text-2xl font-bold text-primary mb-2">Sector Wars 2102</h1>
          <p className="text-muted">Admin Portal</p>
        </div>
        
        <div className="card-body">
          <LoginForm onLoginSuccess={handleLoginSuccess} />
        </div>
        
        <div className="card-footer text-center">
          <p className="text-sm text-muted">Sector Wars 2102 - Admin UI v0.1.0</p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;