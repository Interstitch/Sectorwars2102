import React, { useState, useEffect, useMemo } from 'react';
import './combat-analytics.css';

interface CombatStats {
  totalBattles: number;
  victories: number;
  defeats: number;
  draws: number;
  totalDamageDealt: number;
  totalDamageReceived: number;
  totalDronesDeployed: number;
  totalDronesLost: number;
  averageBattleDuration: number;
  favoriteTarget: string;
  mostDamagingWeapon: string;
  killDeathRatio: number;
}

interface WeaponStats {
  weaponType: string;
  shotsFirered: number;
  hits: number;
  misses: number;
  accuracy: number;
  totalDamage: number;
  criticalHits: number;
}

interface TimeBasedMetric {
  timestamp: string;
  value: number;
}

interface CombatAnalyticsProps {
  playerId: string;
  shipId?: string;
  timeRange?: 'day' | 'week' | 'month' | 'all';
  onExport?: (data: any) => void;
}

const CombatAnalytics: React.FC<CombatAnalyticsProps> = ({
  playerId,
  shipId,
  timeRange = 'week',
  onExport
}) => {
  const [stats, setStats] = useState<CombatStats | null>(null);
  const [weaponStats, setWeaponStats] = useState<WeaponStats[]>([]);
  const [performanceHistory, setPerformanceHistory] = useState<TimeBasedMetric[]>([]);
  const [selectedMetric, setSelectedMetric] = useState<'winRate' | 'damage' | 'efficiency'>('winRate');
  const [isLoading, setIsLoading] = useState(true);

  // Load combat statistics from API
  useEffect(() => {
    const loadStats = async () => {
      setIsLoading(true);
      try {
        // Attempt to fetch combat stats from the API
        const token = localStorage.getItem('accessToken');
        const baseUrl = import.meta.env.VITE_API_URL || window.location.origin;
        const headers: Record<string, string> = { 'Content-Type': 'application/json' };
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }

        const response = await fetch(`${baseUrl}/api/v1/combat/stats?player_id=${playerId}&time_range=${timeRange}`, { headers });

        if (response.ok) {
          const data = await response.json();
          if (data && data.totalBattles > 0) {
            setStats(data);
            setWeaponStats(data.weaponStats || []);
            setPerformanceHistory(data.performanceHistory || []);
          } else {
            // API returned but no combat data
            setStats(null);
            setWeaponStats([]);
            setPerformanceHistory([]);
          }
        } else {
          // API endpoint not available or returned error - show empty state
          console.warn('Combat stats endpoint not available:', response.status);
          setStats(null);
          setWeaponStats([]);
          setPerformanceHistory([]);
        }
      } catch (error) {
        console.error('Failed to load combat statistics:', error);
        setStats(null);
        setWeaponStats([]);
        setPerformanceHistory([]);
      } finally {
        setIsLoading(false);
      }
    };

    loadStats();
  }, [playerId, shipId, timeRange]);

  // Calculate derived metrics
  const derivedMetrics = useMemo(() => {
    if (!stats) return null;

    return {
      winRate: (stats.victories / stats.totalBattles) * 100,
      avgDamagePerBattle: stats.totalDamageDealt / stats.totalBattles,
      avgDamageTaken: stats.totalDamageReceived / stats.totalBattles,
      damageEfficiency: (stats.totalDamageDealt / stats.totalDamageReceived) * 100,
      droneEfficiency: ((stats.totalDronesDeployed - stats.totalDronesLost) / stats.totalDronesDeployed) * 100,
      battlesPerDay: stats.totalBattles / (timeRange === 'day' ? 1 : timeRange === 'week' ? 7 : timeRange === 'month' ? 30 : 365)
    };
  }, [stats, timeRange]);

  const exportData = () => {
    const exportPayload = {
      stats,
      weaponStats,
      performanceHistory,
      derivedMetrics,
      exportDate: new Date().toISOString(),
      timeRange
    };

    if (onExport) {
      onExport(exportPayload);
    } else {
      // Default export to JSON file
      const blob = new Blob([JSON.stringify(exportPayload, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `combat-analytics-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  if (isLoading) {
    return (
      <div className="combat-analytics loading">
        <div className="loading-spinner">Loading combat analytics...</div>
      </div>
    );
  }

  if (!stats || !derivedMetrics) {
    return (
      <div className="combat-analytics no-data">
        <h3>Combat Analytics</h3>
        <p>No combat data available yet. Engage in combat to see your statistics here.</p>
      </div>
    );
  }

  return (
    <div className="combat-analytics">
      <div className="analytics-header">
        <h3>Combat Analytics</h3>
        <div className="header-controls">
          <select 
            className="time-range-selector"
            value={timeRange}
            onChange={(e) => window.location.reload()} // In real app, would update timeRange prop
          >
            <option value="day">Last 24 Hours</option>
            <option value="week">Last Week</option>
            <option value="month">Last Month</option>
            <option value="all">All Time</option>
          </select>
          <button className="export-btn" onClick={exportData}>
            Export Data
          </button>
        </div>
      </div>

      <div className="overview-cards">
        <div className="stat-card primary">
          <h4>Win Rate</h4>
          <div className="stat-value">{derivedMetrics.winRate.toFixed(1)}%</div>
          <div className="stat-breakdown">
            {stats.victories}W - {stats.defeats}L - {stats.draws}D
          </div>
        </div>

        <div className="stat-card">
          <h4>K/D Ratio</h4>
          <div className="stat-value">{stats.killDeathRatio.toFixed(2)}</div>
          <div className="stat-subtitle">Kill/Death Ratio</div>
        </div>

        <div className="stat-card">
          <h4>Damage Efficiency</h4>
          <div className="stat-value">{derivedMetrics.damageEfficiency.toFixed(0)}%</div>
          <div className="stat-subtitle">Dealt vs Received</div>
        </div>

        <div className="stat-card">
          <h4>Battles/Day</h4>
          <div className="stat-value">{derivedMetrics.battlesPerDay.toFixed(1)}</div>
          <div className="stat-subtitle">Average Activity</div>
        </div>
      </div>

      <div className="detailed-stats">
        <div className="combat-performance">
          <h4>Combat Performance</h4>
          <div className="performance-metrics">
            <div className="metric-row">
              <span className="metric-label">Total Battles:</span>
              <span className="metric-value">{stats.totalBattles}</span>
            </div>
            <div className="metric-row">
              <span className="metric-label">Average Battle Duration:</span>
              <span className="metric-value">{stats.averageBattleDuration.toFixed(1)} min</span>
            </div>
            <div className="metric-row">
              <span className="metric-label">Total Damage Dealt:</span>
              <span className="metric-value">{stats.totalDamageDealt.toLocaleString()}</span>
            </div>
            <div className="metric-row">
              <span className="metric-label">Total Damage Received:</span>
              <span className="metric-value">{stats.totalDamageReceived.toLocaleString()}</span>
            </div>
            <div className="metric-row">
              <span className="metric-label">Avg Damage per Battle:</span>
              <span className="metric-value">{derivedMetrics.avgDamagePerBattle.toFixed(0)}</span>
            </div>
            <div className="metric-row">
              <span className="metric-label">Favorite Target:</span>
              <span className="metric-value">{stats.favoriteTarget}</span>
            </div>
          </div>
        </div>

        <div className="drone-performance">
          <h4>Drone Performance</h4>
          <div className="performance-metrics">
            <div className="metric-row">
              <span className="metric-label">Total Deployed:</span>
              <span className="metric-value">{stats.totalDronesDeployed}</span>
            </div>
            <div className="metric-row">
              <span className="metric-label">Total Lost:</span>
              <span className="metric-value">{stats.totalDronesLost}</span>
            </div>
            <div className="metric-row">
              <span className="metric-label">Survival Rate:</span>
              <span className="metric-value">{derivedMetrics.droneEfficiency.toFixed(1)}%</span>
            </div>
          </div>
        </div>
      </div>

      <div className="weapon-statistics">
        <h4>Weapon Performance</h4>
        <div className="weapon-stats-grid">
          {weaponStats.map((weapon, index) => (
            <div key={index} className="weapon-card">
              <h5>{weapon.weaponType}</h5>
              <div className="weapon-metrics">
                <div className="accuracy-display">
                  <div className="accuracy-ring">
                    <svg viewBox="0 0 100 100">
                      <circle
                        cx="50"
                        cy="50"
                        r="40"
                        fill="none"
                        stroke="rgba(255,255,255,0.1)"
                        strokeWidth="8"
                      />
                      <circle
                        cx="50"
                        cy="50"
                        r="40"
                        fill="none"
                        stroke="#4a9eff"
                        strokeWidth="8"
                        strokeDasharray={`${weapon.accuracy * 2.51} 251`}
                        strokeDashoffset="0"
                        transform="rotate(-90 50 50)"
                      />
                    </svg>
                    <div className="accuracy-value">{weapon.accuracy.toFixed(0)}%</div>
                  </div>
                  <span className="accuracy-label">Accuracy</span>
                </div>
                <div className="weapon-details">
                  <div className="detail-row">
                    <span>Shots:</span>
                    <span>{weapon.shotsFirered}</span>
                  </div>
                  <div className="detail-row">
                    <span>Hits:</span>
                    <span>{weapon.hits}</span>
                  </div>
                  <div className="detail-row">
                    <span>Damage:</span>
                    <span>{weapon.totalDamage.toLocaleString()}</span>
                  </div>
                  <div className="detail-row">
                    <span>Crits:</span>
                    <span>{weapon.criticalHits}</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="performance-chart">
        <h4>Performance Trend</h4>
        <div className="chart-controls">
          <button 
            className={`metric-btn ${selectedMetric === 'winRate' ? 'active' : ''}`}
            onClick={() => setSelectedMetric('winRate')}
          >
            Win Rate
          </button>
          <button 
            className={`metric-btn ${selectedMetric === 'damage' ? 'active' : ''}`}
            onClick={() => setSelectedMetric('damage')}
          >
            Damage
          </button>
          <button 
            className={`metric-btn ${selectedMetric === 'efficiency' ? 'active' : ''}`}
            onClick={() => setSelectedMetric('efficiency')}
          >
            Efficiency
          </button>
        </div>
        <div className="chart-container">
          <div className="simple-chart">
            {performanceHistory.map((point, index) => (
              <div 
                key={index}
                className="chart-bar"
                style={{ 
                  height: `${point.value}%`,
                  backgroundColor: point.value > 70 ? '#44ff44' : 
                                   point.value > 40 ? '#ffaa44' : '#ff4444'
                }}
                title={`${new Date(point.timestamp).toLocaleDateString()}: ${point.value.toFixed(0)}%`}
              />
            ))}
          </div>
        </div>
      </div>

      <div className="insights-section">
        <h4>Combat Insights</h4>
        <div className="insights-grid">
          <div className="insight-card">
            <div className="insight-icon">🎯</div>
            <div className="insight-content">
              <h5>Targeting Preference</h5>
              <p>You primarily target {stats.favoriteTarget}, which has proven effective in {derivedMetrics.winRate.toFixed(0)}% of battles.</p>
            </div>
          </div>
          <div className="insight-card">
            <div className="insight-icon">⚔️</div>
            <div className="insight-content">
              <h5>Weapon Mastery</h5>
              <p>{stats.mostDamagingWeapon} is your most effective weapon, dealing {((234500 / stats.totalDamageDealt) * 100).toFixed(0)}% of total damage.</p>
            </div>
          </div>
          <div className="insight-card">
            <div className="insight-icon">🛡️</div>
            <div className="insight-content">
              <h5>Survival Skills</h5>
              <p>Your damage efficiency of {derivedMetrics.damageEfficiency.toFixed(0)}% shows {derivedMetrics.damageEfficiency > 100 ? 'excellent' : 'room for improvement in'} defensive tactics.</p>
            </div>
          </div>
          <div className="insight-card">
            <div className="insight-icon">🤖</div>
            <div className="insight-content">
              <h5>Drone Usage</h5>
              <p>With a {derivedMetrics.droneEfficiency.toFixed(0)}% drone survival rate, your drone deployment strategy is {derivedMetrics.droneEfficiency > 70 ? 'highly effective' : 'could be optimized'}.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CombatAnalytics;