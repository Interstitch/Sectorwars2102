import React, { useState } from 'react';
import PageHeader from '../ui/PageHeader';
import { CustomReportBuilder } from '../analytics/CustomReportBuilder';
import { PredictiveAnalytics } from '../analytics/PredictiveAnalytics';
import { PerformanceMetrics } from '../analytics/PerformanceMetrics';
import './advanced-analytics.css';

interface ReportResult {
  id: string;
  name: string;
  generatedAt: string;
  data: any;
  template: any;
}

export const AdvancedAnalytics: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'reports' | 'predictive' | 'performance' | 'export'>('reports');
  const [generatedReports, setGeneratedReports] = useState<ReportResult[]>([]);
  const [selectedReport, setSelectedReport] = useState<ReportResult | null>(null);
  const [exportFormat, setExportFormat] = useState<'csv' | 'json' | 'excel' | 'pdf'>('csv');
  const [exportLoading, setExportLoading] = useState(false);

  const handleGenerateReport = async (template: any) => {
    try {
      const response = await fetch('/api/v1/admin/reports/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        },
        body: JSON.stringify(template)
      });

      if (response.ok) {
        const report = await response.json();
        setGeneratedReports([report, ...generatedReports]);
        setSelectedReport(report);
        alert(`Report "${template.name}" generated successfully!`);
      } else {
        alert('Failed to generate report. Server returned an error.');
      }
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Failed to generate report. Please check your connection and try again.');
    }
  };

  const handleExportData = async (dataType: string) => {
    setExportLoading(true);
    try {
      const response = await fetch(`/api/v1/admin/analytics/export?type=${dataType}&format=${exportFormat}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
        }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${dataType}-export-${Date.now()}.${exportFormat === 'excel' ? 'xlsx' : exportFormat}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        alert(`Data exported successfully as ${exportFormat.toUpperCase()}`);
      } else {
        alert('Failed to export data. Server returned an error.');
      }
    } catch (error) {
      console.error('Error exporting data:', error);
      alert('Failed to export data. Please check your connection and try again.');
    } finally {
      setExportLoading(false);
    }
  };

  const exportOptions = [
    { id: 'players', name: 'Player Data', description: 'Export all player information including stats and activity' },
    { id: 'economy', name: 'Economy Data', description: 'Export transaction history and market data' },
    { id: 'combat', name: 'Combat Logs', description: 'Export combat encounters and battle statistics' },
    { id: 'teams', name: 'Team Data', description: 'Export team information and alliance data' },
    { id: 'ships', name: 'Fleet Data', description: 'Export ship information and fleet statistics' },
    { id: 'performance', name: 'Performance Metrics', description: 'Export system performance and optimization data' }
  ];

  return (
    <div className="advanced-analytics">
      <PageHeader
        title="Advanced Analytics"
        subtitle="Generate custom reports, view predictions, and export data"
      />

      <div className="analytics-tabs">
        <button
          className={`tab ${activeTab === 'reports' ? 'active' : ''}`}
          onClick={() => setActiveTab('reports')}
        >
          <i className="fas fa-file-alt"></i>
          Custom Reports
        </button>
        <button
          className={`tab ${activeTab === 'predictive' ? 'active' : ''}`}
          onClick={() => setActiveTab('predictive')}
        >
          <i className="fas fa-chart-line"></i>
          Predictive Analytics
        </button>
        <button
          className={`tab ${activeTab === 'performance' ? 'active' : ''}`}
          onClick={() => setActiveTab('performance')}
        >
          <i className="fas fa-tachometer-alt"></i>
          Performance
        </button>
        <button
          className={`tab ${activeTab === 'export' ? 'active' : ''}`}
          onClick={() => setActiveTab('export')}
        >
          <i className="fas fa-download"></i>
          Data Export
        </button>
      </div>

      <div className="analytics-content">
        {activeTab === 'reports' && (
          <div className="reports-section">
            <div className="reports-builder">
              <CustomReportBuilder 
                onGenerate={handleGenerateReport}
                onSave={(template) => console.log('Save template:', template)}
              />
            </div>
            
            {generatedReports.length > 0 && (
              <div className="generated-reports">
                <h3>Generated Reports</h3>
                <div className="reports-list">
                  {generatedReports.map(report => (
                    <div
                      key={report.id}
                      className={`report-item ${selectedReport?.id === report.id ? 'selected' : ''}`}
                      onClick={() => setSelectedReport(report)}
                    >
                      <div className="report-header">
                        <h4>{report.name}</h4>
                        <span className="report-time">
                          {new Date(report.generatedAt).toLocaleString()}
                        </span>
                      </div>
                      <div className="report-actions">
                        <button className="btn-icon" title="Download">
                          <i className="fas fa-download"></i>
                        </button>
                        <button className="btn-icon" title="Share">
                          <i className="fas fa-share"></i>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'predictive' && (
          <PredictiveAnalytics />
        )}

        {activeTab === 'performance' && (
          <PerformanceMetrics />
        )}

        {activeTab === 'export' && (
          <div className="export-section">
            <div className="export-header">
              <h2>Data Export Center</h2>
              <p>Export your game data in various formats for external analysis</p>
            </div>

            <div className="export-format">
              <h3>Select Export Format</h3>
              <div className="format-options">
                <label className={`format-option ${exportFormat === 'csv' ? 'selected' : ''}`}>
                  <input
                    type="radio"
                    value="csv"
                    checked={exportFormat === 'csv'}
                    onChange={(e) => setExportFormat(e.target.value as any)}
                  />
                  <i className="fas fa-file-csv"></i>
                  <span>CSV</span>
                  <small>Comma-separated values</small>
                </label>
                <label className={`format-option ${exportFormat === 'json' ? 'selected' : ''}`}>
                  <input
                    type="radio"
                    value="json"
                    checked={exportFormat === 'json'}
                    onChange={(e) => setExportFormat(e.target.value as any)}
                  />
                  <i className="fas fa-file-code"></i>
                  <span>JSON</span>
                  <small>JavaScript Object Notation</small>
                </label>
                <label className={`format-option ${exportFormat === 'excel' ? 'selected' : ''}`}>
                  <input
                    type="radio"
                    value="excel"
                    checked={exportFormat === 'excel'}
                    onChange={(e) => setExportFormat(e.target.value as any)}
                  />
                  <i className="fas fa-file-excel"></i>
                  <span>Excel</span>
                  <small>Microsoft Excel format</small>
                </label>
                <label className={`format-option ${exportFormat === 'pdf' ? 'selected' : ''}`}>
                  <input
                    type="radio"
                    value="pdf"
                    checked={exportFormat === 'pdf'}
                    onChange={(e) => setExportFormat(e.target.value as any)}
                  />
                  <i className="fas fa-file-pdf"></i>
                  <span>PDF</span>
                  <small>Portable Document Format</small>
                </label>
              </div>
            </div>

            <div className="export-options">
              <h3>Available Data Exports</h3>
              <div className="export-grid">
                {exportOptions.map(option => (
                  <div key={option.id} className="export-card">
                    <div className="export-icon">
                      <i className={`fas fa-${
                        option.id === 'players' ? 'users' :
                        option.id === 'economy' ? 'chart-line' :
                        option.id === 'combat' ? 'swords' :
                        option.id === 'teams' ? 'user-friends' :
                        option.id === 'ships' ? 'rocket' :
                        'chart-bar'
                      }`}></i>
                    </div>
                    <div className="export-info">
                      <h4>{option.name}</h4>
                      <p>{option.description}</p>
                    </div>
                    <button
                      className="btn btn-primary"
                      onClick={() => handleExportData(option.id)}
                      disabled={exportLoading}
                    >
                      {exportLoading ? (
                        <>
                          <i className="fas fa-spinner fa-spin"></i>
                          Exporting...
                        </>
                      ) : (
                        <>
                          <i className="fas fa-download"></i>
                          Export
                        </>
                      )}
                    </button>
                  </div>
                ))}
              </div>
            </div>

            <div className="export-history">
              <h3>Recent Exports</h3>
              <div className="history-list">
                <div style={{ padding: '20px', textAlign: 'center', color: '#9ca3af' }}>
                  <i className="fas fa-history" style={{ fontSize: '1.5rem', marginBottom: '8px', display: 'block' }}></i>
                  No export history available.
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};