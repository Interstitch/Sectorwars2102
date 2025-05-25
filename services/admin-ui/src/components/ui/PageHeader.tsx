import React from 'react';
import UserProfile from '../auth/UserProfile';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

const PageHeader: React.FC<PageHeaderProps> = ({ title, subtitle, actions }) => {
  
  return (
    <header className="page-header">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="page-title">{title}</h1>
          {subtitle && <p className="page-subtitle">{subtitle}</p>}
        </div>
        
        <div className="flex items-center gap-4">
          {actions && <div>{actions}</div>}
          <UserProfile />
        </div>
      </div>
    </header>
  );
};

export default PageHeader;