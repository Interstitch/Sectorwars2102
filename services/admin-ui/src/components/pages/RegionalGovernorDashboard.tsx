import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import './regional-governor-dashboard.css';

interface Region {
  id: string;
  name: string;
  display_name: string;
  owner_id: string;
  subscription_tier: string;
  status: string;
  governance_type: string;
  tax_rate: number;
  voting_threshold: number;
  economic_specialization: string;
  total_sectors: number;
  active_players_30d: number;
  total_trade_volume: number;
  starting_credits: number;
  starting_ship: string;
  constitutional_text?: string;
  language_pack: Record<string, string>;
  aesthetic_theme: Record<string, any>;
  trade_bonuses: Record<string, number>;
}

interface RegionalStats {
  total_population: number;
  citizen_count: number;
  resident_count: number;
  visitor_count: number;
  average_reputation: number;
  total_revenue: number;
  trade_volume_30d: number;
  active_elections: number;
  pending_policies: number;
  treaties_count: number;
  planets_count: number;
  ports_count: number;
  ships_count: number;
}

interface Policy {
  id: string;
  policy_type: string;
  title: string;
  description: string;
  proposed_changes: Record<string, any>;
  proposed_by: string;
  proposed_at: string;
  voting_closes_at: string;
  votes_for: number;
  votes_against: number;
  status: string;
  approval_percentage: number;
}

interface Election {
  id: string;
  position: string;
  candidates: Array<{
    player_id: string;
    player_name: string;
    platform: string;
    vote_count?: number;
  }>;
  voting_opens_at: string;
  voting_closes_at: string;
  status: string;
}

interface Treaty {
  id: string;
  region_a_name: string;
  region_b_name: string;
  treaty_type: string;
  terms: Record<string, any>;
  signed_at: string;
  expires_at?: string;
  status: string;
}

