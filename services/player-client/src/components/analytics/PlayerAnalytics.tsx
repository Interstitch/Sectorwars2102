import React, { useState, useEffect, useMemo } from 'react';
import { gameAPI } from '../../services/api';
import './player-analytics.css';

interface PerformanceMetrics {
  overall: {
    totalPlaytime: number; // hours
    creditsEarned: number;
    creditsSpent: number;
    netWorth: number;
    rank: number;
    percentile: number;
  };
  combat: {
    totalBattles: number;
    victories: number;
    defeats: number;
    winRate: number;
    killDeathRatio: number;
    averageDamageDealt: number;
    favoriteWeapon: string;
    dronesDestroyed: number;
  };
  trading: {
    totalTrades: number;
    totalProfit: number;
    averageProfitPerTrade: number;
    bestTrade: {
      profit: number;
      resource: string;
      route: string;
      date: string;
    };
    favoriteResource: string;
    tradingEfficiency: number;
  };
  exploration: {
    sectorsVisited: number;
    sectorsDiscovered: number;
    planetsColonized: number;
    portsVisited: number;
    tunnelsUsed: number;
    totalDistance: number;
  };
  social: {
    teamContributions: number;
    messagesLent: number;
    alliancesFormed: number;
    reputation: Record<string, number>;
    helpfulnessScore: number;
  };
}

interface TimeSeriesData {
  timestamp: string;
  credits: number;
  rank: number;
  combatPower: number;
  tradingVolume: number;
}

interface SkillAssessment {
  category: string;
  level: number; // 0-100
  trend: 'improving' | 'stable' | 'declining';
  recommendations: string[];
}

interface PlayerAnalyticsProps {
  playerId: string;
  onMetricSelect?: (metric: string, data: any) => void;
}

