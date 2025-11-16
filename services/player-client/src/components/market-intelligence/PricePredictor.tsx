import React, { useState, useEffect, useMemo } from 'react';
import { gameAPI } from '../../services/api';
import './price-predictor.css';

interface PriceHistory {
  timestamp: string;
  price: number;
  volume: number;
}

interface PricePrediction {
  resource: 'fuel' | 'organics' | 'equipment';
  stationId: string;
  stationName: string;
  currentPrice: number;
  predictions: {
    '1h': { price: number; confidence: number; direction: 'up' | 'down' | 'stable' };
    '6h': { price: number; confidence: number; direction: 'up' | 'down' | 'stable' };
    '24h': { price: number; confidence: number; direction: 'up' | 'down' | 'stable' };
    '7d': { price: number; confidence: number; direction: 'up' | 'down' | 'stable' };
  };
  factors: {
    factor: string;
    impact: 'positive' | 'negative' | 'neutral';
    strength: number; // 0-100
    description: string;
  }[];
  volatility: number; // 0-100
  trend: 'bullish' | 'bearish' | 'neutral';
}

interface MarketIndicator {
  name: string;
  value: number;
  signal: 'buy' | 'sell' | 'hold';
  description: string;
}

interface PricePredictorProps {
  selectedPortId?: string;
  selectedResource?: 'fuel' | 'organics' | 'equipment';
  onPredictionSelect?: (prediction: PricePrediction) => void;
}

