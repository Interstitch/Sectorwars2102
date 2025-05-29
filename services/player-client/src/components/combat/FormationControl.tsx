import React, { useState, useCallback, useMemo } from 'react';
import { InputValidator } from '../../utils/security/inputValidation';
import './formation-control.css';

interface FormationMember {
  id: string;
  name: string;
  shipType: string;
  health: number;
  shields: number;
  position: 'leader' | 'wingman' | 'support' | 'flanker';
  status: 'ready' | 'engaged' | 'damaged' | 'retreating' | 'destroyed';
  distance: number; // Distance from formation center in km
}

interface Formation {
  id: string;
  name: string;
  type: 'diamond' | 'line' | 'wedge' | 'box' | 'scattered';
  members: FormationMember[];
  cohesion: number; // 0-100 formation cohesion percentage
  bonuses: {
    attack: number;
    defense: number;
    speed: number;
  };
}

interface FormationControlProps {
  currentPlayer: {
    id: string;
    name: string;
    shipType: string;
  };
  teamMembers: FormationMember[];
  onFormationChange?: (formation: Formation) => void;
  isInCombat?: boolean;
}

const FORMATION_TYPES = {
  diamond: {
    name: 'Diamond',
    positions: ['leader', 'wingman', 'wingman', 'support'],
    bonuses: { attack: 15, defense: 20, speed: -5 },
    description: 'Balanced formation with good defense'
  },
  line: {
    name: 'Line Abreast',
    positions: ['flanker', 'flanker', 'leader', 'flanker', 'flanker'],
    bonuses: { attack: 25, defense: -10, speed: 0 },
    description: 'Maximum firepower, vulnerable to flanking'
  },
  wedge: {
    name: 'Wedge',
    positions: ['leader', 'wingman', 'wingman', 'flanker', 'flanker'],
    bonuses: { attack: 20, defense: 10, speed: 5 },
    description: 'Aggressive formation for breaking through'
  },
  box: {
    name: 'Box',
    positions: ['leader', 'support', 'support', 'support'],
    bonuses: { attack: -5, defense: 30, speed: -10 },
    description: 'Defensive formation, protects vulnerable ships'
  },
  scattered: {
    name: 'Scattered',
    positions: ['leader', 'flanker', 'flanker', 'flanker', 'flanker'],
    bonuses: { attack: 0, defense: 0, speed: 20 },
    description: 'Evasive formation, hard to target'
  }
};

