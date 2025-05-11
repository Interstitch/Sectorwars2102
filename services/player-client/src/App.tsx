import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import axios from 'axios'
import './App.css'

// Import context
import { AuthProvider } from './contexts/AuthContext'

// Import components
import LoginForm from './components/auth/LoginForm'
import RegisterForm from './components/auth/RegisterForm'
import UserProfile from './components/auth/UserProfile'
import OAuthCallback from './components/auth/OAuthCallback'

function MainApp() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<any>(null);
  const [apiStatus, setApiStatus] = useState<string>('Loading...');
  const [apiMessage, setApiMessage] = useState<string>('');
  const [apiEnvironment, setApiEnvironment] = useState<string>('');
  const [authMode, setAuthMode] = useState<'none' | 'login' | 'register'>('none');
  const navigate = useNavigate();
  
  // Use relative API URL to leverage the Vite proxy consistently across environments
  const getApiUrl = () => {
    // If an environment variable is explicitly set, use it
    if (import.meta.env.VITE_API_URL) {
      return import.meta.env.VITE_API_URL;
    }

    console.log('Using relative URL with Vite proxy for', window.location.origin);
    // In all environments, use relative URLs that go through the Vite proxy
    return '';  // Empty string means use relative URL with proxy
  };

  useEffect(() => {
    const apiUrl = getApiUrl()
    console.log('Checking API status at:', apiUrl)

    const checkApiStatus = async () => {
      try {
        // Try the API version endpoint first (properly proxied)
        try {
          console.log('Trying API version endpoint...')
          const versionResponse = await axios.get(`${apiUrl}/api/version`)
          if (versionResponse.status === 200) {
            setApiStatus('Connected')
            setApiMessage(`Game API Server v${versionResponse.data.version}`)
            setApiEnvironment('gameserver')
            console.log('API connection successful via version endpoint')
            return
          }
        } catch (versionError) {
          console.warn('API version endpoint failed:', versionError)
        }

        // Try API status endpoint (properly proxied)
        try {
          console.log('Trying API status endpoint...')
          const statusResponse = await axios.get(`${apiUrl}/api/status`)
          setApiStatus('Connected')
          setApiMessage(statusResponse.data.message || 'Game API Server is operational')
          setApiEnvironment(statusResponse.data.environment || 'gameserver')
          console.log('API connection successful via status endpoint')
          return
        } catch (statusError) {
          console.warn('API status endpoint failed:', statusError)
        }

        // Try API ping endpoint as final fallback
        try {
          console.log('Trying API ping endpoint as final fallback...')
          const pingResponse = await axios.get(`${apiUrl}/api/ping`)
          setApiStatus('Connected')
          setApiMessage('Game API Server is responding')
          setApiEnvironment(pingResponse.data.environment || 'gameserver')
          console.log('API connection successful via ping endpoint')
          return
        } catch (pingError) {
          console.warn('API ping endpoint failed:', pingError)
          throw new Error('All API endpoints failed')
        }
      } catch (error) {
        console.error('Error connecting to API (all attempts failed):', error)
        setApiStatus('Error connecting to API')
      }
    }

    checkApiStatus()

    // Set up interval to check API status every 30 seconds
    const intervalId = setInterval(checkApiStatus, 30000)
    
    // Check if user is authenticated
    const checkAuth = async () => {
      const accessToken = localStorage.getItem('accessToken');
      if (accessToken) {
        try {
          // Set auth header
          axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
          
          // Get user info
          const response = await axios.get(`${apiUrl}/api/auth/me`);
          setUser(response.data);
          setIsAuthenticated(true);
        } catch (error) {
          console.error('Failed to verify authentication:', error);
          // Clear tokens on auth failure
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          localStorage.removeItem('userId');
          setIsAuthenticated(false);
        }
      }
    };
    
    checkAuth();
    
    // Clean up interval on component unmount
    return () => clearInterval(intervalId)
  }, [])

  const handleLoginClick = () => {
    setAuthMode('login');
  };

  const handleRegisterClick = () => {
    setAuthMode('register');
  };

  const handleBackToHome = () => {
    setAuthMode('none');
  };

  const handleLogout = () => {
    // Clear tokens
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('userId');
    
    // Clear auth header
    axios.defaults.headers.common['Authorization'] = '';
    
    // Update state
    setUser(null);
    setIsAuthenticated(false);
    
    // Redirect if needed
    navigate('/');
  };
  
  if (isAuthenticated) {
    return (
      <div className="container">
        <header>
          <h1>Sector Wars 2102</h1>
          <p className="subtitle">Player Client</p>
          <div className="api-status">
            <span className={`status-dot ${apiStatus.includes('Connected') ? 'connected' : 'disconnected'}`}></span>
            <span className="status-text">{apiStatus}</span>
          </div>
        </header>
        
        <main className="dashboard">
          <div className="dashboard-header">
            <h2>Player Dashboard</h2>
            {user && (
              <div className="user-profile">
                <div className="user-info">
                  <span className="username">{user.username}</span>
                  <span className="user-role">Player</span>
                </div>
                <button 
                  onClick={handleLogout} 
                  className="logout-button"
                >
                  Logout
                </button>
              </div>
            )}
          </div>
          
          <div className="dashboard-content">
            <section className="welcome-section">
              <h3>Welcome, {user?.username || 'Player'}!</h3>
              <p>Welcome to Sector Wars 2102, where you can navigate the galaxy, trade valuable resources, and build your own space empire.</p>
            </section>
            
            <section className="status-section">
              <h3>Game Server Status</h3>
              <div className="status-indicator">
                <span className={`status-dot ${apiStatus.includes('Connected') ? 'connected' : 'disconnected'}`}></span>
                <span className="status-text">{apiStatus}</span>
              </div>
              {apiStatus.includes('Connected') && (
                <div className="api-info">
                  <p><strong>Message:</strong> {apiMessage}</p>
                  <p><strong>Environment:</strong> {apiEnvironment}</p>
                </div>
              )}
            </section>
            
            <section className="game-actions">
              <h3>Quick Actions</h3>
              <div className="action-buttons">
                <button className="action-button">Start New Game</button>
                <button className="action-button">Continue Game</button>
                <button className="action-button">View Markets</button>
                <button className="action-button">Fleet Management</button>
              </div>
            </section>
          </div>
        </main>
        
        <footer>
          <p>Sector Wars 2102 - Player Client v0.1.0</p>
        </footer>
      </div>
    );
  }
  
  return (
    <div className="container">
      <header>
        <h1>Sector Wars 2102</h1>
        <p className="subtitle">Player Client</p>
      </header>
      
      <main>
        {authMode === 'login' ? (
          <LoginForm
            onLoginSuccess={() => setAuthMode('none')}
            switchToRegister={() => setAuthMode('register')}
            onClose={() => setAuthMode('none')}
          />
        ) : authMode === 'register' ? (
          <RegisterForm
            onRegisterSuccess={() => setAuthMode('none')}
            switchToLogin={() => setAuthMode('login')}
            onClose={() => setAuthMode('none')}
          />
        ) : (
          <>
            <section className="welcome-section">
              <h2>Welcome to Sector Wars 2102</h2>
              <p>Embark on an epic space trading adventure in the year 2102. Navigate through star systems, trade valuable commodities, build your fleet, and colonize distant planets in this immersive simulation game.</p>
              <div className="cta-buttons">
                <button
                  className="login-button"
                  onClick={handleLoginClick}
                >
                  Play Now
                </button>
                <button
                  className="register-button"
                  onClick={handleRegisterClick}
                >
                  Register to Play
                </button>
              </div>

              <div className="feature-list">
                <div className="feature-item">
                  <div className="feature-icon">🚀</div>
                  <h3 className="feature-title">Build Your Fleet</h3>
                  <p className="feature-description">Acquire and upgrade spaceships to create a powerful trading fleet or combat squadron.</p>
                </div>
                <div className="feature-item">
                  <div className="feature-icon">💱</div>
                  <h3 className="feature-title">Master Trading</h3>
                  <p className="feature-description">Navigate market dynamics, exploit price differences, and become a trading mogul.</p>
                </div>
                <div className="feature-item">
                  <div className="feature-icon">🌌</div>
                  <h3 className="feature-title">Explore Sectors</h3>
                  <p className="feature-description">Chart unexplored territories, discover resources, and establish new trading routes.</p>
                </div>
              </div>
            </section>

            <div className="sidebar-content">
              <section className="status-section">
                <h3>Game Server Status</h3>
                <div className="status-indicator">
                  <span className={`status-dot ${apiStatus.includes('Connected') ? 'connected' : 'disconnected'}`}></span>
                  <span className="status-text">{apiStatus}</span>
                </div>
                {apiStatus.includes('Connected') && (
                  <div className="api-info">
                    <p><strong>Message:</strong> {apiMessage}</p>
                    <p><strong>Environment:</strong> {apiEnvironment}</p>
                  </div>
                )}
              </section>

              <div className="news-section">
                <h3>Latest Updates</h3>
                <div className="news-item">
                  <span className="news-date">May 11, 2025</span>
                  <h4 className="news-title">New Sectors Added</h4>
                  <p className="news-desc">Explore the newly added Andromeda and Orion sectors with unique resources.</p>
                </div>
                <div className="news-item">
                  <span className="news-date">May 5, 2025</span>
                  <h4 className="news-title">Trading System Enhanced</h4>
                  <p className="news-desc">Market fluctuations now respond more dynamically to player actions.</p>
                </div>
              </div>
            </div>
          </>
        )}
      </main>
      
      <footer>
        <p>Sector Wars 2102 - Player Client v0.1.0</p>
      </footer>
    </div>
  )
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/oauth-callback" element={<OAuthCallback />} />
          <Route path="*" element={<MainApp />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App