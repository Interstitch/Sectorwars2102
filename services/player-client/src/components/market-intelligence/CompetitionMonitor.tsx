import React, { useState, useEffect, useMemo } from 'react';
import { gameAPI } from '../../services/api';
import './competition-monitor.css';

interface Competitor {
  playerId: string;
  username: string;
  teamId?: string;
  teamName?: string;
  currentSector: number;
  shipType: string;
  lastActivity: string;
  tradingStats: {
    profitLast24h: number;
    tradesLast24h: number;
    avgProfitPerTrade: number;
    favoriteResource: string;
    favoriteRoute: string;
  };
  competitionScore: number;
  threatLevel: 'low' | 'medium' | 'high';
  isOnline: boolean;
}

interface MarketDominance {
  resource: 'fuel' | 'organics' | 'equipment';
  stationId: string;
  stationName: string;
  dominantTrader: {
    playerId: string;
    username: string;
    marketShare: number; // percentage
  };
  topTraders: {
    playerId: string;
    username: string;
    marketShare: number;
    profitShare: number;
  }[];
}

interface CompetitionInsight {
  type: 'opportunity' | 'threat' | 'trend';
  priority: 'low' | 'medium' | 'high';
  title: string;
  description: string;
  actionable: boolean;
  suggestedAction?: string;
  relatedCompetitors: string[];
  estimatedImpact?: number;
}

interface CompetitionMonitorProps {
  currentPlayerId: string;
  currentSectorId: number;
  onCompetitorSelect?: (competitor: Competitor) => void;
  onInsightAction?: (insight: CompetitionInsight) => void;
}

