/**
 * FleetBattlePanel - Active fleet battles with formation selector and round simulation.
 * Wires into fleetAPI endpoints (getBattles, simulateBattleRound, updateFormation, getFleets).
 */
import React, { useState, useEffect, useCallback } from 'react';
import { fleetAPI } from '../../services/api';

interface FleetSummary { id: string; name: string; ship_count: number; formation: string; }
interface Battle {
  id: string;
  attacker_fleet: FleetSummary;
  defender_fleet: FleetSummary;
  status: 'active' | 'completed';
  current_round: number;
  attacker_ships_remaining: number;
  defender_ships_remaining: number;
  winner?: string;
}

const FORMATIONS = ['standard', 'aggressive', 'defensive', 'flanking', 'turtle'] as const;
type Formation = typeof FORMATIONS[number];
const FORMATION_LABELS: Record<Formation, string> = {
  standard: 'Standard', aggressive: 'Aggressive', defensive: 'Defensive',
  flanking: 'Flanking', turtle: 'Turtle',
};

const s = {
  section: { padding: '12px 16px', borderBottom: '1px solid var(--cockpit-border)', marginBottom: '16px' } as React.CSSProperties,
  sectionTitle: { color: 'var(--cockpit-primary)', margin: '0 0 10px', fontSize: '14px', textTransform: 'uppercase' as const, letterSpacing: '1px' } as React.CSSProperties,
  fleetRow: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', background: 'rgba(0,255,255,0.05)', border: '1px solid var(--cockpit-border)', borderRadius: '4px' } as React.CSSProperties,
  select: { padding: '4px 8px', background: 'rgba(0,0,0,0.4)', border: '1px solid var(--cockpit-primary)', borderRadius: '4px', color: 'var(--cockpit-primary)', fontSize: '13px' } as React.CSSProperties,
  empty: { textAlign: 'center' as const, padding: '40px 20px', color: 'var(--cockpit-text-secondary)' } as React.CSSProperties,
  battleCard: (active: boolean) => ({ background: 'rgba(0,0,0,0.3)', border: `1px solid ${active ? 'var(--cockpit-primary)' : 'var(--cockpit-text-secondary)'}`, borderRadius: '6px', padding: '16px' }) as React.CSSProperties,
  vsRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' } as React.CSSProperties,
  vsLabel: { color: 'var(--cockpit-primary)', fontSize: '12px', textTransform: 'uppercase' as const, letterSpacing: '2px' } as React.CSSProperties,
  statsGrid: { display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: '8px', alignItems: 'center', fontSize: '13px', color: 'var(--cockpit-text-secondary)', marginBottom: '12px' } as React.CSSProperties,
  bigNum: { color: 'var(--cockpit-text)', fontWeight: 'bold' as const, fontSize: '20px' } as React.CSSProperties,
  roundBadge: { textAlign: 'center' as const, padding: '4px 10px', background: 'rgba(0,255,255,0.1)', borderRadius: '4px', color: 'var(--cockpit-primary)', fontWeight: 'bold' as const } as React.CSSProperties,
  outcome: { textAlign: 'center' as const, padding: '10px', background: 'rgba(0,255,0,0.08)', border: '1px solid var(--cockpit-success)', borderRadius: '4px', color: 'var(--cockpit-success)', fontWeight: 'bold' as const, textTransform: 'uppercase' as const, letterSpacing: '1px' } as React.CSSProperties,
};

