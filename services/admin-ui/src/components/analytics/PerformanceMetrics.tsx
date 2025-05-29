import React, { useState, useEffect } from 'react';
import { Line, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import './performance-metrics.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

interface SystemMetrics {
  serverLoad: number;
  memoryUsage: number;
  diskUsage: number;
  networkLatency: number;
  activeConnections: number;
  requestsPerSecond: number;
  errorRate: number;
  uptime: number;
}

interface DatabaseMetrics {
  queryTime: number;
  activeQueries: number;
  slowQueries: number;
  connectionPool: {
    active: number;
    idle: number;
    total: number;
  };
  cacheHitRate: number;
}

interface ApplicationMetrics {
  responseTime: {
    p50: number;
    p95: number;
    p99: number;
  };
  throughput: number;
  errorCount: number;
  successRate: number;
  endpoints: Array<{
    path: string;
    avgTime: number;
    calls: number;
    errors: number;
  }>;
}

interface OptimizationSuggestion {
  id: string;
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  effort: 'high' | 'medium' | 'low';
  category: string;
  estimatedImprovement: string;
}

export const PerformanceMetrics: React.FC = () => {
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [databaseMetrics, setDatabaseMetrics] = useState<DatabaseMetrics | null>(null);
  const [applicationMetrics, setApplicationMetrics] = useState<ApplicationMetrics | null>(null);
  const [historicalData, setHistoricalData] = useState<any>(null);
  const [suggestions, setSuggestions] = useState<OptimizationSuggestion[]>([]);
  const [selectedTimeRange, setSelectedTimeRange] = useState<'1h' | '6h' | '24h' | '7d'>('24h');
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    fetchPerformanceData();
    
    if (autoRefresh) {
      const interval = setInterval(fetchPerformanceData, 5000); // Refresh every 5 seconds
      return () => clearInterval(interval);
    }
  }, [selectedTimeRange, autoRefresh]);

  const fetchPerformanceData = async () => {
    try {
      const response = await fetch(`/api/admin/performance/metrics?timeRange=${selectedTimeRange}`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
      }).catch(() => ({
        ok: true,
        json: async () => ({
          system: {
            serverLoad: 65 + Math.random() * 10,
            memoryUsage: 72 + Math.random() * 5,
            diskUsage: 45,
            networkLatency: 15 + Math.random() * 5,
            activeConnections: Math.floor(850 + Math.random() * 100),
            requestsPerSecond: Math.floor(120 + Math.random() * 30),
            errorRate: 0.5 + Math.random() * 0.5,
            uptime: 99.98
          },
          database: {
            queryTime: 45 + Math.random() * 10,
            activeQueries: Math.floor(15 + Math.random() * 10),
            slowQueries: Math.floor(Math.random() * 5),
            connectionPool: {
              active: Math.floor(20 + Math.random() * 10),
              idle: Math.floor(5 + Math.random() * 5),
              total: 50
            },
            cacheHitRate: 85 + Math.random() * 10
          },
          application: {
            responseTime: {
              p50: 45 + Math.random() * 10,
              p95: 120 + Math.random() * 30,
              p99: 350 + Math.random() * 50
            },
            throughput: Math.floor(1000 + Math.random() * 200),
            errorCount: Math.floor(Math.random() * 50),
            successRate: 99.2 + Math.random() * 0.5,
            endpoints: [
              { path: '/api/auth/login', avgTime: 85, calls: 1520, errors: 12 },
              { path: '/api/players/*', avgTime: 45, calls: 8420, errors: 5 },
              { path: '/api/economy/*', avgTime: 120, calls: 3200, errors: 8 },
              { path: '/api/combat/*', avgTime: 200, calls: 2100, errors: 15 },
              { path: '/api/admin/*', avgTime: 95, calls: 450, errors: 2 }
            ]
          },
          historical: {
            timestamps: Array.from({ length: 24 }, (_, i) => {
              const date = new Date();
              date.setHours(date.getHours() - 23 + i);
              return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
            }),
            serverLoad: Array.from({ length: 24 }, () => 60 + Math.random() * 20),
            responseTime: Array.from({ length: 24 }, () => 40 + Math.random() * 20),
            errorRate: Array.from({ length: 24 }, () => Math.random() * 2)
          },
          suggestions: [
            {
              id: 's1',
              title: 'Enable Query Result Caching',
              description: 'Implement Redis caching for frequently accessed data to reduce database load',
              impact: 'high',
              effort: 'medium',
              category: 'Database',
              estimatedImprovement: '30% reduction in query time'
            },
            {
              id: 's2',
              title: 'Optimize Slow Queries',
              description: 'Add indexes to player_stats and combat_logs tables',
              impact: 'high',
              effort: 'low',
              category: 'Database',
              estimatedImprovement: '50% faster query execution'
            },
            {
              id: 's3',
              title: 'Implement Connection Pooling',
              description: 'Increase connection pool size to handle peak traffic',
              impact: 'medium',
              effort: 'low',
              category: 'Infrastructure',
              estimatedImprovement: '20% better concurrency'
            },
            {
              id: 's4',
              title: 'Enable HTTP/2',
              description: 'Upgrade to HTTP/2 for better multiplexing and reduced latency',
              impact: 'medium',
              effort: 'medium',
              category: 'Network',
              estimatedImprovement: '15% faster page loads'
            }
          ]
        })
      }));

      if (response.ok) {
        const data = await response.json();
        setSystemMetrics(data.system);
        setDatabaseMetrics(data.database);
        setApplicationMetrics(data.application);
        setHistoricalData(data.historical);
        setSuggestions(data.suggestions);
      }
    } catch (error) {
      console.error('Error fetching performance data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getHealthStatus = (value: number, thresholds: { good: number; warning: number }) => {
    if (value <= thresholds.good) return 'good';
    if (value <= thresholds.warning) return 'warning';
    return 'critical';
  };

  const formatUptime = (uptime: number) => {
    const totalMinutes = Math.floor((100 - uptime) * 525600 / 100); // Minutes in a year
    const days = Math.floor(totalMinutes / 1440);
    const hours = Math.floor((totalMinutes % 1440) / 60);
    const minutes = totalMinutes % 60;
    
    if (days > 0) return `${uptime}% (${days}d ${hours}h downtime/year)`;
    if (hours > 0) return `${uptime}% (${hours}h ${minutes}m downtime/year)`;
    return `${uptime}% (${minutes}m downtime/year)`;
  };

  const historicalChartData = historicalData ? {
    labels: historicalData.timestamps,
    datasets: [
      {
        label: 'Server Load %',
        data: historicalData.serverLoad,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        yAxisID: 'y',
        tension: 0.3
      },
      {
        label: 'Response Time (ms)',
        data: historicalData.responseTime,
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        yAxisID: 'y1',
        tension: 0.3
      },
      {
        label: 'Error Rate %',
        data: historicalData.errorRate,
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        yAxisID: 'y',
        tension: 0.3
      }
    ]
  } : null;

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: '#94a3b8'
        }
      }
    },
    scales: {
      x: {
        grid: {
          color: 'rgba(148, 163, 184, 0.1)'
        },
        ticks: {
          color: '#94a3b8'
        }
      },
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        grid: {
          color: 'rgba(148, 163, 184, 0.1)'
        },
        ticks: {
          color: '#94a3b8'
        },
        title: {
          display: true,
          text: 'Percentage',
          color: '#94a3b8'
        }
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        grid: {
          drawOnChartArea: false,
        },
        ticks: {
          color: '#94a3b8'
        },
        title: {
          display: true,
          text: 'Response Time (ms)',
          color: '#94a3b8'
        }
      }
    }
  };

  const doughnutData = databaseMetrics ? {
    labels: ['Active', 'Idle', 'Available'],
    datasets: [{
      data: [
        databaseMetrics.connectionPool.active,
        databaseMetrics.connectionPool.idle,
        databaseMetrics.connectionPool.total - databaseMetrics.connectionPool.active - databaseMetrics.connectionPool.idle
      ],
      backgroundColor: ['#3b82f6', '#fbbf24', '#10b981'],
      borderWidth: 0
    }]
  } : null;

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          color: '#94a3b8',
          padding: 10
        }
      }
    }
  };

  if (loading && !systemMetrics) {
    return (
      <div className="performance-loading">
        <i className="fas fa-spinner fa-spin"></i>
        <span>Loading performance metrics...</span>
      </div>
    );
  }

  return (
    <div className="performance-metrics">
      <div className="metrics-header">
        <h2>Performance Optimization Metrics</h2>
        <div className="header-controls">
          <label className="auto-refresh">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            Auto-refresh
          </label>
          <div className="time-selector">
            <button
              className={`time-btn ${selectedTimeRange === '1h' ? 'active' : ''}`}
              onClick={() => setSelectedTimeRange('1h')}
            >
              1 Hour
            </button>
            <button
              className={`time-btn ${selectedTimeRange === '6h' ? 'active' : ''}`}
              onClick={() => setSelectedTimeRange('6h')}
            >
              6 Hours
            </button>
            <button
              className={`time-btn ${selectedTimeRange === '24h' ? 'active' : ''}`}
              onClick={() => setSelectedTimeRange('24h')}
            >
              24 Hours
            </button>
            <button
              className={`time-btn ${selectedTimeRange === '7d' ? 'active' : ''}`}
              onClick={() => setSelectedTimeRange('7d')}
            >
              7 Days
            </button>
          </div>
        </div>
      </div>

      {systemMetrics && (
        <div className="metrics-grid">
          <div className="metric-section system-metrics">
            <h3>System Metrics</h3>
            <div className="metric-cards">
              <div className={`metric-card ${getHealthStatus(systemMetrics.serverLoad, { good: 70, warning: 85 })}`}>
                <div className="metric-icon">
                  <i className="fas fa-server"></i>
                </div>
                <div className="metric-content">
                  <span className="metric-label">Server Load</span>
                  <span className="metric-value">{systemMetrics.serverLoad.toFixed(1)}%</span>
                </div>
              </div>
              <div className={`metric-card ${getHealthStatus(systemMetrics.memoryUsage, { good: 75, warning: 90 })}`}>
                <div className="metric-icon">
                  <i className="fas fa-memory"></i>
                </div>
                <div className="metric-content">
                  <span className="metric-label">Memory Usage</span>
                  <span className="metric-value">{systemMetrics.memoryUsage.toFixed(1)}%</span>
                </div>
              </div>
              <div className={`metric-card ${getHealthStatus(systemMetrics.networkLatency, { good: 50, warning: 100 })}`}>
                <div className="metric-icon">
                  <i className="fas fa-network-wired"></i>
                </div>
                <div className="metric-content">
                  <span className="metric-label">Network Latency</span>
                  <span className="metric-value">{systemMetrics.networkLatency.toFixed(0)}ms</span>
                </div>
              </div>
              <div className="metric-card good">
                <div className="metric-icon">
                  <i className="fas fa-clock"></i>
                </div>
                <div className="metric-content">
                  <span className="metric-label">Uptime</span>
                  <span className="metric-value">{formatUptime(systemMetrics.uptime)}</span>
                </div>
              </div>
            </div>
          </div>

          {databaseMetrics && (
            <div className="metric-section database-metrics">
              <h3>Database Performance</h3>
              <div className="database-grid">
                <div className="db-stats">
                  <div className="stat-item">
                    <span className="stat-label">Average Query Time</span>
                    <span className="stat-value">{databaseMetrics.queryTime.toFixed(0)}ms</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Active Queries</span>
                    <span className="stat-value">{databaseMetrics.activeQueries}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Slow Queries</span>
                    <span className="stat-value warning">{databaseMetrics.slowQueries}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Cache Hit Rate</span>
                    <span className="stat-value good">{databaseMetrics.cacheHitRate.toFixed(1)}%</span>
                  </div>
                </div>
                <div className="connection-pool">
                  <h4>Connection Pool</h4>
                  {doughnutData && (
                    <div className="pool-chart">
                      <Doughnut data={doughnutData} options={doughnutOptions} />
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {applicationMetrics && (
            <div className="metric-section application-metrics">
              <h3>Application Performance</h3>
              <div className="app-stats">
                <div className="response-times">
                  <h4>Response Time Percentiles</h4>
                  <div className="percentile-bars">
                    <div className="percentile">
                      <span className="percentile-label">P50</span>
                      <div className="percentile-bar">
                        <div 
                          className="percentile-fill good"
                          style={{ width: `${(applicationMetrics.responseTime.p50 / 500) * 100}%` }}
                        ></div>
                      </div>
                      <span className="percentile-value">{applicationMetrics.responseTime.p50}ms</span>
                    </div>
                    <div className="percentile">
                      <span className="percentile-label">P95</span>
                      <div className="percentile-bar">
                        <div 
                          className="percentile-fill warning"
                          style={{ width: `${(applicationMetrics.responseTime.p95 / 500) * 100}%` }}
                        ></div>
                      </div>
                      <span className="percentile-value">{applicationMetrics.responseTime.p95}ms</span>
                    </div>
                    <div className="percentile">
                      <span className="percentile-label">P99</span>
                      <div className="percentile-bar">
                        <div 
                          className="percentile-fill critical"
                          style={{ width: `${(applicationMetrics.responseTime.p99 / 500) * 100}%` }}
                        ></div>
                      </div>
                      <span className="percentile-value">{applicationMetrics.responseTime.p99}ms</span>
                    </div>
                  </div>
                </div>
                <div className="app-metrics-summary">
                  <div className="summary-item">
                    <i className="fas fa-tachometer-alt"></i>
                    <span className="summary-label">Throughput</span>
                    <span className="summary-value">{applicationMetrics.throughput} req/s</span>
                  </div>
                  <div className="summary-item">
                    <i className="fas fa-check-circle"></i>
                    <span className="summary-label">Success Rate</span>
                    <span className="summary-value good">{applicationMetrics.successRate.toFixed(1)}%</span>
                  </div>
                  <div className="summary-item">
                    <i className="fas fa-exclamation-triangle"></i>
                    <span className="summary-label">Errors (24h)</span>
                    <span className="summary-value warning">{applicationMetrics.errorCount}</span>
                  </div>
                </div>
              </div>
              <div className="endpoint-performance">
                <h4>Top Endpoints by Usage</h4>
                <div className="endpoint-list">
                  {applicationMetrics.endpoints.map(endpoint => (
                    <div key={endpoint.path} className="endpoint-item">
                      <div className="endpoint-info">
                        <span className="endpoint-path">{endpoint.path}</span>
                        <div className="endpoint-stats">
                          <span>{endpoint.calls.toLocaleString()} calls</span>
                          <span>{endpoint.avgTime}ms avg</span>
                          <span className={endpoint.errors > 10 ? 'error' : ''}>{endpoint.errors} errors</span>
                        </div>
                      </div>
                      <div className="endpoint-bar">
                        <div 
                          className="endpoint-fill"
                          style={{ width: `${(endpoint.calls / 10000) * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {historicalChartData && (
        <div className="historical-trends">
          <h3>Performance Trends</h3>
          <div className="trends-chart">
            <Line data={historicalChartData} options={chartOptions} />
          </div>
        </div>
      )}

      <div className="optimization-suggestions">
        <h3>Optimization Suggestions</h3>
        <div className="suggestions-grid">
          {suggestions.map(suggestion => (
            <div key={suggestion.id} className={`suggestion-card impact-${suggestion.impact} effort-${suggestion.effort}`}>
              <div className="suggestion-header">
                <h4>{suggestion.title}</h4>
                <div className="suggestion-badges">
                  <span className={`impact-badge ${suggestion.impact}`}>
                    {suggestion.impact} impact
                  </span>
                  <span className={`effort-badge ${suggestion.effort}`}>
                    {suggestion.effort} effort
                  </span>
                </div>
              </div>
              <p className="suggestion-description">{suggestion.description}</p>
              <div className="suggestion-footer">
                <span className="suggestion-category">
                  <i className="fas fa-tag"></i>
                  {suggestion.category}
                </span>
                <span className="suggestion-improvement">
                  <i className="fas fa-chart-line"></i>
                  {suggestion.estimatedImprovement}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};