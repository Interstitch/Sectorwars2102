import React, { useState } from 'react';
import './intervention-panel.css';

interface Commodity {
  name: string;
  buyPrice: number;
  sellPrice: number;
  supply: number;
  demand: number;
}

interface MarketData {
  portId: string;
  portName: string;
  sectorId: string;
  commodities: Commodity[];
}

interface InterventionPanelProps {
  onClose: () => void;
  onIntervene: (type: string, commodity: string, value: number) => void;
  marketData: MarketData[];
}

const InterventionPanel: React.FC<InterventionPanelProps> = ({ onClose, onIntervene, marketData }) => {
  const [interventionType, setInterventionType] = useState<'price_cap' | 'price_floor' | 'supply_injection'>('price_cap');
  const [selectedCommodity, setSelectedCommodity] = useState('Fuel');
  const [value, setValue] = useState(100);
  const [duration, setDuration] = useState(24);

  const commodities = ['Fuel', 'Minerals', 'Food', 'Electronics', 'Weapons', 'Medical'];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onIntervene(interventionType, selectedCommodity, value);
    onClose();
  };

  // Calculate current market stats for selected commodity
  const getMarketStats = () => {
    const prices = marketData.flatMap(port => 
      port.commodities
        .filter(c => c.name === selectedCommodity)
        .map(c => c.buyPrice)
    );
    
    if (prices.length === 0) return { avg: 0, min: 0, max: 0 };
    
    return {
      avg: Math.round(prices.reduce((a, b) => a + b, 0) / prices.length),
      min: Math.min(...prices),
      max: Math.max(...prices)
    };
  };

  const stats = getMarketStats();

  return (
    <div className="intervention-panel-overlay">
      <div className="intervention-panel">
        <div className="panel-header">
          <h2>Market Intervention</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="intervention-form">
          <div className="form-group">
            <label>Intervention Type</label>
            <div className="radio-group">
              <label className="radio-option">
                <input
                  type="radio"
                  value="price_cap"
                  checked={interventionType === 'price_cap'}
                  onChange={(e) => setInterventionType(e.target.value as any)}
                />
                <span>Price Cap</span>
                <small>Set maximum price for commodity</small>
              </label>
              <label className="radio-option">
                <input
                  type="radio"
                  value="price_floor"
                  checked={interventionType === 'price_floor'}
                  onChange={(e) => setInterventionType(e.target.value as any)}
                />
                <span>Price Floor</span>
                <small>Set minimum price for commodity</small>
              </label>
              <label className="radio-option">
                <input
                  type="radio"
                  value="supply_injection"
                  checked={interventionType === 'supply_injection'}
                  onChange={(e) => setInterventionType(e.target.value as any)}
                />
                <span>Supply Injection</span>
                <small>Add supply to stabilize market</small>
              </label>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="commodity">Commodity</label>
            <select
              id="commodity"
              value={selectedCommodity}
              onChange={(e) => setSelectedCommodity(e.target.value)}
              className="form-control"
            >
              {commodities.map(commodity => (
                <option key={commodity} value={commodity}>{commodity}</option>
              ))}
            </select>
          </div>

          <div className="market-info">
            <h4>Current Market Status: {selectedCommodity}</h4>
            <div className="stats-grid">
              <div className="stat">
                <label>Average Price</label>
                <span>{stats.avg} CR</span>
              </div>
              <div className="stat">
                <label>Min Price</label>
                <span>{stats.min} CR</span>
              </div>
              <div className="stat">
                <label>Max Price</label>
                <span>{stats.max} CR</span>
              </div>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="value">
              {interventionType === 'supply_injection' ? 'Supply Amount' : 'Price Value (Credits)'}
            </label>
            <input
              id="value"
              type="number"
              value={value}
              onChange={(e) => setValue(Number(e.target.value))}
              min={interventionType === 'supply_injection' ? 100 : 1}
              max={interventionType === 'supply_injection' ? 10000 : 1000}
              className="form-control"
            />
            {interventionType !== 'supply_injection' && (
              <small className="form-hint">
                Suggested range: {Math.round(stats.min * 0.8)} - {Math.round(stats.max * 1.2)} CR
              </small>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="duration">Duration (hours)</label>
            <input
              id="duration"
              type="number"
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
              min={1}
              max={168}
              className="form-control"
            />
            <small className="form-hint">How long the intervention should last (1-168 hours)</small>
          </div>

          <div className="impact-preview">
            <h4>Estimated Impact</h4>
            <ul>
              <li>Affected ports: {marketData.length}</li>
              <li>
                Price change: 
                {interventionType === 'price_cap' && value < stats.avg && ` -${Math.round((stats.avg - value) / stats.avg * 100)}%`}
                {interventionType === 'price_floor' && value > stats.avg && ` +${Math.round((value - stats.avg) / stats.avg * 100)}%`}
                {interventionType === 'supply_injection' && ' Market stabilization expected'}
              </li>
              <li>Market stability: +{Math.floor(Math.random() * 5) + 3}%</li>
            </ul>
          </div>

          <div className="form-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Execute Intervention
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default InterventionPanel;