import React, { useState, useEffect, useCallback } from 'react';
import { gameAPI } from '../../services/api';
import type { Planet, ResourceAllocations } from '../../types/planetary';
import './colonist-allocator.css';

interface ColonistAllocatorProps {
  planet: Planet;
  onUpdate?: (planet: Planet) => void;
  onClose?: () => void;
}

export const ColonistAllocator: React.FC<ColonistAllocatorProps> = ({ 
  planet, 
  onUpdate,
  onClose 
}) => {
  const [allocations, setAllocations] = useState<ResourceAllocations>(planet.allocations);
  const [tempAllocations, setTempAllocations] = useState<ResourceAllocations>(planet.allocations);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Calculate production preview based on allocations
  const calculatePreviewProduction = useCallback((allocs: ResourceAllocations) => {
    const baseRate = 100;
    const specialized = planet.specialization || 'balanced';
    
    // Apply specialization bonuses
    const bonuses = {
      agricultural: { fuel: 0.8, organics: 1.5, equipment: 0.7 },
      industrial: { fuel: 1.2, organics: 0.6, equipment: 1.4 },
      military: { fuel: 1.0, organics: 0.8, equipment: 1.2 },
      research: { fuel: 0.9, organics: 0.9, equipment: 0.9 },
      balanced: { fuel: 1.0, organics: 1.0, equipment: 1.0 }
    };

    const bonus = bonuses[specialized as keyof typeof bonuses] || bonuses.balanced;

    return {
      fuel: Math.floor(baseRate * (allocs.fuel / 100) * 1.5 * bonus.fuel),
      organics: Math.floor(baseRate * (allocs.organics / 100) * 2 * bonus.organics),
      equipment: Math.floor(baseRate * (allocs.equipment / 100) * bonus.equipment),
      colonists: planet.productionRates.colonists // Colonist growth is separate
    };
  }, [planet.specialization, planet.productionRates.colonists]);

  const previewProduction = calculatePreviewProduction(tempAllocations);

  const handleSliderChange = (resource: keyof Omit<ResourceAllocations, 'unused'>, value: number) => {
    const newAllocations = { ...tempAllocations };
    newAllocations[resource] = value;
    
    // Calculate unused
    const total = newAllocations.fuel + newAllocations.organics + newAllocations.equipment;
    newAllocations.unused = Math.max(0, 100 - total);
    
    // If over 100%, reduce other allocations proportionally
    if (total > 100) {
      const excess = total - 100;
      const otherResources = (['fuel', 'organics', 'equipment'] as const).filter(r => r !== resource);
      const otherTotal = otherResources.reduce((sum, r) => sum + newAllocations[r], 0);
      
      if (otherTotal > 0) {
        otherResources.forEach(r => {
          const proportion = newAllocations[r] / otherTotal;
          newAllocations[r] = Math.max(0, Math.floor(newAllocations[r] - excess * proportion));
        });
      }
      
      newAllocations.unused = 0;
    }
    
    setTempAllocations(newAllocations);
  };

  const handlePresetAllocation = (preset: 'balanced' | 'fuel' | 'organics' | 'equipment' | 'growth') => {
    const presets = {
      balanced: { fuel: 33, organics: 33, equipment: 34, unused: 0 },
      fuel: { fuel: 70, organics: 15, equipment: 15, unused: 0 },
      organics: { fuel: 15, organics: 70, equipment: 15, unused: 0 },
      equipment: { fuel: 15, organics: 15, equipment: 70, unused: 0 },
      growth: { fuel: 20, organics: 50, equipment: 20, unused: 10 } // Unused helps growth
    };
    
    setTempAllocations(presets[preset]);
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccessMessage(null);
      
      const response = await gameAPI.planetary.allocateColonists(planet.id, {
        fuel: tempAllocations.fuel,
        organics: tempAllocations.organics,
        equipment: tempAllocations.equipment
      });
      
      if (response.success) {
        setAllocations(response.allocations);
        setSuccessMessage('Resource allocations updated successfully!');
        
        // Update parent component
        if (onUpdate) {
          const updatedPlanet = {
            ...planet,
            allocations: response.allocations,
            productionRates: response.productionRates
          };
          onUpdate(updatedPlanet);
        }
        
        // Clear success message after 3 seconds
        setTimeout(() => setSuccessMessage(null), 3000);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update allocations');
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    setTempAllocations(allocations);
    setError(null);
    setSuccessMessage(null);
  };

  const hasChanges = JSON.stringify(tempAllocations) !== JSON.stringify(allocations);

  const getResourceColor = (resource: string) => {
    const colors = {
      fuel: '#ff6b6b',
      organics: '#51cf66',
      equipment: '#339af0',
      unused: '#868e96'
    };
    return colors[resource as keyof typeof colors] || '#868e96';
  };

  const getProductionDiff = (resource: keyof typeof previewProduction) => {
    const current = planet.productionRates[resource];
    const preview = previewProduction[resource];
    const diff = preview - current;
    
    if (diff === 0) return null;
    
    return (
      <span className={`production-diff ${diff > 0 ? 'positive' : 'negative'}`}>
        {diff > 0 ? '+' : ''}{diff}
      </span>
    );
  };

  return (
    <div className="colonist-allocator">
      <div className="allocator-header">
        <h3>Resource Allocation - {planet.name}</h3>
        <button className="close-button" onClick={onClose}>✕</button>
      </div>

      <div className="allocator-content">
        <div className="current-stats">
          <div className="stat-item">
            <span className="stat-label">Colonists:</span>
            <span className="stat-value">
              {planet.colonists.toLocaleString()} / {planet.maxColonists.toLocaleString()}
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Specialization:</span>
            <span className="stat-value">{planet.specialization || 'None'}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Efficiency:</span>
            <span className="stat-value">{100 - tempAllocations.unused}%</span>
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

        <div className="preset-buttons">
          <button 
            className="preset-button"
            onClick={() => handlePresetAllocation('balanced')}
            title="Equal distribution across all resources"
          >
            ⚖️ Balanced
          </button>
          <button 
            className="preset-button fuel"
            onClick={() => handlePresetAllocation('fuel')}
            title="Focus on fuel production"
          >
            ⛽ Fuel Focus
          </button>
          <button 
            className="preset-button organics"
            onClick={() => handlePresetAllocation('organics')}
            title="Focus on organics production"
          >
            🌿 Organics Focus
          </button>
          <button 
            className="preset-button equipment"
            onClick={() => handlePresetAllocation('equipment')}
            title="Focus on equipment production"
          >
            ⚙️ Equipment Focus
          </button>
          <button 
            className="preset-button growth"
            onClick={() => handlePresetAllocation('growth')}
            title="Optimize for population growth"
          >
            👥 Growth Focus
          </button>
        </div>

        <div className="allocation-controls">
          <div className="allocation-slider">
            <div className="slider-header">
              <span className="resource-label">
                <span className="resource-icon">⛽</span> Fuel Production
              </span>
              <span className="allocation-value">{tempAllocations.fuel}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={tempAllocations.fuel}
              onChange={(e) => handleSliderChange('fuel', parseInt(e.target.value))}
              className="slider fuel-slider"
              style={{
                background: `linear-gradient(to right, ${getResourceColor('fuel')} 0%, ${getResourceColor('fuel')} ${tempAllocations.fuel}%, var(--surface-secondary) ${tempAllocations.fuel}%, var(--surface-secondary) 100%)`
              }}
            />
            <div className="production-preview">
              <span className="preview-label">Production:</span>
              <span className="preview-value">
                {previewProduction.fuel}/day
                {getProductionDiff('fuel')}
              </span>
            </div>
          </div>

          <div className="allocation-slider">
            <div className="slider-header">
              <span className="resource-label">
                <span className="resource-icon">🌿</span> Organics Production
              </span>
              <span className="allocation-value">{tempAllocations.organics}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={tempAllocations.organics}
              onChange={(e) => handleSliderChange('organics', parseInt(e.target.value))}
              className="slider organics-slider"
              style={{
                background: `linear-gradient(to right, ${getResourceColor('organics')} 0%, ${getResourceColor('organics')} ${tempAllocations.organics}%, var(--surface-secondary) ${tempAllocations.organics}%, var(--surface-secondary) 100%)`
              }}
            />
            <div className="production-preview">
              <span className="preview-label">Production:</span>
              <span className="preview-value">
                {previewProduction.organics}/day
                {getProductionDiff('organics')}
              </span>
            </div>
          </div>

          <div className="allocation-slider">
            <div className="slider-header">
              <span className="resource-label">
                <span className="resource-icon">⚙️</span> Equipment Production
              </span>
              <span className="allocation-value">{tempAllocations.equipment}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={tempAllocations.equipment}
              onChange={(e) => handleSliderChange('equipment', parseInt(e.target.value))}
              className="slider equipment-slider"
              style={{
                background: `linear-gradient(to right, ${getResourceColor('equipment')} 0%, ${getResourceColor('equipment')} ${tempAllocations.equipment}%, var(--surface-secondary) ${tempAllocations.equipment}%, var(--surface-secondary) 100%)`
              }}
            />
            <div className="production-preview">
              <span className="preview-label">Production:</span>
              <span className="preview-value">
                {previewProduction.equipment}/day
                {getProductionDiff('equipment')}
              </span>
            </div>
          </div>

          <div className="allocation-slider unused">
            <div className="slider-header">
              <span className="resource-label">
                <span className="resource-icon">💤</span> Unallocated
              </span>
              <span className="allocation-value">{tempAllocations.unused}%</span>
            </div>
            <div className="unused-bar">
              <div 
                className="unused-fill"
                style={{ width: `${tempAllocations.unused}%` }}
              />
            </div>
            <div className="unused-note">
              Unallocated colonists contribute to population growth and maintenance
            </div>
          </div>
        </div>

        <div className="allocation-summary">
          <h4>Production Summary</h4>
          <div className="summary-grid">
            <div className="summary-item">
              <span className="summary-label">Total Efficiency:</span>
              <span className="summary-value">{100 - tempAllocations.unused}%</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Daily Output:</span>
              <span className="summary-value">
                {previewProduction.fuel + previewProduction.organics + previewProduction.equipment} units
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Population Growth:</span>
              <span className="summary-value">
                +{previewProduction.colonists}/day
                {tempAllocations.unused > 20 && <span className="growth-bonus"> (+{Math.floor(tempAllocations.unused / 10)}% bonus)</span>}
              </span>
            </div>
          </div>
        </div>

        <div className="action-buttons">
          <button
            className="button secondary"
            onClick={handleReset}
            disabled={!hasChanges || saving}
          >
            Reset
          </button>
          <button
            className="button primary"
            onClick={handleSave}
            disabled={!hasChanges || saving}
          >
            {saving ? 'Saving...' : 'Save Allocations'}
          </button>
        </div>
      </div>
    </div>
  );
};