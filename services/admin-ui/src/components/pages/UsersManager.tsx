import React, { useState, useEffect, FormEvent, ChangeEvent, useRef } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useAdmin } from '../../contexts/AdminContext';
import PageHeader from '../ui/PageHeader';
import { api } from '../../utils/auth';

// Types
interface User {
  id: string;
  username: string;
  email: string | null;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  last_login: string | null;
}

const UsersManager: React.FC = () => {
  const { user: currentUser } = useAuth();
  const { users, loadUsers, isLoading, error: contextError } = useAdmin();
  const [error, setError] = useState<string | null>(null);
  const hasLoaded = useRef(false);
  const [editMode, setEditMode] = useState<boolean>(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<boolean>(false);
  const [confirmUsername, setConfirmUsername] = useState<string>('');
  
  // Search/filter state
  const [searchTerm, setSearchTerm] = useState<string>('');
  
  // Form states for new user
  const [newUsername, setNewUsername] = useState<string>('');
  const [newEmail, setNewEmail] = useState<string>('');
  const [newPassword, setNewPassword] = useState<string>('');
  const [isAdmin, setIsAdmin] = useState<boolean>(false);
  
  // Form states for edit user
  const [editUsername, setEditUsername] = useState<string>('');
  const [editEmail, setEditEmail] = useState<string>('');
  const [editIsActive, setEditIsActive] = useState<boolean>(true);

  // Load users when component mounts (only once)
  useEffect(() => {
    if (currentUser && currentUser.is_admin && !hasLoaded.current && users.length === 0) {
      hasLoaded.current = true;
      loadUsers();
    }
  }, [currentUser?.is_admin, users.length]); // Also check if users are already loaded

  // Handle create user form submission
  const handleCreateUser = async (e: FormEvent) => {
    e.preventDefault();
    
    try {
      setError(null);

      const userData = {
        username: newUsername,
        email: newEmail || null,
        password: newPassword,
        is_admin: isAdmin
      };

      await api.post('/api/v1/admin/users', userData);

      // Reset form
      setNewUsername('');
      setNewEmail('');
      setNewPassword('');
      setIsAdmin(false);
      setShowCreateModal(false);
      
      // Refresh users list
      loadUsers();
    } catch (err: any) {
      console.error('Error creating user:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to create user');
    }
  };

  // Handle edit user click
  const handleEditClick = (user: User) => {
    setSelectedUser(user);
    setEditUsername(user.username);
    setEditEmail(user.email || '');
    setEditIsActive(user.is_active);
    setEditMode(true);
  };

  // Handle save edit form submission
  const handleSaveEdit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!selectedUser) return;
    
    try {
      setError(null);

      const updateData = {
        username: editUsername,
        email: editEmail || null,
        is_active: editIsActive
      };

      await api.put(`/api/v1/admin/users/${selectedUser.id}`, updateData);

      // Reset edit state
      setEditMode(false);
      setSelectedUser(null);
      
      // Refresh users list
      loadUsers();
    } catch (err: any) {
      console.error('Error updating user:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to update user');
    }
  };

  // Handle delete user click
  const handleDeleteClick = (user: User) => {
    setSelectedUser(user);
    setConfirmUsername('');
    setShowDeleteConfirm(true);
  };

  // Handle confirm delete
  const handleConfirmDelete = async () => {
    if (!selectedUser || confirmUsername !== selectedUser.username) {
      return;
    }
    
    try {
      setError(null);

      await api.delete(`/api/v1/admin/users/${selectedUser.id}`);

      // Reset delete state
      setShowDeleteConfirm(false);
      setSelectedUser(null);
      setConfirmUsername('');
      
      // Refresh users list
      loadUsers();
    } catch (err: any) {
      console.error('Error deleting user:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to delete user');
    }
  };

  // Handle reset password
  const handleResetPassword = async (userId: string) => {
    try {
      setError(null);

      await api.post(`/api/v1/admin/users/${userId}/reset-password`, {});

      alert('Password reset successfully. New password has been generated.');
    } catch (err: any) {
      console.error('Error resetting password:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to reset password');
    }
  };

  // Format date for display
  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  // Filter users based on search term
  const filteredUsers = users.filter(user => {
    if (!searchTerm) return true;
    
    const searchLower = searchTerm.toLowerCase();
    const statusText = !user.is_active ? 'inactive' : user.is_admin ? 'admin' : 'active';
    
    return (
      user.username.toLowerCase().includes(searchLower) ||
      (user.email && user.email.toLowerCase().includes(searchLower)) ||
      statusText.includes(searchLower)
    );
  });

  // Use context error or local error, but be more specific
  const displayError = error || (contextError && users.length === 0 ? contextError : null);
  
  return (
    <div className="page-container">
      <PageHeader 
        title="User Management" 
        subtitle="Manage user accounts, permissions, and access controls"
      />
      
      <div className="page-content">
        {/* Search and Actions Header */}
        <div className="flex justify-between items-center mb-6 gap-4">
          <div className="flex items-center gap-4 flex-1">
            <div className="text-muted">
              {filteredUsers.length} of {users.length} users
              {searchTerm && (
                <span className="ml-2 text-xs">
                  (filtered by "{searchTerm}")
                </span>
              )}
            </div>
            <div className="search-box flex-1 max-w-md">
              <input
                type="text"
                placeholder="Search users by name, email, or status..."
                className="form-input"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              {searchTerm && (
                <button
                  className="btn btn-sm btn-ghost ml-2"
                  onClick={() => setSearchTerm('')}
                  title="Clear search"
                >
                  ✕
                </button>
              )}
            </div>
          </div>
          <button 
            className="btn btn-primary"
            onClick={() => setShowCreateModal(true)}
          >
            Create User
          </button>
        </div>
      
        {displayError && (
          <div className="alert alert-error mb-6">
            <p>{displayError}</p>
            <button className="btn btn-sm btn-outline" onClick={() => setError(null)}>Dismiss</button>
          </div>
        )}
        
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="loading-spinner mr-3"></div>
            <p className="text-muted">Loading users...</p>
          </div>
        ) : (
          <div className="card">
            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>Last Login</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredUsers.map((user: User) => (
                    <tr key={user.id}>
                      <td className="font-medium">{user.username}</td>
                      <td className="text-muted">{user.email || 'N/A'}</td>
                      <td>
                        <span className={`badge ${!user.is_active ? 'badge-error' : user.is_admin ? 'badge-warning' : 'badge-success'}`}>
                          {!user.is_active ? 'Inactive' : user.is_admin ? 'Admin' : 'Active'}
                        </span>
                      </td>
                      <td className="text-muted date-cell">{formatDate(user.created_at)}</td>
                      <td className="text-muted date-cell">{formatDate(user.last_login)}</td>
                      <td>
                        <div className="action-buttons">
                          {/* Prevent actions on current user and on protected admin account */}
                          {user.username === 'admin' ? (
                            <span className="badge badge-info">Protected Account</span>
                          ) : currentUser && user.id !== currentUser.id ? (
                            <>
                              <button 
                                className="btn btn-sm btn-outline"
                                onClick={() => handleEditClick(user)}
                                title="Edit User"
                              >
                                Edit
                              </button>
                              <button 
                                className="btn btn-sm btn-outline btn-error"
                                onClick={() => handleDeleteClick(user)}
                                title="Delete User"
                              >
                                Delete
                              </button>
                              {user.is_admin && (
                                <button 
                                  className="btn btn-sm btn-outline btn-warning"
                                  onClick={() => handleResetPassword(user.id)}
                                  title="Reset Password"
                                >
                                  Reset
                                </button>
                              )}
                            </>
                          ) : (
                            <span className="badge badge-info">Current User</span>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      
        {/* Create User Modal */}
        {showCreateModal && (
          <div className="modal-overlay">
            <div className="modal">
              <div className="modal-header">
                <h3 className="modal-title">Create New User</h3>
                <button className="btn btn-sm btn-ghost" onClick={() => setShowCreateModal(false)}>×</button>
              </div>
              <div className="modal-body">
                <form onSubmit={handleCreateUser} className="space-y-4">
                  <div className="form-group">
                    <label htmlFor="username" className="form-label">Username</label>
                    <input
                      id="username"
                      type="text"
                      className="form-input"
                      value={newUsername}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => setNewUsername(e.target.value)}
                      required
                      minLength={3}
                      maxLength={50}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="email" className="form-label">Email</label>
                    <input
                      id="email"
                      type="email"
                      className="form-input"
                      value={newEmail}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => setNewEmail(e.target.value)}
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="password" className="form-label">Password</label>
                    <input
                      id="password"
                      type="password"
                      className="form-input"
                      value={newPassword}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => setNewPassword(e.target.value)}
                      required
                      minLength={8}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>
                      <input
                        type="checkbox"
                        checked={isAdmin}
                        onChange={(e: ChangeEvent<HTMLInputElement>) => setIsAdmin(e.target.checked)}
                        className="form-checkbox mr-2"
                      />
                      Grant Admin Privileges
                    </label>
                  </div>
                  
                  <div className="modal-footer">
                    <button type="button" className="btn btn-outline" onClick={() => setShowCreateModal(false)}>
                      Cancel
                    </button>
                    <button type="submit" className="btn btn-primary">
                      Create User
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      
        {/* Edit User Modal */}
        {editMode && selectedUser && (
          <div className="modal-overlay">
            <div className="modal">
              <div className="modal-header">
                <h3 className="modal-title">Edit User: {selectedUser.username}</h3>
                <button className="btn btn-sm btn-ghost" onClick={() => setEditMode(false)}>×</button>
              </div>
              <div className="modal-body">
                <form onSubmit={handleSaveEdit} className="space-y-4">
                  <div className="form-group">
                    <label htmlFor="edit-username" className="form-label">Username</label>
                    <input
                      id="edit-username"
                      type="text"
                      className="form-input"
                      value={editUsername}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => setEditUsername(e.target.value)}
                      required
                      minLength={3}
                      maxLength={50}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="edit-email" className="form-label">Email</label>
                    <input
                      id="edit-email"
                      type="email"
                      className="form-input"
                      value={editEmail}
                      onChange={(e: ChangeEvent<HTMLInputElement>) => setEditEmail(e.target.value)}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>
                      <input
                        type="checkbox"
                        checked={editIsActive}
                        onChange={(e: ChangeEvent<HTMLInputElement>) => setEditIsActive(e.target.checked)}
                        className="form-checkbox mr-2"
                      />
                      Account Active
                    </label>
                  </div>
                  
                  <div className="modal-footer">
                    <button type="button" className="btn btn-outline" onClick={() => {
                      setEditMode(false);
                      setSelectedUser(null);
                    }}>
                      Cancel
                    </button>
                    <button type="submit" className="btn btn-primary">
                      Save Changes
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      
        {/* Delete Confirmation Modal */}
        {showDeleteConfirm && selectedUser && (
          <div className="modal-overlay">
            <div className="modal">
              <div className="modal-header">
                <h3 className="modal-title">Delete User</h3>
                <button className="btn btn-sm btn-ghost" onClick={() => setShowDeleteConfirm(false)}>×</button>
              </div>
              <div className="modal-body">
                <p className="mb-4">
                  Are you sure you want to delete the user <strong>{selectedUser.username}</strong>?
                  This action cannot be undone.
                </p>
                <p className="mb-4">
                  Type the username <strong>{selectedUser.username}</strong> to confirm:
                </p>
                <input
                  type="text"
                  className="form-input"
                  value={confirmUsername}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setConfirmUsername(e.target.value)}
                />
                
                <div className="modal-footer">
                  <button type="button" className="btn btn-outline" onClick={() => {
                    setShowDeleteConfirm(false);
                    setSelectedUser(null);
                  }}>
                    Cancel
                  </button>
                  <button 
                    type="button" 
                    className="btn btn-error"
                    disabled={confirmUsername !== selectedUser.username}
                    onClick={handleConfirmDelete}
                  >
                    Delete User
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UsersManager;