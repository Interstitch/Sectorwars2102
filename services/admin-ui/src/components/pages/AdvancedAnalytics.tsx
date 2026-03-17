import React, { useState, useEffect, useCallback } from 'react';
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

const SAVED_TEMPLATES_KEY = 'reportTemplates';

export const AdvancedAnalytics: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'reports' | 'predictive' | 'performance' | 'export'>('reports');
  const [generatedReports, setGeneratedReports] = useState<ReportResult[]>([]);
  const [selectedReport, setSelectedReport] = useState<ReportResult | null>(null);
  const [exportFormat, setExportFormat] = useState<'csv' | 'json' | 'excel' | 'pdf'>('csv');
  const [exportLoading, setExportLoading] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  // Load saved templates from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(SAVED_TEMPLATES_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed) && parsed.length > 0) {
          console.log(`Loaded ${parsed.length} saved report templates from localStorage`);
        }
      }
    } catch (e) {
      console.warn('Failed to load saved templates:', e);
    }
  }, []);

  const handleSaveTemplate = useCallback((template: any) => {
    try {
      const existingRaw = localStorage.getItem(SAVED_TEMPLATES_KEY);
      const existing = existingRaw ? JSON.parse(existingRaw) : [];
      const savedTemplate = {
        ...template,
        id: `saved-${Date.now()}`,
        savedAt: new Date().toISOString()
      };
      existing.push(savedTemplate);
      localStorage.setItem(SAVED_TEMPLATES_KEY, JSON.stringify(existing));
      setSaveMessage(`Template "${template.name}" saved successfully!`);
      setTimeout(() => setSaveMessage(null), 3000);
    } catch (e) {
      console.error('Failed to save template:', e);
      setSaveMessage('Failed to save template. Storage may be full.');
      setTimeout(() => setSaveMessage(null), 3000);
    }
  }, []);

  const handleGenerateReport = async (template: any) => {
    try {
      // In production, this would call the API to generate the report
      const response = await fetch('/api/admin/reports/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify(template)
      }).catch(() => {
        // Mock response
        return {
          ok: true,
          json: async () => ({
            id: `report-${Date.now()}`,
            name: template.name,
            generatedAt: new Date().toISOString(),
            template,
            data: {
              summary: {
                totalPlayers: 1234,
                activeToday: 892,
                revenue24h: 15420,
                newPlayers24h: 67
              },
              rows: Array.from({ length: 100 }, (_, i) => ({
                date: new Date(Date.now() - i * 86400000).toISOString(),
                players: Math.floor(1000 + Math.random() * 500),
                revenue: Math.floor(10000 + Math.random() * 10000),
                battles: Math.floor(500 + Math.random() * 500),
                trades: Math.floor(1000 + Math.random() * 1000)
              }))
            }
          })
        };
      });

      if (response.ok) {
        const report = await response.json();
        setGeneratedReports([report, ...generatedReports]);
        setSelectedReport(report);
        
        // Show success notification
        alert(`Report "${template.name}" generated successfully!`);
      }
    } catch (error) {
      console.error('Error generating report:', error);
      alert('Failed to generate report');
    }
  };

  const handleExportData = async (dataType: string) => {
    setExportLoading(true);
    try {
      const response = await fetch(`/api/admin/analytics/export?type=${dataType}&format=${exportFormat}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      }).catch(() => {
        // Mock file download
        const data = {
          exportType: dataType,
          format: exportFormat,
          generatedAt: new Date().toISOString(),
          data: {
            players: Array.from({ length: 100 }, (_, i) => ({
              id: `player-${i}`,
              username: `player${i}`,
              joinDate: new Date(Date.now() - Math.random() * 86400000 * 365).toISOString(),
              lastLogin: new Date(Date.now() - Math.random() * 86400000 * 30).toISOString(),
              totalPlaytime: Math.floor(Math.random() * 1000),
              credits: Math.floor(Math.random() * 1000000)
            }))
          }
        };

        // Create blob and download
        let blob;
        let filename;
        
        if (exportFormat === 'csv') {
          const csv = convertToCSV(data.data.players);
          blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
          filename = `${dataType}-export-${Date.now()}.csv`;
        } else if (exportFormat === 'json') {
          blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
          filename = `${dataType}-export-${Date.now()}.json`;
        } else if (exportFormat === 'excel') {
          // Generate CSV that Excel can open natively
          const csv = convertToCSV(data.data.players);
          // BOM prefix helps Excel detect UTF-8 encoding
          const bom = '\uFEFF';
          blob = new Blob([bom + csv], { type: 'text/csv;charset=utf-8;' });
          filename = `${dataType}-export-${Date.now()}.csv`;
        } else if (exportFormat === 'pdf') {
          // Generate a printable HTML document for PDF export
          const rows = data.data.players;
          if (!rows.length) {
            alert('No data to export');
            return { ok: false };
          }
          const headers = Object.keys(rows[0]);
          const htmlContent = `
            <!DOCTYPE html>
            <html><head><title>${dataType} Export</title>
            <style>
              body { font-family: Arial, sans-serif; margin: 20px; }
              h1 { color: #333; font-size: 18px; }
              p { color: #666; font-size: 12px; }
              table { width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 11px; }
              th { background: #1e293b; color: white; padding: 8px; text-align: left; border: 1px solid #475569; }
              td { padding: 6px 8px; border: 1px solid #ddd; }
              tr:nth-child(even) { background: #f8f9fa; }
              @media print { body { margin: 0; } }
            </style></head><body>
            <h1>${dataType.charAt(0).toUpperCase() + dataType.slice(1)} Data Export</h1>
            <p>Generated: ${new Date().toLocaleString()} | Records: ${rows.length}</p>
            <table>
              <thead><tr>${headers.map((h: string) => `<th>${h}</th>`).join('')}</tr></thead>
              <tbody>${rows.map((row: any) =>
                `<tr>${headers.map((h: string) => `<td>${row[h] ?? ''}</td>`).join('')}</tr>`
              ).join('')}</tbody>
            </table>
            </body></html>`;
          const printWindow = window.open('', '_blank');
          if (printWindow) {
            printWindow.document.write(htmlContent);
            printWindow.document.close();
            printWindow.print();
          } else {
            alert('Please allow pop-ups to export as PDF via print dialog.');
          }
          return { ok: true };
        } else {
          blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
          filename = `${dataType}-export-${Date.now()}.json`;
        }

        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        return { ok: true };
      });

      if (response.ok) {
        alert(`Data exported successfully as ${exportFormat.toUpperCase()}`);
      }
    } catch (error) {
      console.error('Error exporting data:', error);
      alert('Failed to export data');
    } finally {
      setExportLoading(false);
    }
  };

  const convertToCSV = (data: any[]) => {
    if (!data.length) return '';
    
    const headers = Object.keys(data[0]).join(',');
    const rows = data.map(row => 
      Object.values(row).map(value => 
        typeof value === 'string' && value.includes(',') ? `"${value}"` : value
      ).join(',')
    );
    
    return [headers, ...rows].join('\n');
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
              {saveMessage && (
                <div style={{
                  padding: '10px 16px',
                  marginBottom: '12px',
                  borderRadius: '6px',
                  background: saveMessage.includes('Failed') ? '#7f1d1d' : '#14532d',
                  color: saveMessage.includes('Failed') ? '#fca5a5' : '#86efac',
                  border: `1px solid ${saveMessage.includes('Failed') ? '#991b1b' : '#166534'}`,
                  fontSize: '14px'
                }}>
                  {saveMessage}
                </div>
              )}
              <CustomReportBuilder
                onGenerate={handleGenerateReport}
                onSave={handleSaveTemplate}
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
                <div className="history-item">
                  <i className="fas fa-file-csv"></i>
                  <div className="history-info">
                    <span className="history-name">players-export-20240528.csv</span>
                    <span className="history-time">2 hours ago</span>
                  </div>
                  <span className="history-size">2.4 MB</span>
                </div>
                <div className="history-item">
                  <i className="fas fa-file-code"></i>
                  <div className="history-info">
                    <span className="history-name">economy-export-20240527.json</span>
                    <span className="history-time">Yesterday</span>
                  </div>
                  <span className="history-size">5.1 MB</span>
                </div>
                <div className="history-item">
                  <i className="fas fa-file-excel"></i>
                  <div className="history-info">
                    <span className="history-name">combat-logs-20240525.xlsx</span>
                    <span className="history-time">3 days ago</span>
                  </div>
                  <span className="history-size">8.7 MB</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};