import React from 'react';
import UserProfile from '../auth/UserProfile';
import './ui.css';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

const PageHeader: React.FC<PageHeaderProps> = ({ title, subtitle, actions }) => {
  
  return (
    <header className="page-header">
      <div className="header-content">
        <div className="header-titles">
          <h1 className="page-title">{title}</h1>
          {subtitle && <p className="page-subtitle">{subtitle}</p>}
        </div>
        
        <div className="header-actions">
          {actions}
        </div>
        
        <div className="header-profile">
          <UserProfile />
        </div>
      </div>
    </header>
  );
};

export default PageHeader;