const RegionalGovernorDashboard: React.FC = () => {
  const { token } = useAuth();
  const [region, setRegion] = useState<Region | null>(null);
  const [stats, setStats] = useState<RegionalStats | null>(null);
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [elections, setElections] = useState<Election[]>([]);
  const [treaties, setTreaties] = useState<Treaty[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'governance' | 'economy' | 'policies' | 'elections' | 'diplomacy' | 'culture'>('overview');

  // Policy creation state
  const [showPolicyForm, setShowPolicyForm] = useState(false);
  const [newPolicy, setNewPolicy] = useState({
    policy_type: 'tax_rate',
    title: '',
    description: '',
    proposed_changes: {}
  });

  // Economic configuration state
  const [economicConfig, setEconomicConfig] = useState({
    tax_rate: 0.10,
    starting_credits: 1000,
    trade_bonuses: {} as Record<string, number>,
    economic_specialization: ''
  });

  // Governance configuration state
  const [governanceConfig, setGovernanceConfig] = useState({
    governance_type: 'autocracy',
    voting_threshold: 0.51,
    election_frequency_days: 90,
    constitutional_text: ''
  });

  useEffect(() => {
    loadRegionalData();
  }, []);

  const loadRegionalData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadRegionInfo(),
        loadRegionalStats(),
        loadPolicies(),
        loadElections(),
        loadTreaties()
      ]);
    } catch (err) {
      setError('Failed to load regional data');
      console.error('Load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadRegionInfo = async () => {
    try {
      const response = await fetch('/api/v1/regions/my-region', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setRegion(data);
        setEconomicConfig({
          tax_rate: data.tax_rate,
          starting_credits: data.starting_credits,
          trade_bonuses: data.trade_bonuses || {},
          economic_specialization: data.economic_specialization || ''
        });
        setGovernanceConfig({
          governance_type: data.governance_type,
          voting_threshold: data.voting_threshold,
          election_frequency_days: data.election_frequency_days,
          constitutional_text: data.constitutional_text || ''
        });
      }
    } catch (err) {
      console.error('Failed to load region info:', err);
    }
  };

  const loadRegionalStats = async () => {
    try {
      const response = await fetch('/api/v1/regions/my-region/stats', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Failed to load regional stats:', err);
    }
  };

  const loadPolicies = async () => {
    try {
      const response = await fetch('/api/v1/regions/my-region/policies', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setPolicies(data);
      }
    } catch (err) {
      console.error('Failed to load policies:', err);
    }
  };

  const loadElections = async () => {
    try {
      const response = await fetch('/api/v1/regions/my-region/elections', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setElections(data);
      }
    } catch (err) {
      console.error('Failed to load elections:', err);
    }
  };

  const loadTreaties = async () => {
    try {
      const response = await fetch('/api/v1/regions/my-region/treaties', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setTreaties(data);
      }
    } catch (err) {
      console.error('Failed to load treaties:', err);
    }
  };

  const updateEconomicConfig = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/regions/my-region/economy', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(economicConfig)
      });

      if (response.ok) {
        alert('Economic configuration updated successfully');
        await loadRegionInfo();
      } else {
        const error = await response.json();
        setError(error.detail || 'Failed to update economic configuration');
      }
    } catch (err) {
      setError('Network error occurred');
      console.error('Update error:', err);
    } finally {
      setLoading(false);
    }
  };

  const updateGovernanceConfig = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/regions/my-region/governance', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(governanceConfig)
      });

      if (response.ok) {
        alert('Governance configuration updated successfully');
        await loadRegionInfo();
      } else {
        const error = await response.json();
        setError(error.detail || 'Failed to update governance configuration');
      }
    } catch (err) {
      setError('Network error occurred');
      console.error('Update error:', err);
    } finally {
      setLoading(false);
    }
  };

  const createPolicy = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/regions/my-region/policies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newPolicy)
      });

      if (response.ok) {
        alert('Policy proposal created successfully');
        setShowPolicyForm(false);
        setNewPolicy({
          policy_type: 'tax_rate',
          title: '',
          description: '',
          proposed_changes: {}
        });
        await loadPolicies();
      } else {
        const error = await response.json();
        setError(error.detail || 'Failed to create policy');
      }
    } catch (err) {
      setError('Network error occurred');
      console.error('Create policy error:', err);
    } finally {
      setLoading(false);
    }
  };

  const startElection = async (position: string) => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/regions/my-region/elections', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          position,
          voting_duration_days: 7
        })
      });

      if (response.ok) {
        alert(`Election for ${position} started successfully`);
        await loadElections();
      } else {
        const error = await response.json();
        setError(error.detail || 'Failed to start election');
      }
    } catch (err) {
      setError('Network error occurred');
      console.error('Start election error:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num: number) => {
    return num?.toLocaleString() || '0';
  };

  const formatCurrency = (amount: number) => {
    return `${amount?.toLocaleString() || '0'} credits`;
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active': return 'status-active';
      case 'voting': return 'status-voting';
      case 'passed': return 'status-passed';
      case 'rejected': return 'status-rejected';
      case 'pending': return 'status-pending';
      default: return 'status-unknown';
    }
  };

  const getPolicyTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      'tax_rate': 'Tax Rate',
      'pvp_rules': 'PvP Rules',
      'trade_policy': 'Trade Policy',
      'immigration': 'Immigration',
      'defense': 'Defense Policy',
      'cultural': 'Cultural Policy'
    };
    return labels[type] || type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getGovernanceTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      'autocracy': 'Autocracy',
      'democracy': 'Democracy',
      'council': 'Council Republic'
    };
    return labels[type] || type;
  };

  if (!region) {
    return (
      <div className="regional-governor-dashboard">
        <div className="loading-message">
          {loading ? 'Loading regional data...' : 'No region found. You need to own a region to access this dashboard.'}
        </div>
      </div>
    );
  }

  return (
    <div className="regional-governor-dashboard">
      <div className="governor-header">
        <h1>Regional Governor Dashboard</h1>
        <div className="region-info">
          <h2>{region.display_name}</h2>
          <p>Governance Type: {getGovernanceTypeLabel(region.governance_type)} | Status: {region.status}</p>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={() => setError(null)} className="error-close">×</button>
        </div>
      )}

      <div className="governor-tabs">
        {['overview', 'governance', 'economy', 'policies', 'elections', 'diplomacy', 'culture'].map(tab => (
          <button
            key={tab}
            className={`tab-button ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab as any)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      <div className="governor-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            {/* Regional Overview */}
            <div className="overview-grid">
              <div className="stat-card">
                <h4>Total Population</h4>
                <div className="stat-value">{formatNumber(stats?.total_population || 0)}</div>
                <div className="stat-breakdown">
                  <div>Citizens: {formatNumber(stats?.citizen_count || 0)}</div>
                  <div>Residents: {formatNumber(stats?.resident_count || 0)}</div>
                  <div>Visitors: {formatNumber(stats?.visitor_count || 0)}</div>
                </div>
              </div>

              <div className="stat-card">
                <h4>Territory</h4>
                <div className="stat-value">{formatNumber(region.total_sectors)}</div>
                <div className="stat-label">Sectors</div>
                <div className="stat-breakdown">
                  <div>Planets: {formatNumber(stats?.planets_count || 0)}</div>
                  <div>Ports: {formatNumber(stats?.ports_count || 0)}</div>
                </div>
              </div>

              <div className="stat-card">
                <h4>Economy</h4>
                <div className="stat-value">{formatCurrency(stats?.total_revenue || 0)}</div>
                <div className="stat-label">Total Revenue</div>
                <div className="stat-breakdown">
                  <div>Trade Volume (30d): {formatCurrency(stats?.trade_volume_30d || 0)}</div>
                  <div>Tax Rate: {formatPercentage(region.tax_rate)}</div>
                </div>
              </div>

              <div className="stat-card">
                <h4>Governance</h4>
                <div className="stat-value">{formatNumber(stats?.active_elections || 0)}</div>
                <div className="stat-label">Active Elections</div>
                <div className="stat-breakdown">
                  <div>Pending Policies: {formatNumber(stats?.pending_policies || 0)}</div>
                  <div>Treaties: {formatNumber(stats?.treaties_count || 0)}</div>
                </div>
              </div>

              <div className="stat-card">
                <h4>Military</h4>
                <div className="stat-value">{formatNumber(stats?.ships_count || 0)}</div>
                <div className="stat-label">Total Ships</div>
                <div className="stat-breakdown">
                  <div>Avg. Reputation: {stats?.average_reputation?.toFixed(1) || '0.0'}</div>
                </div>
              </div>

              <div className="stat-card">
                <h4>Activity</h4>
                <div className="stat-value">{formatNumber(region.active_players_30d)}</div>
                <div className="stat-label">Active Players (30d)</div>
                <div className="stat-breakdown">
                  <div>Specialization: {region.economic_specialization || 'None'}</div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="quick-actions">
              <h3>Quick Actions</h3>
              <div className="action-buttons">
                <button
                  onClick={() => setActiveTab('policies')}
                  className="action-button primary"
                >
                  Create Policy
                </button>
                <button
                  onClick={() => setActiveTab('elections')}
                  className="action-button secondary"
                >
                  Manage Elections
                </button>
                <button
                  onClick={() => setActiveTab('diplomacy')}
                  className="action-button secondary"
                >
                  Diplomatic Relations
                </button>
                <button
                  onClick={loadRegionalData}
                  className="action-button refresh"
                  disabled={loading}
                >
                  Refresh Data
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'governance' && (
          <div className="governance-tab">
            <h3>Governance Configuration</h3>
            
            <div className="config-form">
              <div className="form-group">
                <label>Governance Type</label>
                <select
                  value={governanceConfig.governance_type}
                  onChange={(e) => setGovernanceConfig(prev => ({...prev, governance_type: e.target.value}))}
                >
                  <option value="autocracy">Autocracy</option>
                  <option value="democracy">Democracy</option>
                  <option value="council">Council Republic</option>
                </select>
                <small>Determines how decisions are made in your region</small>
              </div>

              <div className="form-group">
                <label>Voting Threshold</label>
                <input
                  type="number"
                  min="0.1"
                  max="0.9"
                  step="0.01"
                  value={governanceConfig.voting_threshold}
                  onChange={(e) => setGovernanceConfig(prev => ({...prev, voting_threshold: parseFloat(e.target.value)}))}
                />
                <small>Percentage of votes required to pass policies ({formatPercentage(governanceConfig.voting_threshold)})</small>
              </div>

              <div className="form-group">
                <label>Election Frequency (days)</label>
                <input
                  type="number"
                  min="30"
                  max="365"
                  value={governanceConfig.election_frequency_days}
                  onChange={(e) => setGovernanceConfig(prev => ({...prev, election_frequency_days: parseInt(e.target.value)}))}
                />
                <small>How often elections are held for regional positions</small>
              </div>

              <div className="form-group">
                <label>Constitutional Text</label>
                <textarea
                  value={governanceConfig.constitutional_text}
                  onChange={(e) => setGovernanceConfig(prev => ({...prev, constitutional_text: e.target.value}))}
                  placeholder="Define the fundamental laws and principles of your region..."
                  rows={6}
                />
                <small>The fundamental laws that govern your region</small>
              </div>

              <button
                onClick={updateGovernanceConfig}
                className="action-button primary"
                disabled={loading}
              >
                {loading ? 'Updating...' : 'Update Governance'}
              </button>
            </div>
          </div>
        )}

        {activeTab === 'economy' && (
          <div className="economy-tab">
            <h3>Economic Configuration</h3>
            
            <div className="config-form">
              <div className="form-group">
                <label>Tax Rate</label>
                <input
                  type="number"
                  min="0.05"
                  max="0.25"
                  step="0.01"
                  value={economicConfig.tax_rate}
                  onChange={(e) => setEconomicConfig(prev => ({...prev, tax_rate: parseFloat(e.target.value)}))}
                />
                <small>Tax rate applied to economic activities ({formatPercentage(economicConfig.tax_rate)})</small>
              </div>

              <div className="form-group">
                <label>Starting Credits</label>
                <input
                  type="number"
                  min="100"
                  max="10000"
                  value={economicConfig.starting_credits}
                  onChange={(e) => setEconomicConfig(prev => ({...prev, starting_credits: parseInt(e.target.value)}))}
                />
                <small>Credits given to new players when they join your region</small>
              </div>

              <div className="form-group">
                <label>Economic Specialization</label>
                <select
                  value={economicConfig.economic_specialization}
                  onChange={(e) => setEconomicConfig(prev => ({...prev, economic_specialization: e.target.value}))}
                >
                  <option value="">None</option>
                  <option value="mining">Mining</option>
                  <option value="manufacturing">Manufacturing</option>
                  <option value="agriculture">Agriculture</option>
                  <option value="trade">Trade Hub</option>
                  <option value="research">Research & Development</option>
                  <option value="tourism">Tourism</option>
                  <option value="military">Military Industrial</option>
                </select>
                <small>Specialization provides bonuses to specific economic activities</small>
              </div>

              <div className="form-group">
                <label>Trade Bonuses</label>
                <div className="trade-bonuses">
                  {['ore', 'food', 'technology', 'luxury', 'energy'].map(resource => (
                    <div key={resource} className="bonus-input">
                      <label>{resource.charAt(0).toUpperCase() + resource.slice(1)}</label>
                      <input
                        type="number"
                        min="1.0"
                        max="3.0"
                        step="0.1"
                        value={economicConfig.trade_bonuses[resource] || 1.0}
                        onChange={(e) => setEconomicConfig(prev => ({
                          ...prev, 
                          trade_bonuses: {
                            ...prev.trade_bonuses,
                            [resource]: parseFloat(e.target.value)
                          }
                        }))}
                      />
                    </div>
                  ))}
                </div>
                <small>Multipliers for trade in different resource types</small>
              </div>

              <button
                onClick={updateEconomicConfig}
                className="action-button primary"
                disabled={loading}
              >
                {loading ? 'Updating...' : 'Update Economy'}
              </button>
            </div>
          </div>
        )}

        {activeTab === 'policies' && (
          <div className="policies-tab">
            <div className="policies-header">
              <h3>Regional Policies</h3>
              <button
                onClick={() => setShowPolicyForm(true)}
                className="action-button primary"
              >
                Create Policy
              </button>
            </div>

            {showPolicyForm && (
              <div className="policy-form">
                <h4>Create New Policy</h4>
                <div className="form-group">
                  <label>Policy Type</label>
                  <select
                    value={newPolicy.policy_type}
                    onChange={(e) => setNewPolicy(prev => ({...prev, policy_type: e.target.value}))}
                  >
                    <option value="tax_rate">Tax Rate</option>
                    <option value="pvp_rules">PvP Rules</option>
                    <option value="trade_policy">Trade Policy</option>
                    <option value="immigration">Immigration</option>
                    <option value="defense">Defense Policy</option>
                    <option value="cultural">Cultural Policy</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Title</label>
                  <input
                    type="text"
                    value={newPolicy.title}
                    onChange={(e) => setNewPolicy(prev => ({...prev, title: e.target.value}))}
                    placeholder="Policy title..."
                  />
                </div>

                <div className="form-group">
                  <label>Description</label>
                  <textarea
                    value={newPolicy.description}
                    onChange={(e) => setNewPolicy(prev => ({...prev, description: e.target.value}))}
                    placeholder="Detailed description of the policy..."
                    rows={4}
                  />
                </div>

                <div className="form-actions">
                  <button onClick={createPolicy} className="action-button primary" disabled={loading}>
                    {loading ? 'Creating...' : 'Create Policy'}
                  </button>
                  <button onClick={() => setShowPolicyForm(false)} className="action-button secondary">
                    Cancel
                  </button>
                </div>
              </div>
            )}

            <div className="policies-list">
              {policies.length > 0 ? (
                <table>
                  <thead>
                    <tr>
                      <th>Title</th>
                      <th>Type</th>
                      <th>Status</th>
                      <th>Votes For</th>
                      <th>Votes Against</th>
                      <th>Approval</th>
                      <th>Closes</th>
                    </tr>
                  </thead>
                  <tbody>
                    {policies.map(policy => (
                      <tr key={policy.id}>
                        <td>{policy.title}</td>
                        <td>{getPolicyTypeLabel(policy.policy_type)}</td>
                        <td>
                          <span className={`status-badge ${getStatusColor(policy.status)}`}>
                            {policy.status}
                          </span>
                        </td>
                        <td>{formatNumber(policy.votes_for)}</td>
                        <td>{formatNumber(policy.votes_against)}</td>
                        <td>{policy.approval_percentage.toFixed(1)}%</td>
                        <td>{new Date(policy.voting_closes_at).toLocaleDateString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="no-data">No policies found</div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'elections' && (
          <div className="elections-tab">
            <div className="elections-header">
              <h3>Regional Elections</h3>
              <div className="election-actions">
                <button
                  onClick={() => startElection('governor')}
                  className="action-button primary"
                  disabled={loading}
                >
                  Start Governor Election
                </button>
                <button
                  onClick={() => startElection('council_member')}
                  className="action-button secondary"
                  disabled={loading}
                >
                  Start Council Election
                </button>
              </div>
            </div>

            <div className="elections-list">
              {elections.length > 0 ? (
                <div className="elections-grid">
                  {elections.map(election => (
                    <div key={election.id} className="election-card">
                      <h4>{election.position.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</h4>
                      <div className="election-status">
                        <span className={`status-badge ${getStatusColor(election.status)}`}>
                          {election.status}
                        </span>
                      </div>
                      
                      <div className="election-period">
                        <div>Opens: {new Date(election.voting_opens_at).toLocaleDateString()}</div>
                        <div>Closes: {new Date(election.voting_closes_at).toLocaleDateString()}</div>
                      </div>

                      <div className="candidates">
                        <h5>Candidates ({election.candidates.length})</h5>
                        {election.candidates.map(candidate => (
                          <div key={candidate.player_id} className="candidate">
                            <span>{candidate.player_name}</span>
                            {candidate.vote_count !== undefined && (
                              <span className="vote-count">{formatNumber(candidate.vote_count)} votes</span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="no-data">No elections found</div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'diplomacy' && (
          <div className="diplomacy-tab">
            <h3>Diplomatic Relations</h3>
            
            <div className="treaties-list">
              <h4>Active Treaties</h4>
              {treaties.length > 0 ? (
                <table>
                  <thead>
                    <tr>
                      <th>Partner Region</th>
                      <th>Treaty Type</th>
                      <th>Signed</th>
                      <th>Expires</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {treaties.map(treaty => (
                      <tr key={treaty.id}>
                        <td>
                          {treaty.region_a_name === region.name ? treaty.region_b_name : treaty.region_a_name}
                        </td>
                        <td>{treaty.treaty_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</td>
                        <td>{new Date(treaty.signed_at).toLocaleDateString()}</td>
                        <td>{treaty.expires_at ? new Date(treaty.expires_at).toLocaleDateString() : 'Permanent'}</td>
                        <td>
                          <span className={`status-badge ${getStatusColor(treaty.status)}`}>
                            {treaty.status}
                          </span>
                        </td>
                        <td>
                          <button className="action-button small">View Details</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="no-data">No treaties found</div>
              )}
            </div>

            <div className="diplomatic-actions">
              <h4>Diplomatic Actions</h4>
              <div className="action-buttons">
                <button className="action-button primary">Propose Trade Agreement</button>
                <button className="action-button secondary">Negotiate Defense Pact</button>
                <button className="action-button secondary">Cultural Exchange</button>
                <button className="action-button neutral">Send Diplomatic Message</button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'culture' && (
          <div className="culture-tab">
            <h3>Cultural Identity</h3>
            
            <div className="culture-config">
              <div className="form-group">
                <label>Regional Theme</label>
                <select>
                  <option value="default">Default</option>
                  <option value="imperial">Imperial</option>
                  <option value="federation">Federation</option>
                  <option value="pirate">Pirate Republic</option>
                  <option value="corporate">Corporate State</option>
                  <option value="tribal">Tribal Alliance</option>
                  <option value="technocracy">Technocracy</option>
                </select>
                <small>Affects visual theme and cultural descriptions</small>
              </div>

              <div className="form-group">
                <label>Regional Motto</label>
                <input
                  type="text"
                  placeholder="Enter your region's motto..."
                  maxLength={200}
                />
                <small>Displayed in region information</small>
              </div>

              <div className="form-group">
                <label>Cultural Traditions</label>
                <textarea
                  placeholder="Describe the cultural traditions and customs of your region..."
                  rows={4}
                />
                <small>Traditions that define your region's character</small>
              </div>

              <div className="form-group">
                <label>Language Settings</label>
                <select>
                  <option value="universal">Universal (English)</option>
                  <option value="imperial">Imperial Latin</option>
                  <option value="techspeak">Tech Speak</option>
                  <option value="trader">Trader Pidgin</option>
                  <option value="military">Military Code</option>
                </select>
                <small>Language variant used in your region</small>
              </div>

              <button className="action-button primary">Update Cultural Settings</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RegionalGovernorDashboard;