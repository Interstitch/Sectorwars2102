import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { AdminProvider } from './contexts/AdminContext';
import './App.css';

// Layouts
import AppLayout from './components/layouts/AppLayout';

// Pages
import LoginPage from './components/pages/LoginPage';
import Dashboard from './components/pages/Dashboard';
import UsersManager from './components/pages/UsersManager';
import UniverseManager from './components/pages/UniverseManager';
import EconomyDashboard from './components/pages/EconomyDashboard';
import PlayerAnalytics from './components/pages/PlayerAnalytics';
import CombatOverview from './components/pages/CombatOverview';
import FleetManagement from './components/pages/FleetManagement';
import ColonizationOverview from './components/pages/ColonizationOverview';
import TeamManagement from './components/pages/TeamManagement';
import EventManagement from './components/pages/EventManagement';
import AnalyticsReports from './components/pages/AnalyticsReports';
import SectorsManager from './components/pages/SectorsManager';
import PlanetsManager from './components/pages/PlanetsManager';
import PortsManager from './components/pages/PortsManager';
import WarpTunnelsManager from './components/pages/WarpTunnelsManager';

// Components
import ProtectedRoute from './components/auth/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <AdminProvider>
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
              
              <Route
                path="universe"
                element={
                  <ProtectedRoute>
                    <UniverseManager />
                  </ProtectedRoute>
                }
              />

              <Route
                path="economy"
                element={
                  <ProtectedRoute>
                    <EconomyDashboard />
                  </ProtectedRoute>
                }
              />

              <Route
                path="players"
                element={
                  <ProtectedRoute>
                    <PlayerAnalytics />
                  </ProtectedRoute>
                }
              />

              <Route
                path="combat"
                element={
                  <ProtectedRoute>
                    <CombatOverview />
                  </ProtectedRoute>
                }
              />

              <Route
                path="fleets"
                element={
                  <ProtectedRoute>
                    <FleetManagement />
                  </ProtectedRoute>
                }
              />

              <Route
                path="colonies"
                element={
                  <ProtectedRoute>
                    <ColonizationOverview />
                  </ProtectedRoute>
                }
              />

              <Route
                path="teams"
                element={
                  <ProtectedRoute>
                    <TeamManagement />
                  </ProtectedRoute>
                }
              />

              <Route
                path="events"
                element={
                  <ProtectedRoute>
                    <EventManagement />
                  </ProtectedRoute>
                }
              />

              <Route
                path="analytics"
                element={
                  <ProtectedRoute>
                    <AnalyticsReports />
                  </ProtectedRoute>
                }
              />

              <Route
                path="sectors"
                element={
                  <ProtectedRoute>
                    <SectorsManager />
                  </ProtectedRoute>
                }
              />

              {/* Universe CRUD Routes */}
              <Route
                path="universe/sectors"
                element={
                  <ProtectedRoute>
                    <SectorsManager />
                  </ProtectedRoute>
                }
              />

              <Route
                path="universe/planets"
                element={
                  <ProtectedRoute>
                    <PlanetsManager />
                  </ProtectedRoute>
                }
              />

              <Route
                path="universe/ports"
                element={
                  <ProtectedRoute>
                    <PortsManager />
                  </ProtectedRoute>
                }
              />

              <Route
                path="universe/warptunnels"
                element={
                  <ProtectedRoute>
                    <WarpTunnelsManager />
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
      </AdminProvider>
    </AuthProvider>
  );
}

export default App;