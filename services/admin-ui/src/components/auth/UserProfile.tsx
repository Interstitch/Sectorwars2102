import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import LogoutButton from './LogoutButton';
import { MFASetup } from './MFASetup';

const UserProfile: React.FC = () => {
  const { user } = useAuth();
  const [showMFASetup, setShowMFASetup] = useState(false);
  
  if (!user) {
    return null;
  }
  
  const handleMFASetupComplete = () => {
    setShowMFASetup(false);
    // Optionally refresh user data to update MFA status
    window.location.reload();
  };
  
  const handleMFACancel = () => {
    setShowMFASetup(false);
  };
  
  if (showMFASetup) {
    return (
      <div className="user-profile-mfa-setup">
        <MFASetup 
          onSetupComplete={handleMFASetupComplete}
          onCancel={handleMFACancel}
        />
      </div>
    );
  }
  
  return (
    <div className="user-profile">
      <div className="user-info">
        <span className="username">{user.username}</span>
        <span className="user-role">Administrator</span>
        {user.mfaEnabled ? (
          <span className="mfa-status mfa-enabled">
            <i className="fas fa-shield-alt"></i> MFA Enabled
          </span>
        ) : (
          <button 
            className="btn btn-sm btn-warning"
            onClick={() => setShowMFASetup(true)}
          >
            <i className="fas fa-exclamation-triangle"></i> Enable MFA
          </button>
        )}
      </div>
      <LogoutButton className="user-logout" />
    </div>
  );
};

export default UserProfile;