const PricePredictor: React.FC<PricePredictorProps> = ({
  selectedPortId,
  selectedResource = 'fuel',
  onPredictionSelect
}) => {
  const [predictions, setPredictions] = useState<PricePrediction[]>([]);
  const [priceHistory, setPriceHistory] = useState<Record<string, PriceHistory[]>>({});
  const [indicators, setIndicators] = useState<MarketIndicator[]>([]);
  const [timeframe, setTimeframe] = useState<'1h' | '6h' | '24h' | '7d'>('24h');
  const [viewMode, setViewMode] = useState<'predictions' | 'indicators' | 'factors'>('predictions');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch price predictions
  useEffect(() => {
    const fetchPredictions = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const response = await gameAPI.trading.getPricePredictions({
          stationId: selectedPortId,
          resource: selectedResource,
          includeHistory: true
        });
        
        setPredictions(response.predictions || []);
        setPriceHistory(response.history || {});
        setIndicators(response.indicators || []);
      } catch (err) {
        setError('Failed to load price predictions. Please try again.');
        console.error('Price prediction fetch error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPredictions();
    const interval = setInterval(fetchPredictions, 60000); // Refresh every minute
    
    return () => clearInterval(interval);
  }, [selectedPortId, selectedResource]);

  // Calculate average confidence for a timeframe
  const avgConfidence = useMemo(() => {
    if (predictions.length === 0) return 0;
    
    const total = predictions.reduce((sum, pred) => {
      return sum + pred.predictions[timeframe].confidence;
    }, 0);
    
    return total / predictions.length;
  }, [predictions, timeframe]);

  // Get dominant market direction
  const marketDirection = useMemo(() => {
    if (predictions.length === 0) return 'neutral';
    
    const directions = predictions.map(p => p.predictions[timeframe].direction);
    const upCount = directions.filter(d => d === 'up').length;
    const downCount = directions.filter(d => d === 'down').length;
    
    if (upCount > downCount * 1.5) return 'bullish';
    if (downCount > upCount * 1.5) return 'bearish';
    return 'neutral';
  }, [predictions, timeframe]);

  const getDirectionIcon = (direction: string) => {
    switch (direction) {
      case 'up': return '⬆️';
      case 'down': return '⬇️';
      case 'stable': return '➡️';
      default: return '❓';
    }
  };

  const getDirectionColor = (direction: string) => {
    switch (direction) {
      case 'up': 
      case 'bullish': return '#44ff44';
      case 'down': 
      case 'bearish': return '#ff4444';
      default: return '#ffaa44';
    }
  };

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'buy': return '#44ff44';
      case 'sell': return '#ff4444';
      case 'hold': return '#ffaa44';
      default: return '#888';
    }
  };

  const formatPrice = (price: number) => {
    return price.toLocaleString() + ' cr';
  };

  const formatPercentChange = (current: number, predicted: number) => {
    const change = ((predicted - current) / current) * 100;
    const sign = change >= 0 ? '+' : '';
    return sign + change.toFixed(1) + '%';
  };

  // Generate simple price chart
  const PriceChart: React.FC<{ data: PriceHistory[], prediction?: number }> = ({ data, prediction }) => {
    if (data.length === 0) return null;
    
    const maxPrice = Math.max(...data.map(d => d.price), prediction || 0);
    const minPrice = Math.min(...data.map(d => d.price), prediction || 0);
    const range = maxPrice - minPrice || 1;
    
    return (
      <div className="price-chart">
        <div className="chart-container">
          {data.map((point, index) => {
            const height = ((point.price - minPrice) / range) * 100;
            return (
              <div 
                key={index}
                className="chart-bar"
                style={{ height: `${height}%` }}
                title={`${formatPrice(point.price)} at ${new Date(point.timestamp).toLocaleTimeString()}`}
              />
            );
          })}
          {prediction && (
            <div 
              className="prediction-line"
              style={{ bottom: `${((prediction - minPrice) / range) * 100}%` }}
            />
          )}
        </div>
        <div className="chart-labels">
          <span>{formatPrice(maxPrice)}</span>
          <span>{formatPrice(minPrice)}</span>
        </div>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="price-predictor loading">
        <div className="loading-spinner">Analyzing market patterns...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="price-predictor error">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  return (
    <div className="price-predictor">
      <div className="predictor-header">
        <h3>Price Predictions</h3>
        <div className="market-status">
          <span>Market Trend:</span>
          <span 
            className="market-direction"
            style={{ color: getDirectionColor(marketDirection) }}
          >
            {marketDirection.toUpperCase()}
          </span>
        </div>
      </div>

      <div className="predictor-controls">
        <div className="timeframe-selector">
          {(['1h', '6h', '24h', '7d'] as const).map(tf => (
            <button
              key={tf}
              className={`timeframe-btn ${timeframe === tf ? 'active' : ''}`}
              onClick={() => setTimeframe(tf)}
            >
              {tf}
            </button>
          ))}
        </div>

        <div className="view-mode-selector">
          {(['predictions', 'indicators', 'factors'] as const).map(mode => (
            <button
              key={mode}
              className={`mode-btn ${viewMode === mode ? 'active' : ''}`}
              onClick={() => setViewMode(mode)}
            >
              {mode.charAt(0).toUpperCase() + mode.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="confidence-meter">
        <div className="meter-label">Average Confidence</div>
        <div className="meter-bar">
          <div 
            className="meter-fill"
            style={{ 
              width: `${avgConfidence}%`,
              backgroundColor: avgConfidence > 70 ? '#44ff44' : avgConfidence > 40 ? '#ffaa44' : '#ff4444'
            }}
          />
          <span className="meter-value">{avgConfidence.toFixed(0)}%</span>
        </div>
      </div>

      {viewMode === 'predictions' && (
        <div className="predictions-grid">
          {predictions.map((prediction, index) => (
            <div 
              key={index}
              className="prediction-card"
              onClick={() => onPredictionSelect?.(prediction)}
            >
              <div className="prediction-header">
                <h4>{prediction.stationName}</h4>
                <span className="resource-badge">{prediction.resource.toUpperCase()}</span>
              </div>

              <div className="current-price">
                Current: {formatPrice(prediction.currentPrice)}
              </div>

              <div className="prediction-details">
                <div className="prediction-row">
                  <span className="timeframe-label">{timeframe}:</span>
                  <span className="predicted-price">
                    {formatPrice(prediction.predictions[timeframe].price)}
                  </span>
                  <span 
                    className="price-change"
                    style={{ color: getDirectionColor(prediction.predictions[timeframe].direction) }}
                  >
                    {formatPercentChange(prediction.currentPrice, prediction.predictions[timeframe].price)}
                  </span>
                  <span className="direction-icon">
                    {getDirectionIcon(prediction.predictions[timeframe].direction)}
                  </span>
                </div>
                <div className="confidence-bar">
                  <div 
                    className="confidence-fill"
                    style={{ width: `${prediction.predictions[timeframe].confidence}%` }}
                  />
                </div>
              </div>

              <div className="volatility-indicator">
                <span>Volatility:</span>
                <div className="volatility-bar">
                  <div 
                    className="volatility-fill"
                    style={{ 
                      width: `${prediction.volatility}%`,
                      backgroundColor: prediction.volatility > 70 ? '#ff4444' : 
                                     prediction.volatility > 40 ? '#ffaa44' : '#44ff44'
                    }}
                  />
                </div>
              </div>

              {priceHistory[`${prediction.stationId}_${prediction.resource}`] && (
                <PriceChart 
                  data={priceHistory[`${prediction.stationId}_${prediction.resource}`]}
                  prediction={prediction.predictions[timeframe].price}
                />
              )}
            </div>
          ))}
        </div>
      )}

      {viewMode === 'indicators' && (
        <div className="indicators-list">
          {indicators.map((indicator, index) => (
            <div key={index} className="indicator-card">
              <div className="indicator-header">
                <h4>{indicator.name}</h4>
                <span 
                  className="signal-badge"
                  style={{ backgroundColor: getSignalColor(indicator.signal) }}
                >
                  {indicator.signal.toUpperCase()}
                </span>
              </div>
              <div className="indicator-value">
                Value: {indicator.value.toFixed(2)}
              </div>
              <p className="indicator-description">{indicator.description}</p>
            </div>
          ))}
        </div>
      )}

      {viewMode === 'factors' && (
        <div className="factors-analysis">
          {predictions.map((prediction, index) => (
            <div key={index} className="factors-card">
              <h4>{prediction.stationName} - {prediction.resource.toUpperCase()}</h4>
              <div className="factors-list">
                {prediction.factors.map((factor, idx) => (
                  <div key={idx} className="factor-item">
                    <div className="factor-header">
                      <span className="factor-name">{factor.factor}</span>
                      <span 
                        className="factor-impact"
                        style={{ 
                          color: factor.impact === 'positive' ? '#44ff44' : 
                                factor.impact === 'negative' ? '#ff4444' : '#888'
                        }}
                      >
                        {factor.impact === 'positive' ? '↑' : 
                         factor.impact === 'negative' ? '↓' : '─'}
                      </span>
                    </div>
                    <div className="factor-strength">
                      <div 
                        className="strength-bar"
                        style={{ 
                          width: `${factor.strength}%`,
                          backgroundColor: factor.impact === 'positive' ? '#44ff44' : 
                                         factor.impact === 'negative' ? '#ff4444' : '#888'
                        }}
                      />
                    </div>
                    <p className="factor-description">{factor.description}</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PricePredictor;