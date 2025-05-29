/**
 * DroneManager Component
 * 
 * Manages drone deployment, recall, and sector defense operations.
 * Provides interface for both combat and defensive drone management.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { useGame } from '../../contexts/GameContext';
import { gameAPI } from '../../services/api';
import { InputValidator, SecurityAudit } from '../../utils/security/inputValidation';
import './drone-manager.css';

// Define types locally since we're removing mocks
interface DroneDeployment {
  deploymentId: string;
  sectorId: string;
  sectorName: string;
  droneCount: number;
  deployedAt: string;
  status: 'active' | 'combat' | 'returning';
}

interface DroneManagerProps {
  combatMode?: boolean;
  onDroneAction?: (action: string, count: number) => void;
}

export const DroneManager: React.FC<DroneManagerProps> = ({
  combatMode = false,
  onDroneAction
}) => {
  const { playerState, currentSector, refreshPlayerState } = useGame();
  
  // Drone state
  const [deployments, setDeployments] = useState<DroneDeployment[]>([]);
  const [selectedSector, setSelectedSector] = useState<string>('');
  const [droneCount, setDroneCount] = useState<string>('');
  const [isDeploying, setIsDeploying] = useState(false);
  const [isRecalling, setIsRecalling] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // UI state
  const [showDeploymentForm, setShowDeploymentForm] = useState(false);
  
  // Available drones calculation
  const totalDrones = playerState?.attack_drones || 0;
  const deployedDrones = deployments.reduce((sum, d) => sum + d.droneCount, 0);
  const availableDrones = totalDrones - deployedDrones;
  
  // Load deployments on mount
  useEffect(() => {
    loadDeployments();
  }, []);
  
  // Load current drone deployments
  const loadDeployments = async () => {
    try {
      const response = await gameAPI.combat.getDeployedDrones();
      setDeployments(response.deployments || []);
    } catch (err) {
      console.error('Failed to load drone deployments:', err);
    }
  };
  
  // Deploy drones to sector
  const deployDrones = useCallback(async () => {
    if (!playerState) return;
    
    // Validate inputs
    const countValidation = InputValidator.validateNumeric(droneCount, 1, availableDrones);
    if (!countValidation.valid || !countValidation.value) {
      setError(`Invalid drone count. You can deploy 1-${availableDrones} drones.`);
      SecurityAudit.log({
        type: 'validation_failure',
        details: { input: droneCount, availableDrones },
        userId: playerState.id
      });
      return;
    }
    
    const sectorId = selectedSector || currentSector?.id?.toString() || '';
    if (!sectorId) {
      setError('No sector selected for deployment');
      return;
    }
    
    // Rate limiting
    if (!InputValidator.checkRateLimit(`drone_deploy_${playerState.id}`, 10, 60000)) {
      setError('Too many deployment attempts. Please wait.');
      SecurityAudit.log({
        type: 'rate_limit_exceeded',
        details: { action: 'drone_deployment' },
        userId: playerState.id
      });
      return;
    }
    
    setIsDeploying(true);
    setError(null);
    
    try {
      const response = await gameAPI.combat.deployDrones(sectorId, countValidation.value);
      
      if (response.deploymentId) {
        // Success - reload deployments
        await loadDeployments();
        setDroneCount('');
        setShowDeploymentForm(false);
        
        // Notify parent if in combat mode
        if (combatMode && onDroneAction) {
          onDroneAction('deploy', countValidation.value);
        }
        
        // Refresh player state to update drone counts
        refreshPlayerState();
      }
    } catch (err) {
      setError('Failed to deploy drones. Please try again.');
      console.error('Drone deployment failed:', err);
    } finally {
      setIsDeploying(false);
    }
  }, [
    playerState, 
    droneCount, 
    selectedSector, 
    currentSector, 
    availableDrones,
    combatMode,
    onDroneAction,
    refreshPlayerState
  ]);
  
  // Recall drones from deployment
  const recallDrones = useCallback(async (deploymentId: string) => {
    if (!playerState) return;
    
    setIsRecalling(deploymentId);
    setError(null);
    
    try {
      const response = await gameAPI.combat.recallDrones(deploymentId);
      
      if (response.dronesRecalled > 0) {
        // Success - reload deployments
        await loadDeployments();
        
        // Notify parent if in combat mode
        if (combatMode && onDroneAction) {
          onDroneAction('recall', response.dronesRecalled);
        }
        
        // Refresh player state
        refreshPlayerState();
      }
    } catch (err) {
      setError('Failed to recall drones. Please try again.');
      console.error('Drone recall failed:', err);
    } finally {
      setIsRecalling(null);
    }
  }, [playerState, combatMode, onDroneAction, refreshPlayerState]);
  
  // Handle drone count input
  const handleDroneCountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    
    // Only allow numeric input
    if (value === '' || /^\d+$/.test(value)) {
      setDroneCount(value);
      setError(null);
    }
  };
  
  if (combatMode) {
    // Simplified combat mode interface
    return (
      <div className="drone-manager combat-mode">
        <div className="drone-summary">
          <span className="drone-icon">🤖</span>
          <span className="drone-count">
            {availableDrones} / {totalDrones} drones available
          </span>
        </div>
        
        {availableDrones > 0 && (
          <div className="quick-deploy">
            <input
              type="number"
              placeholder="Count"
              value={droneCount}
              onChange={handleDroneCountChange}
              min="1"
              max={availableDrones}
              className="drone-input"
            />
            <button
              className="cockpit-btn primary deploy-btn"
              onClick={deployDrones}
              disabled={!droneCount || isDeploying}
            >
              Deploy
            </button>
          </div>
        )}
        
        {error && <div className="drone-error">{error}</div>}
      </div>
    );
  }
  
  // Full drone management interface
  return (
    <div className="drone-manager">
      <div className="drone-header">
        <h3>DRONE COMMAND</h3>
        <div className="drone-stats">
          <div className="stat">
            <span className="label">Total:</span>
            <span className="value">{totalDrones}</span>
          </div>
          <div className="stat">
            <span className="label">Deployed:</span>
            <span className="value">{deployedDrones}</span>
          </div>
          <div className="stat available">
            <span className="label">Available:</span>
            <span className="value">{availableDrones}</span>
          </div>
        </div>
      </div>
      
      {error && (
        <div className="drone-error">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}
      
      <div className="drone-controls">
        {!showDeploymentForm ? (
          <button
            className="cockpit-btn primary"
            onClick={() => setShowDeploymentForm(true)}
            disabled={availableDrones === 0}
          >
            Deploy Drones
          </button>
        ) : (
          <div className="deployment-form">
            <h4>Deploy Drones</h4>
            <div className="form-group">
              <label>Sector:</label>
              <input
                type="text"
                placeholder={`Current: ${currentSector?.id || 'Unknown'}`}
                value={selectedSector}
                onChange={(e) => setSelectedSector(e.target.value)}
                className="sector-input"
              />
            </div>
            <div className="form-group">
              <label>Drone Count:</label>
              <input
                type="number"
                placeholder={`Max: ${availableDrones}`}
                value={droneCount}
                onChange={handleDroneCountChange}
                min="1"
                max={availableDrones}
                className="drone-input"
              />
            </div>
            <div className="form-actions">
              <button
                className="cockpit-btn primary"
                onClick={deployDrones}
                disabled={!droneCount || isDeploying}
              >
                {isDeploying ? 'Deploying...' : 'Confirm Deploy'}
              </button>
              <button
                className="cockpit-btn secondary"
                onClick={() => {
                  setShowDeploymentForm(false);
                  setDroneCount('');
                  setSelectedSector('');
                  setError(null);
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
      
      <div className="deployments-list">
        <h4>Active Deployments</h4>
        {deployments.length === 0 ? (
          <div className="no-deployments">
            <p>No drones currently deployed</p>
            <p className="hint">Deploy drones to defend sectors or prepare for combat</p>
          </div>
        ) : (
          <div className="deployment-cards">
            {deployments.map((deployment) => (
              <div key={deployment.deploymentId} className="deployment-card">
                <div className="deployment-info">
                  <div className="sector-name">
                    Sector {deployment.sectorId}
                  </div>
                  <div className="drone-count">
                    <span className="drone-icon">🤖</span>
                    {deployment.droneCount} drones
                  </div>
                  <div className="deployment-time">
                    Deployed: {new Date(deployment.deployedAt).toLocaleString()}
                  </div>
                </div>
                <div className="deployment-actions">
                  <button
                    className="cockpit-btn secondary recall-btn"
                    onClick={() => recallDrones(deployment.deploymentId)}
                    disabled={isRecalling === deployment.deploymentId}
                  >
                    {isRecalling === deployment.deploymentId ? 'Recalling...' : 'Recall'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      <div className="drone-tips">
        <h4>Drone Tactics</h4>
        <ul>
          <li>Deploy drones in strategic sectors to defend against attacks</li>
          <li>Each drone provides defensive bonuses in combat</li>
          <li>Drones can be recalled at any time to redeploy elsewhere</li>
          <li>Destroyed drones in combat are permanently lost</li>
        </ul>
      </div>
    </div>
  );
};