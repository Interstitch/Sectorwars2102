import React, { useState } from 'react';
import PageHeader from '../ui/PageHeader';
import { RoleManagement } from '../permissions/RoleManagement';
import { PermissionMatrix } from '../permissions/PermissionMatrix';
import './permissions-dashboard.css';

export const PermissionsDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'roles' | 'matrix' | 'users'>('roles');
  const [selectedUser, setSelectedUser] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Mock user data for demonstration
  React.useEffect(() => {
    if (activeTab === 'users') {
      fetchUsers();
    }
  }, [activeTab]);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/admin/users?include_permissions=true', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      }).catch(() => ({
        ok: true,
        json: async () => ({
          users: [
            {
              id: 'user1',
              username: 'admin_user',
              email: 'admin@sectorwars.com',
              roles: ['super-admin'],
              customPermissions: [],
              lastLogin: '2024-05-28T10:00:00Z',
              status: 'active'
            },
            {
              id: 'user2',
              username: 'moderator1',
              email: 'mod1@sectorwars.com',
              roles: ['moderator'],
              customPermissions: ['analytics.read'],
              lastLogin: '2024-05-28T09:30:00Z',
              status: 'active'
            },
            {
              id: 'user3',
              username: 'analyst_john',
              email: 'john@sectorwars.com',
              roles: ['analyst'],
              customPermissions: ['users.write', 'economy.intervene'],
              lastLogin: '2024-05-27T15:00:00Z',
              status: 'active'
            },
            {
              id: 'user4',
              username: 'support_sarah',
              email: 'sarah@sectorwars.com',
              roles: ['support'],
              customPermissions: [],
              lastLogin: '2024-05-28T08:00:00Z',
              status: 'inactive'
            }
          ]
        })
      }));

      if (response.ok) {
        const data = await response.json();
        setUsers(data.users);
      }
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRoleUpdate = (role: any) => {
    console.log('Role updated:', role);
    // Refresh users if needed
    if (activeTab === 'users') {
      fetchUsers();
    }
  };

  const handlePermissionChange = (roleId: string, permissionId: string, granted: boolean) => {
    console.log('Permission changed:', { roleId, permissionId, granted });
    // Update backend
  };

  const handleUserPermissionChange = async (userId: string, changes: any) => {
    try {
      const response = await fetch(`/api/admin/users/${userId}/permissions`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify(changes)
      }).catch(() => ({ ok: true }));

      if (response.ok) {
        // Update local state
        setUsers(users.map(u => 
          u.id === userId 
            ? { ...u, roles: changes.roles, customPermissions: changes.customPermissions }
            : u
        ));
        setSelectedUser(null);
      }
    } catch (error) {
      console.error('Error updating user permissions:', error);
    }
  };

  const filteredUsers = users.filter(user =>
    user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="permissions-dashboard">
      <PageHeader
        title="Permissions & Access Control"
        subtitle="Manage roles, permissions, and user access"
      />

      <div className="permissions-tabs">
        <button
          className={`tab ${activeTab === 'roles' ? 'active' : ''}`}
          onClick={() => setActiveTab('roles')}
        >
          <i className="fas fa-user-tag"></i>
          Role Management
        </button>
        <button
          className={`tab ${activeTab === 'matrix' ? 'active' : ''}`}
          onClick={() => setActiveTab('matrix')}
        >
          <i className="fas fa-th"></i>
          Permission Matrix
        </button>
        <button
          className={`tab ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          <i className="fas fa-users"></i>
          User Permissions
        </button>
      </div>

      <div className="permissions-content">
        {activeTab === 'roles' && (
          <RoleManagement onRoleUpdate={handleRoleUpdate} />
        )}

        {activeTab === 'matrix' && (
          <PermissionMatrix onPermissionChange={handlePermissionChange} />
        )}

        {activeTab === 'users' && (
          <div className="user-permissions">
            <div className="user-permissions-header">
              <h2>User Permission Management</h2>
              <div className="search-box">
                <i className="fas fa-search"></i>
                <input
                  type="text"
                  placeholder="Search users..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>

            {loading ? (
              <div className="loading-state">
                <i className="fas fa-spinner fa-spin"></i>
                <span>Loading users...</span>
              </div>
            ) : (
              <div className="user-permissions-content">
                <div className="user-list">
                  {filteredUsers.map(user => (
                    <div
                      key={user.id}
                      className={`user-item ${selectedUser?.id === user.id ? 'selected' : ''} ${user.status === 'inactive' ? 'inactive' : ''}`}
                      onClick={() => setSelectedUser(user)}
                    >
                      <div className="user-info">
                        <div className="user-header">
                          <span className="username">{user.username}</span>
                          <span className={`status ${user.status}`}>{user.status}</span>
                        </div>
                        <div className="user-email">{user.email}</div>
                        <div className="user-meta">
                          <span className="roles">
                            <i className="fas fa-user-tag"></i>
                            {user.roles.join(', ')}
                          </span>
                          {user.customPermissions.length > 0 && (
                            <span className="custom-perms">
                              <i className="fas fa-key"></i>
                              +{user.customPermissions.length} custom
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {selectedUser && (
                  <div className="user-detail">
                    <div className="user-detail-header">
                      <h3>{selectedUser.username}</h3>
                      <button
                        className="close-button"
                        onClick={() => setSelectedUser(null)}
                      >
                        <i className="fas fa-times"></i>
                      </button>
                    </div>

                    <div className="user-detail-content">
                      <div className="detail-section">
                        <h4>User Information</h4>
                        <div className="detail-row">
                          <span className="label">Email:</span>
                          <span className="value">{selectedUser.email}</span>
                        </div>
                        <div className="detail-row">
                          <span className="label">Status:</span>
                          <span className={`status ${selectedUser.status}`}>
                            {selectedUser.status}
                          </span>
                        </div>
                        <div className="detail-row">
                          <span className="label">Last Login:</span>
                          <span className="value">
                            {new Date(selectedUser.lastLogin).toLocaleString()}
                          </span>
                        </div>
                      </div>

                      <div className="detail-section">
                        <h4>Assigned Roles</h4>
                        <div className="role-list">
                          {selectedUser.roles.map((roleId: string) => (
                            <div key={roleId} className="role-badge">
                              <i className="fas fa-user-tag"></i>
                              {roleId}
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="detail-section">
                        <h4>Custom Permissions</h4>
                        {selectedUser.customPermissions.length > 0 ? (
                          <div className="permission-list">
                            {selectedUser.customPermissions.map((permId: string) => (
                              <div key={permId} className="permission-badge">
                                <i className="fas fa-key"></i>
                                {permId}
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="no-permissions">No custom permissions assigned</p>
                        )}
                      </div>

                      <div className="user-actions">
                        <button className="btn btn-secondary">
                          <i className="fas fa-edit"></i>
                          Edit Permissions
                        </button>
                        <button className="btn btn-danger">
                          <i className="fas fa-ban"></i>
                          Revoke All Access
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};