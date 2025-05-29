import React, { useState, useEffect, useCallback } from 'react';
import { useAIUpdates } from '../../contexts/WebSocketContext';
import './player-behavior-analytics.css';

interface PlayerProfile {
  playerId: string;
  playerName: string;
  behaviorType: 'aggressive' | 'balanced' | 'conservative' | 'opportunistic' | 'explorer';
  tradingPattern: 'bulk_trader' | 'arbitrage_specialist' | 'route_optimizer' | 'market_manipulator' | 'casual';
  combatStyle: 'hunter' | 'defender' | 'opportunist' | 'avoider';
  activityLevel: 'very_active' | 'active' | 'moderate' | 'casual' | 'inactive';
  riskTolerance: number; // 0-100
  aiEngagement: number; // 0-100
  profitEfficiency: number; // percentage
  combatEffectiveness: number; // percentage
  explorationScore: number; // 0-100
  teamworkScore: number; // 0-100
  predictedActions: string[];
  recommendedInterventions: string[];
  lastUpdated: string;
}

interface BehaviorTrend {
  metric: string;
  current: number;
  previous: number;
  change: number;
  trend: 'increasing' | 'stable' | 'decreasing';
}

interface PlayerSegment {
  name: string;
  count: number;
  percentage: number;
  avgEngagement: number;
  avgRevenue: number;
  characteristics: string[];
}

