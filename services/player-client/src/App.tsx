import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import axios from 'axios'
import './App.css'

// Import contexts
import { AuthProvider } from './contexts/AuthContext'
import { GameProvider } from './contexts/GameContext'
import { FirstLoginProvider } from './contexts/FirstLoginContext'
import { WebSocketProvider } from './contexts/WebSocketContext'
import { ThemeProvider } from './themes/ThemeProvider'

// Import components
import LoginForm from './components/auth/LoginForm'
import RegisterForm from './components/auth/RegisterForm'
import UserProfile from './components/auth/UserProfile'
import OAuthCallback from './components/auth/OAuthCallback'
import GameDashboard from './components/pages/GameDashboard'
import GalaxyMap from './components/pages/GalaxyMap'
import DebugPage from './components/pages/DebugPage'
import TestAuthPage from './components/pages/TestAuthPage'
import { FirstLoginContainer } from './components/first-login'

// Import game feature components
import { TeamManager } from './components/teams'
import { CombatInterface } from './components/combat'
import { PlanetManager } from './components/planetary'
import { ShipSelector } from './components/ships'
import { TradingInterface } from './components/trading'

interface ApiResponse {
  message?: string;
  environment?: string;
  version?: string;
  ping?: number;
}

function MainApp() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<any>(null);
  const [apiStatus, setApiStatus] = useState<string>('Loading...');
  const [apiMessage, setApiMessage] = useState<string>('');
  const [apiEnvironment, setApiEnvironment] = useState<string>('');
  const [authMode, setAuthMode] = useState<'none' | 'login' | 'register'>('none');
  const navigate = useNavigate();
  
  // Simple API URL - use env var or default to localhost:8080
  const getApiUrl = () => {
    return import.meta.env.VITE_API_URL || 'http://localhost:8080';
  };

  useEffect(() => {
    // Check for auth parameter in URL (coming from OAuth)
    const params = new URLSearchParams(window.location.search);
    const authParam = params.get('auth');
    if (authParam) {
      try {
        console.log('Found auth parameter in URL');
        const authData = JSON.parse(decodeURIComponent(authParam));
        
        // Store tokens in localStorage
        if (authData.accessToken) {
          console.log('Setting tokens from URL parameter');
          localStorage.setItem('accessToken', authData.accessToken);
          localStorage.setItem('refreshToken', authData.refreshToken);
          localStorage.setItem('userId', authData.userId);
          
          // Set axios auth header
          axios.defaults.headers.common['Authorization'] = `Bearer ${authData.accessToken}`;
          
          // Remove the auth parameter from URL to avoid exposing tokens
          const url = new URL(window.location.href);
          url.searchParams.delete('auth');
          window.history.replaceState({}, document.title, url.href);
        }
      } catch (error) {
        console.error('Error parsing auth parameter:', error);
      }
    }
    
    const apiUrl = getApiUrl();
    console.log('Checking API status at:', apiUrl);

    const checkApiStatus = async () => {
      try {
        const response = await axios.get(`${apiUrl}/api/v1/status`, {
          timeout: 5000
        });

        if (response.status === 200 && response.data) {
          setApiStatus('Online');
          setApiMessage(response.data.message || 'Game server operational');
          setApiEnvironment(response.data.environment || 'production');
        }
      } catch (error) {
        console.error('API status check failed:', error);
        setApiStatus('Offline');
        setApiMessage('Unable to connect to game server');
        setApiEnvironment('');
      }
    }

    checkApiStatus()

    // Set up interval to check API status every 30 seconds
    const intervalId = setInterval(checkApiStatus, 30000)
    
    // Check if user is authenticated
    const checkAuth = async () => {
      const accessToken = localStorage.getItem('accessToken');
      const isFromOAuth = sessionStorage.getItem('oauth_redirect_completed') === 'true';
      
      if (isFromOAuth) {
        console.log('App detected we are coming from OAuth redirect');
        console.log('Access token exists:', !!accessToken);
        if (accessToken) {
          console.log('Access token substring:', accessToken.substring(0, 20) + '...');
        }
      }
      
      if (accessToken) {
        try {
          // Set auth header
          console.log('Setting authorization header with token (first 20 chars):', accessToken.substring(0, 20) + '...');
          axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
          
          // Log the current headers for debugging
          console.log('Current axios headers:', axios.defaults.headers.common);
          
          // Get user info
          console.log('Making request to /api/v1/auth/me');
          const response = await axios.get(`${apiUrl}/api/v1/auth/me`);
          console.log('Authentication successful, user data:', response.data);
          setUser(response.data);
          setIsAuthenticated(true);
          
          // Clear the OAuth flag if it exists
          if (isFromOAuth) {
            console.log('Clearing OAuth redirect flag');
            sessionStorage.removeItem('oauth_redirect_completed');
          }
        } catch (error) {
          console.error('Failed to verify authentication:', error);
          console.error('Error details:', (error as any).response?.data || (error as any).message);
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
    // Redirect to game dashboard
    return <Navigate to="/game" replace />;
  }
  
  return (
    <div className="container">
      <header className="site-header">
        <div className="header-content">
          <div className="logo">
            <h1>Sector Wars 2102</h1>
            <p className="subtitle">The Future of Space Trading</p>
          </div>
          <div className="header-actions">
            <div className="status-indicator-header" title={`Server: ${apiStatus} - ${apiMessage}`}>
              <span className={`status-dot ${apiStatus === 'Online' ? 'online' : 'offline'}`}></span>
              <span className="status-text-compact">{apiStatus}</span>
            </div>
            {!isAuthenticated && (
              <>
                <button className="header-btn" onClick={handleLoginClick}>Login</button>
                <button className="header-btn primary" onClick={handleRegisterClick}>Join Now</button>
              </>
            )}
          </div>
        </div>
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
            {/* Hero Section */}
            <section className="hero-section">
              <div className="hero-content">
                <div className="hero-badge">
                  <span className="badge-text">🚀 Revolutionary AI-Powered Space Trading</span>
                </div>
                <h1 className="hero-title">
                  Command the Galaxy.<br />
                  <span className="hero-title-accent">Shape the Universe.</span>
                </h1>
                <p className="hero-description">
                  The first space trading game with AI consciousness. Build quantum warp tunnels, create planets with Genesis Devices, and expand the universe itself in this revolutionary multiplayer experience.
                </p>
                
                <div className="hero-stats">
                  <div className="stat-item">
                    <div className="stat-number">1,000</div>
                    <div className="stat-label">Turns per Day</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-number">∞</div>
                    <div className="stat-label">Expanding Universe</div>
                  </div>
                  <div className="stat-item">
                    <div className="stat-number">24/7</div>
                    <div className="stat-label">AI Trading Assistant</div>
                  </div>
                </div>

                <div className="cta-buttons">
                  <button
                    className="cta-primary"
                    onClick={handleLoginClick}
                  >
                    🚀 Launch Into Space
                  </button>
                  <button
                    className="cta-secondary"
                    onClick={handleRegisterClick}
                  >
                    🌟 Join the Galaxy
                  </button>
                </div>
              </div>
              
              <div className="hero-visual">
                <div className="galaxy-animation">
                  <div className="star-field">
                    {[...Array(50)].map((_, i) => (
                      <div key={i} className={`star star-${(i % 3) + 1}`} 
                           style={{
                             left: `${Math.random() * 100}%`,
                             top: `${Math.random() * 100}%`,
                             animationDelay: `${Math.random() * 3}s`
                           }}></div>
                    ))}
                  </div>
                  <div className="central-hub">
                    <div className="hub-core">🌌</div>
                    <div className="orbit-ring"></div>
                    <div className="pulse-ring"></div>
                  </div>
                </div>
              </div>
            </section>

            {/* Revolutionary Features Section */}
            <section className="features-showcase">
              <div className="section-header">
                <h2 className="section-title">Revolutionary Features</h2>
                <p className="section-subtitle">Experience space trading like never before with cutting-edge AI and universe expansion mechanics</p>
              </div>
              
              <div className="features-grid">
                <div className="feature-card featured">
                  <div className="feature-icon-large">🤖</div>
                  <h3>ARIA AI Trading Assistant</h3>
                  <p>World's first learning AI companion that adapts to your trading style, predicts market trends, and optimizes routes in real-time.</p>
                  <div className="feature-tags">
                    <span className="tag">Machine Learning</span>
                    <span className="tag">Personalized</span>
                  </div>
                </div>
                
                <div className="feature-card">
                  <div className="feature-icon-large">🌀</div>
                  <h3>Quantum Warp Tunnels</h3>
                  <p>Build warp gates to reach hidden regions and expand the universe. Create new trade routes to sectors no one has ever seen.</p>
                  <div className="feature-tags">
                    <span className="tag">Universe Expansion</span>
                  </div>
                </div>
                
                <div className="feature-card">
                  <div className="feature-icon-large">🌍</div>
                  <h3>Genesis Devices</h3>
                  <p>Create entirely new planets using rare quantum technology. Transform empty space into thriving worlds.</p>
                  <div className="feature-tags">
                    <span className="tag">Planet Creation</span>
                  </div>
                </div>
                
                <div className="feature-card">
                  <div className="feature-icon-large">⚔️</div>
                  <h3>Strategic Combat</h3>
                  <p>Deploy drones, assault planets, and command fleets with tactical precision. Indestructible escape pods ensure you never lose everything.</p>
                  <div className="feature-tags">
                    <span className="tag">Tactical</span>
                  </div>
                </div>
                
                <div className="feature-card">
                  <div className="feature-icon-large">👥</div>
                  <h3>Real-time Multiplayer</h3>
                  <p>See other players moving through the galaxy instantly. Form teams, collaborate on Genesis projects, and build trading empires together.</p>
                  <div className="feature-tags">
                    <span className="tag">Live Updates</span>
                  </div>
                </div>
                
                <div className="feature-card">
                  <div className="feature-icon-large">📱</div>
                  <h3>Mobile Optimized</h3>
                  <p>Full gameplay experience on any device. Trade on your phone, manage your empire on your tablet, all with seamless synchronization.</p>
                  <div className="feature-tags">
                    <span className="tag">Cross-Platform</span>
                  </div>
                </div>
              </div>
            </section>

            {/* Game Preview Section */}
            <section className="game-preview">
              <div className="section-header">
                <h2 className="section-title">See the Galaxy in Action</h2>
                <p className="section-subtitle">Get a glimpse of the immersive universe that awaits you</p>
              </div>
              
              <div className="preview-showcase">
                <div className="preview-card">
                  <div className="preview-image trading">
                    <div className="mock-ui">
                      <div className="ui-header">🚀 Trading Console</div>
                      <div className="ui-content">
                        <div className="market-item">
                          <span>🔋 Energy Cells</span>
                          <span className="price profit">+32% ↗</span>
                        </div>
                        <div className="market-item">
                          <span>⚙️ Equipment</span>
                          <span className="price loss">-18% ↘</span>
                        </div>
                        <div className="ai-recommendation">
                          <span>🤖 ARIA: Profitable route to Sector 47 detected</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <h3>AI-Powered Trading</h3>
                  <p>Real-time market analysis with personalized AI recommendations</p>
                </div>
                
                <div className="preview-card">
                  <div className="preview-image exploration">
                    <div className="mock-ui">
                      <div className="ui-header">🌌 Navigation</div>
                      <div className="galaxy-mini">
                        <div className="sector current">You</div>
                        <div className="sector discovered">47</div>
                        <div className="sector unknown">??</div>
                        <div className="warp-tunnel">~~~</div>
                      </div>
                      <div className="ui-action">Build Quantum Tunnel →</div>
                    </div>
                  </div>
                  <h3>Universe Expansion</h3>
                  <p>Discover new sectors and build connections to expand the galaxy</p>
                </div>
                
                <div className="preview-card">
                  <div className="preview-image colonization">
                    <div className="mock-ui">
                      <div className="ui-header">🌍 Colonization</div>
                      <div className="planet-progress">
                        <div className="progress-bar">
                          <div className="progress-fill" style={{width: '73%'}}></div>
                        </div>
                        <div className="progress-text">Genesis Device: 73% Complete</div>
                      </div>
                      <div className="ui-action">New Planet: "New Earth" Ready!</div>
                    </div>
                  </div>
                  <h3>Planet Creation</h3>
                  <p>Use Genesis Devices to create new worlds and expand civilization</p>
                </div>
              </div>
            </section>

            {/* Getting Started Section */}
            <section className="getting-started">
              <div className="section-header">
                <h2 className="section-title">Ready to Command the Galaxy?</h2>
                <p className="section-subtitle">Join thousands of players in the ultimate space trading experience</p>
              </div>
              
              <div className="start-steps">
                <div className="step">
                  <div className="step-number">1</div>
                  <div className="step-content">
                    <h3>Create Your Account</h3>
                    <p>Quick registration gets you into the game in under 30 seconds</p>
                  </div>
                </div>
                
                <div className="step">
                  <div className="step-number">2</div>
                  <div className="step-content">
                    <h3>Meet Your AI Assistant</h3>
                    <p>ARIA will guide you through your first trades and help you understand the market</p>
                  </div>
                </div>
                
                <div className="step">
                  <div className="step-number">3</div>
                  <div className="step-content">
                    <h3>Start Trading & Exploring</h3>
                    <p>Use your 1,000 daily turns to build your empire and discover new sectors</p>
                  </div>
                </div>
              </div>
              
              <div className="final-cta">
                <h3>What are you waiting for?</h3>
                <p>The galaxy needs commanders. Will you answer the call?</p>
                <div className="cta-buttons">
                  <button
                    className="cta-primary large"
                    onClick={handleRegisterClick}
                  >
                    🚀 Start Your Journey
                  </button>
                  <button
                    className="cta-secondary large"
                    onClick={handleLoginClick}
                  >
                    ↩️ Returning Commander
                  </button>
                </div>
              </div>
            </section>

            {/* Latest Updates Section */}
            <section className="updates-section">
              <div className="section-header">
                <h2 className="section-title">Latest Updates</h2>
                <p className="section-subtitle">Stay informed about the newest features and improvements</p>
              </div>

              <div className="updates-grid">
                <div className="update-card">
                  <div className="update-icon">🤖</div>
                  <div className="update-content">
                    <span className="update-date">December 2024</span>
                    <h3>AI Trading Assistant ARIA Launched</h3>
                    <p>Revolutionary AI companion now helps players with personalized market analysis and trading recommendations.</p>
                  </div>
                </div>

                <div className="update-card">
                  <div className="update-icon">🌀</div>
                  <div className="update-content">
                    <span className="update-date">November 2024</span>
                    <h3>Quantum Warp Tunnels Live</h3>
                    <p>Players can now build warp gates to access hidden sectors and expand the universe.</p>
                  </div>
                </div>

                <div className="update-card">
                  <div className="update-icon">🌍</div>
                  <div className="update-content">
                    <span className="update-date">October 2024</span>
                    <h3>Genesis Devices Released</h3>
                    <p>Create new planets in empty space using advanced terraforming technology.</p>
                  </div>
                </div>
              </div>
            </section>
          </>
        )}
      </main>
      
      <footer>
        <p>Sector Wars 2102 - Player Client v0.1.0</p>
      </footer>
    </div>
  )
}

// Protected route component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const accessToken = localStorage.getItem('accessToken');
  const isAuthenticated = !!accessToken;
  
  if (!isAuthenticated) {
    console.log('Access token not found, redirecting to home');
    return <Navigate to="/" replace />;
  }
  
  // Ensure the token is set in axios headers
  if (accessToken && !axios.defaults.headers.common['Authorization']) {
    console.log('Setting axios auth header in ProtectedRoute');
    axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
  }
  
  return <>{children}</>;
};

