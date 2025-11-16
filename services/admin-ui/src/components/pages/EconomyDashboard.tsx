import React, { useState, useEffect, useCallback } from 'react';
import PageHeader from '../ui/PageHeader';
import { api } from '../../utils/auth';
import { useEconomyUpdates } from '../../contexts/WebSocketContext';
import './economy-dashboard.css';

interface MarketData {
  station_id: string;
  port_name: string;
  sector_name: string;
  commodity: string;
  buy_price: number;
  sell_price: number;
  quantity: number;
  last_updated: string;
}

interface EconomicMetrics {
  total_trade_volume: number;
  total_credits_in_circulation: number;
  average_profit_margin: number;
  most_traded_commodity: string;
  economic_health_score: number;
}

const EconomyDashboard: React.FC = () => {
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [metrics, setMetrics] = useState<EconomicMetrics | null>(null);
  const [selectedCommodity, setSelectedCommodity] = useState<string>('all');
  const [priceAlerts, setPriceAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const commodities = ['Food', 'Tech', 'Ore', 'Fuel', 'Minerals', 'Electronics', 'Weapons', 'Medical'];

  // WebSocket handlers
  const handleMarketUpdate = useCallback((data: any) => {
    console.log('Market update received:', data);
    setMarketData(prevData => {
      // Update or add the new market data
      const index = prevData.findIndex(item => 
        item.station_id === data.station_id && item.commodity === data.commodity
      );
      
      if (index >= 0) {
        const newData = [...prevData];
        newData[index] = { ...newData[index], ...data };
        return newData;
      } else {
        return [...prevData, data];
      }
    });
    setLastUpdate(new Date());
  }, []);

  const handlePriceChange = useCallback((data: any) => {
    console.log('Price change alert:', data);
    setPriceAlerts(prev => [data, ...prev].slice(0, 10)); // Keep last 10 alerts
  }, []);

  const handleIntervention = useCallback((data: any) => {
    console.log('Market intervention:', data);
    // Refresh market data after intervention
    fetchEconomicData();
  }, []);

  // Subscribe to WebSocket events
  useEconomyUpdates(handleMarketUpdate, handlePriceChange, handleIntervention);

  useEffect(() => {
    fetchEconomicData();
    const interval = setInterval(fetchEconomicData, 60000); // Update every 60 seconds as backup
    
    return () => {
      clearInterval(interval);
    };
  }, [selectedCommodity]);


  const fetchEconomicData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch market data
      const marketResponse = await api.get('/api/v1/admin/economy/market-data', {
        params: {
          commodity_filter: selectedCommodity !== 'all' ? selectedCommodity : undefined,
          limit: 100
        }
      });
      setMarketData(marketResponse.data as MarketData[]);
      
      // Fetch economic metrics
      const metricsResponse = await api.get('/api/v1/admin/economy/metrics', {
        params: { time_period: '24h' }
      });
      setMetrics(metricsResponse.data as EconomicMetrics);
      
      // Fetch price alerts
      const alertsResponse = await api.get('/api/v1/admin/economy/price-alerts');
      setPriceAlerts(Array.isArray(alertsResponse.data) ? alertsResponse.data : []);
      
    } catch (error: any) {
      console.error('Failed to fetch economic data:', error);
      setError(error.response?.data?.detail || 'Failed to load economic data. Please check if the gameserver is running.');
      // Clear data on error
      setMarketData([]);
      setMetrics(null);
      setPriceAlerts([]);
    } finally {
      setLoading(false);
    }
  };

  const handlePriceIntervention = async (stationId: string, commodity: string, newPrice: number) => {
    try {
      await api.post('/api/v1/admin/economy/intervention', {
        station_id: stationId,
        commodity,
        new_price: newPrice
      });
      fetchEconomicData();
    } catch (error) {
      console.error('Price intervention failed:', error);
    }
  };

  const filteredMarketData = selectedCommodity === 'all' 
    ? marketData 
    : marketData.filter(item => item.commodity === selectedCommodity);

  return (
    <div className="economy-dashboard">
      <PageHeader 
        title="Economy Dashboard" 
        subtitle="Monitor and manage the galactic economy"
      />
      
      {/* Real-time update indicator */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'flex-end', 
        marginBottom: '16px',
        fontSize: '12px',
        color: 'var(--text-secondary)'
      }}>
        <span>Last updated: {lastUpdate.toLocaleTimeString()}</span>
      </div>
      
      {loading ? (
        <div className="loading-spinner">Loading economic data...</div>
      ) : (
        <>
          {/* Error Notice */}
          {error && (
            <div className="alert error" style={{ marginBottom: '20px' }}>
              <span className="alert-icon">❌</span>
              <span className="alert-message">
                {error}
              </span>
            </div>
          )}
          
          {/* Economic Health Metrics */}
          <div className="metrics-grid">
            {metrics && (
              <>
                <div className="metric-card">
                  <h3>Trade Volume</h3>
                  <span className="metric-value">{metrics.total_trade_volume.toLocaleString()}</span>
                  <span className="metric-label">Credits/Day</span>
                </div>
                <div className="metric-card">
                  <h3>Credits in Circulation</h3>
                  <span className="metric-value">{metrics.total_credits_in_circulation.toLocaleString()}</span>
                  <span className="metric-label">Total Credits</span>
                </div>
                <div className="metric-card">
                  <h3>Average Profit Margin</h3>
                  <span className="metric-value">{metrics.average_profit_margin.toFixed(1)}%</span>
                  <span className="metric-label">Across All Routes</span>
                </div>
                <div className="metric-card">
                  <h3>Economic Health</h3>
                  <span className={`metric-value ${metrics.economic_health_score > 70 ? 'healthy' : 'warning'}`}>
                    {metrics.economic_health_score.toFixed(0)}%
                  </span>
                  <span className="metric-label">Overall Score</span>
                </div>
              </>
            )}
          </div>

          {/* Price Alerts */}
          {priceAlerts.length > 0 && (
            <div className="alerts-section">
              <h3>Price Alerts</h3>
              <div className="alerts-list">
                {priceAlerts.map((alert, index) => (
                  <div key={index} className={`alert ${alert.severity}`}>
                    <span className="alert-icon">⚠️</span>
                    <span className="alert-message">{alert.message}</span>
                    <span className="alert-time">{alert.timestamp}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Market Data Controls */}
          <div className="market-controls">
            <div className="commodity-filter">
              <label htmlFor="commodity-select">Filter by Commodity:</label>
              <select 
                id="commodity-select"
                value={selectedCommodity} 
                onChange={(e) => setSelectedCommodity(e.target.value)}
              >
                <option value="all">All Commodities</option>
                {commodities.map(commodity => (
                  <option key={commodity} value={commodity}>{commodity}</option>
                ))}
              </select>
            </div>
            
            <button onClick={fetchEconomicData} className="refresh-btn">
              🔄 Refresh Data
            </button>
          </div>

          {/* Market Data Table */}
          <div className="market-data-section">
            <h3>Market Data</h3>
            <div className="market-table-container">
              <table className="market-table">
                <thead>
                  <tr>
                    <th>Port</th>
                    <th>Sector</th>
                    <th>Commodity</th>
                    <th>Buy Price</th>
                    <th>Sell Price</th>
                    <th>Quantity</th>
                    <th>Profit Margin</th>
                    <th>Last Updated</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredMarketData.map((item, index) => {
                    const profitMargin = ((item.sell_price - item.buy_price) / item.buy_price * 100);
                    return (
                      <tr key={index}>
                        <td data-label="Port">{item.port_name}</td>
                        <td data-label="Sector">{item.sector_name}</td>
                        <td data-label="Commodity">
                          <span className={`commodity-badge ${item.commodity.toLowerCase()}`}>
                            {item.commodity}
                          </span>
                        </td>
                        <td data-label="Buy Price" className="price">{item.buy_price.toLocaleString()}</td>
                        <td data-label="Sell Price" className="price">{item.sell_price.toLocaleString()}</td>
                        <td data-label="Quantity">{item.quantity.toLocaleString()}</td>
                        <td data-label="Profit Margin" className={`profit-margin ${profitMargin > 20 ? 'high' : profitMargin > 10 ? 'medium' : 'low'}`}>
                          {profitMargin.toFixed(1)}%
                        </td>
                        <td data-label="Last Updated">{new Date(item.last_updated).toLocaleTimeString()}</td>
                        <td data-label="Actions">
                          <button 
                            className="action-btn intervention"
                            onClick={() => {
                              const newPrice = prompt(`Set new buy price for ${item.commodity}:`, item.buy_price.toString());
                              if (newPrice) {
                                handlePriceIntervention(item.station_id, item.commodity, parseFloat(newPrice));
                              }
                            }}
                          >
                            💱 Intervene
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Economic Analysis Charts */}
          <div className="charts-section">
            <div className="chart-container">
              <h3>Price Trends (24h)</h3>
              <div className="chart-placeholder">
                <p>📈 Interactive price charts would be rendered here using a charting library like Chart.js or D3</p>
                <p>Showing commodity price fluctuations across all ports</p>
              </div>
            </div>
            
            <div className="chart-container">
              <h3>Trade Volume by Route</h3>
              <div className="chart-placeholder">
                <p>📊 Trade flow visualization would be rendered here</p>
                <p>Showing the most active trade routes and volumes</p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default EconomyDashboard;