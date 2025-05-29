import React, { useState, useMemo, useCallback } from 'react';
import { Ship } from '../../types/game';
import { InputValidator } from '../../utils/security/inputValidation';
import './cargo-manager.css';

interface CargoItem {
  id: string;
  name: string;
  category: 'raw' | 'processed' | 'equipment' | 'contraband' | 'special';
  quantity: number;
  unitWeight: number; // tons per unit
  unitValue: number; // credits per unit
  perishable: boolean;
  expiresIn?: number; // hours
  legal: boolean;
  description: string;
  icon?: string;
}

interface CargoContainer {
  id: string;
  type: 'standard' | 'refrigerated' | 'secure' | 'hazmat';
  capacity: number;
  currentLoad: number;
  items: CargoItem[];
  locked: boolean;
  temperature?: number;
}

interface CargoManagerProps {
  ship: Ship;
  cargoContainers: CargoContainer[];
  availableCargo?: CargoItem[];
  playerCredits: number;
  onTransferCargo?: (fromContainer: string, toContainer: string, item: CargoItem, quantity: number) => void;
  onJettisonCargo?: (containerId: string, item: CargoItem, quantity: number) => void;
  onSellCargo?: (item: CargoItem, quantity: number) => void;
  onBuyCargo?: (item: CargoItem, quantity: number) => void;
}

const CARGO_CATEGORIES = {
  raw: { name: 'Raw Materials', color: '#888888', icon: '⛏️' },
  processed: { name: 'Processed Goods', color: '#4a9eff', icon: '🏭' },
  equipment: { name: 'Equipment', color: '#ff44ff', icon: '⚙️' },
  contraband: { name: 'Contraband', color: '#ff4444', icon: '☠️' },
  special: { name: 'Special Items', color: '#ffaa44', icon: '✨' }
};

