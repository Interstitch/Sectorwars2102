import React, { useState, useEffect } from 'react';
import { gameAPI } from '../../services/api';
import type { Planet, Building, BuildingType } from '../../types/planetary';
import './building-manager.css';

interface BuildingManagerProps {
  planet: Planet;
  onUpdate?: (planet: Planet) => void;
  onClose?: () => void;
}

interface BuildingInfo {
  type: BuildingType;
  name: string;
  icon: string;
  description: string;
  baseProduction: {
    fuel?: number;
    organics?: number;
    equipment?: number;
    defense?: number;
    research?: number;
  };
  maxLevel: number;
  upgradeCost: (level: number) => {
    credits: number;
    resources: {
      fuel: number;
      organics: number;
      equipment: number;
    };
    time: number; // minutes
  };
}

const BUILDING_INFO: Record<BuildingType, BuildingInfo> = {
  factory: {
    type: 'factory',
    name: 'Factory',
    icon: '🏭',
    description: 'Produces equipment and machinery for your colony',
    baseProduction: { equipment: 50 },
    maxLevel: 5,
    upgradeCost: (level) => ({
      credits: 1000 * Math.pow(2, level),
      resources: {
        fuel: 200 * level,
        organics: 100 * level,
        equipment: 300 * level
      },
      time: 5 * (level + 1)
    })
  },
  farm: {
    type: 'farm',
    name: 'Agricultural Dome',
    icon: '🌾',
    description: 'Grows food and organic materials for colonists',
    baseProduction: { organics: 75 },
    maxLevel: 5,
    upgradeCost: (level) => ({
      credits: 800 * Math.pow(2, level),
      resources: {
        fuel: 100 * level,
        organics: 200 * level,
        equipment: 200 * level
      },
      time: 4 * (level + 1)
    })
  },
  mine: {
    type: 'mine',
    name: 'Mining Complex',
    icon: '⛏️',
    description: 'Extracts fuel and raw materials from the planet',
    baseProduction: { fuel: 60 },
    maxLevel: 5,
    upgradeCost: (level) => ({
      credits: 1200 * Math.pow(2, level),
      resources: {
        fuel: 150 * level,
        organics: 50 * level,
        equipment: 400 * level
      },
      time: 6 * (level + 1)
    })
  },
  defense: {
    type: 'defense',
    name: 'Defense Network',
    icon: '🛡️',
    description: 'Protects your colony from attacks and sieges',
    baseProduction: { defense: 100 },
    maxLevel: 5,
    upgradeCost: (level) => ({
      credits: 1500 * Math.pow(2, level),
      resources: {
        fuel: 300 * level,
        organics: 100 * level,
        equipment: 500 * level
      },
      time: 8 * (level + 1)
    })
  },
  research: {
    type: 'research',
    name: 'Research Lab',
    icon: '🔬',
    description: 'Advances technology and improves production efficiency',
    baseProduction: { research: 25 },
    maxLevel: 5,
    upgradeCost: (level) => ({
      credits: 2000 * Math.pow(2, level),
      resources: {
        fuel: 200 * level,
        organics: 200 * level,
        equipment: 600 * level
      },
      time: 10 * (level + 1)
    })
  }
};

