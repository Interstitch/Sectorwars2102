/**
 * CombatInterface Component
 * 
 * Main combat engagement interface for ship-to-ship, ship-to-planet, 
 * and ship-to-port combat. Provides real-time combat visualization
 * and player controls during combat encounters.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useGame } from '../../contexts/GameContext';
import { gameAPI } from '../../services/api';
import { InputValidator, SecurityAudit } from '../../utils/security/inputValidation';
import { formatShipType } from '../../utils/formatters';
import './combat-interface.css';

// Define types locally since we're removing mocks
interface CombatStatus {
  combatId: string;
  status: 'initiated' | 'ongoing' | 'completed' | 'error';
  rounds: CombatRound[];
  winner?: string;
  message?: string;
  loot?: {
    credits: number;
    items: string[];
  };
}

interface CombatRound {
  round: number;
  roundNumber?: number;
  actions: Array<{
    attacker: string;
    target: string;
    damage: number;
    critical: boolean;
    message: string;
  }>;
  playerHealth: number;
  playerShields: number;
  targetHealth: number;
  targetShields: number;
  attackerHealth?: number;
  defenderHealth?: number;
  attackerAction?: {
    type: string;
    damage?: number;
  };
  defenderAction?: {
    type: string;
    damage?: number;
  };
}

interface CombatTarget {
  id: string;
  name: string;
  type: 'ship' | 'planet' | 'port';
  health?: number;
  shields?: number;
  drones?: number;
}

interface CombatInterfaceProps {
  target?: CombatTarget;
  onCombatEnd?: (result: CombatStatus) => void;
  onClose?: () => void;
}

export const CombatInterface: React.FC<CombatInterfaceProps> = ({
  target,
  onCombatEnd,
  onClose
}) => {
  const { playerState, currentShip, currentSector, refreshPlayerState } = useGame();
  
  // Combat state
  const [combatId, setCombatId] = useState<string | null>(null);
  const [combatStatus, setCombatStatus] = useState<CombatStatus | null>(null);
  const [isEngaging, setIsEngaging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedAction, setSelectedAction] = useState<'fire' | 'drones' | 'retreat'>('fire');
  
  // UI state
  const [showCombatLog, setShowCombatLog] = useState(true);
  const [animationState, setAnimationState] = useState<'idle' | 'attacking' | 'defending'>('idle');
  
  // Auto-refresh combat status
  useEffect(() => {
    if (!combatId || combatStatus?.status === 'completed') return;
    
    const interval = setInterval(async () => {
      try {
        const status = await gameAPI.combat.getStatus(combatId);
        if (status) {
          setCombatStatus(status);
          
          // Trigger animations based on latest round
          if (status.rounds.length > 0) {
            const latestRound = status.rounds[status.rounds.length - 1];
            if (latestRound.actions && latestRound.actions.length > 0) {
              setAnimationState('attacking');
              setTimeout(() => setAnimationState('idle'), 500);
            }
          }
          
          // Handle combat end
          if (status.status === 'completed') {
            handleCombatEnd(status);
          }
        }
      } catch (err) {
        console.error('Failed to fetch combat status:', err);
      }
    }, 1000);
    
    return () => clearInterval(interval);
  }, [combatId, combatStatus?.status]);
  
  // Initiate combat
  const inititateCombat = useCallback(async () => {
    if (!target || !playerState || isEngaging) return;
    
    // Validate inputs
    const validation = InputValidator.validateCombatParams({
      targetType: target.type,
      targetId: target.id
    });
    
    if (!validation.valid) {
      setError(validation.errors.join(', '));
      SecurityAudit.log({
        type: 'validation_failure',
        details: { errors: validation.errors, target },
        userId: playerState.id
      });
      return;
    }
    
    // Rate limiting check
    if (!InputValidator.checkRateLimit(`combat_${playerState.id}`, 5, 60000)) {
      setError('Too many combat attempts. Please wait before engaging again.');
      SecurityAudit.log({
        type: 'rate_limit_exceeded',
        details: { action: 'combat_initiation' },
        userId: playerState.id
      });
      return;
    }
    
    setIsEngaging(true);
    setError(null);
    
    try {
      const response = await gameAPI.combat.engage(target.type, target.id);
      
      if (response.status === 'initiated' && response.combatId) {
        setCombatId(response.combatId);
        
        // Fetch initial status
        const initialStatus = await gameAPI.combat.getStatus(response.combatId);
        if (initialStatus) {
          setCombatStatus(initialStatus);
        }
      } else {
        setError(response.message || 'Failed to initiate combat');
      }
    } catch (err) {
      setError('Combat system error. Please try again.');
      console.error('Combat initiation failed:', err);
    } finally {
      setIsEngaging(false);
    }
  }, [target, playerState, isEngaging]);
  
  // Handle combat end
  const handleCombatEnd = useCallback((status: CombatStatus) => {
    // Clear rate limit on combat end
    if (playerState) {
      InputValidator.clearRateLimit(`combat_${playerState.id}`);
    }
    
    // Refresh player state to update resources, health, etc.
    refreshPlayerState();
    
    // Notify parent component
    if (onCombatEnd) {
      onCombatEnd(status);
    }
  }, [playerState, refreshPlayerState, onCombatEnd]);
  
  // Attempt retreat
  const attemptRetreat = useCallback(async () => {
    if (!combatId || !playerState || combatStatus?.status === 'completed') return;
    
    // TODO: Implement retreat mechanics when API is available
    console.log('Retreat attempt - not yet implemented');
  }, [combatId, playerState, combatStatus]);
  
  // Calculate health percentages
  const getHealthPercentage = (current: number, max: number = 100): number => {
    return Math.max(0, Math.min(100, (current / max) * 100));
  };
  
  // Get latest round data
  const latestRound = combatStatus?.rounds[combatStatus.rounds.length - 1];
  const playerHealth = latestRound?.playerHealth ?? 100;
  const targetHealth = latestRound?.targetHealth ?? 100;
  
  if (!target) {
    const sectorHazard = currentSector?.hazard_level ?? 0;
    const playersInSector = (currentSector?.players_present || []).filter(
      (p: any) => p.id !== playerState?.id && p.player_id !== playerState?.id
    );
    const hasThreats = playersInSector.length > 0 || sectorHazard > 5;

    return (
      <div className="combat-interface no-target-detailed">
        <div className="combat-header">
          <h2>COMBAT & WEAPONS</h2>
          {onClose && (
            <button className="close-btn" onClick={onClose}>×</button>
          )}
        </div>

        {/* Sector Threat Assessment */}
        <div className="threat-assessment">
          <div className={`threat-status ${hasThreats ? 'alert' : 'clear'}`}>
            <div className="threat-icon">{hasThreats ? '!' : '\u2713'}</div>
            <div className="threat-text">
              <h3>{hasThreats ? 'CONTACTS DETECTED' : 'SECTOR CLEAR'}</h3>
              <p>{hasThreats
                ? `${playersInSector.length} vessel${playersInSector.length !== 1 ? 's' : ''} detected in sector. Stay alert.`
                : 'No hostile contacts detected. All systems nominal.'
              }</p>
            </div>
          </div>
          {currentSector && (
            <div className="sector-threat-level">
              <span className="threat-label">SECTOR THREAT LEVEL</span>
              <div className="threat-bar">
                <div
                  className={`threat-bar-fill ${sectorHazard > 7 ? 'critical' : sectorHazard > 4 ? 'elevated' : 'low'}`}
                  style={{ width: `${sectorHazard * 10}%` }}
                />
              </div>
              <span className="threat-value">{sectorHazard}/10</span>
            </div>
          )}
        </div>

        <div className="readiness-grid">
          {/* Ship Combat Readiness */}
          <div className="readiness-panel">
            <h4>SHIP COMBAT READINESS</h4>
            {currentShip ? (
              <div className="readiness-stats">
                <div className="stat-row">
                  <span className="stat-label">Vessel</span>
                  <span className="stat-value">{currentShip.name}</span>
                </div>
                <div className="stat-row">
                  <span className="stat-label">Class</span>
                  <span className="stat-value">{formatShipType(currentShip.type)}</span>
                </div>
                <div className="stat-row">
                  <span className="stat-label">Attack Rating</span>
                  <span className="stat-value highlight">{currentShip.combat?.attack_rating ?? 0}</span>
                </div>
                <div className="stat-row">
                  <span className="stat-label">Defense Rating</span>
                  <span className="stat-value highlight">{currentShip.combat?.defense_rating ?? 0}</span>
                </div>
                <div className="stat-row">
                  <span className="stat-label">Shield Strength</span>
                  <span className="stat-value">{currentShip.combat?.shields ?? currentShip.combat?.shield_points ?? 'N/A'}</span>
                </div>
                <div className="stat-row">
                  <span className="stat-label">Hull Integrity</span>
                  <span className="stat-value">{currentShip.combat?.hull ?? currentShip.combat?.hull_points ?? 'N/A'}</span>
                </div>
              </div>
            ) : (
              <p className="no-data">No ship data available</p>
            )}
          </div>

          {/* Drone Status */}
          <div className="readiness-panel">
            <h4>DRONE STATUS</h4>
            <div className="readiness-stats">
              <div className="stat-row">
                <span className="stat-label">Attack Drones</span>
                <span className="stat-value highlight">{currentShip?.combat?.attack_drones ?? playerState?.attack_drones ?? 0}</span>
              </div>
              <div className="stat-row">
                <span className="stat-label">Defense Drones</span>
                <span className="stat-value highlight">{currentShip?.combat?.defense_drones ?? playerState?.defense_drones ?? 0}</span>
              </div>
            </div>

            <h4 style={{ marginTop: '20px' }}>SECTOR CONTACTS</h4>
            {playersInSector.length > 0 ? (
              <div className="contacts-list">
                {playersInSector.map((player: any, index: number) => (
                  <div key={player.id || player.player_id || index} className="contact-entry">
                    <span className="contact-name">{player.name || player.username || 'Unknown Vessel'}</span>
                    <span className="contact-type">{player.ship_type ? formatShipType(player.ship_type) : 'Ship'}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="no-data">No other vessels in sector</p>
            )}
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className={`combat-interface ${animationState}`}>
      <div className="combat-header">
        <h2>COMBAT ENGAGEMENT</h2>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>
      
      {error && (
        <div className="combat-error">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}
      
      <div className="combat-main">
        {/* Player Status */}
        <div className="combatant player">
          <h3>{currentShip?.name || 'Your Ship'}</h3>
          <div className="ship-type">{currentShip?.type ? formatShipType(currentShip.type) : 'Unknown'}</div>
          
          <div className="health-bar">
            <div 
              className="health-fill"
              style={{ width: `${getHealthPercentage(playerHealth)}%` }}
            />
            <span className="health-text">{playerHealth}/100</span>
          </div>
          
          {currentShip && (
            <div className="combat-stats">
              <div>Attack: {currentShip.combat?.attack_rating || 0}</div>
              <div>Defense: {currentShip.combat?.defense_rating || 0}</div>
              <div>Drones: {currentShip.combat?.attack_drones || 0}</div>
            </div>
          )}
        </div>
        
        {/* Combat Arena */}
        <div className="combat-arena">
          {!combatId ? (
            <div className="pre-combat">
              <p>Prepare for combat against {target.name}</p>
              <button 
                className="cockpit-btn danger engage-btn"
                onClick={inititateCombat}
                disabled={isEngaging}
              >
                {isEngaging ? 'Engaging...' : 'ENGAGE COMBAT'}
              </button>
            </div>
          ) : (
            <div className="combat-active">
              <div className="combat-status">
                {combatStatus?.status === 'ongoing' ? (
                  <>
                    <div className="round-indicator">
                      Round {combatStatus.rounds.length}
                    </div>
                    <div className="combat-actions">
                      <button 
                        className={`action-btn ${selectedAction === 'fire' ? 'active' : ''}`}
                        onClick={() => setSelectedAction('fire')}
                      >
                        FIRE WEAPONS
                      </button>
                      <button 
                        className={`action-btn ${selectedAction === 'drones' ? 'active' : ''}`}
                        onClick={() => setSelectedAction('drones')}
                        disabled={!currentShip?.combat?.attack_drones}
                      >
                        DEPLOY DRONES
                      </button>
                      <button 
                        className={`action-btn retreat ${selectedAction === 'retreat' ? 'active' : ''}`}
                        onClick={attemptRetreat}
                      >
                        ATTEMPT RETREAT
                      </button>
                    </div>
                  </>
                ) : (
                  <div className="combat-result">
                    <h3>COMBAT COMPLETE</h3>
                    <div className="winner">
                      {combatStatus?.winner === 'attacker' ? 'VICTORY!' : 'DEFEATED'}
                    </div>
                    {combatStatus?.loot && (
                      <div className="loot-display">
                        <h4>Salvage Recovered:</h4>
                        <div>Credits: {combatStatus.loot.credits}</div>
                        {combatStatus.loot.items && combatStatus.loot.items.length > 0 && (
                          <div>
                            Items: {combatStatus.loot.items.join(', ')}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
        
        {/* Target Status */}
        <div className="combatant target">
          <h3>{target.name}</h3>
          <div className="ship-type">{target.type}</div>
          
          <div className="health-bar">
            <div 
              className="health-fill enemy"
              style={{ width: `${getHealthPercentage(targetHealth)}%` }}
            />
            <span className="health-text">{targetHealth}/100</span>
          </div>
          
          <div className="combat-stats">
            <div>Type: {target.type}</div>
            {target.shields && <div>Shields: {target.shields}</div>}
            {target.drones && <div>Drones: {target.drones}</div>}
          </div>
        </div>
      </div>
      
      {/* Combat Log */}
      {showCombatLog && combatStatus && (
        <div className="combat-log">
          <div className="log-header">
            <h4>COMBAT LOG</h4>
            <button 
              className="toggle-log"
              onClick={() => setShowCombatLog(!showCombatLog)}
            >
              {showCombatLog ? '−' : '+'}
            </button>
          </div>
          <div className="log-entries">
            {combatStatus.rounds.map((round, index) => (
              <div key={index} className="log-entry">
                <span className="round-num">R{round.roundNumber}:</span>
                <span className="attacker-action">
                  You {round.attackerAction.type === 'fire' ? 'fired weapons' : round.attackerAction.type}
                  {round.attackerAction.damage && ` (${round.attackerAction.damage} damage)`}
                </span>
                <span className="defender-action">
                  {target.name} {round.defenderAction.type === 'fire' ? 'returned fire' : round.defenderAction.type}
                  {round.defenderAction.damage && ` (${round.defenderAction.damage} damage)`}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};