import React, { useState, useMemo, useCallback } from 'react';
import { Ship } from '../../types/game';
import { InputValidator } from '../../utils/security/inputValidation';
import './upgrade-interface.css';

interface ShipUpgrade {
  id: string;
  category: 'weapons' | 'shields' | 'engines' | 'cargo' | 'special' | 'cosmetic';
  name: string;
  description: string;
  tier: 1 | 2 | 3 | 4 | 5;
  cost: number;
  installTime: number; // hours
  requirements: {
    shipType?: string[];
    minLevel?: number;
    previousUpgrade?: string;
  };
  effects: {
    stat: string;
    value: number;
    type: 'percentage' | 'absolute';
  }[];
  incompatibleWith?: string[];
  image?: string;
}

interface UpgradeSlot {
  id: string;
  category: ShipUpgrade['category'];
  currentUpgrade?: ShipUpgrade;
  locked: boolean;
  unlockLevel?: number;
}

interface UpgradeInterfaceProps {
  ship: Ship;
  playerCredits: number;
  playerLevel: number;
  installedUpgrades: ShipUpgrade[];
  availableSlots: UpgradeSlot[];
  onInstallUpgrade?: (upgrade: ShipUpgrade, slotId: string) => void;
  onRemoveUpgrade?: (slotId: string) => void;
  onPreviewUpgrade?: (upgrade: ShipUpgrade) => void;
}

// Mock upgrade data
const AVAILABLE_UPGRADES: ShipUpgrade[] = [
  // Weapons
  {
    id: 'plasma_cannon_mk2',
    category: 'weapons',
    name: 'Plasma Cannon Mk II',
    description: 'Enhanced plasma weaponry with improved firing rate and damage output',
    tier: 2,
    cost: 15000,
    installTime: 4,
    requirements: { minLevel: 5 },
    effects: [
      { stat: 'weapons', value: 20, type: 'percentage' },
      { stat: 'fireRate', value: 15, type: 'percentage' }
    ]
  },
  {
    id: 'quantum_torpedoes',
    category: 'weapons',
    name: 'Quantum Torpedo Launcher',
    description: 'Devastating long-range torpedoes that bypass some shield systems',
    tier: 4,
    cost: 45000,
    installTime: 8,
    requirements: { minLevel: 15, shipType: ['Battleship', 'Cruiser'] },
    effects: [
      { stat: 'weapons', value: 35, type: 'percentage' },
      { stat: 'range', value: 50, type: 'percentage' }
    ],
    incompatibleWith: ['missile_pods']
  },
  // Shields
  {
    id: 'reinforced_shields',
    category: 'shields',
    name: 'Reinforced Shield Generator',
    description: 'Stronger shield matrix with faster regeneration',
    tier: 2,
    cost: 12000,
    installTime: 3,
    requirements: { minLevel: 3 },
    effects: [
      { stat: 'shields', value: 25, type: 'percentage' },
      { stat: 'shieldRegen', value: 10, type: 'percentage' }
    ]
  },
  {
    id: 'adaptive_shielding',
    category: 'shields',
    name: 'Adaptive Shield System',
    description: 'Shields that adapt to incoming damage types',
    tier: 5,
    cost: 60000,
    installTime: 12,
    requirements: { minLevel: 20, previousUpgrade: 'reinforced_shields' },
    effects: [
      { stat: 'shields', value: 40, type: 'percentage' },
      { stat: 'damageResistance', value: 15, type: 'percentage' }
    ]
  },
  // Engines
  {
    id: 'turbo_thrusters',
    category: 'engines',
    name: 'Turbo Thrusters',
    description: 'High-performance thrusters for increased speed and maneuverability',
    tier: 1,
    cost: 8000,
    installTime: 2,
    requirements: {},
    effects: [
      { stat: 'speed', value: 15, type: 'percentage' },
      { stat: 'turnRate', value: 10, type: 'percentage' }
    ]
  },
  {
    id: 'warp_drive_optimizer',
    category: 'engines',
    name: 'Warp Drive Optimizer',
    description: 'Reduces warp fuel consumption and increases jump range',
    tier: 3,
    cost: 25000,
    installTime: 6,
    requirements: { minLevel: 10 },
    effects: [
      { stat: 'warpEfficiency', value: 30, type: 'percentage' },
      { stat: 'jumpRange', value: 20, type: 'percentage' }
    ]
  },
  // Cargo
  {
    id: 'cargo_expansion',
    category: 'cargo',
    name: 'Cargo Bay Expansion',
    description: 'Increases cargo capacity without sacrificing performance',
    tier: 1,
    cost: 5000,
    installTime: 2,
    requirements: { shipType: ['Freighter', 'Transport'] },
    effects: [
      { stat: 'cargoCapacity', value: 100, type: 'absolute' }
    ]
  },
  {
    id: 'specialized_containers',
    category: 'cargo',
    name: 'Specialized Cargo Containers',
    description: 'Temperature-controlled containers for valuable goods',
    tier: 3,
    cost: 18000,
    installTime: 4,
    requirements: { minLevel: 8, previousUpgrade: 'cargo_expansion' },
    effects: [
      { stat: 'cargoCapacity', value: 50, type: 'absolute' },
      { stat: 'cargoValue', value: 20, type: 'percentage' }
    ]
  },
  // Special
  {
    id: 'cloaking_device',
    category: 'special',
    name: 'Cloaking Device',
    description: 'Temporary invisibility from enemy sensors',
    tier: 5,
    cost: 75000,
    installTime: 10,
    requirements: { minLevel: 25, shipType: ['Scout', 'Stealth Fighter'] },
    effects: [
      { stat: 'stealth', value: 100, type: 'percentage' }
    ],
    incompatibleWith: ['heavy_armor']
  },
  {
    id: 'repair_drones',
    category: 'special',
    name: 'Automated Repair Drones',
    description: 'Drones that automatically repair hull damage during combat',
    tier: 3,
    cost: 30000,
    installTime: 5,
    requirements: { minLevel: 12 },
    effects: [
      { stat: 'hullRepair', value: 5, type: 'absolute' }
    ]
  }
];

