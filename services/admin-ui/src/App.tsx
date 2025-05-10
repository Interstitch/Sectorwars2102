import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [apiStatus, setApiStatus] = useState<string>('Loading...')
  const [apiMessage, setApiMessage] = useState<string>('')
  const [apiEnvironment, setApiEnvironment] = useState<string>('')
  
  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8080'

    const checkApiStatus = async () => {
      try {
        const response = await axios.get(`${apiUrl}/`)
        setApiStatus('Connected')
        setApiMessage(response.data.message)
        setApiEnvironment(response.data.environment)
      } catch (error) {
        console.error('Error connecting to API:', error)
        setApiStatus('Error connecting to API')
      }
    }
    
    checkApiStatus()
  }, [])
  
  return (
    <div className="container">
      <header>
        <h1>Sector Wars 2102</h1>
        <p className="subtitle">Admin UI</p>
      </header>
      
      <main>
        <section className="welcome-section">
          <h2>Universe Administration</h2>
          <p>Welcome to the Sector Wars 2102 Admin Interface. This panel allows you to manage the game universe, monitor players, and configure game mechanics.</p>
        </section>
        
        <section className="status-section">
          <h3>Game Server Status</h3>
          <div className="status-indicator">
            <span className={`status-dot ${apiStatus === 'Connected' ? 'connected' : 'disconnected'}`}></span>
            <span className="status-text">{apiStatus}</span>
          </div>
          {apiStatus === 'Connected' && (
            <div className="api-info">
              <p><strong>Message:</strong> {apiMessage}</p>
              <p><strong>Environment:</strong> {apiEnvironment}</p>
            </div>
          )}
        </section>
        
        <section className="admin-controls">
          <h3>Admin Controls</h3>
          <div className="admin-buttons">
            <button className="admin-button">Generate Universe</button>
            <button className="admin-button">Manage Sectors</button>
            <button className="admin-button">View Players</button>
            <button className="admin-button">Configure Trading</button>
          </div>
        </section>
      </main>
      
      <footer>
        <p>Sector Wars 2102 - Admin UI v0.1.0</p>
      </footer>
    </div>
  )
}

export default App