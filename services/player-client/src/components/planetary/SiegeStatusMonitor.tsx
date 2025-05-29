import React, { useState, useEffect } from 'react';
import { gameAPI } from '../../services/api';
import type { Planet, SiegePhase } from '../../types/planetary';
import './siege-status-monitor.css';

interface SiegeStatusMonitorProps {
  planet: Planet;
  onUpdate?: (planet: Planet) => void;
  onClose?: () => void;
}

interface SiegePhaseInfo {
  phase: SiegePhase;
  name: string;
  icon: string;
  description: string;
  duration: number; // minutes
  effects: string[];
  defenseOptions: string[];
}

const SIEGE_PHASES: SiegePhaseInfo[] = [
  {
    phase: 'orbital',
    name: 'Orbital Blockade',
    icon: '🛸',
    description: 'Enemy ships establish orbital superiority and begin blockade',
    duration: 60,
    effects: [
      'Trade routes blocked',
      'No reinforcements possible',
      'Communication jamming active',
      'Shield generators under stress'
    ],
    defenseOptions: [
      'Deploy fighter squadrons',
      'Activate orbital defense platforms',
      'Request allied assistance',
      'Attempt blockade runner'
    ]
  },
  {
    phase: 'bombardment',
    name: 'Orbital Bombardment',
    icon: '💥',
    description: 'Heavy weapons rain down from orbit, targeting infrastructure',
    duration: 120,
    effects: [
      'Building damage accumulating',
      'Civilian casualties mounting',
      'Defense systems degrading',
      'Production capacity reduced'
    ],
    defenseOptions: [
      'Maximize shield output',
      'Evacuate civilians to bunkers',
      'Counter-battery fire',
      'Sabotage operations'
    ]
  },
  {
    phase: 'invasion',
    name: 'Ground Invasion',
    icon: '⚔️',
    description: 'Enemy troops land and engage in surface combat',
    duration: 180,
    effects: [
      'Direct combat in colonies',
      'Heavy casualties on both sides',
      'Infrastructure capture attempts',
      'Final stand scenarios'
    ],
    defenseOptions: [
      'Urban warfare tactics',
      'Guerrilla resistance',
      'Last stand at command center',
      'Scorched earth protocol'
    ]
  }
];

