import React, { useState, useEffect, FormEvent, ChangeEvent } from 'react';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import PageHeader from '../ui/PageHeader';

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
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [editMode, setEditMode] = useState<boolean>(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<boolean>(false);
  const [confirmUsername, setConfirmUsername] = useState<string>('');
  
  // Form states for new user
  const [newUsername, setNewUsername] = useState<string>('');
  const [newEmail, setNewEmail] = useState<string>('');
  const [newPassword, setNewPassword] = useState<string>('');
  const [isAdmin, setIsAdmin] = useState<boolean>(false);
  
  // Form states for edit user
  const [editUsername, setEditUsername] = useState<string>('');
  const [editEmail, setEditEmail] = useState<string>('');
  const [editIsActive, setEditIsActive] = useState<boolean>(true);

  // Get API URL based on environment
  const getApiUrl = () => {
    // If an environment variable is explicitly set, use it
    if (import.meta.env.VITE_API_URL) {
      return import.meta.env.VITE_API_URL;
    }
    // In all environments, use relative URLs that go through the Vite proxy
    return '';
  };

  const apiUrl = getApiUrl();
  
  // Load users
  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true);
      try {
        const response = await axios.get<User[]>(`${apiUrl}/api/v1/users/`);
        setUsers(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching users:', err);
        setError('Failed to load users. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchUsers();
  }, [apiUrl]);
  
  // Create user
  const handleCreateUser = async (e: FormEvent) => {
    e.preventDefault();
    
    try {
      const userData = {
        username: newUsername,
        email: newEmail,
        password: newPassword,
        is_admin: isAdmin
      };
      
      const endpoint = isAdmin ? `${apiUrl}/api/v1/users/admin` : `${apiUrl}/api/v1/users/`;
      const response = await axios.post<User>(endpoint, userData);
      
      // Add new user to list
      setUsers([...users, response.data]);
      
      // Reset form
      setNewUsername('');
      setNewEmail('');
      setNewPassword('');
      setIsAdmin(false);
      setShowCreateModal(false);
      
      // Show success message
      setError(null);
    } catch (err: any) {
      console.error('Error creating user:', err);
      setError(err.response?.data?.detail || 'Failed to create user. Please try again.');
    }
  };
  
  // Edit user setup
  const handleEditClick = (user: User) => {
    setSelectedUser(user);
    setEditUsername(user.username);
    setEditEmail(user.email || '');
    setEditIsActive(user.is_active);
    setEditMode(true);
  };
  
  // Save edited user
  const handleSaveEdit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!selectedUser) return;
    
    try {
      const userData = {
        username: editUsername,
        email: editEmail || null,
        is_active: editIsActive
      };
      
      const response = await axios.put<User>(`${apiUrl}/api/v1/users/${selectedUser.id}`, userData);
      
      // Update user in list
      setUsers(users.map((u: User) => u.id === selectedUser.id ? response.data : u));
      
      // Exit edit mode
      setEditMode(false);
      setSelectedUser(null);
      setError(null);
    } catch (err: any) {
      console.error('Error updating user:', err);
      setError(err.response?.data?.detail || 'Failed to update user. Please try again.');
    }
  };
  
  // Delete user setup
  const handleDeleteClick = (user: User) => {
    setSelectedUser(user);
    setConfirmUsername('');
    setShowDeleteConfirm(true);
  };
  
  // Confirm delete user
  const handleConfirmDelete = async () => {
    if (!selectedUser) return;
    
    if (confirmUsername !== selectedUser.username) {
      setError('Username does not match. Deletion canceled.');
      return;
    }
    
    try {
      await axios.delete(`${apiUrl}/api/v1/users/${selectedUser.id}`);
      
      // Remove user from list
      setUsers(users.filter((u: User) => u.id !== selectedUser.id));
      
      // Close modal
      setShowDeleteConfirm(false);
      setSelectedUser(null);
      setError(null);
    } catch (err: any) {
      console.error('Error deleting user:', err);
      setError(err.response?.data?.detail || 'Failed to delete user. Please try again.');
    }
  };
  
  // Reset password
  const handleResetPassword = async (userId: string) => {
    const password = prompt('Enter new password (minimum 8 characters):');
    
    if (!password) return;
    
    if (password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }
    
    try {
      await axios.put(`${apiUrl}/api/v1/users/${userId}/password`, { password });
      setError(null);
      alert('Password updated successfully.');
    } catch (err: any) {
      console.error('Error resetting password:', err);
      setError(err.response?.data?.detail || 'Failed to reset password. Please try again.');
    }
  };
  
  // Format date
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
  
  // Determine user status class
  const getUserStatusClass = (user: User) => {
    if (!user.is_active) return 'status-inactive';
    if (user.is_admin) return 'status-admin';
    return 'status-active';
  };
  
  return (
    <div className="page-container">
      <PageHeader 
        title="User Management" 
        subtitle="Manage user accounts, permissions, and access controls"
      />
      
      <div className="page-content">
        <div className="flex justify-between items-center mb-6">
          <div className="text-muted">
            {users.length} total users
          </div>
          <button 
            className="btn btn-primary"
            onClick={() => setShowCreateModal(true)}
          >
            Create User
          </button>
        </div>
      
        {error && (
          <div className="alert alert-error mb-6">
            <p>{error}</p>
            <button className="btn btn-sm btn-outline" onClick={() => setError(null)}>Dismiss</button>
          </div>
        )}
        
        {loading ? (
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
                  {users.map((user: User) => (
                    <tr key={user.id}>
                      <td className="font-medium">{user.username}</td>
                      <td className="text-muted">{user.email || 'N/A'}</td>
                      <td>
                        <span className={`badge ${!user.is_active ? 'badge-error' : user.is_admin ? 'badge-warning' : 'badge-success'}`}>
                          {!user.is_active ? 'Inactive' : user.is_admin ? 'Admin' : 'Active'}
                        </span>
                      </td>
                      <td className="text-muted">{formatDate(user.created_at)}</td>
                      <td className="text-muted">{formatDate(user.last_login)}</td>
                      <td>
                        <div className="flex gap-2">
                          {/* Prevent actions on current user and on protected admin account */}
                          {user.username === 'admin' ? (
                            <span className="badge badge-info">Protected Account</span>
                          ) : currentUser && user.id !== currentUser.id ? (
                            <>
                              <button 
                                className="btn btn-sm btn-outline"
                                onClick={() => handleEditClick(user)}
                              >
                                Edit
                              </button>
                              <button 
                                className="btn btn-sm btn-outline btn-error"
                                onClick={() => handleDeleteClick(user)}
                              >
                                Delete
                              </button>
                              {user.is_admin && (
                                <button 
                                  className="btn btn-sm btn-outline btn-warning"
                                  onClick={() => handleResetPassword(user.id)}
                                >
                                  Reset Password
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
                <button className="modal-close" onClick={() => setShowCreateModal(false)}>×</button>
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
              
              <div className="form-field checkbox-field">
                <label>
                  <input
                    type="checkbox"
                    checked={isAdmin}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => setIsAdmin(e.target.checked)}
                  />
                  Grant Admin Privileges
                </label>
              </div>
              
              <div className="modal-actions">
                <button type="button" onClick={() => setShowCreateModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="primary-button">
                  Create User
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      {/* Edit User Modal */}
      {editMode && selectedUser && (
        <div className="modal-overlay">
          <div className="modal-container">
            <h3>Edit User: {selectedUser.username}</h3>
            <form onSubmit={handleSaveEdit}>
              <div className="form-field">
                <label htmlFor="edit-username">Username</label>
                <input
                  id="edit-username"
                  type="text"
                  value={editUsername}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setEditUsername(e.target.value)}
                  required
                  minLength={3}
                  maxLength={50}
                />
              </div>
              
              <div className="form-field">
                <label htmlFor="edit-email">Email</label>
                <input
                  id="edit-email"
                  type="email"
                  value={editEmail}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setEditEmail(e.target.value)}
                />
              </div>
              
              <div className="form-field checkbox-field">
                <label>
                  <input
                    type="checkbox"
                    checked={editIsActive}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => setEditIsActive(e.target.checked)}
                  />
                  Account Active
                </label>
              </div>
              
              <div className="modal-actions">
                <button type="button" onClick={() => {
                  setEditMode(false);
                  setSelectedUser(null);
                }}>
                  Cancel
                </button>
                <button type="submit" className="primary-button">
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && selectedUser && (
        <div className="modal-overlay">
          <div className="modal-container delete-confirm">
            <h3>Delete User</h3>
            <p>
              Are you sure you want to delete the user <strong>{selectedUser.username}</strong>?
              This action cannot be undone.
            </p>
            <p>
              Type the username <strong>{selectedUser.username}</strong> to confirm:
            </p>
            <input
              type="text"
              value={confirmUsername}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setConfirmUsername(e.target.value)}
              className="confirm-input"
            />
            
            <div className="modal-actions">
              <button type="button" onClick={() => {
                setShowDeleteConfirm(false);
                setSelectedUser(null);
              }}>
                Cancel
              </button>
              <button 
                type="button" 
                className="delete-button"
                disabled={confirmUsername !== selectedUser.username}
                onClick={handleConfirmDelete}
              >
                Delete User
              </button>
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  );
};

export default UsersManager;