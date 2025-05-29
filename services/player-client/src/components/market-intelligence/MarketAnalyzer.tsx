import React, { useState, useEffect, useMemo } from 'react';
import { gameAPI } from '../../services/api';
import { InputValidator } from '../../utils/security/inputValidation';
import './market-analyzer.css';

interface MarketData {
  portId: string;
  portName: string;
  sectorId: number;
  prices: {
    fuel: { buy: number; sell: number; stock: number };
    organics: { buy: number; sell: number; stock: number };
    equipment: { buy: number; sell: number; stock: number };
  };
  lastUpdate: string;
  volume24h: number;
  priceChange24h: {
    fuel: number;
    organics: number;
    equipment: number;
  };
}

interface MarketTrend {
  resource: 'fuel' | 'organics' | 'equipment';
  trend: 'up' | 'down' | 'stable';
  strength: number; // 0-100
  prediction: {
    price: number;
    confidence: number; // 0-100
    timeframe: string;
  };
}

interface MarketOpportunity {
  id: string;
  type: 'arbitrage' | 'supply_shortage' | 'demand_spike' | 'price_crash';
  resource: string;
  buyPort: string;
  sellPort: string;
  potentialProfit: number;
  risk: 'low' | 'medium' | 'high';
  expiresIn: number; // minutes
  description: string;
}

interface MarketAnalyzerProps {
  currentSectorId: number;
  playerCredits: number;
  cargoCapacity: number;
  onSelectOpportunity?: (opportunity: MarketOpportunity) => void;
}