const PlayerAnalytics: React.FC<PlayerAnalyticsProps> = ({
  playerId,
  onMetricSelect
}) => {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [timeSeriesData, setTimeSeriesData] = useState<TimeSeriesData[]>([]);
  const [skillAssessments, setSkillAssessments] = useState<SkillAssessment[]>([]);
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d' | 'all'>('7d');
  const [selectedCategory, setSelectedCategory] = useState<'overview' | 'combat' | 'trading' | 'exploration' | 'social'>('overview');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch analytics data
  useEffect(() => {
    const fetchAnalytics = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const response = await gameAPI.player.getAnalytics(playerId, {
          timeRange,
          includeTimeSeries: true,
          includeSkillAssessment: true
        });
        
        setMetrics(response.metrics);
        setTimeSeriesData(response.timeSeries || []);
        setSkillAssessments(response.skillAssessments || []);
      } catch (err) {
        setError('Failed to load analytics data. Please try again.');
        console.error('Analytics fetch error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnalytics();
  }, [playerId, timeRange]);

  // Calculate growth rates
  const growthRates = useMemo(() => {
    if (timeSeriesData.length < 2) return null;
    
    const first = timeSeriesData[0];
    const last = timeSeriesData[timeSeriesData.length - 1];
    
    return {
      credits: ((last.credits - first.credits) / first.credits) * 100,
      rank: last.rank - first.rank,
      combatPower: ((last.combatPower - first.combatPower) / first.combatPower) * 100,
      tradingVolume: ((last.tradingVolume - first.tradingVolume) / first.tradingVolume) * 100
    };
  }, [timeSeriesData]);

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toLocaleString();
  };

  const formatPercentage = (value: number) => {
    const sign = value >= 0 ? '+' : '';
    return sign + value.toFixed(1) + '%';
  };

  const formatTime = (hours: number) => {
    if (hours < 24) return `${hours.toFixed(1)}h`;
    const days = Math.floor(hours / 24);
    const remainingHours = hours % 24;
    return `${days}d ${remainingHours.toFixed(0)}h`;
  };

  const getSkillColor = (level: number) => {
    if (level >= 80) return '#44ff44';
    if (level >= 60) return '#88ff88';
    if (level >= 40) return '#ffaa44';
    if (level >= 20) return '#ff8844';
    return '#ff4444';
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return '📈';
      case 'declining': return '📉';
      case 'stable': return '➡️';
      default: return '';
    }
  };

  // Render mini chart
  const MiniChart: React.FC<{ data: number[], color: string }> = ({ data, color }) => {
    if (data.length === 0) return null;
    
    const max = Math.max(...data);
    const min = Math.min(...data);
    const range = max - min || 1;
    
    return (
      <div className="mini-chart">
        <svg viewBox="0 0 100 40" preserveAspectRatio="none">
          <polyline
            fill="none"
            stroke={color}
            strokeWidth="2"
            points={
              data.map((value, index) => {
                const x = (index / (data.length - 1)) * 100;
                const y = 40 - ((value - min) / range) * 40;
                return `${x},${y}`;
              }).join(' ')
            }
          />
        </svg>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="player-analytics loading">
        <div className="loading-spinner">Loading analytics...</div>
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <div className="player-analytics error">
        <div className="error-message">{error || 'No data available'}</div>
      </div>
    );
  }

  return (
    <div className="player-analytics">
      <div className="analytics-header">
        <h3>Performance Analytics</h3>
        <div className="time-range-selector">
          {(['24h', '7d', '30d', 'all'] as const).map(range => (
            <button
              key={range}
              className={`range-btn ${timeRange === range ? 'active' : ''}`}
              onClick={() => setTimeRange(range)}
            >
              {range === 'all' ? 'All Time' : range}
            </button>
          ))}
        </div>
      </div>

      <div className="overall-stats">
        <div className="stat-card primary">
          <h4>Net Worth</h4>
          <div className="stat-value">{formatNumber(metrics.overall.netWorth)} cr</div>
          {growthRates && (
            <div className={`stat-change ${growthRates.credits >= 0 ? 'positive' : 'negative'}`}>
              {formatPercentage(growthRates.credits)}
            </div>
          )}
          <MiniChart 
            data={timeSeriesData.map(d => d.credits)} 
            color="#44ff44"
          />
        </div>

        <div className="stat-card">
          <h4>Rank</h4>
          <div className="stat-value">#{metrics.overall.rank}</div>
          <div className="stat-subtitle">Top {metrics.overall.percentile}%</div>
          {growthRates && growthRates.rank !== 0 && (
            <div className={`rank-change ${growthRates.rank < 0 ? 'positive' : 'negative'}`}>
              {growthRates.rank < 0 ? '↑' : '↓'} {Math.abs(growthRates.rank)}
            </div>
          )}
        </div>

        <div className="stat-card">
          <h4>Play Time</h4>
          <div className="stat-value">{formatTime(metrics.overall.totalPlaytime)}</div>
          <div className="stat-subtitle">
            {formatNumber(metrics.overall.creditsEarned / metrics.overall.totalPlaytime)} cr/hour
          </div>
        </div>

        <div className="stat-card">
          <h4>Efficiency</h4>
          <div className="stat-value">
            {((metrics.overall.creditsEarned - metrics.overall.creditsSpent) / metrics.overall.creditsEarned * 100).toFixed(1)}%
          </div>
          <div className="stat-subtitle">Profit margin</div>
        </div>
      </div>

      <div className="category-tabs">
        {(['overview', 'combat', 'trading', 'exploration', 'social'] as const).map(cat => (
          <button
            key={cat}
            className={`category-tab ${selectedCategory === cat ? 'active' : ''}`}
            onClick={() => setSelectedCategory(cat)}
          >
            {cat.charAt(0).toUpperCase() + cat.slice(1)}
          </button>
        ))}
      </div>

      <div className="category-content">
        {selectedCategory === 'overview' && (
          <div className="overview-content">
            <div className="skill-assessments">
              <h4>Skill Assessment</h4>
              <div className="skills-grid">
                {skillAssessments.map((skill, index) => (
                  <div key={index} className="skill-card">
                    <div className="skill-header">
                      <span className="skill-name">{skill.category}</span>
                      <span className="skill-trend">{getTrendIcon(skill.trend)}</span>
                    </div>
                    <div className="skill-bar">
                      <div 
                        className="skill-fill"
                        style={{ 
                          width: `${skill.level}%`,
                          backgroundColor: getSkillColor(skill.level)
                        }}
                      />
                      <span className="skill-level">{skill.level}/100</span>
                    </div>
                    {skill.recommendations.length > 0 && (
                      <div className="skill-recommendations">
                        <h5>Recommendations:</h5>
                        <ul>
                          {skill.recommendations.map((rec, idx) => (
                            <li key={idx}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="performance-summary">
              <h4>Performance Summary</h4>
              <div className="summary-grid">
                <div className="summary-item">
                  <span className="summary-label">Combat Win Rate</span>
                  <span className="summary-value">{metrics.combat.winRate.toFixed(1)}%</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Trading Efficiency</span>
                  <span className="summary-value">{metrics.trading.tradingEfficiency.toFixed(1)}%</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Sectors Explored</span>
                  <span className="summary-value">{metrics.exploration.sectorsVisited}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Team Contributions</span>
                  <span className="summary-value">{metrics.social.teamContributions}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {selectedCategory === 'combat' && (
          <div className="combat-stats">
            <div className="stats-row">
              <div className="stat-group">
                <h5>Battle Statistics</h5>
                <div className="stat-item">
                  <span>Total Battles:</span>
                  <span>{metrics.combat.totalBattles}</span>
                </div>
                <div className="stat-item">
                  <span>Victories:</span>
                  <span className="positive">{metrics.combat.victories}</span>
                </div>
                <div className="stat-item">
                  <span>Defeats:</span>
                  <span className="negative">{metrics.combat.defeats}</span>
                </div>
                <div className="stat-item">
                  <span>Win Rate:</span>
                  <span className={metrics.combat.winRate >= 50 ? 'positive' : 'negative'}>
                    {metrics.combat.winRate.toFixed(1)}%
                  </span>
                </div>
                <div className="stat-item">
                  <span>K/D Ratio:</span>
                  <span>{metrics.combat.killDeathRatio.toFixed(2)}</span>
                </div>
              </div>

              <div className="stat-group">
                <h5>Combat Performance</h5>
                <div className="stat-item">
                  <span>Avg Damage:</span>
                  <span>{formatNumber(metrics.combat.averageDamageDealt)}</span>
                </div>
                <div className="stat-item">
                  <span>Favorite Weapon:</span>
                  <span>{metrics.combat.favoriteWeapon}</span>
                </div>
                <div className="stat-item">
                  <span>Drones Destroyed:</span>
                  <span>{metrics.combat.dronesDestroyed}</span>
                </div>
              </div>
            </div>

            <div className="combat-chart">
              <h5>Combat Power Trend</h5>
              <MiniChart 
                data={timeSeriesData.map(d => d.combatPower)} 
                color="#ff4444"
              />
            </div>
          </div>
        )}

        {selectedCategory === 'trading' && (
          <div className="trading-stats">
            <div className="stats-row">
              <div className="stat-group">
                <h5>Trading Overview</h5>
                <div className="stat-item">
                  <span>Total Trades:</span>
                  <span>{metrics.trading.totalTrades}</span>
                </div>
                <div className="stat-item">
                  <span>Total Profit:</span>
                  <span className="positive">{formatNumber(metrics.trading.totalProfit)} cr</span>
                </div>
                <div className="stat-item">
                  <span>Avg per Trade:</span>
                  <span>{formatNumber(metrics.trading.averageProfitPerTrade)} cr</span>
                </div>
                <div className="stat-item">
                  <span>Favorite Resource:</span>
                  <span>{metrics.trading.favoriteResource}</span>
                </div>
                <div className="stat-item">
                  <span>Efficiency:</span>
                  <span>{metrics.trading.tradingEfficiency.toFixed(1)}%</span>
                </div>
              </div>

              <div className="stat-group">
                <h5>Best Trade</h5>
                <div className="best-trade-card">
                  <div className="trade-profit">{formatNumber(metrics.trading.bestTrade.profit)} cr</div>
                  <div className="trade-details">
                    <div>{metrics.trading.bestTrade.resource}</div>
                    <div>{metrics.trading.bestTrade.route}</div>
                    <div>{new Date(metrics.trading.bestTrade.date).toLocaleDateString()}</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="trading-chart">
              <h5>Trading Volume Trend</h5>
              <MiniChart 
                data={timeSeriesData.map(d => d.tradingVolume)} 
                color="#4a9eff"
              />
            </div>
          </div>
        )}

        {selectedCategory === 'exploration' && (
          <div className="exploration-stats">
            <div className="stats-grid">
              <div className="exploration-stat">
                <div className="stat-icon">🌍</div>
                <div className="stat-label">Sectors Visited</div>
                <div className="stat-value">{metrics.exploration.sectorsVisited}</div>
              </div>
              <div className="exploration-stat">
                <div className="stat-icon">🔍</div>
                <div className="stat-label">Sectors Discovered</div>
                <div className="stat-value">{metrics.exploration.sectorsDiscovered}</div>
              </div>
              <div className="exploration-stat">
                <div className="stat-icon">🏛️</div>
                <div className="stat-label">Planets Colonized</div>
                <div className="stat-value">{metrics.exploration.planetsColonized}</div>
              </div>
              <div className="exploration-stat">
                <div className="stat-icon">🚀</div>
                <div className="stat-label">Ports Visited</div>
                <div className="stat-value">{metrics.exploration.portsVisited}</div>
              </div>
              <div className="exploration-stat">
                <div className="stat-icon">🌌</div>
                <div className="stat-label">Tunnels Used</div>
                <div className="stat-value">{metrics.exploration.tunnelsUsed}</div>
              </div>
              <div className="exploration-stat">
                <div className="stat-icon">📏</div>
                <div className="stat-label">Total Distance</div>
                <div className="stat-value">{formatNumber(metrics.exploration.totalDistance)} sectors</div>
              </div>
            </div>
          </div>
        )}

        {selectedCategory === 'social' && (
          <div className="social-stats">
            <div className="social-overview">
              <div className="social-stat">
                <h5>Team Contributions</h5>
                <div className="stat-value">{metrics.social.teamContributions}</div>
              </div>
              <div className="social-stat">
                <h5>Messages Sent</h5>
                <div className="stat-value">{metrics.social.messagesLent}</div>
              </div>
              <div className="social-stat">
                <h5>Alliances Formed</h5>
                <div className="stat-value">{metrics.social.alliancesFormed}</div>
              </div>
              <div className="social-stat">
                <h5>Helpfulness Score</h5>
                <div className="stat-value">{metrics.social.helpfulnessScore}/100</div>
              </div>
            </div>

            <div className="reputation-section">
              <h5>Faction Reputation</h5>
              <div className="reputation-list">
                {Object.entries(metrics.social.reputation).map(([faction, rep]) => (
                  <div key={faction} className="reputation-item">
                    <span className="faction-name">{faction}</span>
                    <div className="reputation-bar">
                      <div 
                        className="reputation-fill"
                        style={{ 
                          width: `${Math.abs(rep)}%`,
                          backgroundColor: rep >= 0 ? '#44ff44' : '#ff4444'
                        }}
                      />
                    </div>
                    <span className={`reputation-value ${rep >= 0 ? 'positive' : 'negative'}`}>
                      {rep > 0 ? '+' : ''}{rep}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PlayerAnalytics;