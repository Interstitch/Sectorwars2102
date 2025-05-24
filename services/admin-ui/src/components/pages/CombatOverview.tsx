import React, { useState, useEffect } from 'react';
import PageHeader from '../ui/PageHeader';
import { api } from '../../utils/auth';
import './combat-overview.css';

interface CombatLog {
  combat_id: string;
  timestamp: string;
  attacker: {
    username: string;
    ship_type: string;
    ship_name: string;
    fighters: number;
  };
  defender: {
    username: string;
    ship_type: string;
    ship_name: string;
    fighters: number;
  };
  location: {
    sector_name: string;
    sector_id: string;
  };
  outcome: 'attacker_win' | 'defender_win' | 'draw';
  damage_dealt: {
    attacker_damage: number;
    defender_damage: number;
  };
  loot: {
    credits: number;
    cargo: any[];
  };
  combat_duration: number;
}

interface CombatStats {
  total_combats_today: number;
  total_ships_destroyed: number;
  total_credits_looted: number;
  average_combat_duration: number;
  most_active_combatant: string;
  deadliest_ship_type: string;
}

interface BalanceMetrics {
  ship_type_effectiveness: { [key: string]: number };
  fighter_effectiveness: number;
  average_damage_per_fighter: number;
  combat_balance_score: number;
}

