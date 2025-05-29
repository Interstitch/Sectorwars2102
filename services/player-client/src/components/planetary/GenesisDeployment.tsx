import React, { useState, useEffect } from 'react';
import { gameAPI } from '../../services/api';
import type { PlanetType, GenesisDeployment as GenesisDeploymentType } from '../../types/planetary';
import './genesis-deployment.css';

interface GenesisDeploymentProps {
  onSuccess?: (planetId: string) => void;
  onClose?: () => void;
}

interface PlanetTypeInfo {
  type: PlanetType;
  name: string;
  icon: string;
  description: string;
  characteristics: string[];
  maxColonists: number;
  productionBonuses: {
    fuel: number;
    organics: number;
    equipment: number;
  };
}

const PLANET_TYPES: PlanetTypeInfo[] = [
  {
    type: 'terran',
    name: 'Terran',
    icon: '🌍',
    description: 'Earth-like planets with balanced resources and high habitability',
    characteristics: [
      'Balanced resource production',
      'High maximum population',
      'Ideal for general colonies',
      'Good defensive positions'
    ],
    maxColonists: 100000,
    productionBonuses: { fuel: 1.0, organics: 1.0, equipment: 1.0 }
  },
  {
    type: 'oceanic',
    name: 'Oceanic',
    icon: '🌊',
    description: 'Water-covered worlds rich in organic resources',
    characteristics: [
      'Excellent organics production',
      'Limited equipment output',
      'Moderate population capacity',
      'Natural shield advantages'
    ],
    maxColonists: 75000,
    productionBonuses: { fuel: 0.8, organics: 1.5, equipment: 0.7 }
  },
  {
    type: 'mountainous',
    name: 'Mountainous',
    icon: '⛰️',
    description: 'Rocky planets abundant in minerals and fuel',
    characteristics: [
      'High fuel production',
      'Excellent equipment output',
      'Lower population limits',
      'Natural fortress terrain'
    ],
    maxColonists: 50000,
    productionBonuses: { fuel: 1.4, organics: 0.6, equipment: 1.3 }
  },
  {
    type: 'desert',
    name: 'Desert',
    icon: '🏜️',
    description: 'Arid worlds with concentrated mineral deposits',
    characteristics: [
      'Superior fuel extraction',
      'Limited organics production',
      'Harsh living conditions',
      'Hidden resource caches'
    ],
    maxColonists: 40000,
    productionBonuses: { fuel: 1.6, organics: 0.4, equipment: 1.1 }
  },
  {
    type: 'frozen',
    name: 'Frozen',
    icon: '❄️',
    description: 'Ice-covered planets with unique research opportunities',
    characteristics: [
      'Research bonus potential',
      'Reduced production rates',
      'Challenging environment',
      'Defensive ice barriers'
    ],
    maxColonists: 35000,
    productionBonuses: { fuel: 0.7, organics: 0.8, equipment: 0.9 }
  }
];

