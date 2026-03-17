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
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [editingUser, setEditingUser] = useState<any>(null);
  const [editRoles, setEditRoles] = useState<string[]>([]);
  const [editCustomPerms, setEditCustomPerms] = useState<string[]>([]);

  React.useEffect(() => {
    if (activeTab === 'users') {
      fetchUsers();
    }
  }, [activeTab]);

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/v1/admin/users?include_permissions=true', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setUsers(data.users || []);
      } else {
        setUsers([]);
        setError('Failed to load users. Server returned an error.');
      }
    } catch (error) {
      console.error('Error fetching users:', error);
      setUsers([]);
      setError('Failed to load users. Please check your connection and try again.');
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

  const handlePermissionChange = async (roleId: string, permissionId: string, granted: boolean) => {
    try {
      const response = await fetch(`/api/v1/admin/roles/${roleId}/permissions`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        },
        body: JSON.stringify({ permission_id: permissionId, granted })
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({ detail: 'Failed to update permission' }));
        setError(errData.detail || 'Failed to update permission');
      }
    } catch (err) {
      console.error('Error updating permission:', err);
      setError('Network error while updating permission');
    }
  };

  const handleEditPermissions = (user: any) => {
    setEditingUser(user);
    setEditRoles([...(user.roles || [])]);
    setEditCustomPerms([...(user.customPermissions || [])]);
  };

  const handleSaveEditedPermissions = async () => {
    if (!editingUser) return;
    try {
      await handleUserPermissionChange(editingUser.id, {
        roles: editRoles,
        customPermissions: editCustomPerms
      });
      setEditingUser(null);
      alert('Permissions updated successfully');
    } catch (err) {
      console.error('Error saving permissions:', err);
      alert('Failed to save permissions');
    }
  };

  const handleRevokeAllAccess = async (user: any) => {
    if (!confirm(`Are you sure you want to revoke ALL access for user "${user.username}"? This will remove all roles and custom permissions.`)) {
      return;
    }
    if (!confirm(`FINAL CONFIRMATION: This will completely remove "${user.username}"'s access. Proceed?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/admin/users/${user.id}/permissions`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        },
        body: JSON.stringify({ roles: [], customPermissions: [] })
      });

      if (response.ok) {
        setUsers(users.map(u =>
          u.id === user.id ? { ...u, roles: [], customPermissions: [] } : u
        ));
        setSelectedUser(null);
        alert(`All access revoked for ${user.username}`);
      } else {
        const errData = await response.json().catch(() => ({ detail: 'Failed to revoke access' }));
        alert(errData.detail || 'Failed to revoke access');
      }
    } catch (err) {
      console.error('Error revoking access:', err);
      alert('Network error while revoking access');
    }
  };

  const handleUserPermissionChange = async (userId: string, changes: any) => {
    try {
      const response = await fetch(`/api/v1/admin/users/${userId}/permissions`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        },
        body: JSON.stringify(changes)
      });

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

            {error && (
              <div className="error-state" style={{ padding: '16px', margin: '16px 0', backgroundColor: 'rgba(231, 76, 60, 0.1)', border: '1px solid rgba(231, 76, 60, 0.3)', borderRadius: '8px', color: '#e74c3c' }}>
                <i className="fas fa-exclamation-circle" style={{ marginRight: '8px' }}></i>
                {error}
              </div>
            )}

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
                        <button
                          className="btn btn-secondary"
                          onClick={() => handleEditPermissions(selectedUser)}
                        >
                          <i className="fas fa-edit"></i>
                          Edit Permissions
                        </button>
                        <button
                          className="btn btn-danger"
                          onClick={() => handleRevokeAllAccess(selectedUser)}
                        >
                          <i className="fas fa-ban"></i>
                          Revoke All Access
                        </button>
                      </div>

                      {/* Inline Edit Mode */}
                      {editingUser && editingUser.id === selectedUser.id && (
                        <div style={{ marginTop: '16px', padding: '16px', background: 'rgba(59, 130, 246, 0.05)', borderRadius: '8px', border: '1px solid rgba(59, 130, 246, 0.2)' }}>
                          <h4 style={{ margin: '0 0 12px 0' }}>Edit Permissions</h4>

                          <div style={{ marginBottom: '12px' }}>
                            <label style={{ display: 'block', marginBottom: '6px', fontWeight: 600, fontSize: '0.9rem' }}>Roles (comma-separated)</label>
                            <input
                              type="text"
                              value={editRoles.join(', ')}
                              onChange={(e) => setEditRoles(e.target.value.split(',').map(r => r.trim()).filter(Boolean))}
                              style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #374151', background: '#111827', color: '#e5e7eb' }}
                            />
                          </div>

                          <div style={{ marginBottom: '12px' }}>
                            <label style={{ display: 'block', marginBottom: '6px', fontWeight: 600, fontSize: '0.9rem' }}>Custom Permissions (comma-separated)</label>
                            <input
                              type="text"
                              value={editCustomPerms.join(', ')}
                              onChange={(e) => setEditCustomPerms(e.target.value.split(',').map(p => p.trim()).filter(Boolean))}
                              style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #374151', background: '#111827', color: '#e5e7eb' }}
                            />
                          </div>

                          <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                            <button
                              className="btn btn-secondary"
                              onClick={() => setEditingUser(null)}
                            >
                              Cancel
                            </button>
                            <button
                              className="btn btn-primary"
                              onClick={handleSaveEditedPermissions}
                              style={{ background: '#3b82f6', color: 'white', border: 'none', padding: '8px 16px', borderRadius: '6px', cursor: 'pointer' }}
                            >
                              Save Changes
                            </button>
                          </div>
                        </div>
                      )}
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