const CombatOverview: React.FC = () => {
  const [combatLogs, setCombatLogs] = useState<CombatLog[]>([]);
  const [stats, setStats] = useState<CombatStats | null>(null);
  const [balanceMetrics, setBalanceMetrics] = useState<BalanceMetrics | null>(null);
  const [selectedCombat, setSelectedCombat] = useState<CombatLog | null>(null);
  const [timeFilter, setTimeFilter] = useState<string>('24h');
  const [outcomeFilter, setOutcomeFilter] = useState<string>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCombatData();
  }, [timeFilter, outcomeFilter]);

  const fetchCombatData = async () => {
    try {
      setLoading(true);
      
      // Fetch combat logs with current filters
      const logsResponse = await api.get('/api/v1/admin/combat/logs', {
        params: {
          time_filter: timeFilter,
          outcome_filter: outcomeFilter || undefined,
          limit: 100,
          offset: 0
        }
      });
      setCombatLogs(logsResponse.data as CombatLog[]);
      
      // Fetch combat statistics
      const statsResponse = await api.get('/api/v1/admin/combat/stats', {
        params: { time_filter: timeFilter }
      });
      setStats(statsResponse.data as CombatStats);
      
      // Fetch balance metrics
      const balanceResponse = await api.get('/api/v1/admin/combat/balance', {
        params: { time_filter: timeFilter }
      });
      setBalanceMetrics(balanceResponse.data as BalanceMetrics);
      
    } catch (error) {
      console.error('Failed to fetch combat data:', error);
      // Set fallback data on error
      setCombatLogs([]);
      setStats({
        total_combats_today: 0,
        total_ships_destroyed: 0,
        total_credits_looted: 0,
        average_combat_duration: 0,
        most_active_combatant: 'None',
        deadliest_ship_type: 'None'
      });
      setBalanceMetrics({
        ship_type_effectiveness: {},
        fighter_effectiveness: 1.0,
        average_damage_per_fighter: 0,
        combat_balance_score: 0.5
      });
    } finally {
      setLoading(false);
    }
  };

  const resolveCombatDispute = async (combatId: string, resolution: string) => {
    try {
      await api.post(`/api/v1/admin/combat/${combatId}/resolve`, { resolution });
      fetchCombatData();
    } catch (error) {
      console.error('Combat resolution failed:', error);
    }
  };

  const openCombatDetail = (combat: CombatLog) => {
    setSelectedCombat(combat);
  };

  const closeCombatDetail = () => {
    setSelectedCombat(null);
  };

  const getOutcomeIcon = (outcome: string) => {
    switch (outcome) {
      case 'attacker_win': return '⚔️';
      case 'defender_win': return '🛡️';
      case 'draw': return '🤝';
      default: return '❓';
    }
  };

  const getOutcomeColor = (outcome: string) => {
    switch (outcome) {
      case 'attacker_win': return 'attacker-win';
      case 'defender_win': return 'defender-win';
      case 'draw': return 'draw';
      default: return '';
    }
  };

  return (
    <div className="combat-overview">
      <PageHeader 
        title="Combat Overview" 
        subtitle="Monitor combat activity and balance"
      />
      
      {loading ? (
        <div className="loading-spinner">Loading combat data...</div>
      ) : (
        <>
          {/* Combat Statistics */}
          <div className="stats-grid">
            {stats && (
              <>
                <div className="stat-card">
                  <h3>Combats Today</h3>
                  <span className="stat-value">{stats.total_combats_today}</span>
                  <span className="stat-label">Total Engagements</span>
                </div>
                <div className="stat-card">
                  <h3>Ships Destroyed</h3>
                  <span className="stat-value">{stats.total_ships_destroyed}</span>
                  <span className="stat-label">Total Losses</span>
                </div>
                <div className="stat-card">
                  <h3>Credits Looted</h3>
                  <span className="stat-value">{stats.total_credits_looted.toLocaleString()}</span>
                  <span className="stat-label">Total Value</span>
                </div>
                <div className="stat-card">
                  <h3>Avg Duration</h3>
                  <span className="stat-value">{stats.average_combat_duration.toFixed(1)}</span>
                  <span className="stat-label">Minutes</span>
                </div>
              </>
            )}
          </div>

          {/* Balance Metrics */}
          {balanceMetrics && (
            <div className="balance-section">
              <h3>Combat Balance Analysis</h3>
              <div className="balance-grid">
                <div className="balance-card">
                  <h4>Ship Type Effectiveness</h4>
                  <div className="effectiveness-list">
                    {Object.entries(balanceMetrics.ship_type_effectiveness).map(([shipType, effectiveness]) => (
                      <div key={shipType} className="effectiveness-item">
                        <span className="ship-type">{shipType}</span>
                        <div className="effectiveness-bar">
                          <div 
                            className="effectiveness-fill" 
                            style={{ width: `${effectiveness}%` }}
                          ></div>
                        </div>
                        <span className="effectiveness-value">{effectiveness.toFixed(1)}%</span>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="balance-card">
                  <h4>Combat Balance Score</h4>
                  <div className="balance-score">
                    <div className={`score-circle ${balanceMetrics.combat_balance_score > 70 ? 'good' : 'warning'}`}>
                      <span>{balanceMetrics.combat_balance_score.toFixed(0)}%</span>
                    </div>
                    <p>System Balance Health</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Combat Controls */}
          <div className="combat-controls">
            <div className="filter-controls">
              <select 
                value={timeFilter} 
                onChange={(e) => setTimeFilter(e.target.value)}
                className="time-filter"
              >
                <option value="1h">Last Hour</option>
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
              </select>
              
              <select 
                value={outcomeFilter} 
                onChange={(e) => setOutcomeFilter(e.target.value)}
                className="outcome-filter"
              >
                <option value="all">All Outcomes</option>
                <option value="attacker_win">Attacker Wins</option>
                <option value="defender_win">Defender Wins</option>
                <option value="draw">Draws</option>
              </select>
            </div>
            
            <button onClick={fetchCombatData} className="refresh-btn">
              🔄 Refresh
            </button>
          </div>

          {/* Combat Logs */}
          <div className="combat-logs-section">
            <h3>Recent Combat Logs</h3>
            <div className="combat-logs-container">
              {combatLogs.map((combat) => (
                <div 
                  key={combat.combat_id} 
                  className="combat-log-card"
                  onClick={() => openCombatDetail(combat)}
                >
                  <div className="combat-header">
                    <span className={`outcome-badge ${getOutcomeColor(combat.outcome)}`}>
                      {getOutcomeIcon(combat.outcome)} {combat.outcome.replace('_', ' ')}
                    </span>
                    <span className="combat-time">
                      {new Date(combat.timestamp).toLocaleString()}
                    </span>
                  </div>
                  
                  <div className="combat-participants">
                    <div className="participant attacker">
                      <h4>Attacker</h4>
                      <p className="player-name">{combat.attacker.username}</p>
                      <p className="ship-info">{combat.attacker.ship_type} "{combat.attacker.ship_name}"</p>
                      <p className="fighters">⚡ {combat.attacker.fighters} fighters</p>
                    </div>
                    
                    <div className="vs-indicator">VS</div>
                    
                    <div className="participant defender">
                      <h4>Defender</h4>
                      <p className="player-name">{combat.defender.username}</p>
                      <p className="ship-info">{combat.defender.ship_type} "{combat.defender.ship_name}"</p>
                      <p className="fighters">🛡️ {combat.defender.fighters} fighters</p>
                    </div>
                  </div>
                  
                  <div className="combat-footer">
                    <span className="location">📍 {combat.location.sector_name}</span>
                    <span className="duration">⏱️ {combat.combat_duration}s</span>
                    <span className="loot">💰 {combat.loot.credits.toLocaleString()}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Combat Detail Modal */}
          {selectedCombat && (
            <div className="modal-overlay" onClick={closeCombatDetail}>
              <div className="combat-detail-modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                  <h3>Combat Details</h3>
                  <button className="close-btn" onClick={closeCombatDetail}>×</button>
                </div>
                
                <div className="modal-content">
                  <div className="combat-summary">
                    <div className="summary-header">
                      <span className={`outcome-badge large ${getOutcomeColor(selectedCombat.outcome)}`}>
                        {getOutcomeIcon(selectedCombat.outcome)} {selectedCombat.outcome.replace('_', ' ')}
                      </span>
                      <div className="combat-meta">
                        <p>Combat ID: {selectedCombat.combat_id}</p>
                        <p>Time: {new Date(selectedCombat.timestamp).toLocaleString()}</p>
                        <p>Location: {selectedCombat.location.sector_name}</p>
                        <p>Duration: {selectedCombat.combat_duration} seconds</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="participants-detail">
                    <div className="participant-card attacker">
                      <h4>Attacker</h4>
                      <div className="participant-info">
                        <p><strong>Player:</strong> {selectedCombat.attacker.username}</p>
                        <p><strong>Ship:</strong> {selectedCombat.attacker.ship_type} "{selectedCombat.attacker.ship_name}"</p>
                        <p><strong>Fighters:</strong> {selectedCombat.attacker.fighters}</p>
                        <p><strong>Damage Dealt:</strong> {selectedCombat.damage_dealt.attacker_damage}</p>
                      </div>
                    </div>
                    
                    <div className="participant-card defender">
                      <h4>Defender</h4>
                      <div className="participant-info">
                        <p><strong>Player:</strong> {selectedCombat.defender.username}</p>
                        <p><strong>Ship:</strong> {selectedCombat.defender.ship_type} "{selectedCombat.defender.ship_name}"</p>
                        <p><strong>Fighters:</strong> {selectedCombat.defender.fighters}</p>
                        <p><strong>Damage Dealt:</strong> {selectedCombat.damage_dealt.defender_damage}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="loot-section">
                    <h4>Combat Loot</h4>
                    <div className="loot-details">
                      <p><strong>Credits:</strong> {selectedCombat.loot.credits.toLocaleString()}</p>
                      {selectedCombat.loot.cargo.length > 0 && (
                        <div className="cargo-loot">
                          <p><strong>Cargo:</strong></p>
                          <ul>
                            {selectedCombat.loot.cargo.map((item, index) => (
                              <li key={index}>{item.quantity} {item.type}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="admin-actions">
                    <button 
                      className="action-btn reverse"
                      onClick={() => resolveCombatDispute(selectedCombat.combat_id, 'reverse')}
                    >
                      🔄 Reverse Combat
                    </button>
                    <button 
                      className="action-btn compensate"
                      onClick={() => resolveCombatDispute(selectedCombat.combat_id, 'compensate')}
                    >
                      💰 Compensate Loser
                    </button>
                    <button 
                      className="action-btn investigate"
                      onClick={() => resolveCombatDispute(selectedCombat.combat_id, 'investigate')}
                    >
                      🔍 Mark for Investigation
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default CombatOverview;