const FormationControl: React.FC<FormationControlProps> = ({
  currentPlayer,
  teamMembers,
  onFormationChange,
  isInCombat = false
}) => {
  const [selectedFormation, setSelectedFormation] = useState<keyof typeof FORMATION_TYPES>('diamond');
  const [isCreatingFormation, setIsCreatingFormation] = useState(false);
  const [formationName, setFormationName] = useState('');
  const [memberPositions, setMemberPositions] = useState<Map<string, FormationMember['position']>>(new Map());
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

  // Calculate formation cohesion based on member distances and statuses
  const calculateCohesion = useCallback((members: FormationMember[]): number => {
    if (members.length === 0) return 0;
    
    const activeMembers = members.filter(m => m.status !== 'destroyed');
    if (activeMembers.length === 0) return 0;
    
    // Base cohesion from active members
    let cohesion = (activeMembers.length / members.length) * 100;
    
    // Reduce cohesion based on average distance
    const avgDistance = activeMembers.reduce((sum, m) => sum + m.distance, 0) / activeMembers.length;
    const distancePenalty = Math.min(avgDistance / 100, 50); // Max 50% penalty from distance
    cohesion -= distancePenalty;
    
    // Reduce cohesion for damaged members
    const damagedMembers = activeMembers.filter(m => m.status === 'damaged' || m.status === 'retreating');
    const damagePenalty = (damagedMembers.length / activeMembers.length) * 20;
    cohesion -= damagePenalty;
    
    return Math.max(0, Math.min(100, cohesion));
  }, []);

  // Create formation with current settings
  const createFormation = useCallback(() => {
    if (!canPerformAction()) {
      console.warn('Rate limit exceeded');
      return;
    }

    const sanitizedName = InputValidator.sanitizeText(formationName);
    if (!sanitizedName || sanitizedName.length < 3) {
      alert('Formation name must be at least 3 characters');
      return;
    }

    const formationType = FORMATION_TYPES[selectedFormation];
    const allMembers = [
      {
        ...currentPlayer,
        health: 100,
        shields: 100,
        position: 'leader' as const,
        status: 'ready' as const,
        distance: 0
      },
      ...teamMembers
    ];

    // Assign positions based on formation type
    const positionedMembers = allMembers.map((member, index) => {
      const assignedPosition = memberPositions.get(member.id);
      const defaultPosition = formationType.positions[index] || 'support';
      return {
        ...member,
        position: (assignedPosition || defaultPosition) as FormationMember['position']
      };
    });

    const cohesion = calculateCohesion(positionedMembers);
    
    const formation: Formation = {
      id: `formation_${Date.now()}`,
      name: sanitizedName,
      type: selectedFormation,
      members: positionedMembers,
      cohesion,
      bonuses: {
        attack: formationType.bonuses.attack * (cohesion / 100),
        defense: formationType.bonuses.defense * (cohesion / 100),
        speed: formationType.bonuses.speed * (cohesion / 100)
      }
    };

    if (onFormationChange) {
      onFormationChange(formation);
    }

    setIsCreatingFormation(false);
    setFormationName('');
    setMemberPositions(new Map());
  }, [canPerformAction, formationName, selectedFormation, memberPositions, 
      currentPlayer, teamMembers, calculateCohesion, onFormationChange]);

  // Update member position
  const updateMemberPosition = useCallback((memberId: string, position: FormationMember['position']) => {
    setMemberPositions(prev => new Map(prev).set(memberId, position));
  }, []);

  // Formation visualization grid
  const renderFormationGrid = useMemo(() => {
    const formation = FORMATION_TYPES[selectedFormation];
    const positions = formation.positions;
    
    // Simple grid representation
    const grid: (FormationMember | null)[][] = [];
    
    switch (selectedFormation) {
      case 'diamond':
        grid.push([null, teamMembers[0] || null, null]);
        grid.push([teamMembers[1] || null, currentPlayer as any, teamMembers[2] || null]);
        grid.push([null, teamMembers[3] || null, null]);
        break;
      case 'line':
        grid.push([
          teamMembers[0] || null,
          teamMembers[1] || null,
          currentPlayer as any,
          teamMembers[2] || null,
          teamMembers[3] || null
        ]);
        break;
      case 'wedge':
        grid.push([null, currentPlayer as any, null]);
        grid.push([teamMembers[0] || null, null, teamMembers[1] || null]);
        grid.push([teamMembers[2] || null, null, teamMembers[3] || null]);
        break;
      case 'box':
        grid.push([teamMembers[0] || null, teamMembers[1] || null]);
        grid.push([currentPlayer as any, teamMembers[2] || null]);
        grid.push([teamMembers[3] || null, null]);
        break;
      case 'scattered':
        grid.push([teamMembers[0] || null, null, teamMembers[1] || null]);
        grid.push([null, currentPlayer as any, null]);
        grid.push([teamMembers[2] || null, null, teamMembers[3] || null]);
        break;
    }
    
    return grid;
  }, [selectedFormation, currentPlayer, teamMembers]);

  return (
    <div className="formation-control">
      <div className="control-header">
        <h3>Formation Control</h3>
        {isInCombat && <span className="combat-indicator">IN COMBAT</span>}
      </div>

      <div className="formation-selector">
        <h4>Select Formation Type</h4>
        <div className="formation-types">
          {Object.entries(FORMATION_TYPES).map(([key, formation]) => (
            <div
              key={key}
              className={`formation-type ${selectedFormation === key ? 'selected' : ''}`}
              onClick={() => !isInCombat && setSelectedFormation(key as keyof typeof FORMATION_TYPES)}
            >
              <h5>{formation.name}</h5>
              <p>{formation.description}</p>
              <div className="formation-bonuses">
                <span className={`bonus ${formation.bonuses.attack >= 0 ? 'positive' : 'negative'}`}>
                  ATK: {formation.bonuses.attack > 0 ? '+' : ''}{formation.bonuses.attack}%
                </span>
                <span className={`bonus ${formation.bonuses.defense >= 0 ? 'positive' : 'negative'}`}>
                  DEF: {formation.bonuses.defense > 0 ? '+' : ''}{formation.bonuses.defense}%
                </span>
                <span className={`bonus ${formation.bonuses.speed >= 0 ? 'positive' : 'negative'}`}>
                  SPD: {formation.bonuses.speed > 0 ? '+' : ''}{formation.bonuses.speed}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="formation-preview">
        <h4>Formation Preview</h4>
        <div className="formation-grid">
          {renderFormationGrid.map((row, rowIndex) => (
            <div key={rowIndex} className="grid-row">
              {row.map((member, colIndex) => (
                <div key={colIndex} className="grid-cell">
                  {member ? (
                    <div className={`member-icon ${member.id === currentPlayer.id ? 'player' : 'teammate'}`}>
                      <span className="member-name">{member.name}</span>
                      <span className="member-ship">{member.shipType}</span>
                    </div>
                  ) : (
                    <div className="empty-cell" />
                  )}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

      <div className="team-roster">
        <h4>Team Members</h4>
        <div className="member-list">
          <div className="member-item player">
            <div className="member-info">
              <span className="member-name">{currentPlayer.name} (You)</span>
              <span className="member-ship">{currentPlayer.shipType}</span>
            </div>
            <div className="member-position">
              <select
                value={memberPositions.get(currentPlayer.id) || 'leader'}
                onChange={(e) => updateMemberPosition(currentPlayer.id, e.target.value as FormationMember['position'])}
                disabled={isInCombat}
              >
                <option value="leader">Leader</option>
                <option value="wingman">Wingman</option>
                <option value="support">Support</option>
                <option value="flanker">Flanker</option>
              </select>
            </div>
          </div>

          {teamMembers.map(member => (
            <div key={member.id} className={`member-item ${member.status}`}>
              <div className="member-info">
                <span className="member-name">{member.name}</span>
                <span className="member-ship">{member.shipType}</span>
                <div className="member-stats">
                  <div className="stat-bar health">
                    <div className="stat-fill" style={{ width: `${member.health}%` }} />
                  </div>
                  <div className="stat-bar shields">
                    <div className="stat-fill" style={{ width: `${member.shields}%` }} />
                  </div>
                </div>
              </div>
              <div className="member-position">
                <select
                  value={memberPositions.get(member.id) || 'support'}
                  onChange={(e) => updateMemberPosition(member.id, e.target.value as FormationMember['position'])}
                  disabled={isInCombat || member.status === 'destroyed'}
                >
                  <option value="leader">Leader</option>
                  <option value="wingman">Wingman</option>
                  <option value="support">Support</option>
                  <option value="flanker">Flanker</option>
                </select>
              </div>
              <div className={`member-status ${member.status}`}>
                {member.status.toUpperCase()}
              </div>
            </div>
          ))}
        </div>
      </div>

      {!isInCombat && !isCreatingFormation && (
        <button 
          className="create-formation-btn"
          onClick={() => setIsCreatingFormation(true)}
        >
          Create Formation
        </button>
      )}

      {isCreatingFormation && (
        <div className="formation-creator">
          <h4>Name Your Formation</h4>
          <input
            type="text"
            value={formationName}
            onChange={(e) => setFormationName(e.target.value)}
            placeholder="e.g., Alpha Strike Wing"
            maxLength={50}
          />
          <div className="creator-actions">
            <button className="confirm-btn" onClick={createFormation}>
              Confirm Formation
            </button>
            <button 
              className="cancel-btn" 
              onClick={() => {
                setIsCreatingFormation(false);
                setFormationName('');
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {isInCombat && (
        <div className="combat-formation-info">
          <div className="cohesion-meter">
            <label>Formation Cohesion</label>
            <div className="meter-bar">
              <div 
                className="meter-fill"
                style={{ 
                  width: `${calculateCohesion(teamMembers)}%`,
                  backgroundColor: calculateCohesion(teamMembers) > 70 ? '#44ff44' : 
                                   calculateCohesion(teamMembers) > 40 ? '#ffaa44' : '#ff4444'
                }}
              />
            </div>
            <span className="cohesion-value">{calculateCohesion(teamMembers).toFixed(0)}%</span>
          </div>
          
          <div className="formation-commands">
            <button className="command-btn">Tighten Formation</button>
            <button className="command-btn">Break Formation</button>
            <button className="command-btn">Emergency Scatter</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FormationControl;