const FleetBattlePanel: React.FC = () => {
  const [battles, setBattles] = useState<Battle[]>([]);
  const [fleets, setFleets] = useState<FleetSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [simulating, setSimulating] = useState<string | null>(null);
  const [updatingFormation, setUpdatingFormation] = useState<string | null>(null);

  const fetchBattles = useCallback(async () => {
    try {
      const data = await fleetAPI.getBattles(true);
      setBattles(Array.isArray(data) ? data : data.battles || []);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load battles');
    }
  }, []);

  const fetchFleets = useCallback(async () => {
    try {
      const data = await fleetAPI.getFleets();
      setFleets(Array.isArray(data) ? data : data.fleets || []);
    } catch { /* fleets optional */ }
  }, []);

  useEffect(() => {
    const load = async () => { setLoading(true); await Promise.allSettled([fetchBattles(), fetchFleets()]); setLoading(false); };
    load();
  }, [fetchBattles, fetchFleets]);

  const handleSimulateRound = useCallback(async (battleId: string) => {
    setSimulating(battleId); setError(null);
    try { await fleetAPI.simulateBattleRound(battleId); await fetchBattles(); }
    catch (err: unknown) { setError(err instanceof Error ? err.message : 'Simulation failed'); }
    finally { setSimulating(null); }
  }, [fetchBattles]);

  const handleFormationChange = useCallback(async (fleetId: string, formation: string) => {
    setUpdatingFormation(fleetId); setError(null);
    try { await fleetAPI.updateFormation(fleetId, formation); await fetchFleets(); }
    catch (err: unknown) { setError(err instanceof Error ? err.message : 'Formation update failed'); }
    finally { setUpdatingFormation(null); }
  }, [fetchFleets]);

  if (loading) {
    return (
      <div className="combat-interface" style={{ textAlign: 'center', padding: '40px' }}>
        <p style={{ color: 'var(--cockpit-text-secondary)' }}>Loading fleet battles...</p>
      </div>
    );
  }

  return (
    <div className="combat-interface">
      <div className="combat-header"><h2>FLEET BATTLES</h2></div>

      {error && <div className="combat-error"><span className="error-icon">!</span>{error}</div>}

      {fleets.length > 0 && (
        <div style={s.section}>
          <h4 style={s.sectionTitle}>Fleet Formations</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {fleets.map((fleet) => (
              <div key={fleet.id} style={s.fleetRow}>
                <span style={{ color: 'var(--cockpit-text)', fontSize: '14px' }}>
                  {fleet.name} ({fleet.ship_count} ships)
                </span>
                <select
                  value={fleet.formation || 'standard'}
                  onChange={(e) => handleFormationChange(fleet.id, e.target.value)}
                  disabled={updatingFormation === fleet.id}
                  style={{ ...s.select, cursor: updatingFormation === fleet.id ? 'not-allowed' : 'pointer', opacity: updatingFormation === fleet.id ? 0.5 : 1 }}
                >
                  {FORMATIONS.map((f) => <option key={f} value={f}>{FORMATION_LABELS[f]}</option>)}
                </select>
              </div>
            ))}
          </div>
        </div>
      )}

      {battles.length === 0 ? (
        <div style={s.empty}><p>No active fleet battles.</p></div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', padding: '0 4px' }}>
          {battles.map((battle) => (
            <div key={battle.id} style={s.battleCard(battle.status === 'active')}>
              <div style={s.vsRow}>
                <span style={{ color: 'var(--cockpit-success)', fontWeight: 'bold', fontSize: '14px' }}>{battle.attacker_fleet.name}</span>
                <span style={s.vsLabel}>VS</span>
                <span style={{ color: 'var(--cockpit-danger)', fontWeight: 'bold', fontSize: '14px' }}>{battle.defender_fleet.name}</span>
              </div>
              <div style={s.statsGrid}>
                <div style={{ textAlign: 'center' }}>
                  <div style={s.bigNum}>{battle.attacker_ships_remaining}</div>
                  <div>ships left</div>
                </div>
                <div style={s.roundBadge}>RND {battle.current_round}</div>
                <div style={{ textAlign: 'center' }}>
                  <div style={s.bigNum}>{battle.defender_ships_remaining}</div>
                  <div>ships left</div>
                </div>
              </div>
              {battle.status === 'completed' ? (
                <div style={s.outcome}>Battle Complete{battle.winner ? ` - ${battle.winner} wins` : ''}</div>
              ) : (
                <button className="action-btn" onClick={() => handleSimulateRound(battle.id)}
                  disabled={simulating === battle.id} style={{ width: '100%' }}>
                  {simulating === battle.id ? 'Simulating...' : 'Simulate Next Round'}
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FleetBattlePanel;
