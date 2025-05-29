import React, { useState, useMemo, useCallback } from 'react';
import { Ship } from '../../types/game';
import { InputValidator } from '../../utils/security/inputValidation';
import './ship-details.css';

interface ShipModification {
  type: 'weapon' | 'shield' | 'engine' | 'cargo' | 'special';
  name: string;
  level: number;
  bonus: string;
  installDate: string;
}

interface ShipStats {
  baseValue: number;
  modifiedValue: number;
  bonusPercentage: number;
}

interface ShipDetailsProps {
  ship: Ship;
  onRename?: (newName: string) => void;
  onCustomize?: (customization: any) => void;
  onViewHistory?: () => void;
  isCurrentShip?: boolean;
}

const ShipDetails: React.FC<ShipDetailsProps> = ({
  ship,
  onRename,
  onCustomize,
  onViewHistory,
  isCurrentShip = false
}) => {
  const [isRenaming, setIsRenaming] = useState(false);
  const [newShipName, setNewShipName] = useState(ship.name);
  const [activeTab, setActiveTab] = useState<'stats' | 'mods' | 'history' | 'appearance'>('stats');
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

  // Mock modifications data
  const modifications: ShipModification[] = [
    {
      type: 'weapon',
      name: 'Enhanced Targeting System',
      level: 3,
      bonus: '+15% Accuracy',
      installDate: '2025-05-20'
    },
    {
      type: 'shield',
      name: 'Reinforced Shield Generator',
      level: 2,
      bonus: '+20% Shield Capacity',
      installDate: '2025-05-15'
    },
    {
      type: 'engine',
      name: 'Quantum Drive Optimizer',
      level: 1,
      bonus: '+10% Speed',
      installDate: '2025-05-10'
    }
  ];

  // Calculate ship statistics with modifications
  const shipStats = useMemo(() => {
    const stats = {
      weapons: { baseValue: ship.weapons, modifiedValue: ship.weapons, bonusPercentage: 0 },
      shields: { baseValue: ship.shields, modifiedValue: ship.shields, bonusPercentage: 0 },
      speed: { baseValue: ship.speed, modifiedValue: ship.speed, bonusPercentage: 0 },
      cargo: { baseValue: ship.cargoCapacity, modifiedValue: ship.cargoCapacity, bonusPercentage: 0 }
    };

    // Apply modifications
    modifications.forEach(mod => {
      switch (mod.type) {
        case 'weapon':
          stats.weapons.bonusPercentage += 15;
          stats.weapons.modifiedValue = Math.floor(stats.weapons.baseValue * 1.15);
          break;
        case 'shield':
          stats.shields.bonusPercentage += 20;
          stats.shields.modifiedValue = Math.floor(stats.shields.baseValue * 1.20);
          break;
        case 'engine':
          stats.speed.bonusPercentage += 10;
          stats.speed.modifiedValue = Math.floor(stats.speed.baseValue * 1.10);
          break;
      }
    });

    return stats;
  }, [ship, modifications]);

  // Calculate ship condition
  const shipCondition = useMemo(() => {
    const avgHealth = (ship.health + ship.shields) / 2;
    if (avgHealth >= 90) return { status: 'Excellent', color: '#44ff44' };
    if (avgHealth >= 70) return { status: 'Good', color: '#88ff88' };
    if (avgHealth >= 50) return { status: 'Fair', color: '#ffaa44' };
    if (avgHealth >= 30) return { status: 'Poor', color: '#ff8844' };
    return { status: 'Critical', color: '#ff4444' };
  }, [ship.health, ship.shields]);

  // Calculate ship value
  const shipValue = useMemo(() => {
    let baseValue = 50000; // Base value based on ship type
    
    // Add value for modifications
    const modValue = modifications.length * 10000;
    
    // Add value for ship condition
    const conditionMultiplier = ship.health / 100;
    
    return Math.floor((baseValue + modValue) * conditionMultiplier);
  }, [ship, modifications]);

  const handleRename = useCallback(() => {
    if (!canPerformAction() || !onRename) return;

    const sanitizedName = InputValidator.sanitizeText(newShipName);
    if (!sanitizedName || sanitizedName.length < 3) {
      alert('Ship name must be at least 3 characters');
      return;
    }

    onRename(sanitizedName);
    setIsRenaming(false);
  }, [canPerformAction, newShipName, onRename]);

  const renderStatBar = (stat: ShipStats, label: string, color: string) => (
    <div className="stat-item">
      <div className="stat-header">
        <span className="stat-label">{label}</span>
        <span className="stat-value">
          {stat.modifiedValue}
          {stat.bonusPercentage > 0 && (
            <span className="stat-bonus">+{stat.bonusPercentage}%</span>
          )}
        </span>
      </div>
      <div className="stat-bar">
        <div 
          className="stat-bar-fill base"
          style={{ 
            width: `${(stat.baseValue / 200) * 100}%`,
            backgroundColor: color
          }}
        />
        {stat.bonusPercentage > 0 && (
          <div 
            className="stat-bar-fill bonus"
            style={{ 
              width: `${((stat.modifiedValue - stat.baseValue) / 200) * 100}%`,
              backgroundColor: color,
              left: `${(stat.baseValue / 200) * 100}%`,
              opacity: 0.6
            }}
          />
        )}
      </div>
    </div>
  );

  return (
    <div className="ship-details">
      <div className="ship-header">
        <div className="ship-identity">
          {isRenaming ? (
            <div className="rename-container">
              <input
                type="text"
                value={newShipName}
                onChange={(e) => setNewShipName(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleRename()}
                maxLength={50}
                autoFocus
              />
              <button onClick={handleRename} className="confirm-btn">✓</button>
              <button onClick={() => setIsRenaming(false)} className="cancel-btn">✗</button>
            </div>
          ) : (
            <div className="ship-name-container">
              <h2>{ship.name}</h2>
              {onRename && (
                <button 
                  className="rename-btn"
                  onClick={() => setIsRenaming(true)}
                  title="Rename ship"
                >
                  ✏️
                </button>
              )}
            </div>
          )}
          <div className="ship-class">{ship.type}</div>
          {isCurrentShip && <div className="current-ship-badge">ACTIVE</div>}
        </div>
        
        <div className="ship-condition">
          <span className="condition-label">Condition:</span>
          <span 
            className="condition-status"
            style={{ color: shipCondition.color }}
          >
            {shipCondition.status}
          </span>
        </div>
      </div>

      <div className="detail-tabs">
        <button
          className={`tab-btn ${activeTab === 'stats' ? 'active' : ''}`}
          onClick={() => setActiveTab('stats')}
        >
          Statistics
        </button>
        <button
          className={`tab-btn ${activeTab === 'mods' ? 'active' : ''}`}
          onClick={() => setActiveTab('mods')}
        >
          Modifications
        </button>
        <button
          className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          History
        </button>
        <button
          className={`tab-btn ${activeTab === 'appearance' ? 'active' : ''}`}
          onClick={() => setActiveTab('appearance')}
        >
          Appearance
        </button>
      </div>

      <div className="detail-content">
        {activeTab === 'stats' && (
          <div className="stats-panel">
            <div className="vital-stats">
              <div className="vital-stat">
                <label>Health</label>
                <div className="vital-bar">
                  <div 
                    className="vital-fill health"
                    style={{ width: `${ship.health}%` }}
                  />
                  <span className="vital-text">{ship.health}%</span>
                </div>
              </div>
              <div className="vital-stat">
                <label>Shields</label>
                <div className="vital-bar">
                  <div 
                    className="vital-fill shields"
                    style={{ width: `${ship.shields}%` }}
                  />
                  <span className="vital-text">{ship.shields}%</span>
                </div>
              </div>
            </div>

            <div className="performance-stats">
              {renderStatBar(shipStats.weapons, 'Weapons', '#ff4444')}
              {renderStatBar(shipStats.shields, 'Shield Power', '#4444ff')}
              {renderStatBar(shipStats.speed, 'Speed', '#44ff44')}
              {renderStatBar(shipStats.cargo, 'Cargo Capacity', '#ffaa44')}
            </div>

            <div className="additional-stats">
              <div className="stat-group">
                <label>Drone Capacity:</label>
                <span>{ship.drones} / {ship.drones}</span>
              </div>
              <div className="stat-group">
                <label>Cargo Used:</label>
                <span>{ship.cargoUsed} / {ship.cargoCapacity}</span>
              </div>
              <div className="stat-group">
                <label>Maintenance Cost:</label>
                <span>{Math.floor(shipValue * 0.02).toLocaleString()} credits/day</span>
              </div>
              <div className="stat-group">
                <label>Estimated Value:</label>
                <span>{shipValue.toLocaleString()} credits</span>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'mods' && (
          <div className="modifications-panel">
            <h3>Installed Modifications</h3>
            {modifications.length === 0 ? (
              <div className="no-mods">
                <p>No modifications installed</p>
                <p>Visit a shipyard to upgrade your vessel!</p>
              </div>
            ) : (
              <div className="mods-list">
                {modifications.map((mod, index) => (
                  <div key={index} className={`mod-item ${mod.type}`}>
                    <div className="mod-icon">
                      {mod.type === 'weapon' && '⚔️'}
                      {mod.type === 'shield' && '🛡️'}
                      {mod.type === 'engine' && '🚀'}
                      {mod.type === 'cargo' && '📦'}
                      {mod.type === 'special' && '✨'}
                    </div>
                    <div className="mod-info">
                      <h4>{mod.name}</h4>
                      <div className="mod-details">
                        <span className="mod-level">Level {mod.level}</span>
                        <span className="mod-bonus">{mod.bonus}</span>
                      </div>
                      <div className="mod-date">Installed: {mod.installDate}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            <div className="mod-slots">
              <h4>Available Slots</h4>
              <div className="slots-grid">
                <div className="slot-item filled">Weapon Slot 1</div>
                <div className="slot-item filled">Shield Slot 1</div>
                <div className="slot-item filled">Engine Slot 1</div>
                <div className="slot-item empty">Special Slot 1</div>
                <div className="slot-item empty">Special Slot 2</div>
                <div className="slot-item locked">Locked Slot</div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div className="history-panel">
            <h3>Ship History</h3>
            <div className="history-stats">
              <div className="history-stat">
                <label>Battles Fought:</label>
                <span>42</span>
              </div>
              <div className="history-stat">
                <label>Victories:</label>
                <span>38</span>
              </div>
              <div className="history-stat">
                <label>Total Distance:</label>
                <span>15,420 LY</span>
              </div>
              <div className="history-stat">
                <label>Cargo Delivered:</label>
                <span>8,542 tons</span>
              </div>
            </div>
            
            <div className="history-events">
              <h4>Recent Events</h4>
              <div className="event-list">
                <div className="event-item">
                  <span className="event-date">2025-05-28</span>
                  <span className="event-desc">Survived ambush in Sector 7</span>
                </div>
                <div className="event-item">
                  <span className="event-date">2025-05-25</span>
                  <span className="event-desc">Upgraded shields at Station Prime</span>
                </div>
                <div className="event-item">
                  <span className="event-date">2025-05-22</span>
                  <span className="event-desc">Discovered ancient artifact</span>
                </div>
                <div className="event-item">
                  <span className="event-date">2025-05-20</span>
                  <span className="event-desc">Completed trade mission</span>
                </div>
              </div>
            </div>
            
            {onViewHistory && (
              <button className="view-full-history" onClick={onViewHistory}>
                View Full History
              </button>
            )}
          </div>
        )}

        {activeTab === 'appearance' && (
          <div className="appearance-panel">
            <h3>Ship Customization</h3>
            
            <div className="color-selection">
              <h4>Hull Color</h4>
              <div className="color-grid">
                <div className="color-option" style={{ backgroundColor: '#ff4444' }} />
                <div className="color-option" style={{ backgroundColor: '#4444ff' }} />
                <div className="color-option" style={{ backgroundColor: '#44ff44' }} />
                <div className="color-option" style={{ backgroundColor: '#ffaa44' }} />
                <div className="color-option" style={{ backgroundColor: '#ff44ff' }} />
                <div className="color-option" style={{ backgroundColor: '#44ffff' }} />
                <div className="color-option selected" style={{ backgroundColor: '#888888' }} />
                <div className="color-option" style={{ backgroundColor: '#ffffff' }} />
              </div>
            </div>
            
            <div className="decal-selection">
              <h4>Decals & Emblems</h4>
              <div className="decal-grid">
                <div className="decal-option">🎯</div>
                <div className="decal-option">⚡</div>
                <div className="decal-option">🔥</div>
                <div className="decal-option">❄️</div>
                <div className="decal-option">☠️</div>
                <div className="decal-option">🌟</div>
              </div>
            </div>
            
            <div className="ship-preview">
              <h4>Preview</h4>
              <div className="preview-container">
                <div className="ship-model">
                  {/* Placeholder for 3D ship model */}
                  <div className="placeholder-ship">
                    🚀
                    <p>3D Preview Coming Soon</p>
                  </div>
                </div>
              </div>
            </div>
            
            {onCustomize && (
              <button 
                className="apply-customization"
                onClick={() => onCustomize({ color: '#888888', decal: '🎯' })}
              >
                Apply Customization
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ShipDetails;