export const GenesisDeployment: React.FC<GenesisDeploymentProps> = ({ 
  onSuccess,
  onClose 
}) => {
  const [selectedType, setSelectedType] = useState<PlanetType>('terran');
  const [planetName, setPlanetName] = useState('');
  const [selectedSectorId, setSelectedSectorId] = useState('');
  const [deploying, setDeploying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [genesisDevices, setGenesisDevices] = useState(3); // Mock value
  const [availableSectors, setAvailableSectors] = useState<Array<{id: string, name: string}>>([
    { id: 'sector-1', name: 'Sol System' },
    { id: 'sector-42', name: 'Asteroid Belt' },
    { id: 'sector-99', name: 'Outer Rim' },
    { id: 'sector-7', name: 'Nebula Core' },
    { id: 'sector-13', name: 'Trade Route Alpha' }
  ]);

  const selectedPlanetInfo = PLANET_TYPES.find(p => p.type === selectedType)!;

  const validatePlanetName = (name: string): boolean => {
    // Basic validation
    if (name.length < 3) return false;
    if (name.length > 30) return false;
    if (!/^[a-zA-Z0-9\s\-']+$/.test(name)) return false;
    return true;
  };

  const handleDeploy = async () => {
    // Validation
    if (!planetName.trim()) {
      setError('Please enter a planet name');
      return;
    }

    if (!validatePlanetName(planetName)) {
      setError('Planet name must be 3-30 characters and contain only letters, numbers, spaces, hyphens, and apostrophes');
      return;
    }

    if (!selectedSectorId) {
      setError('Please select a target sector');
      return;
    }

    if (genesisDevices <= 0) {
      setError('No Genesis Devices available');
      return;
    }

    try {
      setDeploying(true);
      setError(null);
      setSuccessMessage(null);

      const deployment: GenesisDeploymentType = {
        sectorId: selectedSectorId,
        planetName: planetName.trim(),
        planetType: selectedType
      };

      const response = await gameAPI.planetary.deployGenesis(
        deployment.sectorId,
        deployment.planetName,
        deployment.planetType
      );

      if (response.success) {
        setGenesisDevices(response.genesisDevicesRemaining);
        setSuccessMessage(`Genesis Device deployed! ${planetName} will be ready in ${Math.floor(response.deploymentTime / 60)} minutes.`);
        
        // Clear form
        setPlanetName('');
        setSelectedSectorId('');
        
        // Notify parent
        if (onSuccess) {
          onSuccess(response.planetId);
        }

        // Close after success message
        setTimeout(() => {
          if (onClose) onClose();
        }, 3000);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to deploy Genesis Device');
    } finally {
      setDeploying(false);
    }
  };

  const handlePlanetNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setPlanetName(value);
    
    // Clear error when user starts typing
    if (error && error.includes('planet name')) {
      setError(null);
    }
  };

  return (
    <div className="genesis-deployment">
      <div className="deployment-header">
        <h3>Deploy Genesis Device</h3>
        <button className="close-button" onClick={onClose}>✕</button>
      </div>

      <div className="deployment-content">
        <div className="device-status">
          <div className="status-item">
            <span className="status-label">Genesis Devices Available:</span>
            <span className={`status-value ${genesisDevices === 0 ? 'empty' : ''}`}>
              {genesisDevices}
            </span>
          </div>
          <div className="status-item">
            <span className="status-label">Deployment Time:</span>
            <span className="status-value">5 minutes</span>
          </div>
        </div>

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

        {genesisDevices === 0 ? (
          <div className="no-devices-warning">
            <span className="warning-icon">⚠️</span>
            <p>You have no Genesis Devices available. Purchase more from specialized ports or complete faction missions to earn them.</p>
          </div>
        ) : (
          <>
            <div className="deployment-form">
              <div className="form-section">
                <label htmlFor="planet-name">Planet Name</label>
                <input
                  id="planet-name"
                  type="text"
                  value={planetName}
                  onChange={handlePlanetNameChange}
                  placeholder="Enter planet name..."
                  maxLength={30}
                  className={error && error.includes('planet name') ? 'error' : ''}
                />
                <span className="input-hint">3-30 characters, letters, numbers, spaces, hyphens, and apostrophes only</span>
              </div>

              <div className="form-section">
                <label htmlFor="sector-select">Target Sector</label>
                <select
                  id="sector-select"
                  value={selectedSectorId}
                  onChange={(e) => setSelectedSectorId(e.target.value)}
                  className={error && error.includes('sector') ? 'error' : ''}
                >
                  <option value="">Select a sector...</option>
                  {availableSectors.map(sector => (
                    <option key={sector.id} value={sector.id}>
                      {sector.name}
                    </option>
                  ))}
                </select>
                <span className="input-hint">Choose a sector with available planet slots</span>
              </div>
            </div>

            <div className="planet-types">
              <h4>Select Planet Type</h4>
              <div className="type-grid">
                {PLANET_TYPES.map(planetType => (
                  <div
                    key={planetType.type}
                    className={`planet-type-card ${selectedType === planetType.type ? 'selected' : ''}`}
                    onClick={() => setSelectedType(planetType.type)}
                  >
                    <div className="type-header">
                      <span className="type-icon">{planetType.icon}</span>
                      <h5>{planetType.name}</h5>
                    </div>
                    <p className="type-description">{planetType.description}</p>
                    
                    <div className="type-stats">
                      <div className="stat">
                        <span className="stat-label">Max Population:</span>
                        <span className="stat-value">{planetType.maxColonists.toLocaleString()}</span>
                      </div>
                      <div className="production-bonuses">
                        <span className="bonus-label">Production:</span>
                        <div className="bonus-values">
                          <span className="bonus fuel">⛽ {(planetType.productionBonuses.fuel * 100).toFixed(0)}%</span>
                          <span className="bonus organics">🌿 {(planetType.productionBonuses.organics * 100).toFixed(0)}%</span>
                          <span className="bonus equipment">⚙️ {(planetType.productionBonuses.equipment * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    </div>

                    <ul className="characteristics">
                      {planetType.characteristics.map((char, index) => (
                        <li key={index}>{char}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>

            <div className="deployment-summary">
              <h4>Deployment Summary</h4>
              <div className="summary-grid">
                <div className="summary-item">
                  <span className="summary-label">Planet Name:</span>
                  <span className="summary-value">{planetName || 'Not set'}</span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Planet Type:</span>
                  <span className="summary-value">
                    {selectedPlanetInfo.icon} {selectedPlanetInfo.name}
                  </span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Target Sector:</span>
                  <span className="summary-value">
                    {selectedSectorId ? availableSectors.find(s => s.id === selectedSectorId)?.name : 'Not selected'}
                  </span>
                </div>
                <div className="summary-item">
                  <span className="summary-label">Max Colonists:</span>
                  <span className="summary-value">{selectedPlanetInfo.maxColonists.toLocaleString()}</span>
                </div>
              </div>
            </div>

            <div className="action-buttons">
              <button
                className="button secondary"
                onClick={onClose}
                disabled={deploying}
              >
                Cancel
              </button>
              <button
                className="button primary"
                onClick={handleDeploy}
                disabled={deploying || !planetName || !selectedSectorId}
              >
                {deploying ? 'Deploying...' : 'Deploy Genesis Device'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};