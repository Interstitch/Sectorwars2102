import React, { useState, useCallback, useMemo } from 'react';
import { InputValidator } from '../../utils/security/inputValidation';
import { gameAPI } from '../../services/api';
import { Ship } from '../../types/game';
import './tactical-planner.css';

interface TacticalPlan {
  id: string;
  name: string;
  targetPriority: 'shields' | 'weapons' | 'engines' | 'hull';
  droneStrategy: 'aggressive' | 'defensive' | 'balanced';
  retreatCondition: 'never' | 'hull50' | 'hull25' | 'shields0';
  formationRole?: 'leader' | 'support' | 'flanker';
  useSpecialWeapons: boolean;
  notes: string;
  createdAt: string;
  lastUsed?: string;
}

interface TacticalPlannerProps {
  ship: Ship;
  onPlanSelect?: (plan: TacticalPlan) => void;
  isInFormation?: boolean;
  teamMembers?: Array<{ id: string; name: string; ship: string }>;
}

const TacticalPlanner: React.FC<TacticalPlannerProps> = ({
  ship,
  onPlanSelect,
  isInFormation = false,
  teamMembers = []
}) => {
  const [savedPlans, setSavedPlans] = useState<TacticalPlan[]>([]);
  const [isCreating, setIsCreating] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<TacticalPlan | null>(null);
  const [lastAction, setLastAction] = useState<number>(0);
  
  // New plan form state
  const [planName, setPlanName] = useState('');
  const [targetPriority, setTargetPriority] = useState<TacticalPlan['targetPriority']>('shields');
  const [droneStrategy, setDroneStrategy] = useState<TacticalPlan['droneStrategy']>('balanced');
  const [retreatCondition, setRetreatCondition] = useState<TacticalPlan['retreatCondition']>('hull25');
  const [formationRole, setFormationRole] = useState<TacticalPlan['formationRole']>('support');
  const [useSpecialWeapons, setUseSpecialWeapons] = useState(false);
  const [notes, setNotes] = useState('');

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

  // Load saved plans on mount
  React.useEffect(() => {
    const loadedPlans = localStorage.getItem(`tactical_plans_${ship.id}`);
    if (loadedPlans) {
      try {
        setSavedPlans(JSON.parse(loadedPlans));
      } catch (error) {
        console.error('Failed to load tactical plans:', error);
      }
    }
  }, [ship.id]);

  const savePlan = useCallback(() => {
    if (!canPerformAction()) {
      console.warn('Rate limit exceeded');
      return;
    }

    const sanitizedName = InputValidator.sanitizeText(planName);
    const sanitizedNotes = InputValidator.sanitizeText(notes);

    if (!sanitizedName || sanitizedName.length < 3) {
      alert('Plan name must be at least 3 characters');
      return;
    }

    const newPlan: TacticalPlan = {
      id: `plan_${Date.now()}`,
      name: sanitizedName,
      targetPriority,
      droneStrategy,
      retreatCondition,
      formationRole: isInFormation ? formationRole : undefined,
      useSpecialWeapons,
      notes: sanitizedNotes,
      createdAt: new Date().toISOString()
    };

    const updatedPlans = [...savedPlans, newPlan];
    setSavedPlans(updatedPlans);
    localStorage.setItem(`tactical_plans_${ship.id}`, JSON.stringify(updatedPlans));
    
    // Reset form
    setIsCreating(false);
    setPlanName('');
    setNotes('');
    setTargetPriority('shields');
    setDroneStrategy('balanced');
    setRetreatCondition('hull25');
    setUseSpecialWeapons(false);
  }, [canPerformAction, planName, notes, targetPriority, droneStrategy, 
      retreatCondition, formationRole, useSpecialWeapons, isInFormation, 
      savedPlans, ship.id]);

  const deletePlan = useCallback((planId: string) => {
    if (!canPerformAction()) {
      console.warn('Rate limit exceeded');
      return;
    }

    const updatedPlans = savedPlans.filter(p => p.id !== planId);
    setSavedPlans(updatedPlans);
    localStorage.setItem(`tactical_plans_${ship.id}`, JSON.stringify(updatedPlans));
    
    if (selectedPlan?.id === planId) {
      setSelectedPlan(null);
    }
  }, [canPerformAction, savedPlans, selectedPlan, ship.id]);

  const selectPlan = useCallback((plan: TacticalPlan) => {
    if (!canPerformAction()) {
      console.warn('Rate limit exceeded');
      return;
    }

    setSelectedPlan(plan);
    
    // Update last used
    const updatedPlans = savedPlans.map(p => 
      p.id === plan.id 
        ? { ...p, lastUsed: new Date().toISOString() }
        : p
    );
    setSavedPlans(updatedPlans);
    localStorage.setItem(`tactical_plans_${ship.id}`, JSON.stringify(updatedPlans));
    
    if (onPlanSelect) {
      onPlanSelect(plan);
    }
  }, [canPerformAction, savedPlans, ship.id, onPlanSelect]);

  const simulatePlan = useCallback(async (plan: TacticalPlan) => {
    if (!canPerformAction()) {
      console.warn('Rate limit exceeded');
      return;
    }

    // In a real implementation, this would call an API to simulate combat outcomes
    console.log('Simulating plan:', plan);
    alert(`Simulation for "${plan.name}" would show:\n- Win probability\n- Expected damage taken\n- Resource consumption\n- Time to victory`);
  }, [canPerformAction]);

  // Calculate plan effectiveness based on ship capabilities
  const planEffectiveness = useMemo(() => {
    if (!selectedPlan) return null;

    const effectiveness = {
      offense: 0,
      defense: 0,
      efficiency: 0
    };

    // Calculate based on ship stats and plan strategy
    if (selectedPlan.targetPriority === 'weapons') {
      effectiveness.offense += 20;
    }
    if (selectedPlan.droneStrategy === 'aggressive') {
      effectiveness.offense += 15;
    } else if (selectedPlan.droneStrategy === 'defensive') {
      effectiveness.defense += 15;
    }
    if (selectedPlan.retreatCondition !== 'never') {
      effectiveness.defense += 10;
    }
    if (selectedPlan.useSpecialWeapons && (ship as any).weapons > 100) {
      effectiveness.offense += 25;
    }

    effectiveness.efficiency = (effectiveness.offense + effectiveness.defense) / 2;

    return effectiveness;
  }, [selectedPlan, ship]);

  return (
    <div className="tactical-planner">
      <div className="planner-header">
        <h3>Tactical Planning</h3>
        <span className="ship-info">{ship.name} - {ship.type}</span>
      </div>

      <div className="planner-content">
        <div className="saved-plans">
          <div className="section-header">
            <h4>Saved Plans</h4>
            <button 
              className="create-plan-btn"
              onClick={() => setIsCreating(true)}
              disabled={isCreating}
            >
              + New Plan
            </button>
          </div>

          {savedPlans.length === 0 ? (
            <div className="no-plans">
              <p>No tactical plans saved yet.</p>
              <p>Create your first plan to prepare for combat!</p>
            </div>
          ) : (
            <div className="plans-list">
              {savedPlans.map(plan => (
                <div 
                  key={plan.id} 
                  className={`plan-item ${selectedPlan?.id === plan.id ? 'selected' : ''}`}
                  onClick={() => selectPlan(plan)}
                >
                  <div className="plan-header">
                    <h5>{plan.name}</h5>
                    <button 
                      className="delete-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        deletePlan(plan.id);
                      }}
                    >
                      ×
                    </button>
                  </div>
                  <div className="plan-summary">
                    <span className="priority">Target: {plan.targetPriority}</span>
                    <span className="strategy">Drones: {plan.droneStrategy}</span>
                    {plan.formationRole && (
                      <span className="formation">Formation: {plan.formationRole}</span>
                    )}
                  </div>
                  {plan.lastUsed && (
                    <div className="last-used">
                      Last used: {new Date(plan.lastUsed).toLocaleDateString()}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {isCreating && (
          <div className="plan-creator">
            <h4>Create New Plan</h4>
            <form onSubmit={(e) => { e.preventDefault(); savePlan(); }}>
              <div className="form-group">
                <label>Plan Name</label>
                <input
                  type="text"
                  value={planName}
                  onChange={(e) => setPlanName(e.target.value)}
                  placeholder="e.g., Aggressive Assault"
                  maxLength={50}
                  required
                />
              </div>

              <div className="form-group">
                <label>Target Priority</label>
                <select 
                  value={targetPriority}
                  onChange={(e) => setTargetPriority(e.target.value as TacticalPlan['targetPriority'])}
                >
                  <option value="shields">Shields</option>
                  <option value="weapons">Weapons</option>
                  <option value="engines">Engines</option>
                  <option value="hull">Hull</option>
                </select>
              </div>

              <div className="form-group">
                <label>Drone Strategy</label>
                <select 
                  value={droneStrategy}
                  onChange={(e) => setDroneStrategy(e.target.value as TacticalPlan['droneStrategy'])}
                >
                  <option value="aggressive">Aggressive</option>
                  <option value="defensive">Defensive</option>
                  <option value="balanced">Balanced</option>
                </select>
              </div>

              <div className="form-group">
                <label>Retreat Condition</label>
                <select 
                  value={retreatCondition}
                  onChange={(e) => setRetreatCondition(e.target.value as TacticalPlan['retreatCondition'])}
                >
                  <option value="never">Never Retreat</option>
                  <option value="shields0">When Shields Depleted</option>
                  <option value="hull50">At 50% Hull</option>
                  <option value="hull25">At 25% Hull</option>
                </select>
              </div>

              {isInFormation && (
                <div className="form-group">
                  <label>Formation Role</label>
                  <select 
                    value={formationRole}
                    onChange={(e) => setFormationRole(e.target.value as TacticalPlan['formationRole'])}
                  >
                    <option value="leader">Leader</option>
                    <option value="support">Support</option>
                    <option value="flanker">Flanker</option>
                  </select>
                </div>
              )}

              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    checked={useSpecialWeapons}
                    onChange={(e) => setUseSpecialWeapons(e.target.checked)}
                  />
                  Use Special Weapons
                </label>
              </div>

              <div className="form-group">
                <label>Notes</label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Additional tactical notes..."
                  maxLength={500}
                  rows={3}
                />
              </div>

              <div className="form-actions">
                <button type="submit" className="save-btn">Save Plan</button>
                <button 
                  type="button" 
                  className="cancel-btn"
                  onClick={() => setIsCreating(false)}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {selectedPlan && !isCreating && (
          <div className="plan-details">
            <h4>{selectedPlan.name}</h4>
            
            <div className="plan-stats">
              <div className="stat-group">
                <label>Target Priority:</label>
                <span>{selectedPlan.targetPriority}</span>
              </div>
              <div className="stat-group">
                <label>Drone Strategy:</label>
                <span>{selectedPlan.droneStrategy}</span>
              </div>
              <div className="stat-group">
                <label>Retreat Condition:</label>
                <span>{selectedPlan.retreatCondition}</span>
              </div>
              {selectedPlan.formationRole && (
                <div className="stat-group">
                  <label>Formation Role:</label>
                  <span>{selectedPlan.formationRole}</span>
                </div>
              )}
              <div className="stat-group">
                <label>Special Weapons:</label>
                <span>{selectedPlan.useSpecialWeapons ? 'Enabled' : 'Disabled'}</span>
              </div>
            </div>

            {selectedPlan.notes && (
              <div className="plan-notes">
                <label>Notes:</label>
                <p>{selectedPlan.notes}</p>
              </div>
            )}

            {planEffectiveness && (
              <div className="effectiveness-analysis">
                <h5>Effectiveness Analysis</h5>
                <div className="effectiveness-bars">
                  <div className="bar-group">
                    <label>Offense</label>
                    <div className="bar">
                      <div 
                        className="bar-fill offense"
                        style={{ width: `${planEffectiveness.offense}%` }}
                      />
                    </div>
                  </div>
                  <div className="bar-group">
                    <label>Defense</label>
                    <div className="bar">
                      <div 
                        className="bar-fill defense"
                        style={{ width: `${planEffectiveness.defense}%` }}
                      />
                    </div>
                  </div>
                  <div className="bar-group">
                    <label>Overall</label>
                    <div className="bar">
                      <div 
                        className="bar-fill overall"
                        style={{ width: `${planEffectiveness.efficiency}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div className="plan-actions">
              <button 
                className="simulate-btn"
                onClick={() => simulatePlan(selectedPlan)}
              >
                Simulate Plan
              </button>
              <button 
                className="apply-btn primary"
                onClick={() => onPlanSelect && onPlanSelect(selectedPlan)}
              >
                Apply to Combat
              </button>
            </div>
          </div>
        )}

        {isInFormation && teamMembers.length > 0 && (
          <div className="formation-info">
            <h5>Formation Members</h5>
            <div className="team-members">
              {teamMembers.map(member => (
                <div key={member.id} className="member-item">
                  <span className="member-name">{member.name}</span>
                  <span className="member-ship">{member.ship}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TacticalPlanner;