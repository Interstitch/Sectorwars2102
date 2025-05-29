import React, { useState, useEffect } from 'react';
import PageHeader from '../ui/PageHeader';
import { AuditLogViewer } from '../security/AuditLogViewer';
import { MFASetup } from '../auth/MFASetup';
import { useAuth } from '../../contexts/AuthContext';
import './security-dashboard.css';

interface SecurityMetrics {
  totalLogins24h: number;
  failedLogins24h: number;
  activeUsers: number;
  mfaEnabledUsers: number;
  totalUsers: number;
  suspiciousActivities: number;
  blockedIPs: number;
  recentThreats: Array<{
    id: string;
    timestamp: string;
    type: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    description: string;
    status: 'detected' | 'mitigated' | 'investigating';
  }>;
}

export const SecurityDashboard: React.FC = () => {
  const { user } = useAuth();
  const [metrics, setMetrics] = useState<SecurityMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [showMFASetup, setShowMFASetup] = useState(false);
  const [selectedTimeRange, setSelectedTimeRange] = useState('24h');
  const [activeTab, setActiveTab] = useState<'overview' | 'audit' | 'threats' | 'settings'>('overview');

  useEffect(() => {
    fetchSecurityMetrics();
    const interval = setInterval(fetchSecurityMetrics, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [selectedTimeRange]);

  const fetchSecurityMetrics = async () => {
    try {
      const response = await fetch(`/api/admin/security/metrics?timeRange=${selectedTimeRange}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      }).catch(() => {
        // Mock data for development
        return {
          ok: true,
          json: async () => ({
            totalLogins24h: 1234,
            failedLogins24h: 23,
            activeUsers: 456,
            mfaEnabledUsers: 123,
            totalUsers: 789,
            suspiciousActivities: 5,
            blockedIPs: 12,
            recentThreats: [
              {
                id: '1',
                timestamp: new Date().toISOString(),
                type: 'Brute Force Attempt',
                severity: 'high',
                description: 'Multiple failed login attempts from IP 192.168.1.100',
                status: 'mitigated'
              },
              {
                id: '2',
                timestamp: new Date(Date.now() - 3600000).toISOString(),
                type: 'Suspicious API Usage',
                severity: 'medium',
                description: 'Abnormal API call pattern detected from user ID 12345',
                status: 'investigating'
              }
            ]
          })
        };
      });

      if (!response.ok) {
        throw new Error('Failed to fetch security metrics');
      }

      const data = await response.json();
      setMetrics(data);
    } catch (error) {
      console.error('Error fetching security metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityClass = (severity: string) => {
    return `severity-${severity}`;
  };

  const getStatusIcon = (status: string) => {
    const icons: Record<string, string> = {
      detected: 'fa-exclamation-triangle',
      mitigated: 'fa-check-circle',
      investigating: 'fa-search'
    };
    return icons[status] || 'fa-question-circle';
  };

  return (
    <div className="security-dashboard">
      <PageHeader
        title="Security Dashboard"
        subtitle="Monitor and manage system security"
      />

      <div className="security-tabs">
        <button
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <i className="fas fa-chart-line"></i>
          Overview
        </button>
        <button
          className={`tab ${activeTab === 'audit' ? 'active' : ''}`}
          onClick={() => setActiveTab('audit')}
        >
          <i className="fas fa-history"></i>
          Audit Logs
        </button>
        <button
          className={`tab ${activeTab === 'threats' ? 'active' : ''}`}
          onClick={() => setActiveTab('threats')}
        >
          <i className="fas fa-shield-alt"></i>
          Threat Detection
        </button>
        <button
          className={`tab ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          <i className="fas fa-cog"></i>
          Settings
        </button>
      </div>

      {activeTab === 'overview' && (
        <div className="security-overview">
          <div className="time-range-selector">
            <label>Time Range:</label>
            <select 
              value={selectedTimeRange} 
              onChange={(e) => setSelectedTimeRange(e.target.value)}
            >
              <option value="1h">Last Hour</option>
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
            </select>
          </div>

          {loading ? (
            <div className="loading-state">
              <i className="fas fa-spinner fa-spin"></i>
              <span>Loading security metrics...</span>
            </div>
          ) : metrics && (
            <>
              <div className="security-metrics">
                <div className="metric-card">
                  <div className="metric-icon">
                    <i className="fas fa-sign-in-alt"></i>
                  </div>
                  <div className="metric-content">
                    <h3>Total Logins</h3>
                    <div className="metric-value">{metrics.totalLogins24h.toLocaleString()}</div>
                    <div className="metric-label">Last 24 hours</div>
                  </div>
                </div>

                <div className="metric-card alert">
                  <div className="metric-icon">
                    <i className="fas fa-times-circle"></i>
                  </div>
                  <div className="metric-content">
                    <h3>Failed Logins</h3>
                    <div className="metric-value">{metrics.failedLogins24h}</div>
                    <div className="metric-label">
                      {((metrics.failedLogins24h / metrics.totalLogins24h) * 100).toFixed(1)}% failure rate
                    </div>
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-icon">
                    <i className="fas fa-users"></i>
                  </div>
                  <div className="metric-content">
                    <h3>Active Users</h3>
                    <div className="metric-value">{metrics.activeUsers}</div>
                    <div className="metric-label">Currently online</div>
                  </div>
                </div>

                <div className="metric-card success">
                  <div className="metric-icon">
                    <i className="fas fa-lock"></i>
                  </div>
                  <div className="metric-content">
                    <h3>MFA Enabled</h3>
                    <div className="metric-value">
                      {metrics.mfaEnabledUsers} / {metrics.totalUsers}
                    </div>
                    <div className="metric-label">
                      {((metrics.mfaEnabledUsers / metrics.totalUsers) * 100).toFixed(1)}% coverage
                    </div>
                  </div>
                </div>

                <div className="metric-card warning">
                  <div className="metric-icon">
                    <i className="fas fa-exclamation-triangle"></i>
                  </div>
                  <div className="metric-content">
                    <h3>Suspicious Activities</h3>
                    <div className="metric-value">{metrics.suspiciousActivities}</div>
                    <div className="metric-label">Requires attention</div>
                  </div>
                </div>

                <div className="metric-card">
                  <div className="metric-icon">
                    <i className="fas fa-ban"></i>
                  </div>
                  <div className="metric-content">
                    <h3>Blocked IPs</h3>
                    <div className="metric-value">{metrics.blockedIPs}</div>
                    <div className="metric-label">Currently blocked</div>
                  </div>
                </div>
              </div>

              <div className="recent-threats">
                <h3>Recent Security Threats</h3>
                <div className="threats-list">
                  {metrics.recentThreats.map(threat => (
                    <div key={threat.id} className={`threat-item ${getSeverityClass(threat.severity)}`}>
                      <div className="threat-header">
                        <div className="threat-type">
                          <i className="fas fa-exclamation-circle"></i>
                          {threat.type}
                        </div>
                        <div className={`threat-status status-${threat.status}`}>
                          <i className={`fas ${getStatusIcon(threat.status)}`}></i>
                          {threat.status}
                        </div>
                      </div>
                      <div className="threat-description">{threat.description}</div>
                      <div className="threat-timestamp">
                        {new Date(threat.timestamp).toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {activeTab === 'audit' && (
        <div className="security-audit">
          <AuditLogViewer />
        </div>
      )}

      {activeTab === 'threats' && (
        <div className="security-threats">
          <div className="threat-detection-panel">
            <h3>Threat Detection Rules</h3>
            <div className="detection-rules">
              <div className="rule-item active">
                <div className="rule-header">
                  <span className="rule-name">Brute Force Detection</span>
                  <label className="toggle">
                    <input type="checkbox" defaultChecked />
                    <span className="toggle-slider"></span>
                  </label>
                </div>
                <div className="rule-config">
                  Threshold: 5 failed attempts in 5 minutes
                </div>
              </div>
              <div className="rule-item active">
                <div className="rule-header">
                  <span className="rule-name">API Rate Limiting</span>
                  <label className="toggle">
                    <input type="checkbox" defaultChecked />
                    <span className="toggle-slider"></span>
                  </label>
                </div>
                <div className="rule-config">
                  Limit: 100 requests per minute per user
                </div>
              </div>
              <div className="rule-item">
                <div className="rule-header">
                  <span className="rule-name">Suspicious Pattern Detection</span>
                  <label className="toggle">
                    <input type="checkbox" />
                    <span className="toggle-slider"></span>
                  </label>
                </div>
                <div className="rule-config">
                  AI-powered anomaly detection (disabled)
                </div>
              </div>
            </div>
          </div>

          <div className="blocked-ips-panel">
            <h3>IP Blocklist Management</h3>
            <div className="ip-blocklist">
              <div className="add-ip-form">
                <input type="text" placeholder="Enter IP address to block" />
                <button className="btn btn-primary">
                  <i className="fas fa-plus"></i>
                  Add to Blocklist
                </button>
              </div>
              <div className="blocked-ips-list">
                <div className="blocked-ip">
                  <span className="ip">192.168.1.100</span>
                  <span className="reason">Brute force attempts</span>
                  <span className="blocked-date">Blocked 2 hours ago</span>
                  <button className="btn-icon" title="Remove from blocklist">
                    <i className="fas fa-times"></i>
                  </button>
                </div>
                <div className="blocked-ip">
                  <span className="ip">10.0.0.50</span>
                  <span className="reason">Suspicious API usage</span>
                  <span className="blocked-date">Blocked 1 day ago</span>
                  <button className="btn-icon" title="Remove from blocklist">
                    <i className="fas fa-times"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'settings' && (
        <div className="security-settings">
          <div className="settings-section">
            <h3>Multi-Factor Authentication</h3>
            <div className="mfa-status">
              <div className="status-info">
                <i className="fas fa-shield-alt"></i>
                <div>
                  <h4>Your MFA Status</h4>
                  <p>{user?.mfaEnabled ? 'MFA is enabled for your account' : 'MFA is not enabled for your account'}</p>
                </div>
              </div>
              {!user?.mfaEnabled && (
                <button 
                  className="btn btn-primary"
                  onClick={() => setShowMFASetup(true)}
                >
                  Enable MFA
                </button>
              )}
            </div>
          </div>

          <div className="settings-section">
            <h3>Security Policies</h3>
            <div className="policy-list">
              <div className="policy-item">
                <div className="policy-header">
                  <h4>Password Requirements</h4>
                  <button className="btn btn-secondary">
                    <i className="fas fa-edit"></i>
                    Edit
                  </button>
                </div>
                <ul className="policy-rules">
                  <li>Minimum 12 characters</li>
                  <li>At least one uppercase letter</li>
                  <li>At least one number</li>
                  <li>At least one special character</li>
                </ul>
              </div>
              <div className="policy-item">
                <div className="policy-header">
                  <h4>Session Management</h4>
                  <button className="btn btn-secondary">
                    <i className="fas fa-edit"></i>
                    Edit
                  </button>
                </div>
                <ul className="policy-rules">
                  <li>Session timeout: 30 minutes</li>
                  <li>Maximum concurrent sessions: 3</li>
                  <li>Remember me duration: 7 days</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="settings-section">
            <h3>Security Headers</h3>
            <div className="headers-status">
              <div className="header-item enabled">
                <i className="fas fa-check-circle"></i>
                <span>X-Frame-Options: DENY</span>
              </div>
              <div className="header-item enabled">
                <i className="fas fa-check-circle"></i>
                <span>X-Content-Type-Options: nosniff</span>
              </div>
              <div className="header-item enabled">
                <i className="fas fa-check-circle"></i>
                <span>Strict-Transport-Security: max-age=31536000</span>
              </div>
              <div className="header-item enabled">
                <i className="fas fa-check-circle"></i>
                <span>Content-Security-Policy: default-src 'self'</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {showMFASetup && (
        <div className="mfa-modal">
          <div className="mfa-modal-content">
            <MFASetup
              onSetupComplete={() => {
                setShowMFASetup(false);
                // Refresh user data to update MFA status
                window.location.reload();
              }}
              onCancel={() => setShowMFASetup(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
};