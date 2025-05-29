import React, { useState, useEffect } from 'react';
import './role-management.css';

interface Permission {
  id: string;
  name: string;
  resource: string;
  action: string;
  description: string;
}

interface Role {
  id: string;
  name: string;
  description: string;
  permissions: string[];
  userCount: number;
  isSystem: boolean;
  createdAt: string;
  updatedAt: string;
}

interface RoleManagementProps {
  onRoleUpdate?: (role: Role) => void;
}

export const RoleManagement: React.FC<RoleManagementProps> = ({ onRoleUpdate }) => {
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchRolesAndPermissions();
  }, []);

  const fetchRolesAndPermissions = async () => {
    setLoading(true);
    try {
      // Fetch roles
      const rolesResponse = await fetch('/api/admin/roles', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      }).catch(() => {
        // Mock data
        return {
          ok: true,
          json: async () => ({
            roles: [
              {
                id: 'super-admin',
                name: 'Super Administrator',
                description: 'Full system access with all permissions',
                permissions: ['*'],
                userCount: 2,
                isSystem: true,
                createdAt: '2024-01-01T00:00:00Z',
                updatedAt: '2024-01-01T00:00:00Z'
              },
              {
                id: 'admin',
                name: 'Administrator',
                description: 'General administrative access',
                permissions: ['users.read', 'users.write', 'ships.read', 'ships.write', 'economy.read', 'economy.intervene'],
                userCount: 5,
                isSystem: true,
                createdAt: '2024-01-01T00:00:00Z',
                updatedAt: '2024-01-01T00:00:00Z'
              },
              {
                id: 'moderator',
                name: 'Moderator',
                description: 'Can moderate player actions and content',
                permissions: ['users.read', 'messages.read', 'messages.moderate', 'combat.view'],
                userCount: 12,
                isSystem: false,
                createdAt: '2024-02-01T00:00:00Z',
                updatedAt: '2024-02-15T00:00:00Z'
              },
              {
                id: 'analyst',
                name: 'Data Analyst',
                description: 'Read-only access to analytics and reports',
                permissions: ['analytics.read', 'economy.read', 'users.read', 'combat.view'],
                userCount: 8,
                isSystem: false,
                createdAt: '2024-03-01T00:00:00Z',
                updatedAt: '2024-03-01T00:00:00Z'
              }
            ]
          })
        };
      });

      // Fetch permissions
      const permissionsResponse = await fetch('/api/admin/permissions', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      }).catch(() => {
        // Mock data
        return {
          ok: true,
          json: async () => ({
            permissions: [
              // User permissions
              { id: 'users.read', name: 'View Users', resource: 'users', action: 'read', description: 'View user profiles and lists' },
              { id: 'users.write', name: 'Modify Users', resource: 'users', action: 'write', description: 'Create, update, and delete users' },
              { id: 'users.ban', name: 'Ban Users', resource: 'users', action: 'ban', description: 'Ban and unban user accounts' },
              
              // Ship permissions
              { id: 'ships.read', name: 'View Ships', resource: 'ships', action: 'read', description: 'View ship information' },
              { id: 'ships.write', name: 'Modify Ships', resource: 'ships', action: 'write', description: 'Create, update, and delete ships' },
              { id: 'ships.emergency', name: 'Emergency Ship Actions', resource: 'ships', action: 'emergency', description: 'Perform emergency repairs and teleports' },
              
              // Economy permissions
              { id: 'economy.read', name: 'View Economy', resource: 'economy', action: 'read', description: 'View economic data and reports' },
              { id: 'economy.intervene', name: 'Market Intervention', resource: 'economy', action: 'intervene', description: 'Perform market interventions' },
              
              // Combat permissions
              { id: 'combat.view', name: 'View Combat', resource: 'combat', action: 'view', description: 'View combat logs and statistics' },
              { id: 'combat.intervene', name: 'Combat Intervention', resource: 'combat', action: 'intervene', description: 'Intervene in active combat' },
              
              // Messages permissions
              { id: 'messages.read', name: 'Read Messages', resource: 'messages', action: 'read', description: 'Read all player messages' },
              { id: 'messages.moderate', name: 'Moderate Messages', resource: 'messages', action: 'moderate', description: 'Delete and flag messages' },
              
              // Analytics permissions
              { id: 'analytics.read', name: 'View Analytics', resource: 'analytics', action: 'read', description: 'View analytics and reports' },
              { id: 'analytics.export', name: 'Export Analytics', resource: 'analytics', action: 'export', description: 'Export analytics data' },
              
              // Security permissions
              { id: 'security.manage', name: 'Manage Security', resource: 'security', action: 'manage', description: 'Manage security settings and policies' },
              { id: 'security.audit', name: 'View Audit Logs', resource: 'security', action: 'audit', description: 'View and export audit logs' },
              
              // System permissions
              { id: 'system.config', name: 'System Configuration', resource: 'system', action: 'config', description: 'Modify system configuration' },
              { id: 'roles.manage', name: 'Manage Roles', resource: 'roles', action: 'manage', description: 'Create and modify roles' }
            ]
          })
        };
      });

      if (rolesResponse.ok && permissionsResponse.ok) {
        const rolesData = await rolesResponse.json();
        const permissionsData = await permissionsResponse.json();
        setRoles(rolesData.roles);
        setPermissions(permissionsData.permissions);
      }
    } catch (error) {
      console.error('Error fetching roles and permissions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRole = () => {
    setEditingRole({
      id: '',
      name: '',
      description: '',
      permissions: [],
      userCount: 0,
      isSystem: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    });
    setShowCreateModal(true);
  };

  const handleSaveRole = async () => {
    if (!editingRole) return;

    try {
      const isNew = !editingRole.id;
      const url = isNew ? '/api/admin/roles' : `/api/admin/roles/${editingRole.id}`;
      const method = isNew ? 'POST' : 'PUT';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify(editingRole)
      }).catch(() => {
        // Mock success
        return { ok: true, json: async () => ({ ...editingRole, id: editingRole.id || `role-${Date.now()}` }) };
      });

      if (response.ok) {
        const savedRole = await response.json();
        if (isNew) {
          setRoles([...roles, savedRole]);
        } else {
          setRoles(roles.map(r => r.id === savedRole.id ? savedRole : r));
        }
        setShowCreateModal(false);
        setEditingRole(null);
        onRoleUpdate?.(savedRole);
      }
    } catch (error) {
      console.error('Error saving role:', error);
    }
  };

  const handleDeleteRole = async (roleId: string) => {
    if (!confirm('Are you sure you want to delete this role? Users with this role will lose their permissions.')) {
      return;
    }

    try {
      const response = await fetch(`/api/admin/roles/${roleId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      }).catch(() => {
        // Mock success
        return { ok: true };
      });

      if (response.ok) {
        setRoles(roles.filter(r => r.id !== roleId));
        if (selectedRole?.id === roleId) {
          setSelectedRole(null);
        }
      }
    } catch (error) {
      console.error('Error deleting role:', error);
    }
  };

  const togglePermission = (permissionId: string) => {
    if (!editingRole) return;

    const newPermissions = editingRole.permissions.includes(permissionId)
      ? editingRole.permissions.filter(p => p !== permissionId)
      : [...editingRole.permissions, permissionId];

    setEditingRole({
      ...editingRole,
      permissions: newPermissions
    });
  };

  const groupPermissionsByResource = () => {
    const grouped: Record<string, Permission[]> = {};
    permissions.forEach(permission => {
      if (!grouped[permission.resource]) {
        grouped[permission.resource] = [];
      }
      grouped[permission.resource].push(permission);
    });
    return grouped;
  };

  const filteredRoles = roles.filter(role => 
    role.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    role.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="role-management-loading">
        <i className="fas fa-spinner fa-spin"></i>
        <span>Loading roles and permissions...</span>
      </div>
    );
  }

  return (
    <div className="role-management">
      <div className="role-header">
        <h2>Role Management</h2>
        <div className="role-actions">
          <div className="search-box">
            <i className="fas fa-search"></i>
            <input
              type="text"
              placeholder="Search roles..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <button className="btn btn-primary" onClick={handleCreateRole}>
            <i className="fas fa-plus"></i>
            Create Role
          </button>
        </div>
      </div>

      <div className="role-content">
        <div className="role-list">
          <h3>Roles ({filteredRoles.length})</h3>
          {filteredRoles.map(role => (
            <div
              key={role.id}
              className={`role-item ${selectedRole?.id === role.id ? 'selected' : ''} ${role.isSystem ? 'system' : ''}`}
              onClick={() => setSelectedRole(role)}
            >
              <div className="role-info">
                <div className="role-name">
                  {role.name}
                  {role.isSystem && <span className="system-badge">System</span>}
                </div>
                <div className="role-description">{role.description}</div>
                <div className="role-meta">
                  <span className="user-count">
                    <i className="fas fa-users"></i>
                    {role.userCount} users
                  </span>
                  <span className="permission-count">
                    <i className="fas fa-key"></i>
                    {role.permissions.length === 1 && role.permissions[0] === '*' 
                      ? 'All permissions' 
                      : `${role.permissions.length} permissions`}
                  </span>
                </div>
              </div>
              <div className="role-actions">
                <button
                  className="btn-icon"
                  onClick={(e) => {
                    e.stopPropagation();
                    setEditingRole(role);
                    setShowCreateModal(true);
                  }}
                  disabled={role.isSystem}
                  title={role.isSystem ? 'System roles cannot be edited' : 'Edit role'}
                >
                  <i className="fas fa-edit"></i>
                </button>
                <button
                  className="btn-icon delete"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteRole(role.id);
                  }}
                  disabled={role.isSystem || role.userCount > 0}
                  title={
                    role.isSystem 
                      ? 'System roles cannot be deleted' 
                      : role.userCount > 0 
                        ? 'Cannot delete role with assigned users'
                        : 'Delete role'
                  }
                >
                  <i className="fas fa-trash"></i>
                </button>
              </div>
            </div>
          ))}
        </div>

        {selectedRole && (
          <div className="role-details">
            <h3>Role Details: {selectedRole.name}</h3>
            <div className="role-permissions">
              <h4>Permissions</h4>
              {selectedRole.permissions.length === 1 && selectedRole.permissions[0] === '*' ? (
                <div className="all-permissions">
                  <i className="fas fa-infinity"></i>
                  <span>This role has all permissions</span>
                </div>
              ) : (
                <div className="permission-list">
                  {selectedRole.permissions.length === 0 ? (
                    <div className="no-permissions">No permissions assigned</div>
                  ) : (
                    selectedRole.permissions.map(permId => {
                      const permission = permissions.find(p => p.id === permId);
                      return permission ? (
                        <div key={permId} className="permission-item">
                          <i className="fas fa-check"></i>
                          <div className="permission-details">
                            <span className="permission-name">{permission.name}</span>
                            <span className="permission-description">{permission.description}</span>
                          </div>
                        </div>
                      ) : null;
                    })
                  )}
                </div>
              )}
            </div>

            <div className="role-metadata">
              <div className="metadata-item">
                <span className="label">Created:</span>
                <span className="value">{new Date(selectedRole.createdAt).toLocaleString()}</span>
              </div>
              <div className="metadata-item">
                <span className="label">Last Updated:</span>
                <span className="value">{new Date(selectedRole.updatedAt).toLocaleString()}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {showCreateModal && editingRole && (
        <div className="role-modal" onClick={() => setShowCreateModal(false)}>
          <div className="role-modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editingRole.id ? 'Edit Role' : 'Create New Role'}</h3>
              <button className="close-button" onClick={() => setShowCreateModal(false)}>
                <i className="fas fa-times"></i>
              </button>
            </div>

            <div className="modal-body">
              <div className="form-group">
                <label>Role Name</label>
                <input
                  type="text"
                  value={editingRole.name}
                  onChange={(e) => setEditingRole({ ...editingRole, name: e.target.value })}
                  placeholder="e.g., Content Moderator"
                  disabled={editingRole.isSystem}
                />
              </div>

              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={editingRole.description}
                  onChange={(e) => setEditingRole({ ...editingRole, description: e.target.value })}
                  placeholder="Describe the purpose of this role"
                  rows={3}
                  disabled={editingRole.isSystem}
                />
              </div>

              <div className="form-group">
                <label>Permissions</label>
                <div className="permission-groups">
                  {Object.entries(groupPermissionsByResource()).map(([resource, perms]) => (
                    <div key={resource} className="permission-group">
                      <h4>{resource.charAt(0).toUpperCase() + resource.slice(1)}</h4>
                      {perms.map(permission => (
                        <label key={permission.id} className="permission-checkbox">
                          <input
                            type="checkbox"
                            checked={editingRole.permissions.includes(permission.id)}
                            onChange={() => togglePermission(permission.id)}
                            disabled={editingRole.isSystem}
                          />
                          <div className="permission-label">
                            <span className="name">{permission.name}</span>
                            <span className="description">{permission.description}</span>
                          </div>
                        </label>
                      ))}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowCreateModal(false)}>
                Cancel
              </button>
              <button 
                className="btn btn-primary" 
                onClick={handleSaveRole}
                disabled={!editingRole.name || editingRole.isSystem}
              >
                {editingRole.id ? 'Save Changes' : 'Create Role'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};