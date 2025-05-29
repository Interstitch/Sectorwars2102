/**
 * ShipSelector Component
 * 
 * Allows players to view and switch between their owned ships.
 * Displays ship stats, location, and condition for easy comparison.
 */

import React, { useState, useEffect } from 'react';
import { useGame } from '../../contexts/GameContext';
import { Ship } from '../../types/game';
import { InputValidator, SecurityAudit } from '../../utils/security/inputValidation';
import './ship-selector.css';

interface ShipSelectorProps {
  onShipSelected?: (ship: Ship) => void;
  onClose?: () => void;
}

// Mock ship data for testing (remove when real data is available)
const mockShips: Ship[] = [
  {
    id: 'ship-1',
    name: 'Stellar Wanderer',
    type: 'LIGHT_FREIGHTER',
    sector_id: 42,
    cargo: {
      ore: 50,
      organics: 30,
      equipment: 20,
      luxury_goods: 10,
      medical_supplies: 5,
      technology: 0
    },
    cargo_capacity: 500,
    current_speed: 5,
    base_speed: 5,
    combat: {
      attack_rating: 5,
      defense_rating: 6,
      attack_drones: 10,
      defense_drones: 5,
      max_drones: 50,
      shields: { current: 80, max: 100, recharge_rate: 2 },
      evasion: 15,
      scanner_range: 3
    },
    maintenance: {
      current_rating: 85,
      last_service_date: new Date(Date.now() - 86400000 * 5),
      degradation_rate: 1.5,
      failure_status: 'NONE',
      critical_systems: [],
      performance_impacts: {
        speed_modifier: 0,
        combat_modifier: 0,
        fuel_modifier: 0,
        failure_chance: 0
      },
      next_warning_threshold: 75
    },
    is_flagship: true,
    purchase_value: 50000,
    current_value: 45000
  },
  {
    id: 'ship-2',
    name: 'Cargo Runner',
    type: 'CARGO_HAULER',
    sector_id: 12,
    cargo: {
      ore: 200,
      organics: 150,
      equipment: 100,
      luxury_goods: 50,
      medical_supplies: 0,
      technology: 0
    },
    cargo_capacity: 1500,
    current_speed: 3,
    base_speed: 3,
    combat: {
      attack_rating: 2,
      defense_rating: 8,
      attack_drones: 0,
      defense_drones: 20,
      max_drones: 80,
      shields: { current: 120, max: 150, recharge_rate: 1 },
      evasion: 5,
      scanner_range: 2
    },
    maintenance: {
      current_rating: 45,
      last_service_date: new Date(Date.now() - 86400000 * 20),
      degradation_rate: 2.0,
      failure_status: 'MINOR',
      critical_systems: [
        { name: 'Navigation', status: 60, affects: 'speed' }
      ],
      performance_impacts: {
        speed_modifier: -15,
        combat_modifier: -10,
        fuel_modifier: 20,
        failure_chance: 5
      },
      next_warning_threshold: 25
    },
    is_flagship: false,
    purchase_value: 120000,
    current_value: 95000
  }
];

