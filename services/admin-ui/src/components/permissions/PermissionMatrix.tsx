import React, { useState, useEffect } from 'react';
import './permission-matrix.css';

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
  permissions: string[];
  userCount: number;
  isSystem: boolean;
}

interface PermissionMatrixProps {
  onPermissionChange?: (roleId: string, permissionId: string, granted: boolean) => void;
}

export const PermissionMatrix: React.FC<PermissionMatrixProps> = ({ onPermissionChange }) => {
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [loading, setLoading] = useState(true);
  const [editMode, setEditMode] = useState(false);
  const [changes, setChanges] = useState<Record<string, Record<string, boolean>>>({});
  const [expandedResources, setExpandedResources] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch roles and permissions
      const [rolesResponse, permissionsResponse] = await Promise.all([
        fetch('/api/admin/roles', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
        }).catch(() => ({
          ok: true,
          json: async () => ({
            roles: [
              {
                id: 'super-admin',
                name: 'Super Admin',
                permissions: ['*'],
                userCount: 2,
                isSystem: true
              },
              {
                id: 'admin',
                name: 'Administrator',
                permissions: ['users.read', 'users.write', 'ships.read', 'ships.write', 'economy.read', 'economy.intervene', 'security.audit', 'analytics.read'],
                userCount: 5,
                isSystem: true
              },
              {
                id: 'moderator',
                name: 'Moderator',
                permissions: ['users.read', 'messages.read', 'messages.moderate', 'combat.view'],
                userCount: 12,
                isSystem: false
              },
              {
                id: 'analyst',
                name: 'Data Analyst',
                permissions: ['analytics.read', 'analytics.export', 'economy.read', 'users.read'],
                userCount: 8,
                isSystem: false
              },
              {
                id: 'support',
                name: 'Support Staff',
                permissions: ['users.read', 'messages.read', 'ships.read'],
                userCount: 15,
                isSystem: false
              }
            ]
          })
        })),
        fetch('/api/admin/permissions', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
        }).catch(() => ({
          ok: true,
          json: async () => ({
            permissions: [
              // User permissions
              { id: 'users.read', name: 'View Users', resource: 'users', action: 'read', description: 'View user profiles' },
              { id: 'users.write', name: 'Modify Users', resource: 'users', action: 'write', description: 'Create/update users' },
              { id: 'users.ban', name: 'Ban Users', resource: 'users', action: 'ban', description: 'Ban user accounts' },
              
              // Ship permissions
              { id: 'ships.read', name: 'View Ships', resource: 'ships', action: 'read', description: 'View ship data' },
              { id: 'ships.write', name: 'Modify Ships', resource: 'ships', action: 'write', description: 'Create/update ships' },
              { id: 'ships.emergency', name: 'Emergency Actions', resource: 'ships', action: 'emergency', description: 'Emergency repairs' },
              
              // Economy permissions
              { id: 'economy.read', name: 'View Economy', resource: 'economy', action: 'read', description: 'View economy data' },
              { id: 'economy.intervene', name: 'Market Intervention', resource: 'economy', action: 'intervene', description: 'Market controls' },
              
              // Combat permissions
              { id: 'combat.view', name: 'View Combat', resource: 'combat', action: 'view', description: 'View combat logs' },
              { id: 'combat.intervene', name: 'Combat Intervention', resource: 'combat', action: 'intervene', description: 'Stop combat' },
              
              // Messages permissions
              { id: 'messages.read', name: 'Read Messages', resource: 'messages', action: 'read', description: 'Read messages' },
              { id: 'messages.moderate', name: 'Moderate Messages', resource: 'messages', action: 'moderate', description: 'Delete messages' },
              
              // Analytics permissions
              { id: 'analytics.read', name: 'View Analytics', resource: 'analytics', action: 'read', description: 'View reports' },
              { id: 'analytics.export', name: 'Export Analytics', resource: 'analytics', action: 'export', description: 'Export data' },
              
              // Security permissions
              { id: 'security.manage', name: 'Manage Security', resource: 'security', action: 'manage', description: 'Security settings' },
              { id: 'security.audit', name: 'View Audit Logs', resource: 'security', action: 'audit', description: 'Audit logs' },
              
              // System permissions
              { id: 'system.config', name: 'System Config', resource: 'system', action: 'config', description: 'System settings' },
              { id: 'roles.manage', name: 'Manage Roles', resource: 'roles', action: 'manage', description: 'Create/edit roles' }
            ]
          })
        }))
      ]);

      if (rolesResponse.ok && permissionsResponse.ok) {
        const rolesData = await rolesResponse.json();
        const permissionsData = await permissionsResponse.json();
        setRoles(rolesData.roles);
        setPermissions(permissionsData.permissions);
        
        // Expand all resources by default
        const resources = new Set(permissionsData.permissions.map((p: Permission) => p.resource));
        setExpandedResources(resources);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleResource = (resource: string) => {
    const newExpanded = new Set(expandedResources);
    if (newExpanded.has(resource)) {
      newExpanded.delete(resource);
    } else {
      newExpanded.add(resource);
    }
    setExpandedResources(newExpanded);
  };

  const hasPermission = (roleId: string, permissionId: string): boolean => {
    const role = roles.find(r => r.id === roleId);
    if (!role) return false;
    
    // Check for changes first
    if (changes[roleId] && changes[roleId][permissionId] !== undefined) {
      return changes[roleId][permissionId];
    }
    
    // Check for wildcard permission
    if (role.permissions.includes('*')) return true;
    
    // Check for specific permission
    return role.permissions.includes(permissionId);
  };

  const togglePermission = (roleId: string, permissionId: string) => {
    if (!editMode) return;
    
    const role = roles.find(r => r.id === roleId);
    if (!role || role.isSystem) return;
    
    const currentValue = hasPermission(roleId, permissionId);
    const newChanges = { ...changes };
    
    if (!newChanges[roleId]) {
      newChanges[roleId] = {};
    }
    
    newChanges[roleId][permissionId] = !currentValue;
    setChanges(newChanges);
  };

  const saveChanges = async () => {
    for (const [roleId, permissions] of Object.entries(changes)) {
      for (const [permissionId, granted] of Object.entries(permissions)) {
        onPermissionChange?.(roleId, permissionId, granted);
        
        // Update local state
        const role = roles.find(r => r.id === roleId);
        if (role) {
          if (granted && !role.permissions.includes(permissionId)) {
            role.permissions.push(permissionId);
          } else if (!granted && role.permissions.includes(permissionId)) {
            role.permissions = role.permissions.filter(p => p !== permissionId);
          }
        }
      }
    }
    
    setChanges({});
    setEditMode(false);
  };

  const cancelChanges = () => {
    setChanges({});
    setEditMode(false);
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

  const getResourceIcon = (resource: string) => {
    const icons: Record<string, string> = {
      users: 'fa-users',
      ships: 'fa-rocket',
      economy: 'fa-chart-line',
      combat: 'fa-swords',
      messages: 'fa-comments',
      analytics: 'fa-chart-bar',
      security: 'fa-shield-alt',
      system: 'fa-cog',
      roles: 'fa-user-tag'
    };
    return icons[resource] || 'fa-cube';
  };

  if (loading) {
    return (
      <div className="permission-matrix-loading">
        <i className="fas fa-spinner fa-spin"></i>
        <span>Loading permission matrix...</span>
      </div>
    );
  }

  const groupedPermissions = groupPermissionsByResource();
  const hasChanges = Object.keys(changes).length > 0;

  return (
    <div className="permission-matrix">
      <div className="matrix-header">
        <h2>Permission Matrix</h2>
        <div className="matrix-actions">
          {!editMode ? (
            <button className="btn btn-primary" onClick={() => setEditMode(true)}>
              <i className="fas fa-edit"></i>
              Edit Permissions
            </button>
          ) : (
            <>
              <button className="btn btn-secondary" onClick={cancelChanges}>
                Cancel
              </button>
              <button 
                className="btn btn-primary" 
                onClick={saveChanges}
                disabled={!hasChanges}
              >
                <i className="fas fa-save"></i>
                Save Changes
              </button>
            </>
          )}
        </div>
      </div>

      <div className="matrix-table-container">
        <table className="matrix-table">
          <thead>
            <tr>
              <th className="resource-header">Permission</th>
              {roles.map(role => (
                <th key={role.id} className="role-header">
                  <div className="role-header-content">
                    <span className="role-name">{role.name}</span>
                    <span className="user-count">{role.userCount} users</span>
                    {role.isSystem && <span className="system-badge">System</span>}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Object.entries(groupedPermissions).map(([resource, perms]) => (
              <React.Fragment key={resource}>
                <tr className="resource-row">
                  <td colSpan={roles.length + 1}>
                    <button
                      className="resource-toggle"
                      onClick={() => toggleResource(resource)}
                    >
                      <i className={`fas fa-chevron-${expandedResources.has(resource) ? 'down' : 'right'}`}></i>
                      <i className={`fas ${getResourceIcon(resource)}`}></i>
                      <span>{resource.charAt(0).toUpperCase() + resource.slice(1)}</span>
                      <span className="permission-count">({perms.length} permissions)</span>
                    </button>
                  </td>
                </tr>
                {expandedResources.has(resource) && perms.map(permission => (
                  <tr key={permission.id} className="permission-row">
                    <td className="permission-cell">
                      <div className="permission-info">
                        <span className="permission-name">{permission.name}</span>
                        <span className="permission-description">{permission.description}</span>
                      </div>
                    </td>
                    {roles.map(role => {
                      const hasAccess = hasPermission(role.id, permission.id);
                      const isChanged = changes[role.id]?.[permission.id] !== undefined;
                      const isSystemRole = role.isSystem || role.permissions.includes('*');
                      
                      return (
                        <td key={role.id} className="access-cell">
                          <button
                            className={`access-toggle ${hasAccess ? 'granted' : 'denied'} ${isChanged ? 'changed' : ''} ${isSystemRole ? 'system' : ''}`}
                            onClick={() => togglePermission(role.id, permission.id)}
                            disabled={!editMode || isSystemRole}
                            title={
                              isSystemRole 
                                ? 'System roles cannot be modified' 
                                : hasAccess 
                                  ? 'Permission granted' 
                                  : 'Permission denied'
                            }
                          >
                            {hasAccess ? (
                              <i className="fas fa-check"></i>
                            ) : (
                              <i className="fas fa-times"></i>
                            )}
                          </button>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>

      {editMode && hasChanges && (
        <div className="matrix-changes">
          <h3>Pending Changes</h3>
          <div className="changes-list">
            {Object.entries(changes).map(([roleId, permissions]) => {
              const role = roles.find(r => r.id === roleId);
              if (!role) return null;
              
              return (
                <div key={roleId} className="change-item">
                  <h4>{role.name}</h4>
                  <ul>
                    {Object.entries(permissions).map(([permissionId, granted]) => {
                      const permission = permissions.find(p => p.id === permissionId);
                      if (!permission) return null;
                      
                      return (
                        <li key={permissionId}>
                          {granted ? (
                            <span className="grant">
                              <i className="fas fa-plus-circle"></i>
                              Grant {permission.name}
                            </span>
                          ) : (
                            <span className="revoke">
                              <i className="fas fa-minus-circle"></i>
                              Revoke {permission.name}
                            </span>
                          )}
                        </li>
                      );
                    })}
                  </ul>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};