import React from 'react';
import './planet-port-pair.css';

interface Planet {
  id: string;
  name: string;
  type: string;
  status: string;
  sector_id: number;
  owner_id?: string | null;
  owner_name?: string | null;
  population?: number;
  max_population?: number;
  habitability_score?: number;
}

interface Port {
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
}

interface PlanetPortPairProps {
  planet: Planet;
  port?: Port | null;
  onLandOnPlanet: (planetId: string) => void;
  onDockAtPort?: (portId: string) => void;
  isLanded?: boolean;
  isDocked?: boolean;
}

const PlanetPortPair: React.FC<PlanetPortPairProps> = ({
  planet,
  port,
  onLandOnPlanet,
  onDockAtPort,
  isLanded = false,
  isDocked = false
}) => {
  // Planet type icons
  const planetTypeIcons: { [key: string]: string } = {
    'terran': '🌍',
    'ice': '🧊',
    'volcanic': '🌋',
    'gas_giant': '🪐',
    'barren': '🌑',
    'oceanic': '🌊',
    'desert': '🏜️',
    'jungle': '🌴'
  };

  // Service icons
  const serviceIcons: { [key: string]: string } = {
    'fuel': '⛽',
    'repairs': '🔧',
    'trading': '💰',
    'shipyard': '🚀',
    'equipment': '⚙️',
    'information': '📡'
  };

  // Format population
  const formatPopulation = (pop: number | undefined) => {
    if (!pop) return '0';
    if (pop >= 1000000000) return `${(pop / 1000000000).toFixed(1)}B`;
    if (pop >= 1000000) return `${(pop / 1000000).toFixed(1)}M`;
    if (pop >= 1000) return `${(pop / 1000).toFixed(1)}K`;
    return pop.toString();
  };

  const planetIcon = planetTypeIcons[planet.type?.toLowerCase()] || '🌍';

  // Get available services
  const availableServices = port?.services
    ? Object.entries(port.services)
        .filter(([_, available]) => available)
        .map(([service, _]) => serviceIcons[service] || '•')
    : [];

  // Debug logging
  if (port) {
    console.log('PlanetPortPair - Port data:', {
      name: port.name,
      services: port.services,
      availableServices
    });
  }

  const handlePlanetClick = () => {
    if (isLanded) return;
    if (confirm(`Land on ${planet.name}?`)) {
      onLandOnPlanet(planet.id);
    }
  };

  const handlePortClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent planet click
    if (!port || !onDockAtPort || isDocked) return;
    if (confirm(`Dock at ${port.name}?`)) {
      onDockAtPort(port.id);
    }
  };

  const ownerDisplay = planet.owner_name || (planet.name === 'New Earth' ? 'Terran Federation' : null);

  return (
    <div className="planet-port-pair">
      {/* Planet Section - Clickable */}
      <div
        className={`planet-section ${!isLanded ? 'clickable' : 'landed'}`}
        onClick={handlePlanetClick}
      >
        <span className="planet-icon">{planetIcon}</span>
        <div className="planet-details">
          <div className="planet-name-line">
            <span className="planet-name">{planet.name}</span>
            {ownerDisplay && <span className="planet-owner">{ownerDisplay}</span>}
          </div>
          <div className="planet-stats">
            {planet.habitability_score !== undefined && (
              <span className="stat">🌡️ {planet.habitability_score}%</span>
            )}
            {planet.population !== undefined && (
              <span className="stat">👥 {formatPopulation(planet.population)}</span>
            )}
          </div>
        </div>
      </div>

      {/* Orbital Connector */}
      {port && <div className="orbital-connector">→</div>}

      {/* Port Section - Clickable if exists */}
      {port && (
        <div
          className={`port-section ${!isDocked && port.status.toLowerCase() === 'active' ? 'clickable' : 'inactive'}`}
          onClick={handlePortClick}
        >
          <span className="port-icon">🏢</span>
          <div className="port-details">
            <div className="port-name">{port.name}</div>
            <div className="port-services">
              {availableServices.length > 0 ? (
                availableServices.map((icon, i) => <span key={i}>{icon}</span>)
              ) : (
                <span className="no-services">Offline</span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PlanetPortPair;
