import React from 'react';
import { NavLink } from 'react-router-dom';
import LogoutButton from '../auth/LogoutButton';
import './layouts.css';

const Sidebar: React.FC = () => {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-title">Sector Wars</h1>
        <p className="sidebar-subtitle">Admin Panel</p>
      </div>
      
      <nav className="sidebar-nav">
        <ul className="nav-list">
          <li className="nav-item">
            <NavLink 
              to="/dashboard" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <span className="nav-icon">📊</span>
              <span className="nav-text">Dashboard</span>
            </NavLink>
          </li>
          
          <li className="nav-item">
            <NavLink 
              to="/users" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <span className="nav-icon">👥</span>
              <span className="nav-text">User Management</span>
            </NavLink>
          </li>
          
          <li className="nav-item">
            <NavLink 
              to="/universe" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <span className="nav-icon">🌌</span>
              <span className="nav-text">Universe</span>
            </NavLink>
          </li>
          
          <li className="nav-item">
            <NavLink 
              to="/sectors" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <span className="nav-icon">🔳</span>
              <span className="nav-text">Sectors</span>
            </NavLink>
          </li>
          
          <li className="nav-item">
            <NavLink 
              to="/trading" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <span className="nav-icon">💱</span>
              <span className="nav-text">Trading</span>
            </NavLink>
          </li>
          
          <li className="nav-item">
            <NavLink 
              to="/settings" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <span className="nav-icon">⚙️</span>
              <span className="nav-text">Settings</span>
            </NavLink>
          </li>
        </ul>
      </nav>
      
      <div className="sidebar-footer">
        <LogoutButton />
      </div>
    </aside>
  );
};

export default Sidebar;