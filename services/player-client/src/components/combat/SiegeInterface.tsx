import React, { useState, useCallback, useEffect } from 'react';
import { InputValidator } from '../../utils/security/inputValidation';
import './siege-interface.css';

interface Planet {
  id: string;
  name: string;
  owner: string;
  population: number;
  defenseRating: number;
  shieldStrength: number;
  surfaceWeapons: number;
  orbitalPlatforms: number;
  productionRate: number;
}

interface SiegeStatus {
  id: string;
  planetId: string;
  attackerId: string;
  startTime: string;
  phase: 'orbital' | 'bombardment' | 'invasion' | 'captured' | 'failed';
  shieldsRemaining: number;
  defensesRemaining: number;
  populationRemaining: number;
  attackerLosses: {
    ships: number;
    drones: number;
    troops: number;
  };
  estimatedTimeToCapture: number; // minutes
}

interface BombardmentTarget {
  type: 'shields' | 'weapons' | 'infrastructure' | 'population';
  name: string;
  description: string;
  effectiveness: number;
  collateralDamage: number;
}

interface SiegeInterfaceProps {
  planet: Planet;
  attackingForce: {
    ships: number;
    drones: number;
    troops: number;
    bombardmentPower: number;
  };
  onSiegeStart?: (targetPriority: string) => void;
  onBombardment?: (target: BombardmentTarget['type']) => void;
  onInvasion?: (troopCount: number) => void;
  onRetreat?: () => void;
}

const BOMBARDMENT_TARGETS: BombardmentTarget[] = [
  {
    type: 'shields',
    name: 'Shield Generators',
    description: 'Target planetary shield generators to enable ground assault',
    effectiveness: 90,
    collateralDamage: 10
  },
  {
    type: 'weapons',
    name: 'Defense Systems',
    description: 'Destroy surface weapons and orbital platforms',
    effectiveness: 85,
    collateralDamage: 25
  },
  {
    type: 'infrastructure',
    name: 'Infrastructure',
    description: 'Target production facilities and supply lines',
    effectiveness: 75,
    collateralDamage: 60
  },
  {
    type: 'population',
    name: 'Population Centers',
    description: 'Direct assault on civilian areas (war crime)',
    effectiveness: 95,
    collateralDamage: 100
  }
];

const SiegeInterface: React.FC<SiegeInterfaceProps> = ({
  planet,
  attackingForce,
  onSiegeStart,
  onBombardment,
  onInvasion,
  onRetreat
}) => {
  const [siegeStatus, setSiegeStatus] = useState<SiegeStatus | null>(null);
  const [selectedTarget, setSelectedTarget] = useState<BombardmentTarget['type']>('shields');
  const [invasionTroops, setInvasionTroops] = useState(Math.floor(attackingForce.troops * 0.5));
  const [bombardmentIntensity, setBombardmentIntensity] = useState(50);
  const [lastAction, setLastAction] = useState<number>(0);
  const [warningAccepted, setWarningAccepted] = useState(false);

  // Rate limiting
  const RATE_LIMIT_MS = 2000; // Longer for siege actions
  const canPerformAction = useCallback(() => {
    const now = Date.now();
    if (now - lastAction < RATE_LIMIT_MS) {
      return false;
    }
    setLastAction(now);
    return true;
  }, [lastAction]);

  // Simulate siege progress
  useEffect(() => {
    if (!siegeStatus || siegeStatus.phase === 'captured' || siegeStatus.phase === 'failed') {
      return;
    }

    const interval = setInterval(() => {
      setSiegeStatus(prev => {
        if (!prev) return null;

        // Simulate progress based on phase
        let updated = { ...prev };
        
        if (prev.phase === 'orbital' && prev.shieldsRemaining <= 0) {
          updated.phase = 'bombardment';
        } else if (prev.phase === 'bombardment' && prev.defensesRemaining <= 0) {
          updated.phase = 'invasion';
        } else if (prev.phase === 'invasion' && prev.populationRemaining <= planet.population * 0.1) {
          updated.phase = 'captured';
        }

        // Apply damage based on bombardment intensity
        if (prev.phase === 'orbital' || prev.phase === 'bombardment') {
          const damage = (bombardmentIntensity / 100) * attackingForce.bombardmentPower * 0.1;
          
          if (selectedTarget === 'shields') {
            updated.shieldsRemaining = Math.max(0, prev.shieldsRemaining - damage);
          } else if (selectedTarget === 'weapons') {
            updated.defensesRemaining = Math.max(0, prev.defensesRemaining - damage * 0.8);
          } else if (selectedTarget === 'infrastructure') {
            updated.defensesRemaining = Math.max(0, prev.defensesRemaining - damage * 0.5);
            updated.populationRemaining = Math.max(0, prev.populationRemaining - damage * 0.2);
          } else if (selectedTarget === 'population') {
            updated.populationRemaining = Math.max(0, prev.populationRemaining - damage);
          }
        }

        // Calculate losses
        const defensePower = (prev.defensesRemaining / 100) * planet.defenseRating;
        updated.attackerLosses.drones += Math.floor(Math.random() * defensePower * 0.1);
        
        return updated;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [siegeStatus, bombardmentIntensity, selectedTarget, attackingForce, planet]);

  const startSiege = useCallback(() => {
    if (!canPerformAction()) {
      console.warn('Rate limit exceeded');
      return;
    }

    const newSiege: SiegeStatus = {
      id: `siege_${Date.now()}`,
      planetId: planet.id,
      attackerId: 'player', // Would come from auth context
      startTime: new Date().toISOString(),
      phase: 'orbital',
      shieldsRemaining: planet.shieldStrength,
      defensesRemaining: planet.defenseRating,
      populationRemaining: planet.population,
      attackerLosses: {
        ships: 0,
        drones: 0,
        troops: 0
      },
      estimatedTimeToCapture: Math.floor((planet.defenseRating + planet.shieldStrength) / attackingForce.bombardmentPower * 60)
    };

    setSiegeStatus(newSiege);
    
    if (onSiegeStart) {
      onSiegeStart(selectedTarget);
    }
  }, [canPerformAction, planet, attackingForce, selectedTarget, onSiegeStart]);

  const performBombardment = useCallback(() => {
    if (!canPerformAction() || !siegeStatus) {
      return;
    }

    if (onBombardment) {
      onBombardment(selectedTarget);
    }
  }, [canPerformAction, siegeStatus, selectedTarget, onBombardment]);

  const launchInvasion = useCallback(() => {
    if (!canPerformAction() || !siegeStatus || siegeStatus.phase !== 'invasion') {
      return;
    }

    const sanitizedTroops = Math.max(0, Math.min(attackingForce.troops, invasionTroops));
    
    if (onInvasion) {
      onInvasion(sanitizedTroops);
    }
  }, [canPerformAction, siegeStatus, invasionTroops, attackingForce.troops, onInvasion]);

  const retreatForces = useCallback(() => {
    if (!canPerformAction()) {
      return;
    }

    if (window.confirm('Are you sure you want to retreat? This will end the siege.')) {
      setSiegeStatus(null);
      if (onRetreat) {
        onRetreat();
      }
    }
  }, [canPerformAction, onRetreat]);

  // Calculate siege effectiveness
  const siegeEffectiveness = siegeStatus ? {
    shieldDamage: ((planet.shieldStrength - siegeStatus.shieldsRemaining) / planet.shieldStrength) * 100,
    defenseDamage: ((planet.defenseRating - siegeStatus.defensesRemaining) / planet.defenseRating) * 100,
    populationImpact: ((planet.population - siegeStatus.populationRemaining) / planet.population) * 100
  } : null;

  return (
    <div className="siege-interface">
      <div className="siege-header">
        <h3>Planetary Siege Control</h3>
        {siegeStatus && (
          <div className={`siege-phase ${siegeStatus.phase}`}>
            Phase: {siegeStatus.phase.toUpperCase()}
          </div>
        )}
      </div>

      {!siegeStatus ? (
        <div className="pre-siege">
          <div className="planet-info">
            <h4>{planet.name}</h4>
            <div className="planet-stats">
              <div className="stat-row">
                <span>Owner:</span>
                <span className="owner-name">{planet.owner}</span>
              </div>
              <div className="stat-row">
                <span>Population:</span>
                <span>{planet.population.toLocaleString()}</span>
              </div>
              <div className="stat-row">
                <span>Defense Rating:</span>
                <span>{planet.defenseRating}</span>
              </div>
              <div className="stat-row">
                <span>Shield Strength:</span>
                <span>{planet.shieldStrength}%</span>
              </div>
              <div className="stat-row">
                <span>Surface Weapons:</span>
                <span>{planet.surfaceWeapons}</span>
              </div>
              <div className="stat-row">
                <span>Orbital Platforms:</span>
                <span>{planet.orbitalPlatforms}</span>
              </div>
            </div>
          </div>

          <div className="attacking-force">
            <h4>Your Forces</h4>
            <div className="force-stats">
              <div className="stat-row">
                <span>Ships:</span>
                <span>{attackingForce.ships}</span>
              </div>
              <div className="stat-row">
                <span>Drones:</span>
                <span>{attackingForce.drones}</span>
              </div>
              <div className="stat-row">
                <span>Troops:</span>
                <span>{attackingForce.troops.toLocaleString()}</span>
              </div>
              <div className="stat-row">
                <span>Bombardment Power:</span>
                <span>{attackingForce.bombardmentPower}</span>
              </div>
            </div>
          </div>

          <div className="siege-planning">
            <h4>Siege Strategy</h4>
            <div className="target-selection">
              <label>Primary Target:</label>
              <select 
                value={selectedTarget}
                onChange={(e) => setSelectedTarget(e.target.value as BombardmentTarget['type'])}
              >
                {BOMBARDMENT_TARGETS.map(target => (
                  <option key={target.type} value={target.type}>
                    {target.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="target-info">
              {BOMBARDMENT_TARGETS.find(t => t.type === selectedTarget) && (
                <div className="target-details">
                  <p>{BOMBARDMENT_TARGETS.find(t => t.type === selectedTarget)!.description}</p>
                  <div className="target-stats">
                    <div className="effectiveness">
                      <span>Effectiveness:</span>
                      <div className="bar">
                        <div 
                          className="bar-fill"
                          style={{ 
                            width: `${BOMBARDMENT_TARGETS.find(t => t.type === selectedTarget)!.effectiveness}%`,
                            backgroundColor: '#44ff44'
                          }}
                        />
                      </div>
                    </div>
                    <div className="collateral">
                      <span>Collateral Damage:</span>
                      <div className="bar">
                        <div 
                          className="bar-fill"
                          style={{ 
                            width: `${BOMBARDMENT_TARGETS.find(t => t.type === selectedTarget)!.collateralDamage}%`,
                            backgroundColor: '#ff4444'
                          }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {selectedTarget === 'population' && !warningAccepted && (
              <div className="war-crime-warning">
                <p>⚠️ WARNING: Targeting civilian populations is a war crime!</p>
                <p>This action will severely damage your reputation with all factions.</p>
                <label>
                  <input 
                    type="checkbox"
                    checked={warningAccepted}
                    onChange={(e) => setWarningAccepted(e.target.checked)}
                  />
                  I understand the consequences
                </label>
              </div>
            )}

            <button 
              className="start-siege-btn"
              onClick={startSiege}
              disabled={selectedTarget === 'population' && !warningAccepted}
            >
              Begin Siege
            </button>
          </div>
        </div>
      ) : (
        <div className="active-siege">
          <div className="siege-status">
            <h4>Siege Progress</h4>
            <div className="progress-bars">
              <div className="progress-item">
                <label>Shields</label>
                <div className="progress-bar">
                  <div 
                    className="progress-fill shields"
                    style={{ width: `${(siegeStatus.shieldsRemaining / planet.shieldStrength) * 100}%` }}
                  />
                </div>
                <span>{siegeStatus.shieldsRemaining.toFixed(0)}%</span>
              </div>
              <div className="progress-item">
                <label>Defenses</label>
                <div className="progress-bar">
                  <div 
                    className="progress-fill defenses"
                    style={{ width: `${(siegeStatus.defensesRemaining / planet.defenseRating) * 100}%` }}
                  />
                </div>
                <span>{siegeStatus.defensesRemaining.toFixed(0)}%</span>
              </div>
              <div className="progress-item">
                <label>Population</label>
                <div className="progress-bar">
                  <div 
                    className="progress-fill population"
                    style={{ width: `${(siegeStatus.populationRemaining / planet.population) * 100}%` }}
                  />
                </div>
                <span>{((siegeStatus.populationRemaining / planet.population) * 100).toFixed(0)}%</span>
              </div>
            </div>
          </div>

          <div className="bombardment-controls">
            <h4>Bombardment Controls</h4>
            <div className="intensity-control">
              <label>Bombardment Intensity: {bombardmentIntensity}%</label>
              <input 
                type="range"
                min="0"
                max="100"
                value={bombardmentIntensity}
                onChange={(e) => setBombardmentIntensity(parseInt(e.target.value))}
                className="intensity-slider"
              />
              <div className="intensity-labels">
                <span>Minimal</span>
                <span>Moderate</span>
                <span>Maximum</span>
              </div>
            </div>

            <div className="target-switch">
              <label>Current Target:</label>
              <select 
                value={selectedTarget}
                onChange={(e) => setSelectedTarget(e.target.value as BombardmentTarget['type'])}
              >
                {BOMBARDMENT_TARGETS.map(target => (
                  <option key={target.type} value={target.type}>
                    {target.name}
                  </option>
                ))}
              </select>
            </div>

            <button 
              className="bombardment-btn"
              onClick={performBombardment}
              disabled={siegeStatus.phase === 'invasion' || siegeStatus.phase === 'captured'}
            >
              Execute Bombardment
            </button>
          </div>

          {siegeStatus.phase === 'invasion' && (
            <div className="invasion-controls">
              <h4>Ground Invasion</h4>
              <div className="troop-deployment">
                <label>Deploy Troops: {invasionTroops.toLocaleString()}</label>
                <input 
                  type="range"
                  min="0"
                  max={attackingForce.troops}
                  value={invasionTroops}
                  onChange={(e) => setInvasionTroops(parseInt(e.target.value))}
                  className="troop-slider"
                />
                <div className="troop-info">
                  <span>Available: {attackingForce.troops.toLocaleString()}</span>
                  <span>Reserve: {(attackingForce.troops - invasionTroops).toLocaleString()}</span>
                </div>
              </div>
              <button 
                className="invasion-btn"
                onClick={launchInvasion}
              >
                Launch Ground Assault
              </button>
            </div>
          )}

          <div className="losses-report">
            <h4>Combat Losses</h4>
            <div className="loss-stats">
              <div className="loss-item">
                <span>Ships:</span>
                <span className="loss-value">{siegeStatus.attackerLosses.ships}</span>
              </div>
              <div className="loss-item">
                <span>Drones:</span>
                <span className="loss-value">{siegeStatus.attackerLosses.drones}</span>
              </div>
              <div className="loss-item">
                <span>Troops:</span>
                <span className="loss-value">{siegeStatus.attackerLosses.troops.toLocaleString()}</span>
              </div>
            </div>
          </div>

          {siegeEffectiveness && (
            <div className="effectiveness-report">
              <h4>Siege Effectiveness</h4>
              <div className="effectiveness-stats">
                <div className="eff-item">
                  <span>Shield Damage:</span>
                  <span className={siegeEffectiveness.shieldDamage > 50 ? 'good' : 'poor'}>
                    {siegeEffectiveness.shieldDamage.toFixed(0)}%
                  </span>
                </div>
                <div className="eff-item">
                  <span>Defense Damage:</span>
                  <span className={siegeEffectiveness.defenseDamage > 50 ? 'good' : 'poor'}>
                    {siegeEffectiveness.defenseDamage.toFixed(0)}%
                  </span>
                </div>
                <div className="eff-item">
                  <span>Civilian Impact:</span>
                  <span className={siegeEffectiveness.populationImpact > 20 ? 'severe' : 'minimal'}>
                    {siegeEffectiveness.populationImpact.toFixed(0)}%
                  </span>
                </div>
              </div>
            </div>
          )}

          <div className="siege-actions">
            <button 
              className="retreat-btn"
              onClick={retreatForces}
            >
              Retreat Forces
            </button>
          </div>

          {siegeStatus.phase === 'captured' && (
            <div className="victory-message">
              <h3>🎉 Planet Captured!</h3>
              <p>{planet.name} is now under your control.</p>
              <p>Remaining population: {siegeStatus.populationRemaining.toLocaleString()}</p>
            </div>
          )}

          {siegeStatus.phase === 'failed' && (
            <div className="failure-message">
              <h3>❌ Siege Failed</h3>
              <p>Your forces have been repelled from {planet.name}.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SiegeInterface;