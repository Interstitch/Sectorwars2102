import React, { useState, useEffect } from 'react';
import { useGame } from '../../contexts/GameContext';
import { useWebSocket } from '../../contexts/WebSocketContext';
import './trading-interface.css';

interface Resource {
  name: string;
  quantity: number;
  buy_price: number;
  sell_price: number;
  last_updated?: string;
}

interface TradeCalculation {
  resourceType: string;
  quantity: number;
  unitPrice: number;
  totalCost: number;
  isAffordable: boolean;
  fitsInCargo: boolean;
}

const TradingInterface: React.FC = () => {
  const { 
    playerState, 
    currentShip, 
    marketInfo, 
    getMarketInfo, 
    buyResource, 
    sellResource,
    portsInSector,
    isLoading,
    error 
  } = useGame();
  
  const { addNotification, isConnected } = useWebSocket();
  
  const [selectedPort, setSelectedPort] = useState<string>('');
  const [selectedResource, setSelectedResource] = useState<string>('');
  const [tradeQuantity, setTradeQuantity] = useState<number>(1);
  const [tradeMode, setTradeMode] = useState<'buy' | 'sell'>('buy');
  const [tradeCalculation, setTradeCalculation] = useState<TradeCalculation | null>(null);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);

  // Auto-select first port if only one available
  useEffect(() => {
    if (portsInSector.length === 1 && !selectedPort) {
      setSelectedPort(portsInSector[0].id);
    }
  }, [portsInSector, selectedPort]);

  // Load market info when port is selected
  useEffect(() => {
    if (selectedPort) {
      getMarketInfo(selectedPort);
    }
  }, [selectedPort, getMarketInfo]);

  // Calculate trade costs when parameters change
  useEffect(() => {
    if (selectedResource && marketInfo && tradeQuantity > 0) {
      const resource = marketInfo.resources[selectedResource];
      if (resource) {
        const unitPrice = tradeMode === 'buy' ? resource.buy_price : resource.sell_price;
        const totalCost = unitPrice * tradeQuantity;
        
        // Check affordability and cargo space
        const isAffordable = tradeMode === 'buy' 
          ? (playerState?.credits || 0) >= totalCost
          : true; // Can always sell if you have the resource
        
        const currentCargo = currentShip?.cargo ? Object.values(currentShip.cargo).reduce((a, b) => a + b, 0) : 0;
        const cargoCapacity = currentShip?.cargo_capacity || 0;
        const fitsInCargo = tradeMode === 'buy' 
          ? (currentCargo + tradeQuantity) <= cargoCapacity
          : true; // Selling always frees up cargo space

        setTradeCalculation({
          resourceType: selectedResource,
          quantity: tradeQuantity,
          unitPrice,
          totalCost,
          isAffordable,
          fitsInCargo
        });
      }
    } else {
      setTradeCalculation(null);
    }
  }, [selectedResource, marketInfo, tradeQuantity, tradeMode, playerState, currentShip]);

  const handlePortChange = (stationId: string) => {
    setSelectedPort(stationId);
    setSelectedResource('');
    setTradeQuantity(1);
  };

  const handleResourceChange = (resourceType: string) => {
    setSelectedResource(resourceType);
    setTradeQuantity(1);
  };

  const handleTradeModeChange = (mode: 'buy' | 'sell') => {
    setTradeMode(mode);
    setTradeQuantity(1);
  };

  const getMaxQuantity = (): number => {
    if (!selectedResource || !marketInfo || !playerState || !currentShip) return 0;
    
    const resource = marketInfo.resources[selectedResource];
    if (!resource) return 0;

    if (tradeMode === 'buy') {
      // For buying: limited by credits, cargo space, and port inventory
      const affordableQuantity = Math.floor(playerState.credits / resource.buy_price);
      const currentCargo = currentShip.cargo ? Object.values(currentShip.cargo).reduce((a, b) => a + b, 0) : 0;
      const cargoSpace = currentShip.cargo_capacity - currentCargo;
      const portInventory = resource.quantity;
      
      return Math.min(affordableQuantity, cargoSpace, portInventory);
    } else {
      // For selling: limited by what player has
      return currentShip.cargo?.[selectedResource] || 0;
    }
  };

  const setMaxQuantity = () => {
    const maxQty = getMaxQuantity();
    setTradeQuantity(maxQty);
  };

  const canExecuteTrade = (): boolean => {
    if (!tradeCalculation || !playerState?.is_ported) return false;
    
    if (tradeMode === 'buy') {
      return tradeCalculation.isAffordable && tradeCalculation.fitsInCargo && tradeQuantity <= (marketInfo?.resources[selectedResource]?.quantity || 0);
    } else {
      const playerHas = currentShip?.cargo?.[selectedResource] || 0;
      return tradeQuantity <= playerHas;
    }
  };

  const executeTrade = async () => {
    if (!canExecuteTrade() || !selectedPort || !selectedResource) return;

    try {
      let result;
      if (tradeMode === 'buy') {
        result = await buyResource(selectedPort, selectedResource, tradeQuantity);
      } else {
        result = await sellResource(selectedPort, selectedResource, tradeQuantity);
      }

      // Show success notification
      addNotification({
        title: 'Trade Successful',
        content: result.message,
        level: 'success'
      });

      // Reset form
      setTradeQuantity(1);
      setShowConfirmDialog(false);
      
    } catch (error: any) {
      addNotification({
        title: 'Trade Failed',
        content: error.response?.data?.message || 'Failed to execute trade',
        level: 'error'
      });
    }
  };

  const formatCredits = (amount: number): string => {
    return new Intl.NumberFormat().format(amount);
  };

  const getResourceIcon = (resourceType: string): string => {
    const icons: Record<string, string> = {
      'Food': '🌾',
      'Fuel': '⚡',
      'Ore': '🪨', 
      'Tech': '🔧',
      'Organics': '🧬',
      'Equipment': '⚙️',
      'Luxuries': '💎',
      'Colonists': '👥'
    };
    return icons[resourceType] || '📦';
  };

  if (!playerState?.is_ported) {
    return (
      <div className="trading-interface">
        <div className="trading-header">
          <h2>Trading Interface</h2>
          <div className="status-indicator disconnected">Not Docked</div>
        </div>
        <div className="not-docked-message">
          <div className="message-icon">🚀</div>
          <h3>Dock at a Station to Trade</h3>
          <p>You must be docked at a port to access trading facilities.</p>
          {portsInSector.length > 0 && (
            <div className="available-ports">
              <h4>Available Ports in Sector:</h4>
              <ul>
                {portsInSector.map(port => (
                  <li key={port.id} className="port-item">
                    <span className="port-name">{port.name}</span>
                    <span className="port-type">{port.type}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="trading-interface">
      <div className="trading-header">
        <h2>Trading Interface</h2>
        <div className="connection-status">
          <div className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
            {isConnected ? 'Real-time' : 'Offline'}
          </div>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      <div className="trading-content">
        {/* Station Selection */}
        <div className="port-selection">
          <label htmlFor="port-select">Select Station:</label>
          <select 
            id="port-select"
            value={selectedPort} 
            onChange={(e) => handlePortChange(e.target.value)}
            disabled={portsInSector.length <= 1}
          >
            <option value="">Choose a port...</option>
            {portsInSector.map(port => (
              <option key={port.id} value={port.id}>
                {port.name} ({port.type})
              </option>
            ))}
          </select>
        </div>

        {/* Trade Mode Selection */}
        <div className="trade-mode-selection">
          <button 
            className={`mode-button ${tradeMode === 'buy' ? 'active' : ''}`}
            onClick={() => handleTradeModeChange('buy')}
          >
            Buy Resources
          </button>
          <button 
            className={`mode-button ${tradeMode === 'sell' ? 'active' : ''}`}
            onClick={() => handleTradeModeChange('sell')}
          >
            Sell Resources
          </button>
        </div>

        {/* Market Information */}
        {marketInfo && (
          <div className="market-info">
            <h3>Market at {marketInfo.port.name}</h3>
            <div className="port-details">
              <span>Type: {marketInfo.port.type}</span>
              {marketInfo.port.faction && <span>Faction: {marketInfo.port.faction}</span>}
              <span>Tax Rate: {((marketInfo.port.tax_rate || 0.1) * 100).toFixed(1)}%</span>
            </div>

            <div className="resources-grid">
              {Object.entries(marketInfo.resources).map(([resourceType, resource]) => {
                const canTrade = tradeMode === 'buy' 
                  ? resource.quantity > 0 
                  : (currentShip?.cargo?.[resourceType] || 0) > 0;

                return (
                  <div 
                    key={resourceType}
                    className={`resource-card ${!canTrade ? 'disabled' : ''} ${selectedResource === resourceType ? 'selected' : ''}`}
                    onClick={() => canTrade && handleResourceChange(resourceType)}
                  >
                    <div className="resource-icon">{getResourceIcon(resourceType)}</div>
                    <div className="resource-name">{resourceType}</div>
                    <div className="resource-prices">
                      <div className="buy-price">Buy: {formatCredits(resource.buy_price)}</div>
                      <div className="sell-price">Sell: {formatCredits(resource.sell_price)}</div>
                    </div>
                    <div className="resource-quantity">
                      {tradeMode === 'buy' 
                        ? `Available: ${resource.quantity}`
                        : `You have: ${currentShip?.cargo?.[resourceType] || 0}`
                      }
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Trade Configuration */}
        {selectedResource && (
          <div className="trade-configuration">
            <h3>{tradeMode === 'buy' ? 'Buy' : 'Sell'} {selectedResource}</h3>
            
            <div className="quantity-selector">
              <label htmlFor="quantity">Quantity:</label>
              <div className="quantity-controls">
                <button 
                  onClick={() => setTradeQuantity(Math.max(1, tradeQuantity - 1))}
                  disabled={tradeQuantity <= 1}
                >
                  -
                </button>
                <input 
                  id="quantity"
                  type="number"
                  min="1"
                  max={getMaxQuantity()}
                  value={tradeQuantity}
                  onChange={(e) => setTradeQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                />
                <button 
                  onClick={() => setTradeQuantity(tradeQuantity + 1)}
                  disabled={tradeQuantity >= getMaxQuantity()}
                >
                  +
                </button>
                <button 
                  className="max-button"
                  onClick={setMaxQuantity}
                  disabled={getMaxQuantity() === 0}
                >
                  Max
                </button>
              </div>
            </div>

            {/* Trade Calculation */}
            {tradeCalculation && (
              <div className="trade-calculation">
                <div className="calculation-row">
                  <span>Unit Price:</span>
                  <span>{formatCredits(tradeCalculation.unitPrice)} credits</span>
                </div>
                <div className="calculation-row total">
                  <span>Total {tradeMode === 'buy' ? 'Cost' : 'Earnings'}:</span>
                  <span>{formatCredits(tradeCalculation.totalCost)} credits</span>
                </div>
                
                {tradeMode === 'buy' && (
                  <>
                    <div className={`calculation-row ${!tradeCalculation.isAffordable ? 'error' : ''}`}>
                      <span>Credits Available:</span>
                      <span>{formatCredits(playerState?.credits || 0)}</span>
                    </div>
                    <div className={`calculation-row ${!tradeCalculation.fitsInCargo ? 'error' : ''}`}>
                      <span>Cargo Space:</span>
                      <span>
                        {currentShip ? 
                          `${Object.values(currentShip.cargo || {}).reduce((a, b) => a + b, 0) + tradeQuantity}/${currentShip.cargo_capacity}` 
                          : 'No Ship'
                        }
                      </span>
                    </div>
                  </>
                )}
                
                <button 
                  className="execute-trade-button"
                  onClick={() => setShowConfirmDialog(true)}
                  disabled={!canExecuteTrade() || isLoading}
                >
                  {isLoading ? 'Processing...' : `${tradeMode === 'buy' ? 'Buy' : 'Sell'} ${selectedResource}`}
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Confirmation Dialog */}
      {showConfirmDialog && tradeCalculation && (
        <div className="modal-overlay">
          <div className="confirmation-dialog">
            <h3>Confirm Trade</h3>
            <div className="trade-summary">
              <p>
                {tradeMode === 'buy' ? 'Buy' : 'Sell'} {tradeCalculation.quantity} units of {tradeCalculation.resourceType}
              </p>
              <p>
                {tradeMode === 'buy' ? 'Total Cost' : 'Total Earnings'}: {formatCredits(tradeCalculation.totalCost)} credits
              </p>
              {tradeMode === 'buy' && (
                <p>Credits after trade: {formatCredits((playerState?.credits || 0) - tradeCalculation.totalCost)}</p>
              )}
            </div>
            <div className="dialog-buttons">
              <button onClick={() => setShowConfirmDialog(false)}>Cancel</button>
              <button 
                onClick={executeTrade}
                disabled={!canExecuteTrade() || isLoading}
                className="confirm-button"
              >
                {isLoading ? 'Processing...' : 'Confirm Trade'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TradingInterface;