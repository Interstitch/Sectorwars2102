import React from 'react';
import './port-card.css';

interface StationCardProps {
  port: {
    id: string;
    name: string;
    type: string;
    status: string;
    owner_id?: string | null;
    faction_affiliation?: string | null;
    services?: {
      fuel?: boolean;
      repairs?: boolean;
      trading?: boolean;
      shipyard?: boolean;
      equipment?: boolean;
      information?: boolean;
    };
  };
  onDock: (stationId: string) => void;
  isDocked: boolean;
}

const StationCard: React.FC<StationCardProps> = ({ port, onDock, isDocked }) => {
  const handleClick = () => {
    if (isDocked) return;
    if (confirm(`Dock at ${port.name}?`)) {
      onDock(port.id);
    }
  };
  // Determine port status color and icon
  const getPortStatusInfo = (status: string) => {
    const statusMap: { [key: string]: { color: string; icon: string; label: string } } = {
      'active': { color: '#00ff41', icon: '✓', label: 'ACTIVE' },
      'damaged': { color: '#ffb000', icon: '⚠', label: 'DAMAGED' },
      'destroyed': { color: '#ef4444', icon: '✗', label: 'DESTROYED' },
      'offline': { color: '#6b7280', icon: '○', label: 'OFFLINE' }
    };
    return statusMap[status.toLowerCase()] || statusMap['active'];
  };

  // Get faction badge color
  const getFactionColor = (faction?: string | null) => {
    if (!faction) return '#00d9ff';
    const factionColors: { [key: string]: string } = {
      'federation': '#00d9ff',
      'empire': '#c961de',
      'republic': '#00ff41',
      'syndicate': '#ffb000',
      'independent': '#8b5cf6'
    };
    return factionColors[faction.toLowerCase()] || '#00d9ff';
  };

  // Map service types to icons
  const serviceIcons: { [key: string]: string } = {
    'fuel': '⛽',
    'repairs': '🔧',
    'trading': '💰',
    'shipyard': '🚀',
    'equipment': '⚙️',
    'information': '📡'
  };

  const statusInfo = getPortStatusInfo(port.status);
  const factionColor = getFactionColor(port.faction_affiliation);

  // Get available services
  const availableServices = port.services
    ? Object.entries(port.services)
        .filter(([_, available]) => available)
        .map(([service, _]) => service)
    : [];

  return (
    <div
      className={`port-card ${!isDocked && port.status.toLowerCase() === 'active' ? 'clickable' : ''}`}
      onClick={handleClick}
    >
      {/* Port Header */}
      <div className="port-card-header">
        <div className="port-icon">🏢</div>
        <div className="port-info">
          <div className="port-name">{port.name}</div>
          <div className="port-type-badge" style={{ borderColor: factionColor, color: factionColor }}>
            {port.type}
          </div>
        </div>
        <div className="port-status" style={{ color: statusInfo.color }}>
          <span className="status-icon">{statusInfo.icon}</span>
          <span className="status-label">{statusInfo.label}</span>
        </div>
      </div>

      {/* Port Body */}
      <div className="port-card-body">
        {/* Faction Affiliation */}
        {port.faction_affiliation && (
          <div className="port-faction">
            <span className="faction-icon" style={{ color: factionColor }}>⚑</span>
            <span className="faction-name">{port.faction_affiliation}</span>
          </div>
        )}

        {/* Services */}
        {availableServices.length > 0 && (
          <div className="port-services">
            <div className="services-label">Available Services:</div>
            <div className="services-grid">
              {availableServices.map(service => (
                <div key={service} className="service-item" title={service}>
                  <span className="service-icon">{serviceIcons[service] || '•'}</span>
                  <span className="service-name">{service}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Market Preview (placeholder for future enhancement) */}
        {port.services?.trading && (
          <div className="port-market-preview">
            <div className="market-label">📊 Market Active</div>
            <div className="market-hint">Click to dock</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StationCard;