const CargoManager: React.FC<CargoManagerProps> = ({
  ship,
  cargoContainers,
  availableCargo = [],
  playerCredits,
  onTransferCargo,
  onJettisonCargo,
  onSellCargo,
  onBuyCargo
}) => {
  const [selectedContainer, setSelectedContainer] = useState<string | null>(cargoContainers[0]?.id || null);
  const [selectedItem, setSelectedItem] = useState<CargoItem | null>(null);
  const [transferQuantity, setTransferQuantity] = useState(1);
  const [transferTarget, setTransferTarget] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'inventory' | 'market'>('inventory');
  const [filterCategory, setFilterCategory] = useState<CargoItem['category'] | 'all'>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [lastAction, setLastAction] = useState<number>(0);

  // Rate limiting
  const RATE_LIMIT_MS = 500;
  const canPerformAction = useCallback(() => {
    const now = Date.now();
    if (now - lastAction < RATE_LIMIT_MS) {
      return false;
    }
    setLastAction(now);
    return true;
  }, [lastAction]);

  // Calculate total cargo statistics
  const cargoStats = useMemo(() => {
    let totalWeight = 0;
    let totalValue = 0;
    let itemCount = 0;
    let illegalCount = 0;
    let perishableCount = 0;

    cargoContainers.forEach(container => {
      container.items.forEach(item => {
        const weight = item.quantity * item.unitWeight;
        const value = item.quantity * item.unitValue;
        totalWeight += weight;
        totalValue += value;
        itemCount += item.quantity;
        if (!item.legal) illegalCount += item.quantity;
        if (item.perishable) perishableCount += item.quantity;
      });
    });

    return {
      totalWeight,
      totalValue,
      itemCount,
      illegalCount,
      perishableCount,
      utilization: (totalWeight / ship.cargo_capacity) * 100
    };
  }, [cargoContainers, ship.cargo_capacity]);

  // Filter items based on search and category
  const filteredItems = useMemo(() => {
    const items = viewMode === 'inventory' 
      ? cargoContainers.find(c => c.id === selectedContainer)?.items || []
      : availableCargo;

    return items.filter(item => {
      if (filterCategory !== 'all' && item.category !== filterCategory) {
        return false;
      }
      if (searchTerm) {
        const searchLower = searchTerm.toLowerCase();
        return item.name.toLowerCase().includes(searchLower) ||
               item.description.toLowerCase().includes(searchLower);
      }
      return true;
    });
  }, [viewMode, selectedContainer, availableCargo, cargoContainers, filterCategory, searchTerm]);

  // Handle cargo transfer
  const transferCargo = useCallback(() => {
    if (!canPerformAction() || !onTransferCargo || !selectedItem || !selectedContainer || !transferTarget) {
      return;
    }

    if (transferQuantity <= 0 || transferQuantity > selectedItem.quantity) {
      alert('Invalid transfer quantity');
      return;
    }

    const targetContainer = cargoContainers.find(c => c.id === transferTarget);
    if (!targetContainer) return;

    const transferWeight = transferQuantity * selectedItem.unitWeight;
    const targetSpace = targetContainer.capacity - targetContainer.currentLoad;

    if (transferWeight > targetSpace) {
      alert('Insufficient space in target container');
      return;
    }

    onTransferCargo(selectedContainer, transferTarget, selectedItem, transferQuantity);
    setSelectedItem(null);
    setTransferTarget(null);
    setTransferQuantity(1);
  }, [canPerformAction, onTransferCargo, selectedItem, selectedContainer, transferTarget, 
      transferQuantity, cargoContainers]);

  // Handle cargo jettison
  const jettisonCargo = useCallback(() => {
    if (!canPerformAction() || !onJettisonCargo || !selectedItem || !selectedContainer) {
      return;
    }

    const confirmMessage = selectedItem.legal 
      ? `Jettison ${transferQuantity} units of ${selectedItem.name}?`
      : `Jettison ${transferQuantity} units of ILLEGAL cargo? This will destroy evidence.`;

    if (window.confirm(confirmMessage)) {
      onJettisonCargo(selectedContainer, selectedItem, transferQuantity);
      setSelectedItem(null);
      setTransferQuantity(1);
    }
  }, [canPerformAction, onJettisonCargo, selectedItem, selectedContainer, transferQuantity]);

  // Handle cargo sale
  const sellCargo = useCallback(() => {
    if (!canPerformAction() || !onSellCargo || !selectedItem) {
      return;
    }

    if (!selectedItem.legal) {
      if (!window.confirm('Selling illegal cargo carries risks. Continue?')) {
        return;
      }
    }

    const revenue = transferQuantity * selectedItem.unitValue;
    if (window.confirm(`Sell ${transferQuantity} units for ${revenue.toLocaleString()} credits?`)) {
      onSellCargo(selectedItem, transferQuantity);
      setSelectedItem(null);
      setTransferQuantity(1);
    }
  }, [canPerformAction, onSellCargo, selectedItem, transferQuantity]);

  // Handle cargo purchase
  const buyCargo = useCallback(() => {
    if (!canPerformAction() || !onBuyCargo || !selectedItem) {
      return;
    }

    const cost = transferQuantity * selectedItem.unitValue;
    if (cost > playerCredits) {
      alert('Insufficient credits');
      return;
    }

    const weight = transferQuantity * selectedItem.unitWeight;
    const availableSpace = ship.cargo_capacity - cargoStats.totalWeight;
    if (weight > availableSpace) {
      alert('Insufficient cargo space');
      return;
    }

    onBuyCargo(selectedItem, transferQuantity);
    setSelectedItem(null);
    setTransferQuantity(1);
  }, [canPerformAction, onBuyCargo, selectedItem, transferQuantity, playerCredits, 
      ship.cargo_capacity, cargoStats.totalWeight]);

  const getContainerIcon = (type: string) => {
    switch (type) {
      case 'standard': return '📦';
      case 'refrigerated': return '❄️';
      case 'secure': return '🔒';
      case 'hazmat': return '☢️';
      default: return '📦';
    }
  };

  const getContainerColor = (container: CargoContainer) => {
    const utilization = (container.currentLoad / container.capacity) * 100;
    if (utilization >= 90) return '#ff4444';
    if (utilization >= 70) return '#ffaa44';
    if (utilization >= 50) return '#ffff44';
    return '#44ff44';
  };

  return (
    <div className="cargo-manager">
      <div className="manager-header">
        <h3>Cargo Management</h3>
        <div className="cargo-summary">
          <span className="summary-item">
            <span className="label">Total:</span>
            <span className="value">{cargoStats.totalWeight.toFixed(1)}/{ship.cargo_capacity} tons</span>
          </span>
          <span className="summary-item">
            <span className="label">Value:</span>
            <span className="value">{cargoStats.totalValue.toLocaleString()} cr</span>
          </span>
          <span className="summary-item">
            <span className="label">Utilization:</span>
            <span className="value" style={{ color: getContainerColor({ currentLoad: cargoStats.totalWeight, capacity: ship.cargo_capacity } as CargoContainer) }}>
              {cargoStats.utilization.toFixed(0)}%
            </span>
          </span>
        </div>
      </div>

      <div className="view-controls">
        <div className="view-tabs">
          <button
            className={`view-tab ${viewMode === 'inventory' ? 'active' : ''}`}
            onClick={() => setViewMode('inventory')}
          >
            Ship Inventory
          </button>
          <button
            className={`view-tab ${viewMode === 'market' ? 'active' : ''}`}
            onClick={() => setViewMode('market')}
          >
            Market Goods
          </button>
        </div>
        
        <div className="filter-controls">
          <select 
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value as CargoItem['category'] | 'all')}
          >
            <option value="all">All Categories</option>
            {Object.entries(CARGO_CATEGORIES).map(([key, cat]) => (
              <option key={key} value={key}>{cat.icon} {cat.name}</option>
            ))}
          </select>
          
          <input
            type="text"
            placeholder="Search cargo..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            maxLength={50}
          />
        </div>
      </div>

      <div className="cargo-content">
        {viewMode === 'inventory' && (
          <div className="containers-panel">
            <h4>Cargo Containers</h4>
            <div className="containers-list">
              {cargoContainers.map(container => (
                <div
                  key={container.id}
                  className={`container-item ${selectedContainer === container.id ? 'selected' : ''} ${container.locked ? 'locked' : ''}`}
                  onClick={() => !container.locked && setSelectedContainer(container.id)}
                >
                  <div className="container-icon">{getContainerIcon(container.type)}</div>
                  <div className="container-info">
                    <h5>{container.type} Container</h5>
                    <div className="container-capacity">
                      <div className="capacity-bar">
                        <div 
                          className="capacity-fill"
                          style={{ 
                            width: `${(container.currentLoad / container.capacity) * 100}%`,
                            backgroundColor: getContainerColor(container)
                          }}
                        />
                      </div>
                      <span className="capacity-text">
                        {container.currentLoad.toFixed(1)}/{container.capacity} tons
                      </span>
                    </div>
                    <div className="container-stats">
                      <span>{container.items.length} types</span>
                      {container.temperature !== undefined && (
                        <span>🌡️ {container.temperature}°C</span>
                      )}
                    </div>
                  </div>
                  {container.locked && <span className="lock-indicator">🔒</span>}
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="items-panel">
          <h4>{viewMode === 'inventory' ? 'Container Contents' : 'Available Goods'}</h4>
          <div className="items-grid">
            {filteredItems.map(item => (
              <div
                key={item.id}
                className={`cargo-item ${selectedItem?.id === item.id ? 'selected' : ''} ${!item.legal ? 'illegal' : ''}`}
                onClick={() => setSelectedItem(item)}
              >
                <div className="item-header">
                  <span className="item-icon">{CARGO_CATEGORIES[item.category].icon}</span>
                  <h5>{item.name}</h5>
                  {!item.legal && <span className="illegal-badge">ILLEGAL</span>}
                </div>
                
                <p className="item-description">{item.description}</p>
                
                <div className="item-stats">
                  <div className="stat">
                    <span className="stat-label">Quantity:</span>
                    <span className="stat-value">{item.quantity}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Weight:</span>
                    <span className="stat-value">{item.unitWeight}t/unit</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Value:</span>
                    <span className="stat-value">{item.unitValue.toLocaleString()} cr</span>
                  </div>
                </div>
                
                {item.perishable && item.expiresIn && (
                  <div className="expiry-warning">
                    ⏰ Expires in {item.expiresIn}h
                  </div>
                )}
                
                <div className="item-total">
                  Total: {(item.quantity * item.unitWeight).toFixed(1)}t • {(item.quantity * item.unitValue).toLocaleString()} cr
                </div>
              </div>
            ))}
          </div>
        </div>

        {selectedItem && (
          <div className="action-panel">
            <h4>Cargo Actions</h4>
            <div className="selected-item-info">
              <h5>{selectedItem.name}</h5>
              <p>Available: {selectedItem.quantity} units</p>
            </div>
            
            <div className="quantity-selector">
              <label>Quantity:</label>
              <input
                type="number"
                min="1"
                max={selectedItem.quantity}
                value={transferQuantity}
                onChange={(e) => setTransferQuantity(Math.max(1, Math.min(selectedItem.quantity, parseInt(e.target.value) || 1)))}
              />
              <button 
                className="max-btn"
                onClick={() => setTransferQuantity(selectedItem.quantity)}
              >
                MAX
              </button>
            </div>
            
            <div className="action-calculations">
              <div className="calc-item">
                <span>Weight:</span>
                <span>{(transferQuantity * selectedItem.unitWeight).toFixed(1)} tons</span>
              </div>
              <div className="calc-item">
                <span>Value:</span>
                <span>{(transferQuantity * selectedItem.unitValue).toLocaleString()} cr</span>
              </div>
            </div>
            
            {viewMode === 'inventory' && (
              <>
                {cargoContainers.length > 1 && (
                  <div className="transfer-section">
                    <label>Transfer to:</label>
                    <select 
                      value={transferTarget || ''}
                      onChange={(e) => setTransferTarget(e.target.value || null)}
                    >
                      <option value="">Select container...</option>
                      {cargoContainers
                        .filter(c => c.id !== selectedContainer && !c.locked)
                        .map(container => (
                          <option key={container.id} value={container.id}>
                            {getContainerIcon(container.type)} {container.type} 
                            ({(container.capacity - container.currentLoad).toFixed(1)}t free)
                          </option>
                        ))}
                    </select>
                    <button 
                      className="transfer-btn"
                      onClick={transferCargo}
                      disabled={!transferTarget}
                    >
                      Transfer
                    </button>
                  </div>
                )}
                
                <div className="action-buttons">
                  {onSellCargo && (
                    <button 
                      className="sell-btn"
                      onClick={sellCargo}
                    >
                      Sell Cargo
                    </button>
                  )}
                  {onJettisonCargo && (
                    <button 
                      className="jettison-btn"
                      onClick={jettisonCargo}
                    >
                      Jettison
                    </button>
                  )}
                </div>
              </>
            )}
            
            {viewMode === 'market' && onBuyCargo && (
              <button 
                className="buy-btn"
                onClick={buyCargo}
                disabled={(transferQuantity * selectedItem.unitValue) > playerCredits}
              >
                Buy for {(transferQuantity * selectedItem.unitValue).toLocaleString()} cr
              </button>
            )}
          </div>
        )}
      </div>

      {cargoStats.illegalCount > 0 && (
        <div className="warning-banner">
          ⚠️ Carrying {cargoStats.illegalCount} units of illegal cargo. Security scans may result in fines or confiscation.
        </div>
      )}
      
      {cargoStats.perishableCount > 0 && (
        <div className="info-banner">
          ℹ️ {cargoStats.perishableCount} units of perishable cargo on board. Monitor expiration times.
        </div>
      )}
    </div>
  );
};

export default CargoManager;