import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import LogoutButton from './LogoutButton';
import './auth.css';

const UserProfile: React.FC = () => {
  const { user } = useAuth();
  
  if (!user) {
    return null;
  }
  
  return (
    <div className="user-profile">
      <div className="user-info">
        <span className="username">{user.username}</span>
        <span className="user-role">Player</span>
      </div>
      <LogoutButton className="user-logout" />
    </div>
  );
};

export default UserProfile;