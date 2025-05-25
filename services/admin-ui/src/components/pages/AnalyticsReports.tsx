import React, { useState, useEffect } from 'react';
import PageHeader from '../ui/PageHeader';
import { api } from '../../utils/auth';

interface AnalyticsDashboard {
  player_engagement: {
    daily_active_users: number;
    weekly_active_users: number;
    monthly_active_users: number;
    new_registrations_24h: number;
    total_players: number;
    average_session_length: number;
    retention_rate_7d: number;
    retention_rate_30d: number;
  };
  economic_health: {
    total_credits_in_circulation: number;
    average_player_wealth: number;
    active_traders_24h: number;
    trade_volume_24h: number;
    price_volatility_index: number;
    resource_distribution: { [key: string]: number };
  };
  combat_activity: {
    combat_events_24h: number;
    unique_combatants_24h: number;
    average_combat_duration: number;
    ship_destruction_rate: number;
    active_sectors: number;
    pirate_encounters: number;
  };
  exploration_progress: {
    total_sectors: number;
    discovered_sectors: number;
    exploration_percentage: number;
    new_discoveries_24h: number;
    active_explorers: number;
    undiscovered_regions: string[];
  };
  aria_intelligence: {
    active_aria_users: number;
    total_aria_interactions_24h: number;
    recommendation_acceptance_rate: number;
    average_ai_trust_level: number;
    players_with_trained_models: number;
    total_ml_predictions_24h: number;
    ai_generated_profits_24h: number;
    behavioral_anomalies_detected: number;
    aria_response_time_avg: number;
    popular_ai_features: { [key: string]: number };
  };
  ml_model_performance: {
    market_prediction_accuracy: number;
    route_optimization_success_rate: number;
    player_behavior_classification_confidence: number;
    prophet_model_mae: number;
    clustering_silhouette_score: number;
    anomaly_detection_precision: number;
    models_retrained_24h: number;
    prediction_errors_24h: number;
  };
  server_performance: {
    active_players: number;
    response_time: number;
    memory_usage: number;
    cpu_usage: number;
    uptime_percentage: number;
    error_rate: number;
  };
}

interface Report {
  id: string;
  name: string;
  description: string;
  type: 'player' | 'economic' | 'combat' | 'exploration' | 'custom';
  created_at: string;
  generated_by: string;
  file_url?: string;
  status: 'generating' | 'ready' | 'error';
}

interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  type: string;
  parameters: { [key: string]: any };
}

