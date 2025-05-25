import React from 'react';
import { NavLink } from 'react-router-dom';
import LogoutButton from '../auth/LogoutButton';
import GameServerStatus from '../ui/GameServerStatus';
import AIHealthStatus from '../ui/AIHealthStatus';
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
              to="/universe" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <span className="nav-icon">🌌</span>
              <span className="nav-text">Universe</span>
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
              to="/players" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <span className="nav-icon">👤</span>
              <span className="nav-text">Players</span>
            </NavLink>
          </li>
          
          <li className="nav-item">
            <NavLink 
              to="/teams" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <span className="nav-icon">🤝</span>
              <span className="nav-text">Teams</span>
            </NavLink>
          </li>
          
          <li className="nav-item">
            <NavLink 
              to="/fleets" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <span className="nav-icon">🚀</span>
              <span className="nav-text">Fleets</span>
            </NavLink>
          </li>
          
          <li className="nav-item">
            <NavLink 
              to="/colonies" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <span className="nav-icon">🪐</span>
              <span className="nav-text">Colonies</span>
            </NavLink>
          </li>
          
          <li className="nav-item">
            <NavLink 
              to="/combat" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <span className="nav-icon">⚔️</span>
              <span className="nav-text">Combat</span>
            </NavLink>
          </li>
          
          <li className="nav-item">
            <NavLink 
              to="/events" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <span className="nav-icon">🎯</span>
              <span className="nav-text">Events</span>
            </NavLink>
          </li>
          
          <li className="nav-item">
            <NavLink 
              to="/analytics" 
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              <span className="nav-icon">📈</span>
              <span className="nav-text">Analytics</span>
            </NavLink>
          </li>
        </ul>
      </nav>
      
      <div className="sidebar-footer">
        <AIHealthStatus />
        <GameServerStatus />
        <LogoutButton />
      </div>
    </aside>
  );
};

export default Sidebar;