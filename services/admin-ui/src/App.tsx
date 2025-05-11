import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import './App.css';

// Layouts
import AppLayout from './components/layouts/AppLayout';

// Pages
import LoginPage from './components/pages/LoginPage';
import Dashboard from './components/pages/Dashboard';
import UsersManager from './components/pages/UsersManager';

// Components
import ProtectedRoute from './components/auth/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            {/* Public routes */}
            <Route path="login" element={<LoginPage />} />

            {/* Protected routes */}
            <Route
              path="dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />

            <Route
              path="users"
              element={
                <ProtectedRoute>
                  <UsersManager />
                </ProtectedRoute>
              }
            />

            {/* Redirect root to dashboard */}
            <Route
              path="/"
              element={<Navigate to="/dashboard" replace />}
            />
            
            {/* Fallback route - also redirect to dashboard */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;