import React, { useState, useEffect, useCallback } from 'react';
import PageHeader from '../ui/PageHeader';
import { CombatActivityChart } from '../charts/CombatActivityChart';
import { CombatFeed } from '../combat/CombatFeed';
import { DisputePanel } from '../combat/DisputePanel';
import { api } from '../../utils/auth';
import { useCombatUpdates } from '../../contexts/WebSocketContext';
import './combat-overview.css';

interface CombatEvent {
  id: string;
  timestamp: string;
  type: 'player_vs_player' | 'player_vs_npc' | 'fleet_battle';
  attacker: string;
  defender: string;
  winner?: string;
  damageDealt: number;
  disputed?: boolean;
  sector: string;
}

interface CombatStats {
  totalBattles: number;
  battlesLast24h: number;
  totalDamageDealt: number;
  totalShipsDestroyed: number;
  averageBattleDuration: number;
  mostActiveSector?: string;
  mostActivePlayer?: string;
}

interface CombatRanking {
  playerId: string;
  playerName: string;
  kills: number;
  deaths: number;
  kdRatio: number;
  damageDealt: number;
  rank?: number;
  faction?: string;
  winRate?: number;
  totalDamage: number;
}

interface CombatDispute {
  id: string;
  combatEventId: string;
  reporterId: string;
  reporterName: string;
  reason: string;
  status: 'pending' | 'resolved' | 'rejected';
  createdAt: string;
}

