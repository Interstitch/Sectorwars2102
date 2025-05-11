import React, { useState, useEffect } from 'react';
import { Outlet, useLocation, Navigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import Sidebar from './Sidebar';
import './layouts.css';

const AppLayout: React.FC = () => {
  const { isLoading, isAuthenticated } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(true);
  const [isMobile, setIsMobile] = useState<boolean>(false);
  const [loadingTimeout, setLoadingTimeout] = useState<boolean>(false);
  const location = useLocation();

  // Check if we're on the login page
  const isLoginPage = location.pathname === '/login';

  // Handle responsive sidebar
  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth < 992);
      setSidebarOpen(window.innerWidth >= 992);
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);

    return () => {
      window.removeEventListener('resize', checkScreenSize);
    };
  }, []);

  // Close sidebar when changing routes on mobile
  useEffect(() => {
    if (isMobile) {
      setSidebarOpen(false);
    }
  }, [location.pathname, isMobile]);
  
  // Add timeout for loading state
  useEffect(() => {
    let timer: number;
    if (isLoading && !isLoginPage) {
      timer = window.setTimeout(() => {
        setLoadingTimeout(true);
      }, 3000); // 3 second timeout
    }
    
    return () => {
      window.clearTimeout(timer);
    };
  }, [isLoading, isLoginPage]);

  // Special case for login page - never show loading spinner on login page
  if (isLoginPage) {
    return (
      <div className="app-container">
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    );
  }
  
  // Redirect to login if not authenticated and not already loading
  if (!isLoading && !isAuthenticated && !isLoginPage) {
    return <Navigate to="/login" replace />;
  }

  // Show loading state for other pages
  if (isLoading) {
    if (loadingTimeout) {
      return (
        <div className="app-container">
          <main className="main-content">
            <div className="loading-error">
              <h2>Authentication Timeout</h2>
              <p>We couldn't authenticate you automatically. Please log in again.</p>
              <Navigate to="/login" replace />
            </div>
          </main>
        </div>
      );
    }
    
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading authentication...</p>
      </div>
    );
  }

  return (
    <div className="app-container">
      {/* Don't show sidebar on login page or if not authenticated */}
      {!isLoginPage && isAuthenticated && (
        <>
          <div className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
            <Sidebar />
          </div>

          {isMobile && (
            <button
              className={`sidebar-toggle ${sidebarOpen ? 'open' : ''}`}
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              {sidebarOpen ? '×' : '☰'}
            </button>
          )}
        </>
      )}

      <main className={`main-content ${!isLoginPage && isAuthenticated && sidebarOpen ? 'sidebar-open' : ''}`}>
        <Outlet />
      </main>
    </div>
  );
};

export default AppLayout;