const UpgradeInterface: React.FC<UpgradeInterfaceProps> = ({
  ship,
  playerCredits,
  playerLevel,
  installedUpgrades,
  availableSlots,
  onInstallUpgrade,
  onRemoveUpgrade,
  onPreviewUpgrade
}) => {
  const [selectedCategory, setSelectedCategory] = useState<ShipUpgrade['category'] | 'all'>('all');
  const [selectedUpgrade, setSelectedUpgrade] = useState<ShipUpgrade | null>(null);
  const [selectedSlot, setSelectedSlot] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCompareMode, setShowCompareMode] = useState(false);
  const [compareUpgrades, setCompareUpgrades] = useState<ShipUpgrade[]>([]);
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

  // Filter upgrades based on category and search
  const filteredUpgrades = useMemo(() => {
    return AVAILABLE_UPGRADES.filter(upgrade => {
      // Category filter
      if (selectedCategory !== 'all' && upgrade.category !== selectedCategory) {
        return false;
      }

      // Search filter
      if (searchTerm) {
        const searchLower = searchTerm.toLowerCase();
        return upgrade.name.toLowerCase().includes(searchLower) ||
               upgrade.description.toLowerCase().includes(searchLower);
      }

      return true;
    });
  }, [selectedCategory, searchTerm]);

  // Check if upgrade can be installed
  const canInstallUpgrade = useCallback((upgrade: ShipUpgrade): { canInstall: boolean; reason?: string } => {
    // Check credits
    if (upgrade.cost > playerCredits) {
      return { canInstall: false, reason: 'Insufficient credits' };
    }

    // Check level requirement
    if (upgrade.requirements.minLevel && playerLevel < upgrade.requirements.minLevel) {
      return { canInstall: false, reason: `Requires level ${upgrade.requirements.minLevel}` };
    }

    // Check ship type requirement
    if (upgrade.requirements.shipType && !upgrade.requirements.shipType.includes(ship.type)) {
      return { canInstall: false, reason: 'Incompatible ship type' };
    }

    // Check previous upgrade requirement
    if (upgrade.requirements.previousUpgrade) {
      const hasPrevious = installedUpgrades.some(u => u.id === upgrade.requirements.previousUpgrade);
      if (!hasPrevious) {
        const prevUpgrade = AVAILABLE_UPGRADES.find(u => u.id === upgrade.requirements.previousUpgrade);
        return { canInstall: false, reason: `Requires ${prevUpgrade?.name || 'previous upgrade'}` };
      }
    }

    // Check incompatibilities
    if (upgrade.incompatibleWith) {
      const incompatible = installedUpgrades.find(u => upgrade.incompatibleWith?.includes(u.id));
      if (incompatible) {
        return { canInstall: false, reason: `Incompatible with ${incompatible.name}` };
      }
    }

    // Check available slots
    const hasSlot = availableSlots.some(slot => 
      slot.category === upgrade.category && 
      !slot.currentUpgrade && 
      !slot.locked
    );
    if (!hasSlot) {
      return { canInstall: false, reason: 'No available slot' };
    }

    return { canInstall: true };
  }, [playerCredits, playerLevel, ship.type, installedUpgrades, availableSlots]);

  const installUpgrade = useCallback(() => {
    if (!canPerformAction() || !selectedUpgrade || !selectedSlot || !onInstallUpgrade) return;

    const validation = canInstallUpgrade(selectedUpgrade);
    if (!validation.canInstall) {
      alert(validation.reason || 'Cannot install this upgrade');
      return;
    }

    onInstallUpgrade(selectedUpgrade, selectedSlot);
    setSelectedUpgrade(null);
    setSelectedSlot(null);
  }, [canPerformAction, selectedUpgrade, selectedSlot, onInstallUpgrade, canInstallUpgrade]);

  const removeUpgrade = useCallback((slotId: string) => {
    if (!canPerformAction() || !onRemoveUpgrade) return;

    if (window.confirm('Are you sure you want to remove this upgrade? You will not get a refund.')) {
      onRemoveUpgrade(slotId);
    }
  }, [canPerformAction, onRemoveUpgrade]);

  const toggleCompareMode = useCallback((upgrade: ShipUpgrade) => {
    if (!showCompareMode) {
      setShowCompareMode(true);
      setCompareUpgrades([upgrade]);
    } else {
      if (compareUpgrades.includes(upgrade)) {
        setCompareUpgrades(compareUpgrades.filter(u => u.id !== upgrade.id));
        if (compareUpgrades.length <= 1) {
          setShowCompareMode(false);
        }
      } else if (compareUpgrades.length < 3) {
        setCompareUpgrades([...compareUpgrades, upgrade]);
      }
    }
  }, [showCompareMode, compareUpgrades]);

  const getTierColor = (tier: number) => {
    const colors = ['#888888', '#4a9eff', '#ff44ff', '#ffaa44', '#ff4444'];
    return colors[tier - 1] || '#ffffff';
  };

  const getCategoryIcon = (category: string) => {
    const icons: { [key: string]: string } = {
      weapons: '⚔️',
      shields: '🛡️',
      engines: '🚀',
      cargo: '📦',
      special: '✨',
      cosmetic: '🎨'
    };
    return icons[category] || '❓';
  };

  return (
    <div className="upgrade-interface">
      <div className="interface-header">
        <h3>Ship Upgrades</h3>
        <div className="ship-info">
          <span className="ship-name">{ship.name}</span>
          <span className="player-credits">Credits: {playerCredits.toLocaleString()}</span>
        </div>
      </div>

      <div className="upgrade-categories">
        <button
          className={`category-btn ${selectedCategory === 'all' ? 'active' : ''}`}
          onClick={() => setSelectedCategory('all')}
        >
          All
        </button>
        {(['weapons', 'shields', 'engines', 'cargo', 'special'] as const).map(category => (
          <button
            key={category}
            className={`category-btn ${selectedCategory === category ? 'active' : ''}`}
            onClick={() => setSelectedCategory(category)}
          >
            {getCategoryIcon(category)} {category.charAt(0).toUpperCase() + category.slice(1)}
          </button>
        ))}
      </div>

      <div className="upgrade-search">
        <input
          type="text"
          placeholder="Search upgrades..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          maxLength={50}
        />
        <button 
          className={`compare-mode-btn ${showCompareMode ? 'active' : ''}`}
          onClick={() => setShowCompareMode(!showCompareMode)}
        >
          Compare Mode
        </button>
      </div>

      <div className="upgrade-content">
        <div className="upgrades-list">
          <h4>Available Upgrades</h4>
          <div className="upgrades-grid">
            {filteredUpgrades.map(upgrade => {
              const validation = canInstallUpgrade(upgrade);
              const isSelected = selectedUpgrade?.id === upgrade.id;
              const isComparing = compareUpgrades.includes(upgrade);
              
              return (
                <div
                  key={upgrade.id}
                  className={`upgrade-card ${isSelected ? 'selected' : ''} ${!validation.canInstall ? 'unavailable' : ''} ${isComparing ? 'comparing' : ''}`}
                  onClick={() => !showCompareMode && setSelectedUpgrade(upgrade)}
                >
                  <div className="upgrade-header">
                    <h5>{upgrade.name}</h5>
                    <span 
                      className="upgrade-tier"
                      style={{ backgroundColor: getTierColor(upgrade.tier) }}
                    >
                      Tier {upgrade.tier}
                    </span>
                  </div>
                  
                  <div className="upgrade-category">
                    {getCategoryIcon(upgrade.category)} {upgrade.category}
                  </div>
                  
                  <p className="upgrade-description">{upgrade.description}</p>
                  
                  <div className="upgrade-effects">
                    {upgrade.effects.map((effect, index) => (
                      <div key={index} className="effect-item">
                        <span className="effect-stat">{effect.stat}:</span>
                        <span className="effect-value">
                          {effect.type === 'percentage' ? '+' : ''}
                          {effect.value}
                          {effect.type === 'percentage' ? '%' : ''}
                        </span>
                      </div>
                    ))}
                  </div>
                  
                  <div className="upgrade-footer">
                    <div className="upgrade-cost">
                      <span className="cost-value">{upgrade.cost.toLocaleString()}</span>
                      <span className="cost-label">credits</span>
                    </div>
                    <div className="upgrade-time">
                      <span className="time-value">{upgrade.installTime}h</span>
                      <span className="time-label">install</span>
                    </div>
                  </div>
                  
                  {!validation.canInstall && (
                    <div className="unavailable-reason">{validation.reason}</div>
                  )}
                  
                  {showCompareMode && (
                    <button 
                      className="compare-toggle"
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleCompareMode(upgrade);
                      }}
                    >
                      {isComparing ? '✓' : '+'}
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        <div className="upgrade-slots">
          <h4>Upgrade Slots</h4>
          <div className="slots-list">
            {availableSlots.map(slot => (
              <div 
                key={slot.id}
                className={`slot-item ${slot.locked ? 'locked' : ''} ${selectedSlot === slot.id ? 'selected' : ''}`}
                onClick={() => !slot.locked && !slot.currentUpgrade && setSelectedSlot(slot.id)}
              >
                <div className="slot-icon">{getCategoryIcon(slot.category)}</div>
                <div className="slot-info">
                  <h5>{slot.category} Slot</h5>
                  {slot.currentUpgrade ? (
                    <>
                      <p className="current-upgrade">{slot.currentUpgrade.name}</p>
                      <button 
                        className="remove-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          removeUpgrade(slot.id);
                        }}
                      >
                        Remove
                      </button>
                    </>
                  ) : slot.locked ? (
                    <p className="lock-reason">Unlocks at level {slot.unlockLevel}</p>
                  ) : (
                    <p className="empty-slot">Empty</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {selectedUpgrade && !showCompareMode && (
        <div className="upgrade-details">
          <h4>{selectedUpgrade.name}</h4>
          <div className="details-content">
            <div className="details-section">
              <h5>Description</h5>
              <p>{selectedUpgrade.description}</p>
            </div>
            
            <div className="details-section">
              <h5>Effects</h5>
              <div className="effects-list">
                {selectedUpgrade.effects.map((effect, index) => (
                  <div key={index} className="effect-detail">
                    <span className="effect-name">{effect.stat}:</span>
                    <span className="effect-change">
                      {effect.type === 'percentage' ? '+' : ''}
                      {effect.value}
                      {effect.type === 'percentage' ? '%' : ''}
                    </span>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="details-section">
              <h5>Requirements</h5>
              <ul className="requirements-list">
                {selectedUpgrade.requirements.minLevel && (
                  <li>Level {selectedUpgrade.requirements.minLevel} or higher</li>
                )}
                {selectedUpgrade.requirements.shipType && (
                  <li>Ship type: {selectedUpgrade.requirements.shipType.join(', ')}</li>
                )}
                {selectedUpgrade.requirements.previousUpgrade && (
                  <li>Requires: {AVAILABLE_UPGRADES.find(u => u.id === selectedUpgrade.requirements.previousUpgrade)?.name}</li>
                )}
              </ul>
            </div>
            
            {selectedUpgrade.incompatibleWith && selectedUpgrade.incompatibleWith.length > 0 && (
              <div className="details-section">
                <h5>Incompatible With</h5>
                <ul className="incompatible-list">
                  {selectedUpgrade.incompatibleWith.map(id => {
                    const incompatible = AVAILABLE_UPGRADES.find(u => u.id === id);
                    return incompatible ? <li key={id}>{incompatible.name}</li> : null;
                  })}
                </ul>
              </div>
            )}
            
            <div className="details-actions">
              <button 
                className="install-btn"
                onClick={installUpgrade}
                disabled={!selectedSlot || !canInstallUpgrade(selectedUpgrade).canInstall}
              >
                {!selectedSlot ? 'Select a Slot' : 'Install Upgrade'}
              </button>
              {onPreviewUpgrade && (
                <button 
                  className="preview-btn"
                  onClick={() => onPreviewUpgrade(selectedUpgrade)}
                >
                  Preview
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {showCompareMode && compareUpgrades.length > 0 && (
        <div className="compare-panel">
          <h4>Upgrade Comparison</h4>
          <div className="compare-grid">
            {compareUpgrades.map(upgrade => (
              <div key={upgrade.id} className="compare-item">
                <h5>{upgrade.name}</h5>
                <div className="compare-tier" style={{ color: getTierColor(upgrade.tier) }}>
                  Tier {upgrade.tier}
                </div>
                <div className="compare-cost">{upgrade.cost.toLocaleString()} cr</div>
                <div className="compare-effects">
                  {upgrade.effects.map((effect, index) => (
                    <div key={index} className="compare-effect">
                      <span>{effect.stat}:</span>
                      <span>
                        {effect.type === 'percentage' ? '+' : ''}
                        {effect.value}
                        {effect.type === 'percentage' ? '%' : ''}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default UpgradeInterface;