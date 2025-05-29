import React, { useState, useEffect } from 'react';
import './custom-report-builder.css';

interface ReportMetric {
  id: string;
  name: string;
  category: string;
  dataType: 'number' | 'currency' | 'percentage' | 'date' | 'string';
  aggregations: string[];
  description: string;
}

interface ReportFilter {
  id: string;
  field: string;
  operator: string;
  value: any;
}

interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  metrics: string[];
  filters: ReportFilter[];
  groupBy: string[];
  sortBy: { field: string; direction: 'asc' | 'desc' }[];
  visualization: 'table' | 'chart' | 'both';
  chartType?: 'line' | 'bar' | 'pie' | 'area' | 'scatter';
  schedule?: {
    frequency: 'daily' | 'weekly' | 'monthly';
    recipients: string[];
  };
}

interface CustomReportBuilderProps {
  onGenerate: (template: ReportTemplate) => void;
  onSave?: (template: ReportTemplate) => void;
}

export const CustomReportBuilder: React.FC<CustomReportBuilderProps> = ({ onGenerate, onSave }) => {
  const [availableMetrics, setAvailableMetrics] = useState<ReportMetric[]>([]);
  const [templates, setTemplates] = useState<ReportTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<ReportTemplate | null>(null);
  const [currentReport, setCurrentReport] = useState<Partial<ReportTemplate>>({
    name: '',
    description: '',
    metrics: [],
    filters: [],
    groupBy: [],
    sortBy: [],
    visualization: 'table'
  });
  const [activeTab, setActiveTab] = useState<'metrics' | 'filters' | 'visualization' | 'schedule'>('metrics');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReportData();
  }, []);

  const fetchReportData = async () => {
    setLoading(true);
    try {
      // Fetch available metrics and templates
      const [metricsResponse, templatesResponse] = await Promise.all([
        fetch('/api/admin/reports/metrics', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
        }).catch(() => ({
          ok: true,
          json: async () => ({
            metrics: [
              // Player metrics
              { id: 'player.count', name: 'Total Players', category: 'Players', dataType: 'number', aggregations: ['sum', 'avg'], description: 'Total number of players' },
              { id: 'player.active', name: 'Active Players', category: 'Players', dataType: 'number', aggregations: ['sum', 'avg'], description: 'Currently active players' },
              { id: 'player.new', name: 'New Players', category: 'Players', dataType: 'number', aggregations: ['sum'], description: 'New player registrations' },
              { id: 'player.retention', name: 'Player Retention', category: 'Players', dataType: 'percentage', aggregations: ['avg'], description: 'Player retention rate' },
              
              // Economy metrics
              { id: 'economy.volume', name: 'Trade Volume', category: 'Economy', dataType: 'currency', aggregations: ['sum', 'avg'], description: 'Total trade volume' },
              { id: 'economy.transactions', name: 'Transaction Count', category: 'Economy', dataType: 'number', aggregations: ['sum', 'avg'], description: 'Number of transactions' },
              { id: 'economy.inflation', name: 'Inflation Rate', category: 'Economy', dataType: 'percentage', aggregations: ['avg'], description: 'Economic inflation rate' },
              { id: 'economy.gdp', name: 'GDP', category: 'Economy', dataType: 'currency', aggregations: ['sum'], description: 'Gross domestic product' },
              
              // Combat metrics
              { id: 'combat.battles', name: 'Total Battles', category: 'Combat', dataType: 'number', aggregations: ['sum'], description: 'Total combat encounters' },
              { id: 'combat.casualties', name: 'Ship Casualties', category: 'Combat', dataType: 'number', aggregations: ['sum', 'avg'], description: 'Ships destroyed in combat' },
              { id: 'combat.damage', name: 'Damage Dealt', category: 'Combat', dataType: 'number', aggregations: ['sum', 'avg', 'max'], description: 'Total damage in combat' },
              
              // Fleet metrics
              { id: 'fleet.ships', name: 'Total Ships', category: 'Fleet', dataType: 'number', aggregations: ['sum', 'avg'], description: 'Total ships in game' },
              { id: 'fleet.health', name: 'Average Fleet Health', category: 'Fleet', dataType: 'percentage', aggregations: ['avg'], description: 'Average fleet health' },
              { id: 'fleet.maintenance', name: 'Maintenance Cost', category: 'Fleet', dataType: 'currency', aggregations: ['sum', 'avg'], description: 'Fleet maintenance costs' },
              
              // Team metrics
              { id: 'team.count', name: 'Total Teams', category: 'Teams', dataType: 'number', aggregations: ['sum'], description: 'Number of teams' },
              { id: 'team.members', name: 'Average Team Size', category: 'Teams', dataType: 'number', aggregations: ['avg'], description: 'Average members per team' },
              { id: 'team.activity', name: 'Team Activity', category: 'Teams', dataType: 'percentage', aggregations: ['avg'], description: 'Team activity level' }
            ]
          })
        })),
        fetch('/api/admin/reports/templates', {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
        }).catch(() => ({
          ok: true,
          json: async () => ({
            templates: [
              {
                id: 'daily-overview',
                name: 'Daily Overview Report',
                description: 'Daily summary of key metrics',
                metrics: ['player.active', 'economy.volume', 'combat.battles'],
                filters: [],
                groupBy: [],
                sortBy: [],
                visualization: 'both',
                chartType: 'line'
              },
              {
                id: 'economy-health',
                name: 'Economy Health Report',
                description: 'Detailed economic analysis',
                metrics: ['economy.volume', 'economy.transactions', 'economy.inflation', 'economy.gdp'],
                filters: [],
                groupBy: ['date'],
                sortBy: [{ field: 'date', direction: 'desc' }],
                visualization: 'chart',
                chartType: 'area'
              },
              {
                id: 'player-engagement',
                name: 'Player Engagement Report',
                description: 'Player activity and retention analysis',
                metrics: ['player.active', 'player.new', 'player.retention'],
                filters: [],
                groupBy: ['date'],
                sortBy: [{ field: 'date', direction: 'desc' }],
                visualization: 'both',
                chartType: 'bar'
              }
            ]
          })
        }))
      ]);

      if (metricsResponse.ok && templatesResponse.ok) {
        const metricsData = await metricsResponse.json();
        const templatesData = await templatesResponse.json();
        setAvailableMetrics(metricsData.metrics);
        setTemplates(templatesData.templates);
      }
    } catch (error) {
      console.error('Error fetching report data:', error);
    } finally {
      setLoading(false);
    }
  };

  const groupMetricsByCategory = () => {
    const grouped: Record<string, ReportMetric[]> = {};
    availableMetrics.forEach(metric => {
      if (!grouped[metric.category]) {
        grouped[metric.category] = [];
      }
      grouped[metric.category].push(metric);
    });
    return grouped;
  };

  const toggleMetric = (metricId: string) => {
    setCurrentReport(prev => ({
      ...prev,
      metrics: prev.metrics?.includes(metricId)
        ? prev.metrics.filter(m => m !== metricId)
        : [...(prev.metrics || []), metricId]
    }));
  };

  const addFilter = () => {
    const newFilter: ReportFilter = {
      id: `filter-${Date.now()}`,
      field: '',
      operator: 'equals',
      value: ''
    };
    setCurrentReport(prev => ({
      ...prev,
      filters: [...(prev.filters || []), newFilter]
    }));
  };

  const updateFilter = (filterId: string, updates: Partial<ReportFilter>) => {
    setCurrentReport(prev => ({
      ...prev,
      filters: prev.filters?.map(f => 
        f.id === filterId ? { ...f, ...updates } : f
      ) || []
    }));
  };

  const removeFilter = (filterId: string) => {
    setCurrentReport(prev => ({
      ...prev,
      filters: prev.filters?.filter(f => f.id !== filterId) || []
    }));
  };

  const handleGenerateReport = () => {
    if (!currentReport.name || !currentReport.metrics?.length) {
      alert('Please provide a report name and select at least one metric');
      return;
    }

    const template: ReportTemplate = {
      id: `custom-${Date.now()}`,
      name: currentReport.name,
      description: currentReport.description || '',
      metrics: currentReport.metrics,
      filters: currentReport.filters || [],
      groupBy: currentReport.groupBy || [],
      sortBy: currentReport.sortBy || [],
      visualization: currentReport.visualization || 'table',
      chartType: currentReport.chartType,
      schedule: currentReport.schedule
    };

    onGenerate(template);
  };

  const handleSaveTemplate = () => {
    if (!currentReport.name || !currentReport.metrics?.length) {
      alert('Please provide a report name and select at least one metric');
      return;
    }

    const template: ReportTemplate = {
      id: `template-${Date.now()}`,
      name: currentReport.name,
      description: currentReport.description || '',
      metrics: currentReport.metrics,
      filters: currentReport.filters || [],
      groupBy: currentReport.groupBy || [],
      sortBy: currentReport.sortBy || [],
      visualization: currentReport.visualization || 'table',
      chartType: currentReport.chartType,
      schedule: currentReport.schedule
    };

    onSave?.(template);
    setTemplates([...templates, template]);
  };

  const loadTemplate = (template: ReportTemplate) => {
    setSelectedTemplate(template);
    setCurrentReport({
      name: template.name,
      description: template.description,
      metrics: template.metrics,
      filters: template.filters,
      groupBy: template.groupBy,
      sortBy: template.sortBy,
      visualization: template.visualization,
      chartType: template.chartType,
      schedule: template.schedule
    });
  };

  if (loading) {
    return (
      <div className="report-builder-loading">
        <i className="fas fa-spinner fa-spin"></i>
        <span>Loading report builder...</span>
      </div>
    );
  }

  const groupedMetrics = groupMetricsByCategory();

  return (
    <div className="custom-report-builder">
      <div className="report-builder-header">
        <h2>Custom Report Builder</h2>
        <div className="header-actions">
          <button className="btn btn-secondary" onClick={handleSaveTemplate}>
            <i className="fas fa-save"></i>
            Save as Template
          </button>
          <button className="btn btn-primary" onClick={handleGenerateReport}>
            <i className="fas fa-play"></i>
            Generate Report
          </button>
        </div>
      </div>

      <div className="report-builder-content">
        <div className="report-templates">
          <h3>Report Templates</h3>
          <div className="template-list">
            {templates.map(template => (
              <div
                key={template.id}
                className={`template-item ${selectedTemplate?.id === template.id ? 'selected' : ''}`}
                onClick={() => loadTemplate(template)}
              >
                <div className="template-name">{template.name}</div>
                <div className="template-description">{template.description}</div>
                <div className="template-metrics">{template.metrics.length} metrics</div>
              </div>
            ))}
          </div>
        </div>

        <div className="report-configuration">
          <div className="config-header">
            <input
              type="text"
              placeholder="Report Name"
              value={currentReport.name}
              onChange={(e) => setCurrentReport({ ...currentReport, name: e.target.value })}
              className="report-name-input"
            />
            <textarea
              placeholder="Report Description (optional)"
              value={currentReport.description}
              onChange={(e) => setCurrentReport({ ...currentReport, description: e.target.value })}
              className="report-description-input"
              rows={2}
            />
          </div>

          <div className="config-tabs">
            <button
              className={`tab ${activeTab === 'metrics' ? 'active' : ''}`}
              onClick={() => setActiveTab('metrics')}
            >
              <i className="fas fa-chart-line"></i>
              Metrics
            </button>
            <button
              className={`tab ${activeTab === 'filters' ? 'active' : ''}`}
              onClick={() => setActiveTab('filters')}
            >
              <i className="fas fa-filter"></i>
              Filters
            </button>
            <button
              className={`tab ${activeTab === 'visualization' ? 'active' : ''}`}
              onClick={() => setActiveTab('visualization')}
            >
              <i className="fas fa-chart-bar"></i>
              Visualization
            </button>
            <button
              className={`tab ${activeTab === 'schedule' ? 'active' : ''}`}
              onClick={() => setActiveTab('schedule')}
            >
              <i className="fas fa-clock"></i>
              Schedule
            </button>
          </div>

          <div className="config-content">
            {activeTab === 'metrics' && (
              <div className="metrics-selection">
                <h4>Select Metrics ({currentReport.metrics?.length || 0} selected)</h4>
                {Object.entries(groupedMetrics).map(([category, metrics]) => (
                  <div key={category} className="metric-category">
                    <h5>{category}</h5>
                    <div className="metric-list">
                      {metrics.map(metric => (
                        <label key={metric.id} className="metric-item">
                          <input
                            type="checkbox"
                            checked={currentReport.metrics?.includes(metric.id) || false}
                            onChange={() => toggleMetric(metric.id)}
                          />
                          <div className="metric-info">
                            <span className="metric-name">{metric.name}</span>
                            <span className="metric-description">{metric.description}</span>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'filters' && (
              <div className="filters-configuration">
                <div className="filters-header">
                  <h4>Report Filters</h4>
                  <button className="btn btn-sm btn-primary" onClick={addFilter}>
                    <i className="fas fa-plus"></i>
                    Add Filter
                  </button>
                </div>
                <div className="filter-list">
                  {currentReport.filters?.map(filter => (
                    <div key={filter.id} className="filter-item">
                      <select
                        value={filter.field}
                        onChange={(e) => updateFilter(filter.id, { field: e.target.value })}
                        className="filter-field"
                      >
                        <option value="">Select field...</option>
                        <option value="date">Date</option>
                        <option value="player">Player</option>
                        <option value="team">Team</option>
                        <option value="sector">Sector</option>
                      </select>
                      <select
                        value={filter.operator}
                        onChange={(e) => updateFilter(filter.id, { operator: e.target.value })}
                        className="filter-operator"
                      >
                        <option value="equals">Equals</option>
                        <option value="not_equals">Not Equals</option>
                        <option value="greater_than">Greater Than</option>
                        <option value="less_than">Less Than</option>
                        <option value="between">Between</option>
                      </select>
                      <input
                        type="text"
                        value={filter.value}
                        onChange={(e) => updateFilter(filter.id, { value: e.target.value })}
                        placeholder="Value"
                        className="filter-value"
                      />
                      <button
                        className="btn-icon delete"
                        onClick={() => removeFilter(filter.id)}
                      >
                        <i className="fas fa-trash"></i>
                      </button>
                    </div>
                  ))}
                  {(!currentReport.filters || currentReport.filters.length === 0) && (
                    <div className="no-filters">No filters configured</div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'visualization' && (
              <div className="visualization-configuration">
                <h4>Visualization Options</h4>
                <div className="viz-options">
                  <div className="viz-type">
                    <label>Display Type:</label>
                    <select
                      value={currentReport.visualization}
                      onChange={(e) => setCurrentReport({ ...currentReport, visualization: e.target.value as any })}
                    >
                      <option value="table">Table Only</option>
                      <option value="chart">Chart Only</option>
                      <option value="both">Table & Chart</option>
                    </select>
                  </div>
                  {(currentReport.visualization === 'chart' || currentReport.visualization === 'both') && (
                    <div className="chart-type">
                      <label>Chart Type:</label>
                      <select
                        value={currentReport.chartType || 'line'}
                        onChange={(e) => setCurrentReport({ ...currentReport, chartType: e.target.value as any })}
                      >
                        <option value="line">Line Chart</option>
                        <option value="bar">Bar Chart</option>
                        <option value="pie">Pie Chart</option>
                        <option value="area">Area Chart</option>
                        <option value="scatter">Scatter Plot</option>
                      </select>
                    </div>
                  )}
                  <div className="group-by">
                    <label>Group By:</label>
                    <select
                      value={currentReport.groupBy?.[0] || ''}
                      onChange={(e) => setCurrentReport({ 
                        ...currentReport, 
                        groupBy: e.target.value ? [e.target.value] : [] 
                      })}
                    >
                      <option value="">None</option>
                      <option value="date">Date</option>
                      <option value="hour">Hour</option>
                      <option value="player">Player</option>
                      <option value="team">Team</option>
                      <option value="sector">Sector</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'schedule' && (
              <div className="schedule-configuration">
                <h4>Report Scheduling</h4>
                <div className="schedule-options">
                  <label className="schedule-enable">
                    <input
                      type="checkbox"
                      checked={!!currentReport.schedule}
                      onChange={(e) => setCurrentReport({
                        ...currentReport,
                        schedule: e.target.checked ? {
                          frequency: 'daily',
                          recipients: []
                        } : undefined
                      })}
                    />
                    Enable scheduled delivery
                  </label>
                  {currentReport.schedule && (
                    <>
                      <div className="schedule-frequency">
                        <label>Frequency:</label>
                        <select
                          value={currentReport.schedule.frequency}
                          onChange={(e) => setCurrentReport({
                            ...currentReport,
                            schedule: {
                              ...currentReport.schedule!,
                              frequency: e.target.value as any
                            }
                          })}
                        >
                          <option value="daily">Daily</option>
                          <option value="weekly">Weekly</option>
                          <option value="monthly">Monthly</option>
                        </select>
                      </div>
                      <div className="schedule-recipients">
                        <label>Email Recipients:</label>
                        <textarea
                          placeholder="Enter email addresses, one per line"
                          value={currentReport.schedule.recipients.join('\n')}
                          onChange={(e) => setCurrentReport({
                            ...currentReport,
                            schedule: {
                              ...currentReport.schedule!,
                              recipients: e.target.value.split('\n').filter(email => email.trim())
                            }
                          })}
                          rows={3}
                        />
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};