export const CombatOverview: React.FC = () => {
  const [combatEvents, setCombatEvents] = useState<CombatEvent[]>([]);
  const [combatStats, setCombatStats] = useState<CombatStats | null>(null);
  const [rankings, setRankings] = useState<CombatRanking[]>([]);
  const [disputes, setDisputes] = useState<CombatDispute[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedView, setSelectedView] = useState<'feed' | 'disputes' | 'rankings'>('feed');
  const [showInterventionModal, setShowInterventionModal] = useState(false);
  const [selectedCombatId, setSelectedCombatId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // WebSocket handlers
  const handleNewCombatEvent = useCallback((data: any) => {
    console.log('New combat event received:', data);
    setCombatEvents(prev => [data, ...prev].slice(0, 100)); // Keep last 100 events
    setLastUpdate(new Date());
  }, []);

  const handleDisputeFiled = useCallback((data: any) => {
    console.log('New dispute filed:', data);
    setDisputes(prev => [data, ...prev]);
    setLastUpdate(new Date());
  }, []);

  const handleStatsUpdate = useCallback((data: any) => {
    console.log('Combat stats updated:', data);
    setCombatStats(data);
    setLastUpdate(new Date());
  }, []);

  // Subscribe to WebSocket events
  useCombatUpdates(handleNewCombatEvent, handleDisputeFiled, handleStatsUpdate);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Fetch combat events
      const eventsResponse = await api.get('/api/v1/admin/combat/live');
      setCombatEvents(eventsResponse.data as CombatEvent[]);
      
      // Fetch combat statistics  
      const statsResponse = await api.get('/api/v1/admin/combat/balance');
      setCombatStats(statsResponse.data as CombatStats);
      
      // Fetch combat rankings (from balance endpoint)
      const rankingsResponse = await api.get('/api/v1/admin/combat/balance');
      setRankings(rankingsResponse.data.topPlayers || []);
      
      // Fetch combat disputes
      const disputesResponse = await api.get('/api/v1/admin/combat/disputes');
      setDisputes(disputesResponse.data as CombatDispute[]);
    } catch (error: any) {
      console.error('Failed to load combat data:', error);
      setError(error.response?.data?.detail || 'Failed to load combat data. Please check if the gameserver is running.');
      // Clear data on error
      setCombatEvents([]);
      setCombatStats(null);
      setRankings([]);
      setDisputes([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Load initial data
  useEffect(() => {
    loadData();
    
    // Refresh data every 30 seconds
    const interval = setInterval(loadData, 30000);

    return () => clearInterval(interval);
  }, []);

  const handleDisputeClick = (_eventId: string) => {
    setSelectedView('disputes');
  };

  const handleInterventionClick = (eventId: string) => {
    setSelectedCombatId(eventId);
    setShowInterventionModal(true);
  };

  const handleIntervention = async (action: string) => {
    if (selectedCombatId) {
      try {
        await api.post(`/api/v1/admin/combat/${selectedCombatId}/intervene`, {
          action: action
        });
        setShowInterventionModal(false);
        setSelectedCombatId(null);
        // Refresh data
        await loadData();
      } catch (error: any) {
        console.error('Failed to intervene:', error);
        alert(error.response?.data?.detail || 'Failed to intervene in combat');
      }
    }
  };

  if (isLoading) {
    return (
      <div className="combat-overview loading">
        <PageHeader title="Combat Overview" />
        <div className="loading-spinner">Loading combat data...</div>
      </div>
    );
  }

  return (
    <div className="combat-overview">
      <PageHeader title="Combat Overview" />
      
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
      
      {/* Error Notice */}
      {error && (
        <div className="alert error" style={{ marginBottom: '20px' }}>
          <span className="alert-icon">❌</span>
          <span className="alert-message">
            {error}
          </span>
        </div>
      )}
      
      {/* Combat Statistics Dashboard */}
      <div className="combat-stats-grid">
        <div className="stat-card primary">
          <h3>Total Battles</h3>
          <div className="stat-value">{combatStats?.totalBattles.toLocaleString() || 0}</div>
          <div className="stat-change">+{combatStats?.battlesLast24h || 0} today</div>
        </div>
        
        <div className="stat-card">
          <h3>Total Damage</h3>
          <div className="stat-value">{combatStats?.totalDamageDealt.toLocaleString() || 0}</div>
          <div className="stat-label">damage dealt</div>
        </div>
        
        <div className="stat-card">
          <h3>Ships Destroyed</h3>
          <div className="stat-value">{combatStats?.totalShipsDestroyed.toLocaleString() || 0}</div>
          <div className="stat-label">total losses</div>
        </div>
        
        <div className="stat-card">
          <h3>Avg Battle Duration</h3>
          <div className="stat-value">{Math.floor((combatStats?.averageBattleDuration || 0) / 60)}m</div>
          <div className="stat-label">average time</div>
        </div>
        
        <div className="stat-card highlight">
          <h3>Most Active Sector</h3>
          <div className="stat-value">{combatStats?.mostActiveSector || 'N/A'}</div>
          <div className="stat-label">hotspot</div>
        </div>
        
        <div className="stat-card highlight">
          <h3>Most Active Player</h3>
          <div className="stat-value">{combatStats?.mostActivePlayer || 'N/A'}</div>
          <div className="stat-label">combat leader</div>
        </div>
      </div>

      {/* Combat Activity Chart */}
      <div className="combat-chart-section">
        <CombatActivityChart events={combatEvents} width={1200} height={300} />
      </div>

      {/* View Selector */}
      <div className="view-selector">
        <button 
          className={`view-btn ${selectedView === 'feed' ? 'active' : ''}`}
          onClick={() => setSelectedView('feed')}
        >
          Live Feed
        </button>
        <button 
          className={`view-btn ${selectedView === 'disputes' ? 'active' : ''}`}
          onClick={() => setSelectedView('disputes')}
        >
          Disputes ({disputes.filter(d => d.status === 'pending').length})
        </button>
        <button 
          className={`view-btn ${selectedView === 'rankings' ? 'active' : ''}`}
          onClick={() => setSelectedView('rankings')}
        >
          Rankings
        </button>
      </div>

      {/* Content Area */}
      <div className="combat-content">
        {selectedView === 'feed' && (
          <CombatFeed 
            events={combatEvents}
            onDisputeClick={handleDisputeClick}
            onInterventionClick={handleInterventionClick}
          />
        )}
        
        {selectedView === 'disputes' && (
          <DisputePanel 
            disputes={disputes}
            onResolve={loadData}
          />
        )}
        
        {selectedView === 'rankings' && (
          <div className="combat-rankings">
            <h3>Combat Rankings</h3>
            <table className="rankings-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Player</th>
                  <th>Faction</th>
                  <th>Kills</th>
                  <th>Deaths</th>
                  <th>K/D Ratio</th>
                  <th>Win Rate</th>
                  <th>Total Damage</th>
                </tr>
              </thead>
              <tbody>
                {rankings.map((player: CombatRanking, index: number) => (
                  <tr key={player.playerId}>
                    <td className="rank">#{index + 1}</td>
                    <td className="player-name">{player.playerName}</td>
                    <td className="faction">{player.faction || 'Unknown'}</td>
                    <td className="kills">{player.kills}</td>
                    <td className="deaths">{player.deaths}</td>
                    <td className="kd-ratio">{player.kdRatio.toFixed(2)}</td>
                    <td className="win-rate">{player.winRate || 0}%</td>
                    <td className="damage">{player.totalDamage.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Intervention Modal */}
      {showInterventionModal && (
        <div className="modal-overlay" onClick={() => setShowInterventionModal(false)}>
          <div className="intervention-modal" onClick={(e: React.MouseEvent) => e.stopPropagation()}>
            <h3>Combat Intervention</h3>
            <p>Select intervention action for combat: {selectedCombatId}</p>
            
            <div className="intervention-options">
              <button 
                className="btn btn-warning"
                onClick={() => handleIntervention('pause')}
              >
                Pause Combat
              </button>
              
              <button 
                className="btn btn-danger"
                onClick={() => handleIntervention('end')}
              >
                Force End Combat
              </button>
              
              <button 
                className="btn btn-info"
                onClick={() => handleIntervention('reset')}
              >
                Reset Combat State
              </button>
              
              <button 
                className="btn btn-success"
                onClick={() => handleIntervention('restore')}
              >
                Restore Ships
              </button>
            </div>
            
            <button 
              className="btn btn-secondary"
              onClick={() => setShowInterventionModal(false)}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CombatOverview;