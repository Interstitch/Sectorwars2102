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
  
  // Get API URL - prioritize proxy for all environments
  const getApiUrl = () => {
    // If an environment variable is explicitly set, use it as override
    if (import.meta.env.VITE_API_URL) {
      console.log('Using VITE_API_URL override:', import.meta.env.VITE_API_URL);
      return import.meta.env.VITE_API_URL;
    }

    // IMPORTANT CHANGE: In all environments, we'll now use the Vite proxy by default
    // This solves container name resolution and CORS issues
    console.log('Using Vite proxy for API requests (empty baseUrl)');
    
    // Empty string enables Vite proxy which routes /api to the gameserver
    // This works better than direct URLs when running in Docker or any environment
    // The proxy is configured in vite.config.ts to handle the routing
    return '';
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
              maxRedirects: isCodespaces ? 0 : 5, // Disable auto-redirects in Codespaces
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
                    maxRedirects: 0 // Still no auto-redirects
                  });
                  
                  // If we get a successful response, use it
                  if (redirectResponse.status >= 200 && redirectResponse.status < 300) {
                    console.log(`Redirect successful:`, redirectResponse.data);
                    setApiStatus('Connected');
                    setApiMessage(redirectResponse.data.message || `Game API Server is operational (redirected)`);
                    setApiEnvironment(redirectResponse.data.environment || 'gameserver');
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
                        maxRedirects: 0
                      });
                      
                      if (nestedResponse.status >= 200 && nestedResponse.status < 300) {
                        console.log(`Final redirect successful:`, nestedResponse.data);
                        setApiStatus('Connected');
                        setApiMessage(nestedResponse.data.message || `Game API Server operational`);
                        setApiEnvironment(nestedResponse.data.environment || 'gameserver');
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
                setApiMessage(`Game API Server v${response.data.version || '0.1.0'}`);
              } else if (endpoint.path.includes('ping')) {
                setApiMessage(`Game API Server is operational (ping: ${response.data.ping})`);
              } else {
                setApiMessage(response.data.message || 'Game API Server is operational');
              }
              
              setApiEnvironment(response.data.environment || 'gameserver');
              
              // Log success for debugging
              console.log(`SUCCESS: Connected to API via ${endpoint.name}`);
              return;
            }
          } catch (endpointError) {
            // More detailed error logging
            console.warn(`${endpoint.name} endpoint failed:`, endpointError);
            if (endpointError.response) {
              // The request was made and the server responded with a status code
              // that falls out of the range of 2xx
              console.error('Error response data:', endpointError.response.data);
              console.error('Error response status:', endpointError.response.status);
              console.error('Error response headers:', endpointError.response.headers);
            } else if (endpointError.request) {
              // The request was made but no response was received
              console.error('Error request (no response received):', endpointError.request);
            } else {
              // Something happened in setting up the request that triggered an Error
              console.error('Error message:', endpointError.message);
            }
            console.error('Error config:', endpointError.config);
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
          console.error('Error details:', error.response?.data || error.message);
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