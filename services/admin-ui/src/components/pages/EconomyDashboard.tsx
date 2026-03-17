import React, { useState, useEffect, useCallback, useRef } from 'react';
import * as d3 from 'd3';
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

/** Price Trends chart - shows buy/sell prices by commodity using D3 grouped bar chart */
const PriceTrendsChart: React.FC<{ marketData: MarketData[] }> = ({ marketData }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || marketData.length === 0) return;

    // Clear previous
    d3.select(svgRef.current).selectAll('*').remove();

    // Aggregate: average buy/sell price per commodity
    const commodityMap: Record<string, { buyPrices: number[]; sellPrices: number[] }> = {};
    for (const item of marketData) {
      if (!commodityMap[item.commodity]) {
        commodityMap[item.commodity] = { buyPrices: [], sellPrices: [] };
      }
      commodityMap[item.commodity].buyPrices.push(item.buy_price);
      commodityMap[item.commodity].sellPrices.push(item.sell_price);
    }

    const data = Object.entries(commodityMap).map(([commodity, vals]) => ({
      commodity,
      avgBuy: vals.buyPrices.reduce((a, b) => a + b, 0) / vals.buyPrices.length,
      avgSell: vals.sellPrices.reduce((a, b) => a + b, 0) / vals.sellPrices.length
    })).sort((a, b) => b.avgBuy - a.avgBuy);

    if (data.length === 0) return;

    const margin = { top: 20, right: 20, bottom: 60, left: 60 };
    const width = 500 - margin.left - margin.right;
    const height = 280 - margin.top - margin.bottom;

    const svg = d3.select(svgRef.current)
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const x0 = d3.scaleBand()
      .domain(data.map(d => d.commodity))
      .rangeRound([0, width])
      .paddingInner(0.2);

    const x1 = d3.scaleBand()
      .domain(['avgBuy', 'avgSell'])
      .rangeRound([0, x0.bandwidth()])
      .padding(0.05);

    const maxPrice = d3.max(data, d => Math.max(d.avgBuy, d.avgSell)) || 100;
    const y = d3.scaleLinear()
      .domain([0, maxPrice * 1.1])
      .rangeRound([height, 0]);

    // X axis
    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x0))
      .selectAll('text')
      .style('text-anchor', 'end')
      .attr('dx', '-0.5em')
      .attr('dy', '0.15em')
      .attr('transform', 'rotate(-35)')
      .attr('fill', '#94a3b8')
      .style('font-size', '11px');

    // Y axis
    g.append('g')
      .call(d3.axisLeft(y).ticks(5).tickFormat(d => d3.format(',.0f')(d as number)))
      .selectAll('text')
      .attr('fill', '#94a3b8');

    g.append('g')
      .call(d3.axisLeft(y).ticks(5).tickSize(-width).tickFormat(() => ''))
      .selectAll('line')
      .attr('stroke', '#334155')
      .attr('stroke-opacity', 0.5);

    // Bars
    const groups = g.selectAll('.bar-group')
      .data(data)
      .enter().append('g')
      .attr('transform', d => `translate(${x0(d.commodity)},0)`);

    groups.append('rect')
      .attr('x', x1('avgBuy') as number)
      .attr('y', d => y(d.avgBuy))
      .attr('width', x1.bandwidth())
      .attr('height', d => height - y(d.avgBuy))
      .attr('fill', '#3b82f6')
      .attr('rx', 2);

    groups.append('rect')
      .attr('x', x1('avgSell') as number)
      .attr('y', d => y(d.avgSell))
      .attr('width', x1.bandwidth())
      .attr('height', d => height - y(d.avgSell))
      .attr('fill', '#10b981')
      .attr('rx', 2);

    // Legend
    const legend = g.append('g')
      .attr('transform', `translate(${width - 140}, -10)`);

    legend.append('rect').attr('width', 12).attr('height', 12).attr('fill', '#3b82f6').attr('rx', 2);
    legend.append('text').attr('x', 16).attr('y', 10).text('Avg Buy').attr('fill', '#94a3b8').style('font-size', '11px');
    legend.append('rect').attr('x', 80).attr('width', 12).attr('height', 12).attr('fill', '#10b981').attr('rx', 2);
    legend.append('text').attr('x', 96).attr('y', 10).text('Avg Sell').attr('fill', '#94a3b8').style('font-size', '11px');

  }, [marketData]);

  if (marketData.length === 0) {
    return <div className="chart-placeholder"><p>No market data available for price trends.</p></div>;
  }

  return <svg ref={svgRef}></svg>;
};

/** Trade Volume chart - shows quantity per port as a horizontal bar chart using D3 */
const TradeVolumeChart: React.FC<{ marketData: MarketData[] }> = ({ marketData }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || marketData.length === 0) return;

    // Clear previous
    d3.select(svgRef.current).selectAll('*').remove();

    // Aggregate: total quantity per port
    const portMap: Record<string, number> = {};
    for (const item of marketData) {
      const key = item.port_name || item.sector_name || `Port ${item.station_id?.slice(0, 6)}`;
      portMap[key] = (portMap[key] || 0) + item.quantity;
    }

    const data = Object.entries(portMap)
      .map(([port, volume]) => ({ port, volume }))
      .sort((a, b) => b.volume - a.volume)
      .slice(0, 10); // Top 10 ports

    if (data.length === 0) return;

    const margin = { top: 10, right: 30, bottom: 30, left: 120 };
    const width = 500 - margin.left - margin.right;
    const barHeight = 24;
    const height = data.length * (barHeight + 6);

    const svg = d3.select(svgRef.current)
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const y = d3.scaleBand()
      .domain(data.map(d => d.port))
      .rangeRound([0, height])
      .padding(0.2);

    const maxVolume = d3.max(data, d => d.volume) || 100;
    const x = d3.scaleLinear()
      .domain([0, maxVolume * 1.1])
      .range([0, width]);

    // Y axis (port names)
    g.append('g')
      .call(d3.axisLeft(y))
      .selectAll('text')
      .attr('fill', '#94a3b8')
      .style('font-size', '11px');

    // X axis
    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x).ticks(5).tickFormat(d => d3.format(',.0f')(d as number)))
      .selectAll('text')
      .attr('fill', '#94a3b8');

    // Grid lines
    g.append('g')
      .call(d3.axisBottom(x).ticks(5).tickSize(-height).tickFormat(() => ''))
      .attr('transform', `translate(0,${height})`)
      .selectAll('line')
      .attr('stroke', '#334155')
      .attr('stroke-opacity', 0.5);

    // Bars
    g.selectAll('.bar')
      .data(data)
      .enter().append('rect')
      .attr('y', d => y(d.port) as number)
      .attr('width', d => x(d.volume))
      .attr('height', y.bandwidth())
      .attr('fill', '#8b5cf6')
      .attr('rx', 3);

    // Value labels
    g.selectAll('.label')
      .data(data)
      .enter().append('text')
      .attr('x', d => x(d.volume) + 5)
      .attr('y', d => (y(d.port) as number) + y.bandwidth() / 2 + 4)
      .text(d => d3.format(',.0f')(d.volume))
      .attr('fill', '#94a3b8')
      .style('font-size', '10px');

  }, [marketData]);

  if (marketData.length === 0) {
    return <div className="chart-placeholder"><p>No market data available for trade volume.</p></div>;
  }

  return <svg ref={svgRef}></svg>;
};

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
              <PriceTrendsChart marketData={filteredMarketData} />
            </div>

            <div className="chart-container">
              <h3>Trade Volume by Route</h3>
              <TradeVolumeChart marketData={filteredMarketData} />
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default EconomyDashboard;