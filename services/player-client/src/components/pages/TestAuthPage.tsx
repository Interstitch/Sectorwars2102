import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useGame } from '../../contexts/GameContext';
import axios from 'axios';

const TestAuthPage: React.FC = () => {
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const { playerState, currentShip, isLoading: gameLoading, error: gameError } = useGame();
  const [testResults, setTestResults] = useState<any[]>([]);

  const runTests = async () => {
    const results = [];
    
    // Test 1: Check localStorage
    const accessToken = localStorage.getItem('accessToken');
    const refreshToken = localStorage.getItem('refreshToken');
    const userId = localStorage.getItem('userId');
    
    results.push({
      test: 'LocalStorage tokens',
      result: accessToken ? 'PASS' : 'FAIL',
      details: {
        accessToken: accessToken ? accessToken.substring(0, 20) + '...' : 'Missing',
        refreshToken: refreshToken ? refreshToken.substring(0, 20) + '...' : 'Missing',
        userId: userId || 'Missing'
      }
    });

    // Test 2: Check axios headers
    const authHeader = axios.defaults.headers.common['Authorization'];
    results.push({
      test: 'Axios auth header',
      result: authHeader ? 'PASS' : 'FAIL',
      details: authHeader || 'Missing'
    });

    // Test 3: Direct API test with stored token
    if (accessToken) {
      try {
        const response = await axios.get('/api/v1/auth/me', {
          headers: { Authorization: `Bearer ${accessToken}` }
        });
        results.push({
          test: 'Direct API auth test',
          result: 'PASS',
          details: response.data
        });
      } catch (error) {
        results.push({
          test: 'Direct API auth test',
          result: 'FAIL',
          details: error.response?.data || error.message
        });
      }

      // Test 4: Direct player API test
      try {
        const response = await axios.get('/api/v1/player/state', {
          headers: { Authorization: `Bearer ${accessToken}` }
        });
        results.push({
          test: 'Direct API player test',
          result: 'PASS',
          details: response.data
        });
      } catch (error) {
        results.push({
          test: 'Direct API player test',
          result: 'FAIL',
          details: error.response?.data || error.message
        });
      }
    }

    setTestResults(results);
  };

  useEffect(() => {
    runTests();
  }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h1>Authentication Test Page</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <button onClick={runTests} style={{ padding: '10px', marginRight: '10px' }}>
          Run Tests
        </button>
        <button onClick={() => localStorage.clear()} style={{ padding: '10px' }}>
          Clear Storage
        </button>
      </div>

      <div style={{ marginBottom: '20px', padding: '10px', border: '1px solid #ccc' }}>
        <h2>Auth Context Status</h2>
        <p>Is Authenticated: {isAuthenticated ? 'Yes' : 'No'}</p>
        <p>Auth Loading: {authLoading ? 'Yes' : 'No'}</p>
        <p>User: {user ? user.username : 'None'}</p>
      </div>

      <div style={{ marginBottom: '20px', padding: '10px', border: '1px solid #ccc' }}>
        <h2>Game Context Status</h2>
        <p>Game Loading: {gameLoading ? 'Yes' : 'No'}</p>
        <p>Game Error: {gameError || 'None'}</p>
        <p>Player State: {playerState ? `${playerState.username} (${playerState.credits} credits)` : 'Not loaded'}</p>
        <p>Current Ship: {currentShip ? currentShip.name : 'Not loaded'}</p>
      </div>

      <div style={{ marginBottom: '20px', padding: '10px', border: '1px solid #ccc' }}>
        <h2>Test Results</h2>
        {testResults.map((result, index) => (
          <div key={index} style={{ 
            marginBottom: '10px', 
            padding: '10px', 
            backgroundColor: result.result === 'PASS' ? '#e6ffe6' : '#ffe6e6' 
          }}>
            <h3>{result.test}: {result.result}</h3>
            <pre>{JSON.stringify(result.details, null, 2)}</pre>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TestAuthPage;