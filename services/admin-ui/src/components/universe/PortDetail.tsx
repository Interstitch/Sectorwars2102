import React from 'react';
import './universe-detail.css';

interface PortDetailProps {
  port: any;
  onBack: () => void;
}

const PortDetail: React.FC<PortDetailProps> = ({ port, onBack }) => {
  const getPortClassInfo = (portClass: number) => {
    const classInfo: { [key: number]: { name: string; description: string; color: string } } = {
      1: { name: 'Small Outpost', description: 'Basic trading post with minimal services', color: '#888' },
      2: { name: 'Standard Port', description: 'Common trading hub with standard services', color: '#668' },
      3: { name: 'Major Port', description: 'Large trading center with full services', color: '#486' },
      4: { name: 'Regional Hub', description: 'Advanced facility with premium services', color: '#468' },
      5: { name: 'Federation HQ', description: 'Elite trading center with all services', color: '#846' }
    };
    return classInfo[portClass] || classInfo[1];
  };

  const commodities = port.commodities || {};
  const services = port.services || {};
  const classInfo = getPortClassInfo(port.port_class);

  return (
    <div className="port-detail">
      <div className="detail-header">
        <button className="back-button" onClick={onBack}>
          ← Back to Sector
        </button>
        <h2>🏪 {port.name}</h2>
        <div className="port-class" style={{ backgroundColor: classInfo.color }}>
          Class {port.port_class}: {classInfo.name}
        </div>
      </div>

      <div className="detail-content">
        <div className="port-overview">
          <h3>Port Overview</h3>
          <div className="info-grid">
            <div className="info-item">
              <span className="label">Owner:</span>
              <span className="value">{port.owner_name || 'Federation'}</span>
            </div>
            <div className="info-item">
              <span className="label">Tax Rate:</span>
              <span className="value">{port.tax_rate}%</span>
            </div>
            <div className="info-item">
              <span className="label">Defense Drones:</span>
              <span className="value">{port.defense_fighters}</span>
            </div>
            <div className="info-item">
              <span className="label">Purchase Price:</span>
              <span className="value">{(port.port_class * 250000).toLocaleString()} credits</span>
            </div>
          </div>
          <p className="port-description">{classInfo.description}</p>
        </div>

        <div className="commodities-section">
          <h3>Commodities Trading</h3>
          <div className="commodities-grid">
            {Object.entries(commodities).map(([commodity, data]: [string, any]) => (
              <div key={commodity} className="commodity-card">
                <h4>{commodity.charAt(0).toUpperCase() + commodity.slice(1).replace('_', ' ')}</h4>
                <div className="commodity-info">
                  <div className="quantity">
                    <span className="label">Quantity:</span>
                    <span className="value">{data.quantity.toLocaleString()}</span>
                  </div>
                  <div className="prices">
                    <div className="buy-price">
                      <span className="label">Buy:</span>
                      <span className="value">{data.buy_price} cr</span>
                    </div>
                    <div className="sell-price">
                      <span className="label">Sell:</span>
                      <span className="value">{data.sell_price} cr</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="services-section">
          <h3>Available Services</h3>
          <div className="services-grid">
            {Object.entries(services).map(([service, available]) => (
              <div key={service} className={`service-item ${available ? 'available' : 'unavailable'}`}>
                <span className="service-icon">{getServiceIcon(service)}</span>
                <span className="service-name">
                  {service.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                </span>
                <span className="service-status">{available ? '✓' : '✗'}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="trading-tips">
          <h3>Trading Tips</h3>
          <ul>
            <li>Ports buy commodities at lower prices and sell at higher prices</li>
            <li>Class {port.port_class} ports typically trade in {getPortTradingPattern(port.port_class)}</li>
            <li>Check neighboring sectors for complementary ports to maximize profits</li>
            <li>Higher class ports offer better services but charge higher fees</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

// Helper functions
const getServiceIcon = (service: string): string => {
  const icons: { [key: string]: string } = {
    ship_dealer: '🚀',
    ship_repair: '🔧',
    ship_maintenance: '🛠️',
    insurance: '🛡️',
    drone_shop: '🤖',
    genesis_dealer: '🌟',
    mine_dealer: '💣',
    diplomatic_services: '🤝'
  };
  return icons[service] || '📦';
};

const getPortTradingPattern = (portClass: number): string => {
  const patterns: { [key: number]: string } = {
    1: 'basic commodities with limited quantities',
    2: 'standard goods with moderate prices',
    3: 'diverse commodities with good availability',
    4: 'premium goods and specialized equipment',
    5: 'all commodities with best prices and quantities'
  };
  return patterns[portClass] || 'various commodities';
};

export default PortDetail;