export const BuildingManager: React.FC<BuildingManagerProps> = ({ 
  planet, 
  onUpdate,
  onClose 
}) => {
  const [selectedBuilding, setSelectedBuilding] = useState<Building | null>(null);
  const [upgrading, setUpgrading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Calculate total production bonuses from buildings
  const calculateProductionBonus = (buildingType: BuildingType, level: number) => {
    const info = BUILDING_INFO[buildingType];
    const bonus: any = {};
    
    Object.entries(info.baseProduction).forEach(([resource, base]) => {
      bonus[resource] = base * level * 0.5; // 50% bonus per level
    });
    
    return bonus;
  };

  // Calculate if player can afford upgrade
  const canAffordUpgrade = (building: Building): { canAfford: boolean; missing: string[] } => {
    const info = BUILDING_INFO[building.type];
    const cost = info.upgradeCost(building.level);
    const missing: string[] = [];

    // Check credits (mock - in real game would check player credits)
    const playerCredits = 50000; // Mock value
    if (playerCredits < cost.credits) {
      missing.push(`${(cost.credits - playerCredits).toLocaleString()} credits`);
    }

    // Check resources (mock - in real game would check player resources)
    const playerResources = {
      fuel: 5000,
      organics: 5000,
      equipment: 5000
    };

    if (playerResources.fuel < cost.resources.fuel) {
      missing.push(`${cost.resources.fuel - playerResources.fuel} fuel`);
    }
    if (playerResources.organics < cost.resources.organics) {
      missing.push(`${cost.resources.organics - playerResources.organics} organics`);
    }
    if (playerResources.equipment < cost.resources.equipment) {
      missing.push(`${cost.resources.equipment - playerResources.equipment} equipment`);
    }

    return {
      canAfford: missing.length === 0,
      missing
    };
  };

  const handleUpgrade = async (building: Building) => {
    if (building.level >= 5) {
      setError('Building is already at maximum level');
      return;
    }

    const affordCheck = canAffordUpgrade(building);
    if (!affordCheck.canAfford) {
      setError(`Insufficient resources: ${affordCheck.missing.join(', ')}`);
      return;
    }

    try {
      setUpgrading(building.type);
      setError(null);
      setSuccessMessage(null);

      const response = await gameAPI.planetary.upgradeBuilding(
        planet.id,
        building.type,
        building.level + 1
      );

      if (response.success) {
        setSuccessMessage(`${BUILDING_INFO[building.type].name} upgrade started!`);
        
        // Update the planet data
        if (onUpdate) {
          const updatedPlanet = { ...planet };
          const buildingIndex = updatedPlanet.buildings.findIndex(b => b.type === building.type);
          if (buildingIndex !== -1) {
            updatedPlanet.buildings[buildingIndex] = {
              ...updatedPlanet.buildings[buildingIndex],
              upgrading: true,
              completionTime: response.completionTime
            };
          }
          onUpdate(updatedPlanet);
        }

        // Clear success message after 3 seconds
        setTimeout(() => setSuccessMessage(null), 3000);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upgrade building');
    } finally {
      setUpgrading(null);
    }
  };

  const formatTime = (minutes: number) => {
    if (minutes < 60) return `${minutes} minutes`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours} hours`;
  };

  const formatCompletionTime = (isoString: string) => {
    const completion = new Date(isoString);
    const now = new Date();
    const diff = completion.getTime() - now.getTime();
    
    if (diff <= 0) return 'Complete';
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    
    if (hours > 0) {
      return `${hours}h ${mins}m remaining`;
    }
    return `${mins}m remaining`;
  };

  return (
    <div className="building-manager">
      <div className="manager-header">
        <h3>Building Management - {planet.name}</h3>
        <button className="close-button" onClick={onClose}>✕</button>
      </div>

      <div className="manager-content">
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}

        {successMessage && (
          <div className="success-message">
            <span className="success-icon">✅</span>
            {successMessage}
          </div>
        )}

        <div className="buildings-grid">
          {planet.buildings.map(building => {
            const info = BUILDING_INFO[building.type];
            const isMaxLevel = building.level >= info.maxLevel;
            const isUpgrading = building.upgrading;
            const canUpgrade = !isMaxLevel && !isUpgrading;
            const affordCheck = canAffordUpgrade(building);

            return (
              <div 
                key={building.type} 
                className={`building-card ${selectedBuilding?.type === building.type ? 'selected' : ''} ${isUpgrading ? 'upgrading' : ''}`}
                onClick={() => setSelectedBuilding(building)}
              >
                <div className="building-header">
                  <span className="building-icon">{info.icon}</span>
                  <div className="building-title">
                    <h4>{info.name}</h4>
                    <span className="building-level">Level {building.level}</span>
                  </div>
                </div>

                <p className="building-description">{info.description}</p>

                <div className="building-production">
                  <h5>Production Bonus:</h5>
                  <div className="production-values">
                    {Object.entries(calculateProductionBonus(building.type, building.level)).map(([resource, value]) => (
                      <span key={resource} className="production-item">
                        {resource === 'fuel' && '⛽'}
                        {resource === 'organics' && '🌿'}
                        {resource === 'equipment' && '⚙️'}
                        {resource === 'defense' && '🛡️'}
                        {resource === 'research' && '🔬'}
                        +{String(value)} {resource}
                      </span>
                    ))}
                  </div>
                </div>

                {isUpgrading && building.completionTime && (
                  <div className="upgrade-status">
                    <div className="upgrade-progress">
                      <div className="progress-bar">
                        <div className="progress-fill" style={{ width: '30%' }} />
                      </div>
                      <span className="upgrade-time">
                        {formatCompletionTime(building.completionTime)}
                      </span>
                    </div>
                  </div>
                )}

                {canUpgrade && (
                  <div className="upgrade-section">
                    <div className="upgrade-cost">
                      <h5>Upgrade to Level {building.level + 1}:</h5>
                      <div className="cost-items">
                        <span className="cost-item">
                          💰 {info.upgradeCost(building.level).credits.toLocaleString()} credits
                        </span>
                        <span className="cost-item">
                          ⛽ {info.upgradeCost(building.level).resources.fuel} fuel
                        </span>
                        <span className="cost-item">
                          🌿 {info.upgradeCost(building.level).resources.organics} organics
                        </span>
                        <span className="cost-item">
                          ⚙️ {info.upgradeCost(building.level).resources.equipment} equipment
                        </span>
                        <span className="cost-item time">
                          ⏱️ {formatTime(info.upgradeCost(building.level).time)}
                        </span>
                      </div>
                    </div>

                    <button
                      className={`upgrade-button ${!affordCheck.canAfford ? 'disabled' : ''}`}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleUpgrade(building);
                      }}
                      disabled={!affordCheck.canAfford || upgrading === building.type}
                    >
                      {upgrading === building.type ? 'Upgrading...' : 'Upgrade'}
                    </button>

                    {!affordCheck.canAfford && (
                      <div className="insufficient-resources">
                        Missing: {affordCheck.missing.join(', ')}
                      </div>
                    )}
                  </div>
                )}

                {isMaxLevel && (
                  <div className="max-level-badge">
                    <span className="badge-icon">⭐</span>
                    Maximum Level
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <div className="building-tips">
          <h4>Building Tips</h4>
          <ul>
            <li>
              <span className="tip-icon">💡</span>
              Higher level buildings provide exponentially better production bonuses
            </li>
            <li>
              <span className="tip-icon">🎯</span>
              Research labs improve efficiency of all other buildings on the planet
            </li>
            <li>
              <span className="tip-icon">🛡️</span>
              Defense networks are crucial for protecting against sieges
            </li>
            <li>
              <span className="tip-icon">⚖️</span>
              Balance your building upgrades based on your colony's specialization
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};