const CompetitionMonitor: React.FC<CompetitionMonitorProps> = ({
  currentPlayerId,
  currentSectorId,
  onCompetitorSelect,
  onInsightAction
}) => {
  const [competitors, setCompetitors] = useState<Competitor[]>([]);
  const [marketDominance, setMarketDominance] = useState<MarketDominance[]>([]);
  const [insights, setInsights] = useState<CompetitionInsight[]>([]);
  const [viewMode, setViewMode] = useState<'competitors' | 'dominance' | 'insights'>('competitors');
  const [filterMode, setFilterMode] = useState<'all' | 'sector' | 'team' | 'threats'>('all');
  const [sortBy, setSortBy] = useState<'score' | 'profit' | 'activity' | 'threat'>('score');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch competition data
  useEffect(() => {
    const fetchCompetitionData = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const response = await gameAPI.trading.getCompetitionAnalysis({
          playerId: currentPlayerId,
          sectorId: currentSectorId,
          includeMarketDominance: true,
          includeInsights: true
        });
        
        setCompetitors(response.competitors || []);
        setMarketDominance(response.marketDominance || []);
        setInsights(response.insights || []);
      } catch (err) {
        setError('Failed to load competition data. Please try again.');
        console.error('Competition data fetch error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCompetitionData();
    const interval = setInterval(fetchCompetitionData, 60000); // Refresh every minute
    
    return () => clearInterval(interval);
  }, [currentPlayerId, currentSectorId]);

  // Filter and sort competitors
  const filteredCompetitors = useMemo(() => {
    let filtered = [...competitors];
    
    switch (filterMode) {
      case 'sector':
        filtered = filtered.filter(c => c.currentSector === currentSectorId);
        break;
      case 'team':
        filtered = filtered.filter(c => c.teamId);
        break;
      case 'threats':
        filtered = filtered.filter(c => c.threatLevel !== 'low');
        break;
    }
    
    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'score':
          return b.competitionScore - a.competitionScore;
        case 'profit':
          return b.tradingStats.profitLast24h - a.tradingStats.profitLast24h;
        case 'activity':
          return new Date(b.lastActivity).getTime() - new Date(a.lastActivity).getTime();
        case 'threat':
          const threatOrder = { high: 3, medium: 2, low: 1 };
          return threatOrder[b.threatLevel] - threatOrder[a.threatLevel];
        default:
          return 0;
      }
    });
    
    return filtered;
  }, [competitors, filterMode, sortBy, currentSectorId]);

  // Calculate competition statistics
  const competitionStats = useMemo(() => {
    if (competitors.length === 0) return null;
    
    const totalProfit = competitors.reduce((sum, c) => sum + c.tradingStats.profitLast24h, 0);
    const avgProfit = totalProfit / competitors.length;
    const onlineCount = competitors.filter(c => c.isOnline).length;
    const highThreatCount = competitors.filter(c => c.threatLevel === 'high').length;
    
    return {
      totalCompetitors: competitors.length,
      onlineCompetitors: onlineCount,
      avgProfitPerTrader: avgProfit,
      highThreats: highThreatCount,
      marketActivity: competitors.reduce((sum, c) => sum + c.tradingStats.tradesLast24h, 0)
    };
  }, [competitors]);

  const getThreatColor = (threat: string) => {
    switch (threat) {
      case 'low': return '#44ff44';
      case 'medium': return '#ffaa44';
      case 'high': return '#ff4444';
      default: return '#888';
    }
  };

  const getResourceIcon = (resource: string) => {
    switch (resource) {
      case 'fuel': return '⛽';
      case 'organics': return '🌿';
      case 'equipment': return '⚙️';
      default: return '📦';
    }
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'opportunity': return '💡';
      case 'threat': return '⚠️';
      case 'trend': return '📊';
      default: return '📌';
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  if (isLoading) {
    return (
      <div className="competition-monitor loading">
        <div className="loading-spinner">Analyzing competition...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="competition-monitor error">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  return (
    <div className="competition-monitor">
      <div className="monitor-header">
        <h3>Competition Monitor</h3>
        {competitionStats && (
          <div className="competition-summary">
            <span className="summary-stat">
              <span className="stat-value">{competitionStats.totalCompetitors}</span>
              <span className="stat-label">Traders</span>
            </span>
            <span className="summary-stat online">
              <span className="stat-value">{competitionStats.onlineCompetitors}</span>
              <span className="stat-label">Online</span>
            </span>
            <span className="summary-stat threats">
              <span className="stat-value">{competitionStats.highThreats}</span>
              <span className="stat-label">Threats</span>
            </span>
          </div>
        )}
      </div>

      <div className="monitor-controls">
        <div className="view-tabs">
          {(['competitors', 'dominance', 'insights'] as const).map(mode => (
            <button
              key={mode}
              className={`view-tab ${viewMode === mode ? 'active' : ''}`}
              onClick={() => setViewMode(mode)}
            >
              {mode.charAt(0).toUpperCase() + mode.slice(1)}
            </button>
          ))}
        </div>

        {viewMode === 'competitors' && (
          <div className="filter-controls">
            <div className="filter-buttons">
              {(['all', 'sector', 'team', 'threats'] as const).map(filter => (
                <button
                  key={filter}
                  className={`filter-btn ${filterMode === filter ? 'active' : ''}`}
                  onClick={() => setFilterMode(filter)}
                >
                  {filter.charAt(0).toUpperCase() + filter.slice(1)}
                </button>
              ))}
            </div>
            
            <select 
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
              className="sort-select"
            >
              <option value="score">Competition Score</option>
              <option value="profit">24h Profit</option>
              <option value="activity">Last Activity</option>
              <option value="threat">Threat Level</option>
            </select>
          </div>
        )}
      </div>

      {viewMode === 'competitors' && (
        <div className="competitors-grid">
          {filteredCompetitors.map(competitor => (
            <div 
              key={competitor.playerId}
              className="competitor-card"
              onClick={() => onCompetitorSelect?.(competitor)}
            >
              <div className="competitor-header">
                <div className="competitor-info">
                  <h4>{competitor.username}</h4>
                  {competitor.teamName && (
                    <span className="team-badge">{competitor.teamName}</span>
                  )}
                </div>
                <div className="competitor-status">
                  <span 
                    className={`online-indicator ${competitor.isOnline ? 'online' : 'offline'}`}
                  />
                  <span 
                    className="threat-level"
                    style={{ color: getThreatColor(competitor.threatLevel) }}
                  >
                    {competitor.threatLevel.toUpperCase()}
                  </span>
                </div>
              </div>

              <div className="competitor-details">
                <div className="detail-row">
                  <span className="detail-label">Ship:</span>
                  <span className="detail-value">{competitor.shipType}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Sector:</span>
                  <span className="detail-value">#{competitor.currentSector}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Last Seen:</span>
                  <span className="detail-value">{formatTime(competitor.lastActivity)}</span>
                </div>
              </div>

              <div className="trading-stats">
                <h5>24h Trading Stats</h5>
                <div className="stats-grid">
                  <div className="stat">
                    <span className="stat-label">Profit:</span>
                    <span className="stat-value profit">
                      {competitor.tradingStats.profitLast24h.toLocaleString()} cr
                    </span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Trades:</span>
                    <span className="stat-value">{competitor.tradingStats.tradesLast24h}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Avg/Trade:</span>
                    <span className="stat-value">
                      {competitor.tradingStats.avgProfitPerTrade.toLocaleString()} cr
                    </span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Focus:</span>
                    <span className="stat-value">
                      {getResourceIcon(competitor.tradingStats.favoriteResource)} 
                      {competitor.tradingStats.favoriteResource}
                    </span>
                  </div>
                </div>
              </div>

              <div className="competition-score">
                <div className="score-label">Competition Score</div>
                <div className="score-bar">
                  <div 
                    className="score-fill"
                    style={{ width: `${competitor.competitionScore}%` }}
                  />
                  <span className="score-value">{competitor.competitionScore}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {viewMode === 'dominance' && (
        <div className="market-dominance">
          {marketDominance.map((market, index) => (
            <div key={index} className="dominance-card">
              <div className="dominance-header">
                <h4>{market.stationName}</h4>
                <span className="resource-badge">
                  {getResourceIcon(market.resource)} {market.resource.toUpperCase()}
                </span>
              </div>

              <div className="dominant-trader">
                <h5>Market Leader</h5>
                <div className="trader-info">
                  <span className="trader-name">{market.dominantTrader.username}</span>
                  <span className="market-share">
                    {market.dominantTrader.marketShare.toFixed(1)}% market share
                  </span>
                </div>
              </div>

              <div className="top-traders">
                <h5>Top Traders</h5>
                <div className="traders-list">
                  {market.topTraders.map((trader, idx) => (
                    <div key={idx} className="trader-row">
                      <span className="rank">#{idx + 1}</span>
                      <span className="name">{trader.username}</span>
                      <span className="share">{trader.marketShare.toFixed(1)}%</span>
                      <div className="share-bar">
                        <div 
                          className="share-fill"
                          style={{ width: `${trader.marketShare}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {viewMode === 'insights' && (
        <div className="competition-insights">
          {insights.map((insight, index) => (
            <div 
              key={index}
              className={`insight-card ${insight.priority}`}
              onClick={() => insight.actionable && onInsightAction?.(insight)}
            >
              <div className="insight-header">
                <span className="insight-icon">{getInsightIcon(insight.type)}</span>
                <h4>{insight.title}</h4>
                <span className={`priority-badge ${insight.priority}`}>
                  {insight.priority.toUpperCase()}
                </span>
              </div>

              <p className="insight-description">{insight.description}</p>

              {insight.suggestedAction && (
                <div className="suggested-action">
                  <strong>Suggested Action:</strong> {insight.suggestedAction}
                </div>
              )}

              {insight.estimatedImpact && (
                <div className="impact-estimate">
                  Potential Impact: {insight.estimatedImpact.toLocaleString()} cr
                </div>
              )}

              {insight.relatedCompetitors.length > 0 && (
                <div className="related-competitors">
                  <span>Related traders:</span>
                  {insight.relatedCompetitors.join(', ')}
                </div>
              )}

              {insight.actionable && (
                <button className="action-btn">Take Action</button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CompetitionMonitor;