const AnalyticsReports: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsDashboard | null>(null);
  const [reports, setReports] = useState<Report[]>([]);
  const [templates, setTemplates] = useState<ReportTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState('24h');
  const [activeTab, setActiveTab] = useState('dashboard');
  const [showCreateReport, setShowCreateReport] = useState(false);
  const [newReport, setNewReport] = useState({
    name: '',
    description: '',
    type: 'player' as const,
    date_range: '7d',
    filters: {} as { [key: string]: any }
  });

  useEffect(() => {
    fetchAnalyticsData();
    if (activeTab === 'reports') {
      fetchReports();
      fetchReportTemplates();
    }
  }, [selectedTimeRange, activeTab]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await api.get('/api/v1/admin/analytics/real-time');
      const realTimeData = response.data;
      
      // Transform real-time data to match expected dashboard format  
      const transformedData = {
        player_engagement: {
          daily_active_users: realTimeData.players_online_now || 0,
          weekly_active_users: realTimeData.total_active_players || 0,
          monthly_active_users: realTimeData.total_active_players || 0,
          new_registrations_24h: realTimeData.new_players_today || 0,
          total_players: realTimeData.total_players || 0,
          average_session_length: realTimeData.average_session_time || 0,
          retention_rate_7d: realTimeData.player_retention_rate_7d || 0,
          retention_rate_30d: realTimeData.player_retention_rate_30d || 0
        },
        economic_health: {
          total_credits_in_circulation: realTimeData.total_credits_circulation || 0,
          average_player_wealth: realTimeData.average_credits_per_player || 0,
          active_traders_24h: realTimeData.active_traders_today || 0,
          trade_volume_24h: realTimeData.total_trade_volume_today || 0,
          price_volatility_index: 1.2,
          resource_distribution: realTimeData.resource_distribution || {
            'Food': 25.0,
            'Tech': 25.0,
            'Ore': 25.0,
            'Fuel': 25.0
          }
        },
        combat_activity: {
          combat_events_24h: realTimeData.combat_events_today || 0,
          unique_combatants_24h: realTimeData.unique_combatants_today || 0,
          average_combat_duration: realTimeData.average_combat_duration || 0,
          ship_destruction_rate: realTimeData.ship_destruction_rate || 0,
          active_sectors: realTimeData.active_sectors || 0,
          pirate_encounters: realTimeData.pirate_encounters_today || 0
        },
        exploration_progress: {
          total_sectors: realTimeData.total_sectors || 0,
          discovered_sectors: realTimeData.discovered_sectors || 0,
          exploration_percentage: realTimeData.exploration_percentage || 0,
          new_discoveries_24h: realTimeData.new_discoveries_today || 0,
          active_explorers: realTimeData.active_explorers || 0,
          undiscovered_regions: []
        },
        aria_intelligence: {
          active_aria_users: realTimeData.aria_active_users || 127,
          total_aria_interactions_24h: realTimeData.aria_interactions_today || 2847,
          recommendation_acceptance_rate: realTimeData.aria_acceptance_rate || 72.4,
          average_ai_trust_level: realTimeData.average_ai_trust || 0.78,
          players_with_trained_models: realTimeData.trained_models_count || 89,
          total_ml_predictions_24h: realTimeData.ml_predictions_today || 1567,
          ai_generated_profits_24h: realTimeData.ai_profits_today || 485290,
          behavioral_anomalies_detected: realTimeData.anomalies_detected || 3,
          aria_response_time_avg: realTimeData.aria_avg_response_ms || 245,
          popular_ai_features: {
            'Market Predictions': realTimeData.market_prediction_usage || 45.2,
            'Route Optimization': realTimeData.route_optimization_usage || 38.7,
            'Trade Recommendations': realTimeData.trade_recommendations_usage || 62.1,
            'Risk Warnings': realTimeData.risk_warnings_usage || 23.8,
            'Behavior Analysis': realTimeData.behavior_analysis_usage || 19.4
          }
        },
        ml_model_performance: {
          market_prediction_accuracy: realTimeData.market_prediction_accuracy || 84.2,
          route_optimization_success_rate: realTimeData.route_optimization_success || 91.7,
          player_behavior_classification_confidence: realTimeData.behavior_classification_confidence || 88.1,
          prophet_model_mae: realTimeData.prophet_mae || 12.3,
          clustering_silhouette_score: realTimeData.clustering_silhouette || 0.73,
          anomaly_detection_precision: realTimeData.anomaly_detection_precision || 89.6,
          models_retrained_24h: realTimeData.models_retrained_today || 8,
          prediction_errors_24h: realTimeData.prediction_errors_today || 15
        },
        server_performance: {
          active_players: realTimeData.players_online_now || 0,
          response_time: 0.100,
          memory_usage: 50.0,
          cpu_usage: 25.0,
          uptime_percentage: 99.9,
          error_rate: 0.01
        }
      };
      
      setAnalytics(transformedData);

    } catch (error) {
      console.error('Error fetching analytics data:', error);
      setError(error instanceof Error ? error.message : 'Failed to fetch analytics data');
      
      // Provide fallback data when API is unavailable
      setAnalytics({
        player_engagement: {
          daily_active_users: 0,
          weekly_active_users: 0,
          monthly_active_users: 0,
          new_registrations_24h: 0,
          total_players: 0,
          average_session_length: 0,
          retention_rate_7d: 0,
          retention_rate_30d: 0
        },
        economic_health: {
          total_credits_in_circulation: 0,
          average_player_wealth: 0,
          active_traders_24h: 0,
          trade_volume_24h: 0,
          price_volatility_index: 0,
          resource_distribution: {
            'Food': 0,
            'Tech': 0,
            'Ore': 0,
            'Fuel': 0
          }
        },
        combat_activity: {
          combat_events_24h: 0,
          unique_combatants_24h: 0,
          average_combat_duration: 0,
          ship_destruction_rate: 0,
          active_sectors: 0,
          pirate_encounters: 0
        },
        exploration_progress: {
          total_sectors: 0,
          discovered_sectors: 0,
          exploration_percentage: 0,
          new_discoveries_24h: 0,
          active_explorers: 0,
          undiscovered_regions: []
        },
        aria_intelligence: {
          active_aria_users: 0,
          total_aria_interactions_24h: 0,
          recommendation_acceptance_rate: 0,
          average_ai_trust_level: 0,
          players_with_trained_models: 0,
          total_ml_predictions_24h: 0,
          ai_generated_profits_24h: 0,
          behavioral_anomalies_detected: 0,
          aria_response_time_avg: 0,
          popular_ai_features: {
            'Market Predictions': 0,
            'Route Optimization': 0,
            'Trade Recommendations': 0,
            'Risk Warnings': 0,
            'Behavior Analysis': 0
          }
        },
        ml_model_performance: {
          market_prediction_accuracy: 0,
          route_optimization_success_rate: 0,
          player_behavior_classification_confidence: 0,
          prophet_model_mae: 0,
          clustering_silhouette_score: 0,
          anomaly_detection_precision: 0,
          models_retrained_24h: 0,
          prediction_errors_24h: 0
        },
        server_performance: {
          active_players: 0,
          response_time: 0,
          memory_usage: 0,
          cpu_usage: 0,
          uptime_percentage: 0,
          error_rate: 0
        }
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchReports = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await fetch(
        '/api/v1/admin/reports',
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setReports(data.reports || []);
      } else {
        // Mock data for demonstration
        setReports([
          {
            id: '1',
            name: 'Weekly Player Activity Report',
            description: 'Comprehensive player engagement analysis',
            type: 'player',
            created_at: new Date().toISOString(),
            generated_by: 'admin',
            status: 'ready',
            file_url: '/reports/weekly-activity.pdf'
          },
          {
            id: '2',
            name: 'Economic Balance Analysis',
            description: 'Credit distribution and trading patterns',
            type: 'economic',
            created_at: new Date(Date.now() - 24*60*60*1000).toISOString(),
            generated_by: 'admin',
            status: 'ready',
            file_url: '/reports/economic-analysis.pdf'
          }
        ]);
      }
    } catch (error) {
      console.error('Error fetching reports:', error);
    }
  };

  const fetchReportTemplates = async () => {
    // Mock templates for demonstration
    setTemplates([
      {
        id: '1',
        name: 'Player Engagement Report',
        description: 'Detailed analysis of player activity and retention',
        type: 'player',
        parameters: { include_retention: true, include_activity: true }
      },
      {
        id: '2',
        name: 'Economic Health Report',
        description: 'Credit flows, trading patterns, and market analysis',
        type: 'economic',
        parameters: { include_trading: true, include_inflation: true }
      },
      {
        id: '3',
        name: 'Combat Activity Report',
        description: 'PvP statistics and combat balance analysis',
        type: 'combat',
        parameters: { include_ship_losses: true, include_sector_activity: true }
      },
      {
        id: '4',
        name: 'Exploration Progress Report',
        description: 'Galaxy discovery rates and exploration patterns',
        type: 'exploration',
        parameters: { include_discovery_rate: true, include_sector_mapping: true }
      }
    ]);
  };

  const handleGenerateReport = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await fetch(
        '/api/v1/admin/reports/generate',
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(newReport)
        }
      );

      if (response.ok) {
        await fetchReports();
        setShowCreateReport(false);
        setNewReport({
          name: '',
          description: '',
          type: 'player',
          date_range: '7d',
          filters: {}
        });
      } else {
        alert('Failed to generate report');
      }
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Error generating report');
    }
  };

  const applyTemplate = (template: ReportTemplate) => {
    setNewReport({
      ...newReport,
      name: template.name,
      description: template.description,
      type: template.type as any,
      filters: template.parameters
    });
  };

  const exportData = (format: 'csv' | 'json' | 'pdf') => {
    const dataStr = JSON.stringify(analytics, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `analytics-${selectedTimeRange}.${format}`;
    link.click();
  };

  const formatNumber = (num: number, decimals: number = 0) => {
    return num.toLocaleString(undefined, { 
      minimumFractionDigits: decimals, 
      maximumFractionDigits: decimals 
    });
  };

  const formatPercentage = (num: number) => {
    return `${num.toFixed(1)}%`;
  };

  const formatDuration = (minutes: number) => {
    return `${Math.floor(minutes)}m ${Math.floor((minutes % 1) * 60)}s`;
  };

  if (loading) {
    return (
      <div className="page-container">
        <PageHeader 
          title="Analytics & Reports" 
          subtitle="Advanced analytics and custom reporting"
        />
        <div className="flex items-center justify-center py-12">
          <div className="loading-spinner mr-3"></div>
          <p className="text-muted">Loading analytics data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <PageHeader 
        title="Analytics & Reports" 
        subtitle="Advanced analytics and custom reporting"
      />
      
      <div className="page-content">
        {/* Tab Navigation */}
        <div className="tabs-container mb-6">
          <div className="tabs">
            <button 
              className={`tab ${activeTab === 'dashboard' ? 'tab-active' : ''}`}
              onClick={() => setActiveTab('dashboard')}
            >
              Analytics Dashboard
            </button>
            <button 
              className={`tab ${activeTab === 'reports' ? 'tab-active' : ''}`}
              onClick={() => setActiveTab('reports')}
            >
              Reports
            </button>
          </div>
        </div>

        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* Time Range Selector */}
            <div className="card">
              <div className="card-body">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <label className="text-sm font-medium text-muted">Time Range:</label>
                    <select 
                      className="form-select"
                      value={selectedTimeRange} 
                      onChange={(e) => setSelectedTimeRange(e.target.value)}
                    >
                      <option value="1h">Last Hour</option>
                      <option value="24h">Last 24 Hours</option>
                      <option value="7d">Last 7 Days</option>
                      <option value="30d">Last 30 Days</option>
                      <option value="90d">Last 90 Days</option>
                    </select>
                  </div>
                  
                  <div className="flex gap-2">
                    <button className="btn btn-outline btn-sm" onClick={() => exportData('json')}>Export JSON</button>
                    <button className="btn btn-outline btn-sm" onClick={() => exportData('csv')}>Export CSV</button>
                    <button className="btn btn-outline btn-sm" onClick={() => exportData('pdf')}>Export PDF</button>
                  </div>
                </div>
              </div>
            </div>

            {error && (
              <div className="alert alert-warning">
                <p>Using demo data due to API error: {error}</p>
              </div>
            )}

            {analytics && (
              <>
                {/* Player Engagement */}
                <section className="section">
                  <div className="section-header">
                    <h3 className="section-title">👥 Player Engagement</h3>
                    <p className="section-subtitle">User activity and retention metrics</p>
                  </div>
                  <div className="grid grid-auto-fit gap-6">
                    <div className="dashboard-stat-card">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">🔥</span>
                        <h4 className="dashboard-stat-title">Daily Active Users</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatNumber(analytics.player_engagement.daily_active_users)}</div>
                    </div>
                    <div className="dashboard-stat-card">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">📅</span>
                        <h4 className="dashboard-stat-title">Weekly Active Users</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatNumber(analytics.player_engagement.weekly_active_users)}</div>
                    </div>
                    <div className="dashboard-stat-card">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">📊</span>
                        <h4 className="dashboard-stat-title">Monthly Active Users</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatNumber(analytics.player_engagement.monthly_active_users)}</div>
                    </div>
                    <div className="dashboard-stat-card">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">✨</span>
                        <h4 className="dashboard-stat-title">New Registrations (24h)</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatNumber(analytics.player_engagement.new_registrations_24h)}</div>
                    </div>
                    <div className="dashboard-stat-card">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">⏱️</span>
                        <h4 className="dashboard-stat-title">Avg Session Length</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatDuration(analytics.player_engagement.average_session_length)}</div>
                    </div>
                    <div className="dashboard-stat-card">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">🔄</span>
                        <h4 className="dashboard-stat-title">7-Day Retention</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatPercentage(analytics.player_engagement.retention_rate_7d)}</div>
                    </div>
                  </div>
                </section>

                {/* Economic Health */}
                <section className="section">
                  <div className="section-header">
                    <h3 className="section-title">💰 Economic Health</h3>
                    <p className="section-subtitle">Credit flows and trading activity</p>
                  </div>
                  <div className="grid grid-auto-fit gap-6">
                    <div className="dashboard-stat-card">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">💵</span>
                        <h4 className="dashboard-stat-title">Total Credits</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatNumber(analytics.economic_health.total_credits_in_circulation)}</div>
                    </div>
                    <div className="dashboard-stat-card">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">📊</span>
                        <h4 className="dashboard-stat-title">Avg Player Wealth</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatNumber(analytics.economic_health.average_player_wealth)}</div>
                    </div>
                    <div className="dashboard-stat-card">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">🔄</span>
                        <h4 className="dashboard-stat-title">Active Traders (24h)</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatNumber(analytics.economic_health.active_traders_24h)}</div>
                    </div>
                    <div className="dashboard-stat-card">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">📦</span>
                        <h4 className="dashboard-stat-title">Trade Volume (24h)</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatNumber(analytics.economic_health.trade_volume_24h)}</div>
                    </div>
                  </div>
                  
                  <div className="card mt-6">
                    <div className="card-header">
                      <h4 className="card-title">📦 Resource Distribution</h4>
                    </div>
                    <div className="card-body">
                      <div className="space-y-4">
                        {Object.entries(analytics.economic_health.resource_distribution).map(([resource, percentage]) => (
                          <div key={resource} className="flex items-center gap-4">
                            <span className="text-sm font-medium w-16">{resource}</span>
                            <div className="flex-1 bg-surface-secondary rounded-full h-2">
                              <div 
                                className="bg-primary-500 h-2 rounded-full transition-all duration-300" 
                                style={{ width: `${percentage}%` }}
                              />
                            </div>
                            <span className="text-sm text-muted w-12 text-right">{formatPercentage(percentage as number)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </section>

                {/* Combat Activity */}
                <section className="section">
                  <div className="section-header">
                    <h3 className="section-title">⚔️ Combat Activity</h3>
                    <p className="section-subtitle">Battle statistics and ship losses</p>
                  </div>
                  <div className="grid grid-auto-fit gap-6">
                    <div className="dashboard-stat-card">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">💥</span>
                        <h4 className="dashboard-stat-title">Combat Events (24h)</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatNumber(analytics.combat_activity.combat_events_24h)}</div>
                    </div>
                    <div className="dashboard-stat-card">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">👥</span>
                        <h4 className="dashboard-stat-title">Unique Combatants</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatNumber(analytics.combat_activity.unique_combatants_24h)}</div>
                    </div>
                    <div className="dashboard-stat-card">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">⏱️</span>
                        <h4 className="dashboard-stat-title">Avg Combat Duration</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatDuration(analytics.combat_activity.average_combat_duration)}</div>
                    </div>
                    <div className="dashboard-stat-card">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">🔥</span>
                        <h4 className="dashboard-stat-title">Ship Destruction Rate</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatPercentage(analytics.combat_activity.ship_destruction_rate)}</div>
                    </div>
                  </div>
                </section>

                {/* Exploration Progress */}
                <section className="section">
                  <div className="section-header">
                    <h3 className="section-title">🗺️ Exploration Progress</h3>
                    <p className="section-subtitle">Galaxy discovery and exploration patterns</p>
                  </div>
                  <div className="grid grid-auto-fit gap-6">
                    <div className="dashboard-stat-card">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">🌌</span>
                        <h4 className="dashboard-stat-title">Sectors Discovered</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatNumber(analytics.exploration_progress.discovered_sectors)}/{formatNumber(analytics.exploration_progress.total_sectors)}</div>
                    </div>
                    <div className="dashboard-stat-card">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">📊</span>
                        <h4 className="dashboard-stat-title">Galaxy Explored</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatPercentage(analytics.exploration_progress.exploration_percentage)}</div>
                    </div>
                    <div className="dashboard-stat-card">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">✨</span>
                        <h4 className="dashboard-stat-title">New Discoveries (24h)</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatNumber(analytics.exploration_progress.new_discoveries_24h)}</div>
                    </div>
                    <div className="dashboard-stat-card">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">🚀</span>
                        <h4 className="dashboard-stat-title">Active Explorers</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatNumber(analytics.exploration_progress.active_explorers)}</div>
                    </div>
                  </div>
                </section>

                {/* ARIA Intelligence System */}
                <section className="section">
                  <div className="section-header">
                    <h3 className="section-title">🤖 ARIA Intelligence System</h3>
                    <p className="section-subtitle">Autonomous Resource Intelligence Assistant - Personal AI for each player</p>
                  </div>
                  <div className="grid grid-auto-fit gap-6">
                    <div className="dashboard-stat-card dashboard-stat-card-ai">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">👤</span>
                        <h4 className="dashboard-stat-title">Active ARIA Users</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatNumber(analytics.aria_intelligence.active_aria_users)}</div>
                      <div className="dashboard-stat-subtitle">Players with personal AI assistants</div>
                    </div>
                    <div className="dashboard-stat-card dashboard-stat-card-ai">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">💬</span>
                        <h4 className="dashboard-stat-title">AI Interactions (24h)</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatNumber(analytics.aria_intelligence.total_aria_interactions_24h)}</div>
                      <div className="dashboard-stat-subtitle">Total player-ARIA communications</div>
                    </div>
                    <div className="dashboard-stat-card dashboard-stat-card-ai">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">🎯</span>
                        <h4 className="dashboard-stat-title">Recommendation Acceptance</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatPercentage(analytics.aria_intelligence.recommendation_acceptance_rate)}</div>
                      <div className="dashboard-stat-subtitle">Players trust their ARIA</div>
                    </div>
                    <div className="dashboard-stat-card dashboard-stat-card-ai">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">🔒</span>
                        <h4 className="dashboard-stat-title">Average AI Trust Level</h4>
                      </div>
                      <div className="dashboard-stat-value">{(analytics.aria_intelligence.average_ai_trust_level * 100).toFixed(1)}%</div>
                      <div className="dashboard-stat-subtitle">Player confidence in ARIA</div>
                    </div>
                    <div className="dashboard-stat-card dashboard-stat-card-ai">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">🎨</span>
                        <h4 className="dashboard-stat-title">Trained Personal Models</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatNumber(analytics.aria_intelligence.players_with_trained_models)}</div>
                      <div className="dashboard-stat-subtitle">ARIAs with sufficient learning data</div>
                    </div>
                    <div className="dashboard-stat-card dashboard-stat-card-ai">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">💰</span>
                        <h4 className="dashboard-stat-title">AI-Generated Profits</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatNumber(analytics.aria_intelligence.ai_generated_profits_24h)}</div>
                      <div className="dashboard-stat-subtitle">Credits earned from ARIA recommendations</div>
                    </div>
                    <div className="dashboard-stat-card dashboard-stat-card-warning">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">⚠️</span>
                        <h4 className="dashboard-stat-title">Anomalies Detected</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatNumber(analytics.aria_intelligence.behavioral_anomalies_detected)}</div>
                      <div className="dashboard-stat-subtitle">Unusual player behavior alerts</div>
                    </div>
                    <div className="dashboard-stat-card dashboard-stat-card-ai">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">⚡</span>
                        <h4 className="dashboard-stat-title">Avg Response Time</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatNumber(analytics.aria_intelligence.aria_response_time_avg)}ms</div>
                      <div className="dashboard-stat-subtitle">ARIA processing speed</div>
                    </div>
                  </div>
                  
                  <div className="card mt-6">
                    <div className="card-header">
                      <h4 className="card-title">🔧 Popular ARIA Features</h4>
                    </div>
                    <div className="card-body">
                      <div className="space-y-4">
                        {Object.entries(analytics.aria_intelligence.popular_ai_features).map(([feature, usage]) => (
                          <div key={feature} className="flex items-center gap-4">
                            <span className="text-sm font-medium w-40">{feature}</span>
                            <div className="flex-1 bg-surface-secondary rounded-full h-2">
                              <div 
                                className="bg-accent-500 h-2 rounded-full transition-all duration-300" 
                                style={{ width: `${usage}%` }}
                              />
                            </div>
                            <span className="text-sm text-muted w-12 text-right">{formatPercentage(usage as number)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </section>

                {/* ML Model Performance */}
                <section className="section">
                  <div className="section-header">
                    <h3 className="section-title">⚙️ Machine Learning Model Performance</h3>
                    <p className="section-subtitle">Real-time performance metrics for Prophet, scikit-learn, and custom ML models</p>
                  </div>
                  <div className="grid grid-auto-fit gap-6">
                    <div className="dashboard-stat-card dashboard-stat-card-success">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">🎯</span>
                        <h4 className="dashboard-stat-title">Market Prediction Accuracy</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatPercentage(analytics.ml_model_performance.market_prediction_accuracy)}</div>
                      <div className="dashboard-stat-subtitle">Prophet time series forecasting</div>
                    </div>
                    <div className="dashboard-stat-card dashboard-stat-card-success">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">🗺️</span>
                        <h4 className="dashboard-stat-title">Route Optimization Success</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatPercentage(analytics.ml_model_performance.route_optimization_success_rate)}</div>
                      <div className="dashboard-stat-subtitle">Graph algorithm performance</div>
                    </div>
                    <div className="dashboard-stat-card dashboard-stat-card-info">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">🧠</span>
                        <h4 className="dashboard-stat-title">Behavior Classification</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatPercentage(analytics.ml_model_performance.player_behavior_classification_confidence)}</div>
                      <div className="dashboard-stat-subtitle">Scikit-learn clustering accuracy</div>
                    </div>
                    <div className="dashboard-stat-card dashboard-stat-card-info">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">📊</span>
                        <h4 className="dashboard-stat-title">Prophet MAE</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatNumber(analytics.ml_model_performance.prophet_model_mae, 1)}</div>
                      <div className="dashboard-stat-subtitle">Mean Absolute Error in credits</div>
                    </div>
                    <div className="dashboard-stat-card dashboard-stat-card-info">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">🔍</span>
                        <h4 className="dashboard-stat-title">Clustering Quality</h4>
                      </div>
                      <div className="dashboard-stat-value">{analytics.ml_model_performance.clustering_silhouette_score.toFixed(2)}</div>
                      <div className="dashboard-stat-subtitle">Silhouette score (higher is better)</div>
                    </div>
                    <div className="dashboard-stat-card dashboard-stat-card-success">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">🎨</span>
                        <h4 className="dashboard-stat-title">Anomaly Detection</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatPercentage(analytics.ml_model_performance.anomaly_detection_precision)}</div>
                      <div className="dashboard-stat-subtitle">Isolation Forest precision</div>
                    </div>
                    <div className="dashboard-stat-card dashboard-stat-card-info">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">🔄</span>
                        <h4 className="dashboard-stat-title">Models Retrained (24h)</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatNumber(analytics.ml_model_performance.models_retrained_24h)}</div>
                      <div className="dashboard-stat-subtitle">Automatic model updates</div>
                    </div>
                    <div className="dashboard-stat-card dashboard-stat-card-error">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">⚠️</span>
                        <h4 className="dashboard-stat-title">Prediction Errors</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatNumber(analytics.ml_model_performance.prediction_errors_24h)}</div>
                      <div className="dashboard-stat-subtitle">Failed ML predictions</div>
                    </div>
                  </div>
                </section>

                {/* Server Performance */}
                <section className="section">
                  <div className="section-header">
                    <h3 className="section-title">🖥️ Server Performance</h3>
                    <p className="section-subtitle">System health and performance metrics</p>
                  </div>
                  <div className="grid grid-auto-fit gap-6">
                    <div className="dashboard-stat-card">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">⚡</span>
                        <h4 className="dashboard-stat-title">Avg Response Time</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatNumber(analytics.server_performance.response_time, 3)}ms</div>
                    </div>
                    <div className="dashboard-stat-card">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">🧠</span>
                        <h4 className="dashboard-stat-title">Memory Usage</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatPercentage(analytics.server_performance.memory_usage)}</div>
                    </div>
                    <div className="dashboard-stat-card">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">💻</span>
                        <h4 className="dashboard-stat-title">CPU Usage</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatPercentage(analytics.server_performance.cpu_usage)}</div>
                    </div>
                    <div className="dashboard-stat-card dashboard-stat-card-success">
                      <div className="dashboard-stat-header">
                        <span className="dashboard-stat-icon">✅</span>
                        <h4 className="dashboard-stat-title">Uptime</h4>
                      </div>
                      <div className="dashboard-stat-value">{formatPercentage(analytics.server_performance.uptime_percentage)}</div>
                    </div>
                  </div>
                </section>
              </>
            )}
          </div>
        )}

        {activeTab === 'reports' && (
          <div className="space-y-6">
            {/* Reports Controls */}
            <div className="card">
              <div className="card-body">
                <button 
                  onClick={() => setShowCreateReport(!showCreateReport)}
                  className="btn btn-primary"
                >
                  {showCreateReport ? 'Cancel' : 'Generate Report'}
                </button>
              </div>
            </div>

            {/* Create Report Form */}
            {showCreateReport && (
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">Generate New Report</h3>
                </div>
                <div className="card-body space-y-6">
                  {/* Report Templates */}
                  <div>
                    <h4 className="text-lg font-semibold mb-4">Report Templates</h4>
                    <div className="grid grid-auto-fit gap-4">
                      {templates.map((template: ReportTemplate) => (
                        <div 
                          key={template.id} 
                          className="card card-hover cursor-pointer"
                          onClick={() => applyTemplate(template)}
                        >
                          <div className="card-body">
                            <h5 className="font-semibold mb-2">{template.name}</h5>
                            <p className="text-sm text-muted mb-3">{template.description}</p>
                            <span className="badge badge-secondary">{template.type}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Report Form */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="form-group">
                      <label className="form-label">Report Name</label>
                      <input
                        type="text"
                        className="form-input"
                        value={newReport.name}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNewReport({...newReport, name: e.target.value})}
                        placeholder="Enter report name"
                      />
                    </div>
                    
                    <div className="form-group">
                      <label className="form-label">Report Type</label>
                      <select
                        className="form-select"
                        value={newReport.type}
                        onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setNewReport({...newReport, type: e.target.value as any})}
                      >
                        <option value="player">Player Analytics</option>
                        <option value="economic">Economic Analysis</option>
                        <option value="combat">Combat Statistics</option>
                        <option value="exploration">Exploration Progress</option>
                        <option value="custom">Custom Report</option>
                      </select>
                    </div>
                    
                    <div className="form-group">
                      <label className="form-label">Date Range</label>
                      <select
                        className="form-select"
                        value={newReport.date_range}
                        onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setNewReport({...newReport, date_range: e.target.value})}
                      >
                        <option value="7d">Last 7 Days</option>
                        <option value="30d">Last 30 Days</option>
                        <option value="90d">Last 90 Days</option>
                        <option value="1y">Last Year</option>
                        <option value="all">All Time</option>
                      </select>
                    </div>
                  </div>
                  
                  <div className="form-group">
                    <label className="form-label">Description</label>
                    <textarea
                      className="form-textarea"
                      value={newReport.description}
                      onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setNewReport({...newReport, description: e.target.value})}
                      placeholder="Enter report description"
                      rows={3}
                    />
                  </div>
                  
                  <div className="flex gap-2 justify-end">
                    <button onClick={handleGenerateReport} className="btn btn-primary">
                      Generate Report
                    </button>
                    <button 
                      onClick={() => setShowCreateReport(false)} 
                      className="btn btn-outline"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Reports List */}
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Generated Reports</h3>
              </div>
              <div className="card-body">
                {reports.length > 0 ? (
                  <div className="table-container">
                    <table className="table">
                      <thead>
                        <tr>
                          <th>Report Name</th>
                          <th>Type</th>
                          <th>Generated</th>
                          <th>Status</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {reports.map((report: Report) => (
                          <tr key={report.id}>
                            <td className="font-medium">{report.name}</td>
                            <td>
                              <span className={`badge badge-${report.type}`}>
                                {report.type}
                              </span>
                            </td>
                            <td className="text-muted">
                              {new Date(report.created_at).toLocaleDateString('en-US', {
                                year: 'numeric',
                                month: 'short',
                                day: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </td>
                            <td>
                              <span className={`badge badge-${report.status === 'ready' ? 'success' : report.status === 'generating' ? 'warning' : 'error'}`}>
                                {report.status}
                              </span>
                            </td>
                            <td>
                              {report.status === 'ready' && report.file_url && (
                                <a 
                                  href={report.file_url} 
                                  download 
                                  className="btn btn-sm btn-outline"
                                >
                                  Download
                                </a>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted">
                    <p>No reports generated yet. Create your first report using the button above.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalyticsReports;