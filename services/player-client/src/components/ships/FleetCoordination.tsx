import React, { useState, useMemo, useCallback } from 'react';
import { Ship } from '../../types/game';
import { InputValidator } from '../../utils/security/inputValidation';
import './fleet-coordination.css';

interface FleetShip extends Ship {
  location: string;
  status: 'idle' | 'traveling' | 'trading' | 'combat' | 'docked' | 'maintenance';
  currentMission?: Mission;
  distanceFromLeader?: number;
  eta?: string;
}

interface Mission {
  id: string;
  type: 'patrol' | 'trade' | 'escort' | 'mining' | 'exploration' | 'combat';
  name: string;
  description: string;
  destination: string;
  reward: number;
  duration: number; // hours
  danger: 'low' | 'medium' | 'high';
  requirements?: {
    minShips?: number;
    shipTypes?: string[];
    minCombatPower?: number;
  };
  assignedShips: string[];
}

interface FleetFormation {
  id: string;
  name: string;
  type: 'convoy' | 'combat' | 'mining' | 'exploration';
  leader: string;
  members: string[];
  bonuses: {
    speed: number;
    defense: number;
    efficiency: number;
  };
}

interface FleetCoordinationProps {
  playerShips: FleetShip[];
  availableMissions: Mission[];
  activeFormations: FleetFormation[];
  currentLocation: string;
  onCreateFormation?: (formation: Omit<FleetFormation, 'id'>) => void;
  onDisbandFormation?: (formationId: string) => void;
  onAssignMission?: (shipIds: string[], missionId: string) => void;
  onRecallShip?: (shipId: string) => void;
  onSetWaypoint?: (shipIds: string[], destination: string) => void;
}

const FORMATION_TYPES = {
  convoy: {
    name: 'Trade Convoy',
    description: 'Optimized for safe cargo transport',
    bonuses: { speed: -10, defense: 20, efficiency: 15 },
    icon: '🚛'
  },
  combat: {
    name: 'Combat Wing',
    description: 'Maximizes firepower and coordination',
    bonuses: { speed: 5, defense: 15, efficiency: -5 },
    icon: '⚔️'
  },
  mining: {
    name: 'Mining Fleet',
    description: 'Efficient resource extraction',
    bonuses: { speed: -15, defense: 0, efficiency: 30 },
    icon: '⛏️'
  },
  exploration: {
    name: 'Explorer Group',
    description: 'Extended range and sensor coverage',
    bonuses: { speed: 20, defense: -10, efficiency: 10 },
    icon: '🔭'
  }
};

const FleetCoordination: React.FC<FleetCoordinationProps> = ({
  playerShips,
  availableMissions,
  activeFormations,
  currentLocation,
  onCreateFormation,
  onDisbandFormation,
  onAssignMission,
  onRecallShip,
  onSetWaypoint
}) => {
  const [selectedShips, setSelectedShips] = useState<Set<string>>(new Set());
  const [viewMode, setViewMode] = useState<'overview' | 'missions' | 'formations'>('overview');
  const [selectedMission, setSelectedMission] = useState<Mission | null>(null);
  const [isCreatingFormation, setIsCreatingFormation] = useState(false);
  const [formationName, setFormationName] = useState('');
  const [formationType, setFormationType] = useState<keyof typeof FORMATION_TYPES>('convoy');
  const [formationLeader, setFormationLeader] = useState<string>('');
  const [lastAction, setLastAction] = useState<number>(0);

  // Rate limiting
  const RATE_LIMIT_MS = 1000;
  const canPerformAction = useCallback(() => {
    const now = Date.now();
    if (now - lastAction < RATE_LIMIT_MS) {
      return false;
    }
    setLastAction(now);
    return true;
  }, [lastAction]);

  // Fleet statistics
  const fleetStats = useMemo(() => {
    const stats = {
      totalShips: playerShips.length,
      idleShips: playerShips.filter(s => s.status === 'idle').length,
      onMission: playerShips.filter(s => s.currentMission).length,
      inFormation: activeFormations.reduce((count, f) => count + f.members.length, 0),
      totalCombatPower: playerShips.reduce((sum, s) => sum + ((s as any).weapons || 0) + ((s as any).shields || 0), 0),
      totalCargoCapacity: playerShips.reduce((sum, s) => sum + s.cargo_capacity, 0),
      fleetValue: playerShips.reduce((sum, s) => sum + 50000, 0) // Mock value calculation
    };
    return stats;
  }, [playerShips, activeFormations]);

  // Available ships for operations
  const availableShips = useMemo(() => {
    return playerShips.filter(ship => 
      ship.status === 'idle' && 
      ship.location === currentLocation &&
      !activeFormations.some(f => f.members.includes(ship.id))
    );
  }, [playerShips, currentLocation, activeFormations]);

  // Toggle ship selection
  const toggleShipSelection = useCallback((shipId: string) => {
    setSelectedShips(prev => {
      const newSet = new Set(prev);
      if (newSet.has(shipId)) {
        newSet.delete(shipId);
      } else {
        newSet.add(shipId);
      }
      return newSet;
    });
  }, []);

  // Select all available ships
  const selectAllAvailable = useCallback(() => {
    setSelectedShips(new Set(availableShips.map(s => s.id)));
  }, [availableShips]);

  // Create formation
  const createFormation = useCallback(() => {
    if (!canPerformAction() || !onCreateFormation) return;

    const sanitizedName = InputValidator.sanitizeText(formationName);
    if (!sanitizedName || sanitizedName.length < 3) {
      alert('Formation name must be at least 3 characters');
      return;
    }

    if (selectedShips.size < 2) {
      alert('A formation requires at least 2 ships');
      return;
    }

    if (!formationLeader || !selectedShips.has(formationLeader)) {
      alert('Please select a valid formation leader');
      return;
    }

    const formation: Omit<FleetFormation, 'id'> = {
      name: sanitizedName,
      type: formationType,
      leader: formationLeader,
      members: Array.from(selectedShips),
      bonuses: FORMATION_TYPES[formationType].bonuses
    };

    onCreateFormation(formation);
    setIsCreatingFormation(false);
    setFormationName('');
    setSelectedShips(new Set());
    setFormationLeader('');
  }, [canPerformAction, onCreateFormation, formationName, selectedShips, 
      formationType, formationLeader]);

  // Assign mission
  const assignMission = useCallback(() => {
    if (!canPerformAction() || !onAssignMission || !selectedMission) return;

    if (selectedShips.size === 0) {
      alert('Select ships to assign to this mission');
      return;
    }

    // Check mission requirements
    if (selectedMission.requirements) {
      const selectedShipsList = playerShips.filter(s => selectedShips.has(s.id));
      
      if (selectedMission.requirements.minShips && selectedShips.size < selectedMission.requirements.minShips) {
        alert(`This mission requires at least ${selectedMission.requirements.minShips} ships`);
        return;
      }

      if (selectedMission.requirements.minCombatPower) {
        const combatPower = selectedShipsList.reduce((sum, s) => sum + ((s as any).weapons || 0) + ((s as any).shields || 0), 0);
        if (combatPower < selectedMission.requirements.minCombatPower) {
          alert(`Insufficient combat power. Required: ${selectedMission.requirements.minCombatPower}`);
          return;
        }
      }
    }

    onAssignMission(Array.from(selectedShips), selectedMission.id);
    setSelectedShips(new Set());
    setSelectedMission(null);
  }, [canPerformAction, onAssignMission, selectedMission, selectedShips, playerShips]);

  // Recall ship
  const recallShip = useCallback((shipId: string) => {
    if (!canPerformAction() || !onRecallShip) return;

    if (window.confirm('Recall this ship to base? Any mission progress will be lost.')) {
      onRecallShip(shipId);
    }
  }, [canPerformAction, onRecallShip]);

  // Get ship status color
  const getStatusColor = (status: FleetShip['status']) => {
    const colors = {
      idle: '#44ff44',
      traveling: '#4a9eff',
      trading: '#ffaa44',
      combat: '#ff4444',
      docked: '#888888',
      maintenance: '#ff8844'
    };
    return colors[status] || '#ffffff';
  };

  // Get mission danger color
  const getDangerColor = (danger: Mission['danger']) => {
    const colors = {
      low: '#44ff44',
      medium: '#ffaa44',
      high: '#ff4444'
    };
    return colors[danger];
  };

  return (
    <div className="fleet-coordination">
      <div className="coordination-header">
        <h3>Fleet Coordination</h3>
        <div className="fleet-summary">
          <span className="stat-item">
            <span className="stat-label">Ships:</span>
            <span className="stat-value">{fleetStats.totalShips}</span>
          </span>
          <span className="stat-item">
            <span className="stat-label">Available:</span>
            <span className="stat-value">{fleetStats.idleShips}</span>
          </span>
          <span className="stat-item">
            <span className="stat-label">On Mission:</span>
            <span className="stat-value">{fleetStats.onMission}</span>
          </span>
          <span className="stat-item">
            <span className="stat-label">Fleet Value:</span>
            <span className="stat-value">{fleetStats.fleetValue.toLocaleString()} cr</span>
          </span>
        </div>
      </div>

      <div className="view-tabs">
        <button
          className={`tab-btn ${viewMode === 'overview' ? 'active' : ''}`}
          onClick={() => setViewMode('overview')}
        >
          Fleet Overview
        </button>
        <button
          className={`tab-btn ${viewMode === 'missions' ? 'active' : ''}`}
          onClick={() => setViewMode('missions')}
        >
          Missions ({availableMissions.length})
        </button>
        <button
          className={`tab-btn ${viewMode === 'formations' ? 'active' : ''}`}
          onClick={() => setViewMode('formations')}
        >
          Formations ({activeFormations.length})
        </button>
      </div>

      <div className="coordination-content">
        {viewMode === 'overview' && (
          <div className="fleet-overview">
            <div className="ships-panel">
              <div className="panel-header">
                <h4>Fleet Ships</h4>
                <div className="ship-actions">
                  <button 
                    className="select-all-btn"
                    onClick={selectAllAvailable}
                    disabled={availableShips.length === 0}
                  >
                    Select Available
                  </button>
                  {selectedShips.size > 0 && (
                    <span className="selection-count">{selectedShips.size} selected</span>
                  )}
                </div>
              </div>

              <div className="ships-grid">
                {playerShips.map(ship => {
                  const isSelected = selectedShips.has(ship.id);
                  const isAvailable = availableShips.includes(ship);
                  const formation = activeFormations.find(f => f.members.includes(ship.id));
                  
                  return (
                    <div
                      key={ship.id}
                      className={`fleet-ship ${isSelected ? 'selected' : ''} ${!isAvailable ? 'unavailable' : ''}`}
                      onClick={() => isAvailable && toggleShipSelection(ship.id)}
                    >
                      <div className="ship-header">
                        <h5>{ship.name}</h5>
                        <span 
                          className="ship-status"
                          style={{ color: getStatusColor(ship.status) }}
                        >
                          {ship.status.toUpperCase()}
                        </span>
                      </div>
                      
                      <div className="ship-info">
                        <div className="info-row">
                          <span>Type:</span>
                          <span>{ship.type}</span>
                        </div>
                        <div className="info-row">
                          <span>Location:</span>
                          <span>{ship.location}</span>
                        </div>
                        <div className="info-row">
                          <span>Combat:</span>
                          <span>{(ship as any).weapons + (ship as any).shields}</span>
                        </div>
                        <div className="info-row">
                          <span>Cargo:</span>
                          <span>{(ship as any).cargoUsed || 0}/{ship.cargo_capacity}</span>
                        </div>
                      </div>

                      {ship.currentMission && (
                        <div className="mission-badge">
                          Mission: {ship.currentMission.name}
                        </div>
                      )}

                      {formation && (
                        <div className="formation-badge">
                          {FORMATION_TYPES[formation.type].icon} {formation.name}
                        </div>
                      )}

                      {ship.eta && (
                        <div className="eta-info">
                          ETA: {ship.eta}
                        </div>
                      )}

                      {ship.status !== 'idle' && ship.location !== currentLocation && onRecallShip && (
                        <button 
                          className="recall-btn"
                          onClick={(e) => {
                            e.stopPropagation();
                            recallShip(ship.id);
                          }}
                        >
                          Recall
                        </button>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {selectedShips.size > 0 && (
              <div className="quick-actions">
                <h4>Quick Actions</h4>
                <div className="action-buttons">
                  <button 
                    className="action-btn"
                    onClick={() => setIsCreatingFormation(true)}
                  >
                    Create Formation
                  </button>
                  <button 
                    className="action-btn"
                    onClick={() => setViewMode('missions')}
                  >
                    Assign Mission
                  </button>
                  {onSetWaypoint && (
                    <button 
                      className="action-btn"
                      onClick={() => {
                        const destination = prompt('Enter destination:');
                        if (destination) {
                          onSetWaypoint(Array.from(selectedShips), destination);
                        }
                      }}
                    >
                      Set Waypoint
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {viewMode === 'missions' && (
          <div className="missions-view">
            <div className="missions-list">
              <h4>Available Missions</h4>
              <div className="missions-grid">
                {availableMissions.map(mission => (
                  <div
                    key={mission.id}
                    className={`mission-card ${selectedMission?.id === mission.id ? 'selected' : ''}`}
                    onClick={() => setSelectedMission(mission)}
                  >
                    <div className="mission-header">
                      <h5>{mission.name}</h5>
                      <span 
                        className="danger-level"
                        style={{ color: getDangerColor(mission.danger) }}
                      >
                        {mission.danger.toUpperCase()}
                      </span>
                    </div>
                    
                    <p className="mission-description">{mission.description}</p>
                    
                    <div className="mission-details">
                      <div className="detail-row">
                        <span>Type:</span>
                        <span>{mission.type}</span>
                      </div>
                      <div className="detail-row">
                        <span>Destination:</span>
                        <span>{mission.destination}</span>
                      </div>
                      <div className="detail-row">
                        <span>Duration:</span>
                        <span>{mission.duration}h</span>
                      </div>
                      <div className="detail-row">
                        <span>Reward:</span>
                        <span className="reward">{mission.reward.toLocaleString()} cr</span>
                      </div>
                    </div>
                    
                    {mission.requirements && (
                      <div className="mission-requirements">
                        <h6>Requirements:</h6>
                        {mission.requirements.minShips && (
                          <p>Min Ships: {mission.requirements.minShips}</p>
                        )}
                        {mission.requirements.shipTypes && (
                          <p>Ship Types: {mission.requirements.shipTypes.join(', ')}</p>
                        )}
                        {mission.requirements.minCombatPower && (
                          <p>Min Combat Power: {mission.requirements.minCombatPower}</p>
                        )}
                      </div>
                    )}
                    
                    {mission.assignedShips.length > 0 && (
                      <div className="assigned-ships">
                        {mission.assignedShips.length} ships assigned
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {selectedMission && (
              <div className="mission-assignment">
                <h4>Assign Ships to Mission</h4>
                <div className="assignment-info">
                  <h5>{selectedMission.name}</h5>
                  <p>Select ships from the overview to assign to this mission.</p>
                  <p>Selected: {selectedShips.size} ships</p>
                  
                  <button 
                    className="assign-btn"
                    onClick={assignMission}
                    disabled={selectedShips.size === 0}
                  >
                    Assign to Mission
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {viewMode === 'formations' && (
          <div className="formations-view">
            <div className="formations-header">
              <h4>Active Formations</h4>
              <button 
                className="create-formation-btn"
                onClick={() => setIsCreatingFormation(true)}
              >
                Create New Formation
              </button>
            </div>

            <div className="formations-grid">
              {activeFormations.map(formation => {
                const leader = playerShips.find(s => s.id === formation.leader);
                const members = playerShips.filter(s => formation.members.includes(s.id));
                
                return (
                  <div key={formation.id} className="formation-card">
                    <div className="formation-header">
                      <h5>
                        {FORMATION_TYPES[formation.type].icon} {formation.name}
                      </h5>
                      <span className="formation-type">{formation.type}</span>
                    </div>
                    
                    <div className="formation-stats">
                      <div className="stat">
                        <span>Ships:</span>
                        <span>{formation.members.length}</span>
                      </div>
                      <div className="stat">
                        <span>Leader:</span>
                        <span>{leader?.name || 'Unknown'}</span>
                      </div>
                    </div>
                    
                    <div className="formation-bonuses">
                      <h6>Bonuses:</h6>
                      <div className="bonus-list">
                        <span className={formation.bonuses.speed >= 0 ? 'positive' : 'negative'}>
                          Speed: {formation.bonuses.speed > 0 ? '+' : ''}{formation.bonuses.speed}%
                        </span>
                        <span className={formation.bonuses.defense >= 0 ? 'positive' : 'negative'}>
                          Defense: {formation.bonuses.defense > 0 ? '+' : ''}{formation.bonuses.defense}%
                        </span>
                        <span className={formation.bonuses.efficiency >= 0 ? 'positive' : 'negative'}>
                          Efficiency: {formation.bonuses.efficiency > 0 ? '+' : ''}{formation.bonuses.efficiency}%
                        </span>
                      </div>
                    </div>
                    
                    <div className="formation-members">
                      <h6>Members:</h6>
                      <div className="members-list">
                        {members.map(ship => (
                          <div key={ship.id} className="member-item">
                            <span className="member-name">{ship.name}</span>
                            <span className="member-status" style={{ color: getStatusColor(ship.status) }}>
                              {ship.status}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    {onDisbandFormation && (
                      <button 
                        className="disband-btn"
                        onClick={() => {
                          if (window.confirm(`Disband formation "${formation.name}"?`)) {
                            onDisbandFormation(formation.id);
                          }
                        }}
                      >
                        Disband Formation
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {isCreatingFormation && (
        <div className="formation-creator-overlay">
          <div className="formation-creator">
            <h4>Create New Formation</h4>
            
            <div className="form-group">
              <label>Formation Name</label>
              <input
                type="text"
                value={formationName}
                onChange={(e) => setFormationName(e.target.value)}
                placeholder="e.g., Alpha Trading Wing"
                maxLength={50}
              />
            </div>
            
            <div className="form-group">
              <label>Formation Type</label>
              <div className="formation-type-selector">
                {Object.entries(FORMATION_TYPES).map(([key, type]) => (
                  <div
                    key={key}
                    className={`type-option ${formationType === key ? 'selected' : ''}`}
                    onClick={() => setFormationType(key as keyof typeof FORMATION_TYPES)}
                  >
                    <span className="type-icon">{type.icon}</span>
                    <h5>{type.name}</h5>
                    <p>{type.description}</p>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="form-group">
              <label>Formation Leader</label>
              <select 
                value={formationLeader}
                onChange={(e) => setFormationLeader(e.target.value)}
              >
                <option value="">Select leader...</option>
                {Array.from(selectedShips).map(shipId => {
                  const ship = playerShips.find(s => s.id === shipId);
                  return ship ? (
                    <option key={ship.id} value={ship.id}>
                      {ship.name} ({ship.type})
                    </option>
                  ) : null;
                })}
              </select>
            </div>
            
            <div className="selected-ships-summary">
              <h5>Selected Ships: {selectedShips.size}</h5>
              <div className="ships-list">
                {Array.from(selectedShips).map(shipId => {
                  const ship = playerShips.find(s => s.id === shipId);
                  return ship ? (
                    <span key={ship.id} className="ship-tag">
                      {ship.name}
                    </span>
                  ) : null;
                })}
              </div>
            </div>
            
            <div className="creator-actions">
              <button 
                className="create-btn"
                onClick={createFormation}
                disabled={!formationName || selectedShips.size < 2 || !formationLeader}
              >
                Create Formation
              </button>
              <button 
                className="cancel-btn"
                onClick={() => {
                  setIsCreatingFormation(false);
                  setFormationName('');
                  setFormationLeader('');
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FleetCoordination;