export const PlayerBehaviorAnalytics: React.FC = () => {
  const [profiles, setProfiles] = useState<PlayerProfile[]>([]);
  const [selectedPlayer, setSelectedPlayer] = useState<PlayerProfile | null>(null);
  const [segments, setSegments] = useState<PlayerSegment[]>([]);
  const [trends, setTrends] = useState<BehaviorTrend[]>([]);
  const [filterBehavior, setFilterBehavior] = useState<string>('all');
  const [filterActivity, setFilterActivity] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleProfileUpdate = useCallback((data: any) => {
    console.log('Player profile update received:', data);
    setProfiles(prev => {
      const updated = [...prev];
      const index = updated.findIndex(p => p.playerId === data.playerId);
      if (index >= 0) {
        updated[index] = data;
      } else {
        updated.push(data);
      }
      return updated.sort((a, b) => b.aiEngagement - a.aiEngagement);
    });
  }, []);

  const handleSegmentUpdate = useCallback((data: any) => {
    console.log('Segment update received:', data);
    setSegments(data);
  }, []);

  const handleTrendUpdate = useCallback((data: any) => {
    console.log('Trend update received:', data);
    setTrends(data);
  }, []);

  useAIUpdates(undefined, undefined, undefined, handleProfileUpdate, undefined, undefined, undefined, undefined, handleSegmentUpdate, handleTrendUpdate);

  useEffect(() => {
    fetchPlayerProfiles();
    fetchSegments();
    fetchTrends();
  }, [filterBehavior, filterActivity]);

  const fetchPlayerProfiles = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filterBehavior !== 'all') params.append('behavior', filterBehavior);
      if (filterActivity !== 'all') params.append('activity', filterActivity);
      
      const response = await fetch(`/api/ai/behavior/profiles?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) throw new Error('Failed to fetch player profiles');
      
      const data = await response.json();
      setProfiles(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load profiles');
    } finally {
      setLoading(false);
    }
  };

  const fetchSegments = async () => {
    try {
      const response = await fetch('/api/ai/behavior/segments', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) throw new Error('Failed to fetch segments');
      
      const data = await response.json();
      setSegments(data);
    } catch (err) {
      console.error('Failed to load segments:', err);
    }
  };

  const fetchTrends = async () => {
    try {
      const response = await fetch('/api/ai/behavior/trends', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) throw new Error('Failed to fetch trends');
      
      const data = await response.json();
      setTrends(data);
    } catch (err) {
      console.error('Failed to load trends:', err);
    }
  };

  const getBehaviorIcon = (type: string) => {
    const icons: { [key: string]: string } = {
      aggressive: '⚔️',
      balanced: '⚖️',
      conservative: '🛡️',
      opportunistic: '🎯',
      explorer: '🧭'
    };
    return icons[type] || '❓';
  };

  const getActivityColor = (level: string) => {
    const colors: { [key: string]: string } = {
      very_active: '#4caf50',
      active: '#8bc34a',
      moderate: '#ffc107',
      casual: '#ff9800',
      inactive: '#f44336'
    };
    return colors[level] || '#999';
  };

  if (loading) return <div className="loading">Loading behavior analytics...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="player-behavior-analytics">
      <div className="analytics-header">
        <div className="segment-overview">
          <h3>Player Segments</h3>
          <div className="segments-grid">
            {segments.map(segment => (
              <div key={segment.name} className="segment-card">
                <h4>{segment.name}</h4>
                <div className="segment-stats">
                  <div className="segment-stat">
                    <span className="stat-value">{segment.count}</span>
                    <span className="stat-label">Players</span>
                  </div>
                  <div className="segment-stat">
                    <span className="stat-value">{segment.percentage.toFixed(1)}%</span>
                    <span className="stat-label">of Total</span>
                  </div>
                  <div className="segment-stat">
                    <span className="stat-value">{segment.avgEngagement.toFixed(0)}%</span>
                    <span className="stat-label">Engagement</span>
                  </div>
                </div>
                <div className="segment-characteristics">
                  {segment.characteristics.slice(0, 2).map((char, i) => (
                    <span key={i} className="characteristic">{char}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="behavior-trends">
          <h3>Behavior Trends</h3>
          <div className="trends-list">
            {trends.map(trend => (
              <div key={trend.metric} className="trend-item">
                <span className="trend-metric">{trend.metric}</span>
                <div className="trend-values">
                  <span className="trend-current">{trend.current.toFixed(1)}</span>
                  <span className={`trend-change ${trend.trend}`}>
                    {trend.change > 0 ? '+' : ''}{trend.change.toFixed(1)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="analytics-filters">
        <div className="filter-group">
          <label>Behavior Type:</label>
          <select value={filterBehavior} onChange={(e) => setFilterBehavior(e.target.value)}>
            <option value="all">All Types</option>
            <option value="aggressive">Aggressive</option>
            <option value="balanced">Balanced</option>
            <option value="conservative">Conservative</option>
            <option value="opportunistic">Opportunistic</option>
            <option value="explorer">Explorer</option>
          </select>
        </div>
        <div className="filter-group">
          <label>Activity Level:</label>
          <select value={filterActivity} onChange={(e) => setFilterActivity(e.target.value)}>
            <option value="all">All Levels</option>
            <option value="very_active">Very Active</option>
            <option value="active">Active</option>
            <option value="moderate">Moderate</option>
            <option value="casual">Casual</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </div>

      <div className="profiles-grid">
        <div className="profiles-list">
          <h3>Player Behavior Profiles</h3>
          <div className="profiles-table">
            <table>
              <thead>
                <tr>
                  <th>Player</th>
                  <th>Behavior</th>
                  <th>Trading</th>
                  <th>Activity</th>
                  <th>AI Engagement</th>
                  <th>Risk Tolerance</th>
                  <th>Efficiency</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {profiles.map(profile => (
                  <tr key={profile.playerId}>
                    <td>{profile.playerName}</td>
                    <td>
                      <span className="behavior-type">
                        {getBehaviorIcon(profile.behaviorType)} {profile.behaviorType}
                      </span>
                    </td>
                    <td className="trading-pattern">{profile.tradingPattern.replace(/_/g, ' ')}</td>
                    <td>
                      <span 
                        className="activity-badge"
                        style={{ backgroundColor: getActivityColor(profile.activityLevel) }}
                      >
                        {profile.activityLevel.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td>
                      <div className="engagement-bar">
                        <div 
                          className="engagement-fill"
                          style={{ width: `${profile.aiEngagement}%` }}
                        />
                        <span className="engagement-value">{profile.aiEngagement}%</span>
                      </div>
                    </td>
                    <td>
                      <div className="risk-indicator">
                        <div 
                          className="risk-fill"
                          style={{ 
                            width: `${profile.riskTolerance}%`,
                            backgroundColor: profile.riskTolerance > 70 ? '#f44336' : 
                                           profile.riskTolerance > 40 ? '#ff9800' : '#4caf50'
                          }}
                        />
                        <span className="risk-value">{profile.riskTolerance}%</span>
                      </div>
                    </td>
                    <td>{profile.profitEfficiency.toFixed(1)}%</td>
                    <td>
                      <button 
                        className="detail-button"
                        onClick={() => setSelectedPlayer(profile)}
                      >
                        Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {selectedPlayer && (
          <div className="player-detail-panel">
            <div className="panel-header">
              <h3>{selectedPlayer.playerName}</h3>
              <button 
                className="close-button"
                onClick={() => setSelectedPlayer(null)}
              >
                ×
              </button>
            </div>
            
            <div className="panel-content">
              <div className="behavior-summary">
                <div className="behavior-badge">
                  {getBehaviorIcon(selectedPlayer.behaviorType)}
                  <span>{selectedPlayer.behaviorType}</span>
                </div>
                <div className="combat-style">
                  Combat: {selectedPlayer.combatStyle}
                </div>
              </div>

              <div className="metrics-grid">
                <div className="metric-card">
                  <label>AI Engagement</label>
                  <div className="metric-bar">
                    <div 
                      className="metric-fill"
                      style={{ width: `${selectedPlayer.aiEngagement}%` }}
                    />
                  </div>
                  <span>{selectedPlayer.aiEngagement}%</span>
                </div>
                <div className="metric-card">
                  <label>Combat Effectiveness</label>
                  <div className="metric-bar">
                    <div 
                      className="metric-fill"
                      style={{ width: `${selectedPlayer.combatEffectiveness}%` }}
                    />
                  </div>
                  <span>{selectedPlayer.combatEffectiveness}%</span>
                </div>
                <div className="metric-card">
                  <label>Exploration Score</label>
                  <div className="metric-bar">
                    <div 
                      className="metric-fill"
                      style={{ width: `${selectedPlayer.explorationScore}%` }}
                    />
                  </div>
                  <span>{selectedPlayer.explorationScore}%</span>
                </div>
                <div className="metric-card">
                  <label>Teamwork Score</label>
                  <div className="metric-bar">
                    <div 
                      className="metric-fill"
                      style={{ width: `${selectedPlayer.teamworkScore}%` }}
                    />
                  </div>
                  <span>{selectedPlayer.teamworkScore}%</span>
                </div>
              </div>

              <div className="predictions-section">
                <h4>Predicted Actions</h4>
                <ul>
                  {selectedPlayer.predictedActions.map((action, i) => (
                    <li key={i}>{action}</li>
                  ))}
                </ul>
              </div>

              <div className="interventions-section">
                <h4>Recommended Interventions</h4>
                <ul>
                  {selectedPlayer.recommendedInterventions.map((intervention, i) => (
                    <li key={i}>{intervention}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};