export const ShipSelector: React.FC<ShipSelectorProps> = ({
  onShipSelected,
  onClose
}) => {
  const { ships: gameShips, currentShip, setCurrentShip, playerState } = useGame();
  
  // Use mock ships if no real ships available (for testing)
  const ships = gameShips.length > 0 ? gameShips : mockShips;
  
  const [selectedShipId, setSelectedShipId] = useState<string | null>(currentShip?.id || null);
  const [isChangingShip, setIsChangingShip] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'active' | 'docked'>('all');
  const [sortBy, setSortBy] = useState<'name' | 'type' | 'location' | 'condition'>('name');
  
  // Filter ships based on selected filter
  const filteredShips = ships.filter(ship => {
    if (filter === 'all') return true;
    if (filter === 'active') return ship.id === currentShip?.id;
    if (filter === 'docked') return ship.id !== currentShip?.id;
    return true;
  });
  
  // Sort ships
  const sortedShips = [...filteredShips].sort((a, b) => {
    switch (sortBy) {
      case 'name':
        return a.name.localeCompare(b.name);
      case 'type':
        return a.type.localeCompare(b.type);
      case 'location':
        return a.sector_id - b.sector_id;
      case 'condition':
        return (b.maintenance?.current_rating || 100) - (a.maintenance?.current_rating || 100);
      default:
        return 0;
    }
  });
  
  // Handle ship selection
  const handleShipSelect = (ship: Ship) => {
    setSelectedShipId(ship.id);
    setError(null);
  };
  
  // Change active ship
  const handleChangeShip = async () => {
    if (!selectedShipId || selectedShipId === currentShip?.id || !playerState) return;
    
    // Rate limiting
    if (!InputValidator.checkRateLimit(`ship_change_${playerState.id}`, 5, 300000)) {
      setError('Too many ship changes. Please wait before switching again.');
      SecurityAudit.log({
        type: 'rate_limit_exceeded',
        details: { action: 'ship_change' },
        userId: playerState.id
      });
      return;
    }
    
    setIsChangingShip(true);
    setError(null);
    
    try {
      await setCurrentShip(selectedShipId);
      
      const selectedShip = ships.find(s => s.id === selectedShipId);
      if (selectedShip && onShipSelected) {
        onShipSelected(selectedShip);
      }
      
      // Clear rate limit on successful change
      InputValidator.clearRateLimit(`ship_change_${playerState.id}`);
      
      if (onClose) {
        setTimeout(onClose, 500); // Brief delay to show success
      }
    } catch (err) {
      setError('Failed to change ship. Please try again.');
      console.error('Ship change failed:', err);
    } finally {
      setIsChangingShip(false);
    }
  };
  
  // Calculate cargo usage percentage
  const getCargoUsage = (ship: Ship): number => {
    const used = Object.values(ship.cargo || {}).reduce((sum, val) => sum + (typeof val === 'number' ? val : 0), 0);
    return ship.cargo_capacity > 0 ? (used / ship.cargo_capacity * 100) : 0;
  };
  
  // Get ship condition color
  const getConditionColor = (rating: number): string => {
    if (rating >= 80) return 'excellent';
    if (rating >= 60) return 'good';
    if (rating >= 40) return 'fair';
    if (rating >= 20) return 'poor';
    return 'critical';
  };
  
  // Get ship type display name
  const getShipTypeDisplay = (type: string): string => {
    return type.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase());
  };
  
  return (
    <div className="ship-selector">
      <div className="selector-header">
        <h2>SHIP HANGAR</h2>
        {onClose && (
          <button className="close-btn" onClick={onClose}>×</button>
        )}
      </div>
      
      {error && (
        <div className="selector-error">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}
      
      <div className="selector-controls">
        <div className="filter-group">
          <button
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All Ships ({ships.length})
          </button>
          <button
            className={`filter-btn ${filter === 'active' ? 'active' : ''}`}
            onClick={() => setFilter('active')}
          >
            Active
          </button>
          <button
            className={`filter-btn ${filter === 'docked' ? 'active' : ''}`}
            onClick={() => setFilter('docked')}
          >
            Docked
          </button>
        </div>
        
        <div className="sort-group">
          <label>Sort by:</label>
          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value as any)}
            className="sort-select"
          >
            <option value="name">Name</option>
            <option value="type">Type</option>
            <option value="location">Location</option>
            <option value="condition">Condition</option>
          </select>
        </div>
      </div>
      
      <div className="ships-grid">
        {sortedShips.map(ship => (
          <div 
            key={ship.id}
            className={`ship-card ${selectedShipId === ship.id ? 'selected' : ''} ${ship.is_flagship ? 'flagship' : ''}`}
            onClick={() => handleShipSelect(ship)}
          >
            <div className="ship-header">
              <h3>{ship.name}</h3>
              {ship.is_flagship && <span className="flagship-badge">FLAGSHIP</span>}
              {ship.id === currentShip?.id && <span className="active-badge">ACTIVE</span>}
            </div>
            
            <div className="ship-type">{getShipTypeDisplay(ship.type)}</div>
            
            <div className="ship-stats">
              <div className="stat-group">
                <div className="stat">
                  <span className="label">Location:</span>
                  <span className="value">Sector {ship.sector_id}</span>
                </div>
                <div className="stat">
                  <span className="label">Speed:</span>
                  <span className="value">{ship.current_speed}/{ship.base_speed}</span>
                </div>
              </div>
              
              <div className="stat-group">
                <div className="stat">
                  <span className="label">Combat:</span>
                  <span className="value">
                    ⚔️ {ship.combat?.attack_rating || 0} / 🛡️ {ship.combat?.defense_rating || 0}
                  </span>
                </div>
                <div className="stat">
                  <span className="label">Drones:</span>
                  <span className="value">
                    {(ship.combat?.attack_drones || 0) + (ship.combat?.defense_drones || 0)} / {ship.combat?.max_drones || 0}
                  </span>
                </div>
              </div>
              
              <div className="condition-section">
                <div className="condition-label">Condition:</div>
                <div className="condition-bar">
                  <div 
                    className={`condition-fill ${getConditionColor(ship.maintenance?.current_rating || 100)}`}
                    style={{ width: `${ship.maintenance?.current_rating || 100}%` }}
                  />
                  <span className="condition-text">
                    {ship.maintenance?.current_rating || 100}%
                  </span>
                </div>
                {ship.maintenance?.failure_status && ship.maintenance.failure_status !== 'NONE' && (
                  <div className="failure-warning">
                    ⚠️ {ship.maintenance.failure_status} failure detected
                  </div>
                )}
              </div>
              
              <div className="cargo-section">
                <div className="cargo-label">Cargo Hold:</div>
                <div className="cargo-bar">
                  <div 
                    className="cargo-fill"
                    style={{ width: `${getCargoUsage(ship)}%` }}
                  />
                  <span className="cargo-text">
                    {Math.round(getCargoUsage(ship))}% full
                  </span>
                </div>
              </div>
              
              <div className="ship-value">
                <span className="label">Value:</span>
                <span className="value">{ship.current_value.toLocaleString()} credits</span>
              </div>
            </div>
            
            {ship.combat?.shields && (
              <div className="shields-section">
                <div className="shields-label">Shields:</div>
                <div className="shields-bar">
                  <div 
                    className="shields-fill"
                    style={{ width: `${(ship.combat.shields.current / ship.combat.shields.max) * 100}%` }}
                  />
                  <span className="shields-text">
                    {ship.combat.shields.current}/{ship.combat.shields.max}
                  </span>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
      
      <div className="selector-actions">
        <button
          className="cockpit-btn primary"
          onClick={handleChangeShip}
          disabled={!selectedShipId || selectedShipId === currentShip?.id || isChangingShip}
        >
          {isChangingShip ? 'Changing Ship...' : 'Make Active Ship'}
        </button>
        {onClose && (
          <button
            className="cockpit-btn secondary"
            onClick={onClose}
          >
            Cancel
          </button>
        )}
      </div>
    </div>
  );
};