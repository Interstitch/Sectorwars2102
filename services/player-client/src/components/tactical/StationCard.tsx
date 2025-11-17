import React from 'react';
import './station-card.css';

interface StationCardProps {
  station: {
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

const StationCard: React.FC<StationCardProps> = ({ station, onDock, isDocked }) => {
  const handleClick = () => {
    if (isDocked) return;
    if (confirm(`Dock at ${station.name}?`)) {
      onDock(station.id);
    }
  };
  // Determine station status color and icon
  const getStationStatusInfo = (status: string) => {
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

  const statusInfo = getStationStatusInfo(station.status);
  const factionColor = getFactionColor(station.faction_affiliation);

  // Get available services
  const availableServices = station.services
    ? Object.entries(station.services)
        .filter(([_, available]) => available)
        .map(([service, _]) => service)
    : [];

  return (
    <div
      className={`station-card ${!isDocked && station.status.toLowerCase() === 'active' ? 'clickable' : ''}`}
      onClick={handleClick}
    >
      {/* Station Header */}
      <div className="station-card-header">
        <div className="station-icon">🏢</div>
        <div className="station-info">
          <div className="station-name">{station.name}</div>
          <div className="station-type-badge" style={{ borderColor: factionColor, color: factionColor }}>
            {station.type}
          </div>
        </div>
        <div className="station-status" style={{ color: statusInfo.color }}>
          <span className="status-icon">{statusInfo.icon}</span>
          <span className="status-label">{statusInfo.label}</span>
        </div>
      </div>

      {/* Station Body */}
      <div className="station-card-body">
        {/* Faction Affiliation */}
        {station.faction_affiliation && (
          <div className="station-faction">
            <span className="faction-icon" style={{ color: factionColor }}>⚑</span>
            <span className="faction-name">{station.faction_affiliation}</span>
          </div>
        )}

        {/* Services */}
        {availableServices.length > 0 && (
          <div className="station-services">
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
        {station.services?.trading && (
          <div className="station-market-preview">
            <div className="market-label">📊 Market Active</div>
            <div className="market-hint">Click to dock</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StationCard;
