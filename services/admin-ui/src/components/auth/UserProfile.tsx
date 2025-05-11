import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import LogoutButton from './LogoutButton';

const UserProfile: React.FC = () => {
  const { user } = useAuth();
  
  if (!user) {
    return null;
  }
  
  return (
    <div className="user-profile">
      <div className="user-info">
        <span className="username">{user.username}</span>
        <span className="user-role">Administrator</span>
      </div>
      <LogoutButton className="user-logout" />
    </div>
  );
};

export default UserProfile;