const MarketAnalyzer: React.FC<MarketAnalyzerProps> = ({
  currentSectorId,
  playerCredits,
  cargoCapacity,
  onSelectOpportunity
}) => {
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [trends, setTrends] = useState<MarketTrend[]>([]);
  const [opportunities, setOpportunities] = useState<MarketOpportunity[]>([]);
  const [selectedResource, setSelectedResource] = useState<'all' | 'fuel' | 'organics' | 'equipment'>('all');
  const [analysisDepth, setAnalysisDepth] = useState<'local' | 'regional' | 'global'>('regional');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Fetch market data based on analysis depth
  useEffect(() => {
    const fetchMarketData = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        let response;
        switch (analysisDepth) {
          case 'local':
            response = await gameAPI.trading.getMarketData(currentSectorId, 3);
            break;
          case 'regional':
            response = await gameAPI.trading.getMarketData(currentSectorId, 10);
            break;
          case 'global':
            response = await gameAPI.trading.getMarketData(null, 50);
            break;
        }
        
        setMarketData(response.markets || []);
        setTrends(response.trends || []);
        setOpportunities(response.opportunities || []);
        setLastUpdate(new Date());
      } catch (err) {
        setError('Failed to load market data. Please try again.');
        console.error('Market data fetch error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMarketData();
    const interval = setInterval(fetchMarketData, 30000); // Refresh every 30 seconds
    
    return () => clearInterval(interval);
  }, [currentSectorId, analysisDepth]);

  // Calculate market statistics
  const marketStats = useMemo(() => {
    if (marketData.length === 0) return null;

    const stats = {
      avgPrices: {
        fuel: { buy: 0, sell: 0 },
        organics: { buy: 0, sell: 0 },
        equipment: { buy: 0, sell: 0 }
      },
      priceRanges: {
        fuel: { min: Infinity, max: -Infinity },
        organics: { min: Infinity, max: -Infinity },
        equipment: { min: Infinity, max: -Infinity }
      },
      totalVolume: 0,
      marketCount: marketData.length
    };

    marketData.forEach(market => {
      ['fuel', 'organics', 'equipment'].forEach(resource => {
        const res = resource as keyof typeof stats.avgPrices;
        stats.avgPrices[res].buy += market.prices[res].buy;
        stats.avgPrices[res].sell += market.prices[res].sell;
        stats.priceRanges[res].min = Math.min(stats.priceRanges[res].min, market.prices[res].sell);
        stats.priceRanges[res].max = Math.max(stats.priceRanges[res].max, market.prices[res].buy);
      });
      stats.totalVolume += market.volume24h;
    });

    // Calculate averages
    Object.keys(stats.avgPrices).forEach(resource => {
      const res = resource as keyof typeof stats.avgPrices;
      stats.avgPrices[res].buy /= marketData.length;
      stats.avgPrices[res].sell /= marketData.length;
    });

    return stats;
  }, [marketData]);

  // Filter opportunities based on player capabilities
  const viableOpportunities = useMemo(() => {
    return opportunities.filter(opp => {
      // Check if player has enough credits
      const estimatedCost = opp.potentialProfit * 0.3; // Rough estimate
      if (estimatedCost > playerCredits) return false;
      
      // Check if opportunity matches selected resource filter
      if (selectedResource !== 'all' && opp.resource !== selectedResource) return false;
      
      return true;
    }).sort((a, b) => b.potentialProfit - a.potentialProfit);
  }, [opportunities, playerCredits, selectedResource]);

  const getTrendIcon = (trend: MarketTrend['trend']) => {
    switch (trend) {
      case 'up': return '📈';
      case 'down': return '📉';
      case 'stable': return '➡️';
    }
  };

  const getRiskColor = (risk: MarketOpportunity['risk']) => {
    switch (risk) {
      case 'low': return '#44ff44';
      case 'medium': return '#ffaa44';
      case 'high': return '#ff4444';
    }
  };

  const formatCredits = (amount: number) => {
    return amount.toLocaleString() + ' cr';
  };

  const formatPercentage = (value: number) => {
    const sign = value >= 0 ? '+' : '';
    return sign + value.toFixed(1) + '%';
  };

  if (isLoading) {
    return (
      <div className="market-analyzer loading">
        <div className="loading-spinner">Analyzing market data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="market-analyzer error">
        <div className="error-message">{error}</div>
        <button className="retry-btn" onClick={() => window.location.reload()}>
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="market-analyzer">
      <div className="analyzer-header">
        <h3>Market Intelligence</h3>
        <div className="last-update">
          Last update: {lastUpdate.toLocaleTimeString()}
        </div>
      </div>

      <div className="analysis-controls">
        <div className="depth-selector">
          <label>Analysis Depth:</label>
          <div className="depth-buttons">
            {(['local', 'regional', 'global'] as const).map(depth => (
              <button
                key={depth}
                className={`depth-btn ${analysisDepth === depth ? 'active' : ''}`}
                onClick={() => setAnalysisDepth(depth)}
              >
                {depth.charAt(0).toUpperCase() + depth.slice(1)}
              </button>
            ))}
          </div>
        </div>

        <div className="resource-filter">
          <label>Resource Filter:</label>
          <select 
            value={selectedResource}
            onChange={(e) => setSelectedResource(e.target.value as typeof selectedResource)}
          >
            <option value="all">All Resources</option>
            <option value="fuel">⛽ Fuel</option>
            <option value="organics">🌿 Organics</option>
            <option value="equipment">⚙️ Equipment</option>
          </select>
        </div>
      </div>

      {marketStats && (
        <div className="market-overview">
          <h4>Market Overview</h4>
          <div className="stats-grid">
            <div className="stat-card">
              <h5>Markets Analyzed</h5>
              <div className="stat-value">{marketStats.marketCount}</div>
            </div>
            <div className="stat-card">
              <h5>24h Volume</h5>
              <div className="stat-value">{formatCredits(marketStats.totalVolume)}</div>
            </div>
            <div className="stat-card">
              <h5>Average Spreads</h5>
              <div className="spreads">
                {Object.entries(marketStats.avgPrices).map(([resource, prices]) => (
                  <div key={resource} className="spread-item">
                    <span className="resource-name">{resource}:</span>
                    <span className="spread-value">
                      {((prices.buy - prices.sell) / prices.sell * 100).toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="market-trends">
        <h4>Market Trends</h4>
        <div className="trends-list">
          {trends.filter(t => selectedResource === 'all' || t.resource === selectedResource).map((trend, index) => (
            <div key={index} className="trend-card">
              <div className="trend-header">
                <span className="trend-icon">{getTrendIcon(trend.trend)}</span>
                <span className="trend-resource">{trend.resource.toUpperCase()}</span>
                <span className="trend-strength" style={{ width: `${trend.strength}%` }}></span>
              </div>
              <div className="trend-prediction">
                <div className="prediction-price">
                  Predicted: {formatCredits(trend.prediction.price)}
                </div>
                <div className="prediction-confidence">
                  Confidence: {trend.prediction.confidence}%
                </div>
                <div className="prediction-timeframe">
                  {trend.prediction.timeframe}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="market-opportunities">
        <h4>Trading Opportunities ({viableOpportunities.length})</h4>
        <div className="opportunities-list">
          {viableOpportunities.map(opportunity => (
            <div 
              key={opportunity.id} 
              className="opportunity-card"
              onClick={() => onSelectOpportunity?.(opportunity)}
            >
              <div className="opportunity-header">
                <span className="opportunity-type">{opportunity.type.replace('_', ' ').toUpperCase()}</span>
                <span 
                  className="opportunity-risk"
                  style={{ color: getRiskColor(opportunity.risk) }}
                >
                  {opportunity.risk.toUpperCase()} RISK
                </span>
              </div>
              
              <div className="opportunity-details">
                <div className="trade-route">
                  <span className="buy-port">{opportunity.buyPort}</span>
                  <span className="arrow">→</span>
                  <span className="sell-port">{opportunity.sellPort}</span>
                </div>
                <div className="resource-info">
                  Resource: {opportunity.resource.toUpperCase()}
                </div>
                <div className="profit-info">
                  Potential Profit: {formatCredits(opportunity.potentialProfit)}
                </div>
                <div className="expires-info">
                  Expires in: {opportunity.expiresIn} minutes
                </div>
              </div>
              
              <p className="opportunity-description">{opportunity.description}</p>
            </div>
          ))}
          
          {viableOpportunities.length === 0 && (
            <div className="no-opportunities">
              No viable opportunities found with current filters and resources.
            </div>
          )}
        </div>
      </div>

      <div className="market-heatmap">
        <h4>Price Heatmap</h4>
        <div className="heatmap-grid">
          {marketData.slice(0, 20).map(market => (
            <div key={market.portId} className="heatmap-cell">
              <div className="port-name">{market.portName}</div>
              <div className="price-indicators">
                {(['fuel', 'organics', 'equipment'] as const).map(resource => {
                  const change = market.priceChange24h[resource];
                  const intensity = Math.min(Math.abs(change) / 10, 1);
                  const color = change > 0 ? 
                    `rgba(68, 255, 68, ${intensity})` : 
                    `rgba(255, 68, 68, ${intensity})`;
                  
                  return (
                    <div 
                      key={resource}
                      className="price-indicator"
                      style={{ backgroundColor: color }}
                      title={`${resource}: ${formatPercentage(change)}`}
                    >
                      {resource.charAt(0).toUpperCase()}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MarketAnalyzer;