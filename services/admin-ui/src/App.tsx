import React, { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { AdminProvider } from './contexts/AdminContext';
import { WebSocketProvider } from './contexts/WebSocketContext';
import './App.css';

// Layouts
import AppLayout from './components/layouts/AppLayout';

// Components
import ProtectedRoute from './components/auth/ProtectedRoute';
import PageLoader from './components/common/PageLoader';

// Lazy load all pages for better performance
const LoginPage = lazy(() => import('./components/pages/LoginPage'));
const Dashboard = lazy(() => import('./components/pages/Dashboard'));
const UsersManager = lazy(() => import('./components/pages/UsersManager'));
const UniverseManager = lazy(() => import('./components/pages/UniverseManager'));
const EconomyDashboard = lazy(() => import('./components/pages/EconomyDashboard'));
const PlayerAnalytics = lazy(() => import('./components/pages/PlayerAnalytics'));
const CombatOverview = lazy(() => import('./components/pages/CombatOverview').then(module => ({
  default: module.CombatOverview
})));
const FleetManagement = lazy(() => import('./components/pages/FleetManagement'));
const TeamManagement = lazy(() => import('./components/pages/TeamManagement'));
const EventManagement = lazy(() => import('./components/pages/EventManagement'));
const SectorsManager = lazy(() => import('./components/pages/SectorsManager'));
const PlanetsManager = lazy(() => import('./components/pages/PlanetsManager'));
const PortsManager = lazy(() => import('./components/pages/PortsManager'));
const WarpTunnelsManager = lazy(() => import('./components/pages/WarpTunnelsManager'));
const SecurityDashboard = lazy(() => import('./components/pages/SecurityDashboard').then(module => ({
  default: module.SecurityDashboard
})));
const PermissionsDashboard = lazy(() => import('./components/pages/PermissionsDashboard').then(module => ({
  default: module.PermissionsDashboard
})));
const AdvancedAnalytics = lazy(() => import('./components/pages/AdvancedAnalytics').then(module => ({
  default: module.AdvancedAnalytics
})));
const ColonizationManagement = lazy(() => import('./components/pages/ColonizationManagement').then(module => ({
  default: module.ColonizationManagement
})));
const AITradingDashboard = lazy(() => import('./components/pages/AITradingDashboard'));
const CentralNexusManager = lazy(() => import('./components/pages/CentralNexusManager'));
const RegionalGovernorDashboard = lazy(() => import('./components/pages/RegionalGovernorDashboard'));

// Helper component for protected lazy routes
const ProtectedLazyRoute: React.FC<{ element: React.ReactElement }> = ({ element }) => (
  <ProtectedRoute>
    <Suspense fallback={<PageLoader />}>
      {element}
    </Suspense>
  </ProtectedRoute>
);

function App() {
  return (
    <AuthProvider>
      <AdminProvider>
        <WebSocketProvider>
          <Router>
            <Routes>
              <Route path="/" element={<AppLayout />}>
                {/* Public routes */}
                <Route path="login" element={
                  <Suspense fallback={<PageLoader />}>
                    <LoginPage />
                  </Suspense>
                } />

                {/* Protected routes */}
                <Route path="dashboard" element={<ProtectedLazyRoute element={<Dashboard />} />} />
                <Route path="users" element={<ProtectedLazyRoute element={<UsersManager />} />} />
                <Route path="universe" element={<ProtectedLazyRoute element={<UniverseManager />} />} />
                <Route path="economy" element={<ProtectedLazyRoute element={<EconomyDashboard />} />} />
                <Route path="players" element={<ProtectedLazyRoute element={<PlayerAnalytics />} />} />
                <Route path="combat" element={<ProtectedLazyRoute element={<CombatOverview />} />} />
                <Route path="fleets" element={<ProtectedLazyRoute element={<FleetManagement />} />} />
                <Route path="colonies" element={<ProtectedLazyRoute element={<ColonizationManagement />} />} />
                <Route path="teams" element={<ProtectedLazyRoute element={<TeamManagement />} />} />
                <Route path="events" element={<ProtectedLazyRoute element={<EventManagement />} />} />
                <Route path="analytics" element={<ProtectedLazyRoute element={<AdvancedAnalytics />} />} />
                <Route path="security" element={<ProtectedLazyRoute element={<SecurityDashboard />} />} />
                <Route path="permissions" element={<ProtectedLazyRoute element={<PermissionsDashboard />} />} />
                <Route path="ai-trading" element={<ProtectedLazyRoute element={<AITradingDashboard />} />} />
                <Route path="sectors" element={<ProtectedLazyRoute element={<SectorsManager />} />} />

                {/* Universe CRUD Routes */}
                <Route path="universe/sectors" element={<ProtectedLazyRoute element={<SectorsManager />} />} />
                <Route path="universe/planets" element={<ProtectedLazyRoute element={<PlanetsManager />} />} />
                <Route path="universe/ports" element={<ProtectedLazyRoute element={<PortsManager />} />} />
                <Route path="universe/warptunnels" element={<ProtectedLazyRoute element={<WarpTunnelsManager />} />} />
                <Route path="nexus" element={<ProtectedLazyRoute element={<CentralNexusManager />} />} />

                {/* Regional Governance Routes */}
                <Route path="regional-governor" element={<ProtectedLazyRoute element={<RegionalGovernorDashboard />} />} />

                {/* Redirect root to dashboard */}
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                
                {/* Fallback route - also redirect to dashboard */}
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Route>
            </Routes>
          </Router>
        </WebSocketProvider>
      </AdminProvider>
    </AuthProvider>
  );
}

export default App;