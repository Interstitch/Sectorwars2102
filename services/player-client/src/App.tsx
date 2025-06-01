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
  
  // Get API URL - use gameserver directly
  const getApiUrl = () => {
    // If an environment variable is explicitly set, use it as override
    if (import.meta.env.VITE_API_URL) {
      console.log('Using VITE_API_URL override:', import.meta.env.VITE_API_URL);
      return import.meta.env.VITE_API_URL;
    }

    const windowUrl = window.location.origin;
    console.log('Current window URL:', windowUrl);

    // For GitHub Codespaces, use direct gameserver URL
    if (windowUrl.includes('.app.github.dev')) {
      console.log('GitHub Codespaces detected - using direct gameserver URL');
      // Replace port 3000 with 8080 for gameserver
      const gameserverUrl = windowUrl.replace('-3000.app.github.dev', '-8080.app.github.dev');
      console.log('Using gameserver URL:', gameserverUrl);
      return gameserverUrl;
    }

    // Use direct gameserver URL - port 8080 for the gameserver
    console.log('Using direct gameserver URL for API requests');
    
    // Point directly to the gameserver at port 8080
    return 'http://localhost:8080';
  };
  
  // Get full API URL for display purposes, showing the complete endpoint
  const getFullApiUrl = () => {
    const baseUrl = getApiUrl();
    if (baseUrl) {
      // Try the path that matches what's defined in the gameserver's main.py
      return `${baseUrl}/api/v1/status`;
    } else {
      // If using proxy, show the window origin + proxy path
      return `${window.location.origin}/api/v1/status`;
    }
  };
  
  // Get the URLs that will actually be tried
  const getAllTestUrls = () => {
    const baseUrl = getApiUrl();
    const endpoints = [
      '/api/status',
      '/api/status/', 
      '/api/v1/status',
      '/api/v1/status/',
      '/api/version',
      '/api/v1/status/version',
      '/'
    ];
    
    if (baseUrl) {
      return endpoints.map(endpoint => `${baseUrl}${endpoint}`).join('\n');
    } else {
      return endpoints.map(endpoint => `${window.location.origin}${endpoint}`).join('\n');
    }
  };

  // Create a special axios instance for GitHub Codespaces
  const createCodespacesAxios = () => {
    const instance = axios.create();
    
    // Add a response interceptor to handle redirect responses
    instance.interceptors.response.use(
      (response) => {
        // If it's a redirect, check for port doubling
        if (response.status >= 300 && response.status < 400 && response.headers.location) {
          const location = response.headers.location;
          console.log(`Intercepted redirect to: ${location}`);
          
          // Check if location has duplicated port
          if (location.includes(':8080')) {
            // We'll handle this redirect manually
            const fixedLocation = location.replace(':8080', '');
            console.log(`Fixed redirect location: ${fixedLocation}`);
            
            // Store the fixed location for the caller to use
            response.headers.fixedLocation = fixedLocation;
          }
        }
        return response;
      },
      (error) => {
        return Promise.reject(error);
      }
    );
    
    return instance;
  };
  
  // Create the instance if we're in Codespaces
  const isCodespaces = window.location.hostname.includes('.app.github.dev');
  const codespacesAxios = isCodespaces ? createCodespacesAxios() : null;

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
          if (codespacesAxios) {
            codespacesAxios.defaults.headers.common['Authorization'] = `Bearer ${authData.accessToken}`;
          }
          
          // Remove the auth parameter from URL to avoid exposing tokens
          const url = new URL(window.location.href);
          url.searchParams.delete('auth');
          window.history.replaceState({}, document.title, url.href);
        }
      } catch (error) {
        console.error('Error parsing auth parameter:', error);
      }
    }
    
    const apiUrl = getApiUrl()
    console.log('Checking API status at:', apiUrl)

    const checkApiStatus = async () => {
      try {
        console.log('Starting API status check. App version: 0.1.1');
        
        // Try multiple endpoints in order of reliability
        const endpoints = [
          // Simplified ping endpoint - most reliable
          { path: '/api/status/ping', name: 'ping endpoint' },
          { path: '/api/v1/status/ping', name: 'versioned ping endpoint' },
          
          // Direct API endpoints - prefer these for maximum compatibility
          { path: '/api/status', name: 'direct status' },
          { path: '/api/status/', name: 'direct status with trailing slash' },
          
          // Main versioned API endpoints
          { path: '/api/v1/status', name: 'versioned status' },
          { path: '/api/v1/status/', name: 'versioned status with trailing slash' },
          
          // Version endpoints as alternative
          { path: '/api/version', name: 'direct version' },
          { path: '/api/v1/status/version', name: 'versioned status/version' },
          
          // Root endpoints as last resort
          { path: '/', name: 'server root' }
        ];
        
        // Try each endpoint until one works
        for (const endpoint of endpoints) {
          try {
            console.log(`Trying ${endpoint.name} endpoint: ${apiUrl}${endpoint.path}`)
            // For Codespaces, handle redirects ourselves to prevent port doubling
            const isCodespaces = window.location.hostname.includes('.app.github.dev');
            const options = {
              // Disable auto-redirects in Codespaces
              validateStatus: function (status) {
                return status < 500; // Accept any status code less than 500
              },
              headers: {
                // Add headers to help with Codespaces port forwarding
                'X-Forwarded-Host': window.location.host,
                'X-Forwarded-Proto': 'https'
              }
            };
            
            console.log(`Request options:`, options);
            
            // Use our special Codespaces axios instance if available
            const axiosToUse = isCodespaces && codespacesAxios ? codespacesAxios : axios;
            console.log(`Using ${isCodespaces ? 'Codespaces' : 'standard'} axios instance`);
            
            const response = await axiosToUse.get(`${apiUrl}${endpoint.path}`, options)
            
            // Special handling for GitHub Codespaces redirects
            if (isCodespaces && response.status >= 300 && response.status < 400) {
              console.log(`Received redirect status: ${response.status}`);
              
              // Check for the location header (regular or our fixed one)
              const location = response.headers.location;
              const fixedLocation = response.headers.fixedLocation || location;
              
              if (location) {
                console.log(`Redirect location: ${location}`);
                if (fixedLocation !== location) {
                  console.log(`Using fixed location: ${fixedLocation}`);
                }
                
                try {
                  // Check for double port issue
                  if (location.includes(':8080') && location.includes('-8080.app.github.dev')) {
                    console.log(`⚠️ Detected double port in redirect URL, fixing it...`);
                  }
                  
                  // Follow the redirect manually with the appropriate URL
                  console.log(`Following redirect to: ${fixedLocation}`);
                  const redirectResponse = await axiosToUse.get(fixedLocation, {
                    ...options,
                    // Still no auto-redirects
                  });
                  
                  // If we get a successful response, use it
                  if (redirectResponse.status >= 200 && redirectResponse.status < 300) {
                    console.log(`Redirect successful:`, redirectResponse.data);
                    setApiStatus('Connected');
                    setApiMessage((redirectResponse.data as ApiResponse).message || `Game API Server is operational (redirected)`);
                    setApiEnvironment((redirectResponse.data as ApiResponse).environment || 'gameserver');
                    return;
                  } else if (redirectResponse.status >= 300 && redirectResponse.status < 400) {
                    // Try one more level of redirection
                    const nestedLocation = redirectResponse.headers.location;
                    const nestedFixedLocation = 
                      (nestedLocation && nestedLocation.includes(':8080') && nestedLocation.includes('-8080.app.github.dev')) 
                        ? nestedLocation.replace(':8080', '') 
                        : nestedLocation;
                    
                    console.log(`Another redirect detected to: ${nestedFixedLocation}`);
                    try {
                      const nestedResponse = await axiosToUse.get(nestedFixedLocation, {
                        ...options,
                        // No auto-redirects
                      });
                      
                      if (nestedResponse.status >= 200 && nestedResponse.status < 300) {
                        console.log(`Final redirect successful:`, nestedResponse.data);
                        setApiStatus('Connected');
                        setApiMessage((nestedResponse.data as ApiResponse).message || `Game API Server operational`);
                        setApiEnvironment((nestedResponse.data as ApiResponse).environment || 'gameserver');
                        return;
                      }
                    } catch (nestedError) {
                      console.warn(`Failed to follow nested redirect:`, nestedError);
                    }
                  }
                } catch (redirectError) {
                  console.warn(`Failed to follow redirect:`, redirectError);
                }
                
                // Just mark as connected if any response comes back
                setApiStatus('Connected (with redirect)');
                setApiMessage(`Game server is responding`);
                setApiEnvironment('gameserver');
                return;
              }
            }
            
            // Accept any 2xx status as success
            if (response.status >= 200 && response.status < 300) {
              console.log(`API connection successful via ${endpoint.name} endpoint`, response.data);
              setApiStatus('Connected');
              
              // Extract message and environment based on endpoint
              if (endpoint.path.includes('version')) {
                setApiMessage(`Game API Server v${(response.data as ApiResponse).version || '0.1.0'}`);
              } else if (endpoint.path.includes('ping')) {
                setApiMessage(`Game API Server is operational (ping: ${(response.data as ApiResponse).ping})`);
              } else {
                setApiMessage((response.data as ApiResponse).message || 'Game API Server is operational');
              }
              
              setApiEnvironment((response.data as ApiResponse).environment || 'gameserver');
              
              // Log success for debugging
              console.log(`SUCCESS: Connected to API via ${endpoint.name}`);
              return;
            }
          } catch (endpointError) {
            // More detailed error logging
            console.warn(`${endpoint.name} endpoint failed:`, endpointError);
            const err = endpointError as any;
            if (err.response) {
              // The request was made and the server responded with a status code
              // that falls out of the range of 2xx
              console.error('Error response data:', err.response.data);
              console.error('Error response status:', err.response.status);
              console.error('Error response headers:', err.response.headers);
            } else if (err.request) {
              // The request was made but no response was received
              console.error('Error request (no response received):', err.request);
            } else {
              // Something happened in setting up the request that triggered an Error
              console.error('Error message:', err.message);
            }
            console.error('Error config:', err.config);
          }
        }
        
        // If we get here, all endpoints failed
        throw new Error('All API endpoints failed')
      } catch (error) {
        console.error('Error connecting to API (all attempts failed):', error)
        console.error('apiUrl used:', apiUrl)
        console.error('Current location:', window.location.toString())
        setApiStatus('Error connecting to API')
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

            {/* Status and News Section */}
            <section className="sidebar-content">
              <div className="status-section">
                <h3>Game Server Status</h3>
                <div className="status-indicator">
                  <span className={`status-dot ${apiStatus.includes('Connected') ? 'connected' : 'disconnected'}`}></span>
                  <span className="status-text">{apiStatus}</span>
                </div>
                {apiStatus.includes('Connected') ? (
                  <div className="api-info">
                    <p><strong>Message:</strong> {apiMessage}</p>
                    <p><strong>Environment:</strong> {apiEnvironment}</p>
                  </div>
                ) : (
                  <div className="api-info error-info">
                    <p><strong>API URL:</strong> {getFullApiUrl()}</p>
                    <p><strong>URLs tried:</strong></p>
                    <pre className="api-urls-tried">{getAllTestUrls()}</pre>
                  </div>
                )}
              </div>

              <div className="news-section">
                <h3>Latest Updates</h3>
                <div className="news-item">
                  <span className="news-date">December 2024</span>
                  <h4 className="news-title">AI Trading Assistant ARIA Launched</h4>
                  <p className="news-desc">Revolutionary AI companion now helps players with personalized market analysis and trading recommendations.</p>
                </div>
                <div className="news-item">
                  <span className="news-date">November 2024</span>
                  <h4 className="news-title">Quantum Warp Tunnels Live</h4>
                  <p className="news-desc">Players can now build warp gates to access hidden sectors and expand the universe.</p>
                </div>
                <div className="news-item">
                  <span className="news-date">October 2024</span>
                  <h4 className="news-title">Genesis Devices Released</h4>
                  <p className="news-desc">Create new planets in empty space using advanced terraforming technology.</p>
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