export const SiegeStatusMonitor: React.FC<SiegeStatusMonitorProps> = ({ 
  planet, 
  onUpdate,
  onClose 
}) => {
  const [selectedAction, setSelectedAction] = useState<string | null>(null);
  const [executing, setExecuting] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState<number>(0);

  useEffect(() => {
    if (!planet.siegeDetails) return;

    // Calculate time remaining in current phase
    const phaseInfo = SIEGE_PHASES.find(p => p.phase === planet.siegeDetails!.phase);
    if (!phaseInfo) return;

    const startTime = new Date(planet.siegeDetails.startTime).getTime();
    const phaseEnd = startTime + (phaseInfo.duration * 60 * 1000);
    const now = Date.now();
    const remaining = Math.max(0, phaseEnd - now);
    
    setTimeRemaining(Math.floor(remaining / 1000)); // Convert to seconds

    // Update timer every second
    const timer = setInterval(() => {
      setTimeRemaining(prev => Math.max(0, prev - 1));
    }, 1000);

    return () => clearInterval(timer);
  }, [planet.siegeDetails]);

  if (!planet.underSiege || !planet.siegeDetails) {
    return (
      <div className="siege-status-monitor">
        <div className="monitor-header">
          <h3>Siege Status - {planet.name}</h3>
          <button className="close-button" onClick={onClose}>✕</button>
        </div>
        <div className="monitor-content">
          <div className="no-siege">
            <span className="peace-icon">🕊️</span>
            <h4>Planet at Peace</h4>
            <p>This planet is not currently under siege.</p>
          </div>
        </div>
      </div>
    );
  }

  const currentPhase = SIEGE_PHASES.find(p => p.phase === planet.siegeDetails!.phase);
  const phaseIndex = SIEGE_PHASES.findIndex(p => p.phase === planet.siegeDetails!.phase);
  const defenseEffectiveness = planet.siegeDetails.defenseEffectiveness || 50;

  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    }
    return `${secs}s`;
  };

  const getEffectivenessClass = (effectiveness: number): string => {
    if (effectiveness >= 80) return 'excellent';
    if (effectiveness >= 60) return 'good';
    if (effectiveness >= 40) return 'fair';
    if (effectiveness >= 20) return 'poor';
    return 'critical';
  };

  const handleDefenseAction = async (action: string) => {
    setSelectedAction(action);
    setExecuting(true);

    // Simulate defense action execution
    setTimeout(() => {
      setExecuting(false);
      // In real implementation, this would call an API
    }, 2000);
  };

  return (
    <div className="siege-status-monitor">
      <div className="monitor-header">
        <h3>🚨 SIEGE IN PROGRESS - {planet.name}</h3>
        <button className="close-button" onClick={onClose}>✕</button>
      </div>

      <div className="monitor-content">
        <div className="siege-alert">
          <div className="alert-content">
            <span className="alert-icon">⚠️</span>
            <div className="alert-text">
              <h4>Planet Under Attack!</h4>
              <p>Enemy: {planet.siegeDetails.attackerName}</p>
            </div>
          </div>
        </div>

        <div className="siege-overview">
          <div className="overview-stats">
            <div className="stat-item">
              <span className="stat-label">Current Phase:</span>
              <span className="stat-value phase">{currentPhase?.name}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Phase Timer:</span>
              <span className="stat-value timer">{formatTime(timeRemaining)}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Defense Effectiveness:</span>
              <span className={`stat-value effectiveness ${getEffectivenessClass(defenseEffectiveness)}`}>
                {defenseEffectiveness}%
              </span>
            </div>
          </div>

          <div className="phase-progress">
            <div className="progress-track">
              {SIEGE_PHASES.map((phase, index) => (
                <div
                  key={phase.phase}
                  className={`phase-marker ${index <= phaseIndex ? 'active' : ''} ${index === phaseIndex ? 'current' : ''}`}
                >
                  <span className="phase-icon">{phase.icon}</span>
                  <span className="phase-name">{phase.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {currentPhase && (
          <div className="phase-details">
            <div className="phase-header">
              <span className="phase-icon-large">{currentPhase.icon}</span>
              <div className="phase-info">
                <h4>{currentPhase.name}</h4>
                <p>{currentPhase.description}</p>
              </div>
            </div>

            <div className="phase-effects">
              <h5>Current Effects:</h5>
              <ul>
                {currentPhase.effects.map((effect, index) => (
                  <li key={index} className="effect-item">
                    <span className="effect-icon">⚡</span>
                    {effect}
                  </li>
                ))}
              </ul>
            </div>

            <div className="defense-options">
              <h5>Defense Options:</h5>
              <div className="options-grid">
                {currentPhase.defenseOptions.map((option, index) => (
                  <button
                    key={index}
                    className={`defense-option ${selectedAction === option ? 'selected' : ''}`}
                    onClick={() => handleDefenseAction(option)}
                    disabled={executing}
                  >
                    <span className="option-icon">🛡️</span>
                    <span className="option-text">{option}</span>
                  </button>
                ))}
              </div>
              {executing && selectedAction && (
                <div className="action-feedback">
                  <span className="executing-icon">⚙️</span>
                  Executing: {selectedAction}...
                </div>
              )}
            </div>
          </div>
        )}

        {planet.siegeDetails.casualties && (
          <div className="casualties-report">
            <h5>Casualty Report:</h5>
            <div className="casualties-grid">
              <div className="casualty-item">
                <span className="casualty-icon">👥</span>
                <span className="casualty-label">Colonists Lost:</span>
                <span className="casualty-value">{planet.siegeDetails.casualties.colonists.toLocaleString()}</span>
              </div>
              <div className="casualty-item">
                <span className="casualty-icon">✈️</span>
                <span className="casualty-label">Fighters Lost:</span>
                <span className="casualty-value">{planet.siegeDetails.casualties.fighters}</span>
              </div>
            </div>
          </div>
        )}

        <div className="defense-status">
          <h5>Defense Systems Status:</h5>
          <div className="defense-grid">
            <div className="defense-item">
              <span className="defense-label">🔫 Turrets:</span>
              <div className="status-bar">
                <div 
                  className="status-fill turrets"
                  style={{ width: `${Math.max(20, defenseEffectiveness)}%` }}
                />
                <span className="status-text">{planet.defenses.turrets} active</span>
              </div>
            </div>
            <div className="defense-item">
              <span className="defense-label">🛡️ Shields:</span>
              <div className="status-bar">
                <div 
                  className="status-fill shields"
                  style={{ width: `${Math.max(15, defenseEffectiveness * 0.8)}%` }}
                />
                <span className="status-text">{planet.defenses.shields} generators</span>
              </div>
            </div>
            <div className="defense-item">
              <span className="defense-label">✈️ Fighters:</span>
              <div className="status-bar">
                <div 
                  className="status-fill fighters"
                  style={{ width: `${Math.max(10, defenseEffectiveness * 0.6)}%` }}
                />
                <span className="status-text">{planet.defenses.fighters} squadrons</span>
              </div>
            </div>
          </div>
        </div>

        <div className="siege-recommendations">
          <h5>Tactical Recommendations:</h5>
          <div className="recommendations-list">
            {defenseEffectiveness < 40 && (
              <div className="recommendation critical">
                <span className="rec-icon">🚨</span>
                <p>Critical: Defense effectiveness below 40%. Consider evacuation protocols.</p>
              </div>
            )}
            {phaseIndex === 0 && (
              <div className="recommendation">
                <span className="rec-icon">💡</span>
                <p>Reinforce shields while bombardment hasn't started yet.</p>
              </div>
            )}
            {phaseIndex === 1 && (
              <div className="recommendation">
                <span className="rec-icon">💡</span>
                <p>Move civilians to underground bunkers immediately.</p>
              </div>
            )}
            {phaseIndex === 2 && (
              <div className="recommendation">
                <span className="rec-icon">💡</span>
                <p>Prepare for urban combat. Arm civilian militia if necessary.</p>
              </div>
            )}
          </div>
        </div>

        <div className="action-buttons">
          <button className="button emergency">
            🆘 Request Emergency Aid
          </button>
          <button className="button surrender">
            🏳️ Negotiate Surrender
          </button>
        </div>
      </div>
    </div>
  );
};