function App() {
  return (
    <ThemeProvider defaultTheme="cockpit">
      <Router>
        <AuthProvider>
          <WebSocketProvider>
            <GameProvider>
              <FirstLoginProvider>
                <Routes>
              <Route path="/oauth-callback" element={<OAuthCallback />} />
              <Route path="/debug" element={<DebugPage />} />
              <Route path="/test-auth" element={<TestAuthPage />} />
              <Route path="/game" element={
                <ProtectedRoute>
                  <GameDashboard />
                </ProtectedRoute>
              } />
              <Route path="/game/map" element={
                <ProtectedRoute>
                  <GalaxyMap />
                </ProtectedRoute>
              } />
              <Route path="/game/team" element={
                <ProtectedRoute>
                  <TeamManager />
                </ProtectedRoute>
              } />
              <Route path="/game/combat" element={
                <ProtectedRoute>
                  <CombatInterface />
                </ProtectedRoute>
              } />
              <Route path="/game/planets" element={
                <ProtectedRoute>
                  <PlanetManager />
                </ProtectedRoute>
              } />
              <Route path="/game/ships" element={
                <ProtectedRoute>
                  <ShipSelector />
                </ProtectedRoute>
              } />
              <Route path="/game/trading" element={
                <ProtectedRoute>
                  <TradingInterface />
                </ProtectedRoute>
              } />
              <Route path="*" element={<MainApp />} />
                </Routes>
                <FirstLoginContainer />
              </FirstLoginProvider>
            </GameProvider>
          </WebSocketProvider>
        </AuthProvider>
      </Router>
    </ThemeProvider>
  );
}

export default App