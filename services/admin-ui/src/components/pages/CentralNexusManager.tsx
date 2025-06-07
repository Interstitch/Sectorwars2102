import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import './central-nexus-manager.css';

interface NexusStatus {
  exists: boolean;
  status: string;
  nexus_id?: string;
  created_at?: string;
  total_sectors: number;
  total_ports: number;
  total_planets: number;
}

interface District {
  district_type: string;
  name: string;
  sector_range: [number, number];
  security_level: number;
  development_level: number;
  sectors_count: number;
  ports_count: number;
  planets_count: number;
  current_traffic: number;
}

interface NexusStats {
  total_sectors: number;
  total_ports: number;
  total_planets: number;
  total_warp_gates: number;
  active_players: number;
  daily_traffic: number;
  districts: Array<{
    district_type: string;
    sectors: number;
    avg_security: number;
    avg_development: number;
  }>;
}

const CentralNexusManager: React.FC = () => {
  const { token } = useAuth();
  const [nexusStatus, setNexusStatus] = useState<NexusStatus | null>(null);
  const [districts, setDistricts] = useState<District[]>([]);
  const [stats, setStats] = useState<NexusStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'districts' | 'generation'>('overview');

  useEffect(() => {
    loadNexusStatus();
    loadDistricts();
    loadStats();
  }, []);

  const loadNexusStatus = async () => {
    try {
      const response = await fetch('/api/v1/nexus/status', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setNexusStatus(data);
      }
    } catch (err) {
      console.error('Failed to load nexus status:', err);
    }
  };

  const loadDistricts = async () => {
    try {
      const response = await fetch('/api/v1/nexus/districts', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setDistricts(data);
      }
    } catch (err) {
      console.error('Failed to load districts:', err);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch('/api/v1/nexus/stats', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const generateNexus = async (forceRegenerate: boolean = false) => {
    if (!confirm('Are you sure you want to generate the Central Nexus? This process takes 15-20 minutes.')) {
      return;
    }

    setGenerating(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/nexus/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          force_regenerate: forceRegenerate,
          preserve_player_data: true
        })
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Generation started: ${result.message}`);
        setTimeout(() => {
          loadNexusStatus();
          loadDistricts();
          loadStats();
        }, 2000);
      } else {
        const error = await response.json();
        setError(error.detail || 'Failed to start generation');
      }
    } catch (err) {
      setError('Network error occurred');
      console.error('Generation error:', err);
    } finally {
      setGenerating(false);
    }
  };

  const regenerateDistrict = async (districtType: string) => {
    if (!confirm(`Are you sure you want to regenerate the ${districtType.replace('_', ' ')} district?`)) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/v1/nexus/districts/${districtType}/regenerate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const result = await response.json();
        alert(`District regeneration started: ${result.message}`);
        setTimeout(loadDistricts, 2000);
      } else {
        const error = await response.json();
        setError(error.detail || 'Failed to start regeneration');
      }
    } catch (err) {
      setError('Network error occurred');
      console.error('Regeneration error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'status-active';
      case 'generating': return 'status-generating';
      case 'not_generated': return 'status-not-generated';
      default: return 'status-unknown';
    }
  };

  const formatNumber = (num: number) => {
    return num?.toLocaleString() || '0';
  };

  const formatDistrictName = (districtType: string) => {
    return districtType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <div className="central-nexus-manager">
      <div className="nexus-header">
        <h1>Central Nexus Management</h1>
        <p>Manage the galactic hub connecting all regional territories</p>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="nexus-tabs">
        <button 
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab-button ${activeTab === 'districts' ? 'active' : ''}`}
          onClick={() => setActiveTab('districts')}
        >
          Districts
        </button>
        <button 
          className={`tab-button ${activeTab === 'generation' ? 'active' : ''}`}
          onClick={() => setActiveTab('generation')}
        >
          Generation
        </button>
      </div>

      <div className="nexus-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            {/* Status Card */}
            <div className="status-card">
              <h3>Central Nexus Status</h3>
              {nexusStatus ? (
                <div className="status-info">
                  <div className="status-item">
                    <label>Status:</label>
                    <span className={`status-badge ${getStatusColor(nexusStatus.status)}`}>
                      {nexusStatus.exists ? nexusStatus.status : 'Not Generated'}
                    </span>
                  </div>
                  {nexusStatus.exists && (
                    <>
                      <div className="status-item">
                        <label>Created:</label>
                        <span>{nexusStatus.created_at ? new Date(nexusStatus.created_at).toLocaleDateString() : 'Unknown'}</span>
                      </div>
                      <div className="status-item">
                        <label>Nexus ID:</label>
                        <span className="nexus-id">{nexusStatus.nexus_id}</span>
                      </div>
                    </>
                  )}
                </div>
              ) : (
                <div className="loading">Loading status...</div>
              )}
            </div>

            {/* Statistics Cards */}
            {stats && nexusStatus?.exists && (
              <div className="stats-grid">
                <div className="stat-card">
                  <h4>Sectors</h4>
                  <div className="stat-value">{formatNumber(stats.total_sectors)}</div>
                </div>
                <div className="stat-card">
                  <h4>Ports</h4>
                  <div className="stat-value">{formatNumber(stats.total_ports)}</div>
                </div>
                <div className="stat-card">
                  <h4>Planets</h4>
                  <div className="stat-value">{formatNumber(stats.total_planets)}</div>
                </div>
                <div className="stat-card">
                  <h4>Warp Gates</h4>
                  <div className="stat-value">{formatNumber(stats.total_warp_gates)}</div>
                </div>
                <div className="stat-card">
                  <h4>Active Players</h4>
                  <div className="stat-value">{formatNumber(stats.active_players)}</div>
                </div>
                <div className="stat-card">
                  <h4>Daily Traffic</h4>
                  <div className="stat-value">{formatNumber(stats.daily_traffic)}</div>
                </div>
              </div>
            )}

            {/* Quick Actions */}
            <div className="quick-actions">
              <h3>Quick Actions</h3>
              <div className="action-buttons">
                <button 
                  onClick={() => loadNexusStatus()}
                  className="action-button refresh"
                  disabled={loading}
                >
                  Refresh Status
                </button>
                <button 
                  onClick={() => loadStats()}
                  className="action-button refresh"
                  disabled={loading}
                >
                  Refresh Stats
                </button>
                {!nexusStatus?.exists && (
                  <button 
                    onClick={() => generateNexus()}
                    className="action-button generate"
                    disabled={generating}
                  >
                    {generating ? 'Generating...' : 'Generate Nexus'}
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'districts' && (
          <div className="districts-tab">
            <h3>District Overview</h3>
            {districts.length > 0 ? (
              <div className="districts-table">
                <table>
                  <thead>
                    <tr>
                      <th>District Name</th>
                      <th>Sector Range</th>
                      <th>Sectors</th>
                      <th>Ports</th>
                      <th>Planets</th>
                      <th>Security</th>
                      <th>Development</th>
                      <th>Traffic</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {districts.map((district) => (
                      <tr key={district.district_type}>
                        <td className="district-name">{district.name}</td>
                        <td>{district.sector_range[0]} - {district.sector_range[1]}</td>
                        <td>{formatNumber(district.sectors_count)}</td>
                        <td>{formatNumber(district.ports_count)}</td>
                        <td>{formatNumber(district.planets_count)}</td>
                        <td>
                          <div className="security-level">
                            <div className="security-bar">
                              <div 
                                className="security-fill" 
                                style={{ width: `${(district.security_level / 10) * 100}%` }}
                              ></div>
                            </div>
                            <span>{district.security_level}/10</span>
                          </div>
                        </td>
                        <td>
                          <div className="development-level">
                            <div className="development-bar">
                              <div 
                                className="development-fill" 
                                style={{ width: `${(district.development_level / 10) * 100}%` }}
                              ></div>
                            </div>
                            <span>{district.development_level}/10</span>
                          </div>
                        </td>
                        <td>{formatNumber(district.current_traffic)}</td>
                        <td>
                          <button 
                            onClick={() => regenerateDistrict(district.district_type)}
                            className="action-button regenerate"
                            disabled={loading}
                          >
                            Regenerate
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="no-districts">
                {nexusStatus?.exists ? 'Loading districts...' : 'Central Nexus not generated yet'}
              </div>
            )}
          </div>
        )}

        {activeTab === 'generation' && (
          <div className="generation-tab">
            <h3>Central Nexus Generation</h3>
            
            <div className="generation-info">
              <div className="info-card">
                <h4>About Central Nexus</h4>
                <p>
                  The Central Nexus is the galactic hub containing 5,000 sectors across 10 specialized districts.
                  It serves as the connection point between all regional territories and provides unique galactic services.
                </p>
                
                <h5>District Types:</h5>
                <ul>
                  <li><strong>Commerce Central:</strong> Primary trading hub with premium markets</li>
                  <li><strong>Diplomatic Quarter:</strong> Embassies and inter-regional negotiations</li>
                  <li><strong>Industrial Zone:</strong> Manufacturing and shipyard complexes</li>
                  <li><strong>Residential District:</strong> Living quarters and citizen services</li>
                  <li><strong>Transit Hub:</strong> Warp gates and transportation infrastructure</li>
                  <li><strong>High Security Zone:</strong> Restricted access premium facilities</li>
                  <li><strong>Cultural Center:</strong> Events, festivals, and cultural exchange</li>
                  <li><strong>Research Campus:</strong> Technology development and innovation</li>
                  <li><strong>Free Trade Zone:</strong> Unrestricted commerce and trading</li>
                  <li><strong>Gateway Plaza:</strong> Welcome center and orientation services</li>
                </ul>
              </div>

              <div className="generation-controls">
                <h4>Generation Options</h4>
                
                {nexusStatus?.exists ? (
                  <div className="regeneration-section">
                    <p className="warning">
                      ⚠️ Central Nexus already exists. Regeneration will rebuild all sectors.
                    </p>
                    <button 
                      onClick={() => generateNexus(true)}
                      className="action-button regenerate-full"
                      disabled={generating}
                    >
                      {generating ? 'Regenerating...' : 'Force Regenerate Entire Nexus'}
                    </button>
                  </div>
                ) : (
                  <div className="initial-generation-section">
                    <p>
                      Generate the Central Nexus galaxy with all districts and infrastructure.
                      This process takes approximately 15-20 minutes to complete.
                    </p>
                    <button 
                      onClick={() => generateNexus()}
                      className="action-button generate-initial"
                      disabled={generating}
                    >
                      {generating ? 'Generating...' : 'Generate Central Nexus'}
                    </button>
                  </div>
                )}

                <div className="generation-status">
                  {generating && (
                    <div className="progress-indicator">
                      <div className="spinner"></div>
                      <span>Generating Central Nexus... This may take several minutes.</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CentralNexusManager;