import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [apiStatus, setApiStatus] = useState<string>('Loading...')
  const [apiMessage, setApiMessage] = useState<string>('')
  const [apiEnvironment, setApiEnvironment] = useState<string>('')
  
  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:5000'
    
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
        <p className="subtitle">Player Client</p>
      </header>
      
      <main>
        <section className="welcome-section">
          <h2>Welcome to Sector Wars 2102</h2>
          <p>A space trading simulation game where you navigate sectors, trade commodities, and colonize planets.</p>
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
      </main>
      
      <footer>
        <p>Sector Wars 2102 - Player Client v0.1.0</p>
      </footer>
    </div>
  )
}

export default App