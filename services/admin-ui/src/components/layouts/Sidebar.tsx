import React from 'react';
import { NavLink } from 'react-router-dom';
import LogoutButton from '../auth/LogoutButton';
import GameServerStatus from '../ui/GameServerStatus';
import AIHealthStatus from '../ui/AIHealthStatus';
import DatabaseHealthStatus from '../ui/DatabaseHealthStatus';

const Sidebar: React.FC = () => {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-title">Sector Wars</h1>
        <p className="sidebar-subtitle">Admin Panel</p>
      </div>
      
      <nav className="sidebar-nav">
        <NavLink 
          to="/dashboard" 
          className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}
        >
          <span className="sidebar-nav-icon">📊</span>
          <span>Dashboard</span>
        </NavLink>
        
        <NavLink 
          to="/universe" 
          className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}
        >
          <span className="sidebar-nav-icon">🌌</span>
          <span>Universe</span>
        </NavLink>
        
        <NavLink 
          to="/users" 
          className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}
        >
          <span className="sidebar-nav-icon">👥</span>
          <span>User Management</span>
        </NavLink>
        
        <NavLink 
          to="/players" 
          className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}
        >
          <span className="sidebar-nav-icon">👤</span>
          <span>Players</span>
        </NavLink>
        
        <NavLink 
          to="/teams" 
          className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}
        >
          <span className="sidebar-nav-icon">🤝</span>
          <span>Teams</span>
        </NavLink>
        
        <NavLink 
          to="/fleets" 
          className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}
        >
          <span className="sidebar-nav-icon">🚀</span>
          <span>Fleets</span>
        </NavLink>
        
        <NavLink 
          to="/colonies" 
          className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}
        >
          <span className="sidebar-nav-icon">🏙️</span>
          <span>Colonization</span>
        </NavLink>
        
        <NavLink 
          to="/combat" 
          className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}
        >
          <span className="sidebar-nav-icon">⚔️</span>
          <span>Combat</span>
        </NavLink>
        
        <NavLink 
          to="/events" 
          className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}
        >
          <span className="sidebar-nav-icon">🎯</span>
          <span>Events</span>
        </NavLink>
        
        <NavLink 
          to="/analytics" 
          className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}
        >
          <span className="sidebar-nav-icon">📈</span>
          <span>Analytics</span>
        </NavLink>
        
        <NavLink 
          to="/ai-trading" 
          className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}
        >
          <span className="sidebar-nav-icon">🤖</span>
          <span>AI Trading</span>
        </NavLink>
        
        <NavLink 
          to="/security" 
          className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}
        >
          <span className="sidebar-nav-icon">🔒</span>
          <span>Security</span>
        </NavLink>
        
        <NavLink 
          to="/permissions" 
          className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}
        >
          <span className="sidebar-nav-icon">🔑</span>
          <span>Permissions</span>
        </NavLink>
      </nav>
      
      <div className="sidebar-footer">
        <div style={{ padding: 'var(--space-6)', display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
          <DatabaseHealthStatus />
          <AIHealthStatus />
          <GameServerStatus />
          <LogoutButton />
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;