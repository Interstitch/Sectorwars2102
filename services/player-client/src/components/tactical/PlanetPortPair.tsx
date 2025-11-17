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

interface Station {
  id: string;
  name: string;
  port_class?: number;  // Station class 0-11 (from specification)
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
  station?: Station | null;
  onLandOnPlanet: (planetId: string) => void;
  onDockAtStation?: (stationId: string) => void;
  isLanded?: boolean;
  isDocked?: boolean;
}

const PlanetPortPair: React.FC<PlanetPortPairProps> = ({
  planet,
  station,
  onLandOnPlanet,
  onDockAtStation,
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

  // Station class names (from specification)
  const portClassNames: { [key: number]: string } = {
    0: 'Sol System',
    1: 'Mining Operation',
    2: 'Agricultural Center',
    3: 'Industrial Hub',
    4: 'Distribution Center',
    5: 'Collection Hub',
    6: 'Mixed Market',
    7: 'Resource Exchange',
    8: 'Black Hole',
    9: 'Nova',
    10: 'Luxury Market',
    11: 'Advanced Tech Hub'
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

  // Get station owner display name
  const stationOwnerDisplay = station?.owner_name || (station?.faction_affiliation ? `${station.faction_affiliation} Faction` : null);

  const handlePlanetClick = () => {
    if (isLanded) return;
    if (confirm(`Land on ${planet.name}?`)) {
      onLandOnPlanet(planet.id);
    }
  };

  const handleStationClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent planet click
    if (!station || !onDockAtStation || isDocked) return;
    if (confirm(`Dock at ${station.name}?`)) {
      onDockAtStation(station.id);
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
      {station && <div className="orbital-connector">→</div>}

      {/* Station Section - Clickable if exists */}
      {station && (
        <div
          className={`station-section ${!isDocked && station.status.toLowerCase() === 'operational' ? 'clickable' : 'inactive'}`}
          onClick={handleStationClick}
        >
          <span className="station-icon">🛰️</span>
          <div className="station-details">
            <div className="station-name-line">
              <div className="station-name-status">
                <span className="station-name">{station.name}</span>
                <span className="station-status">
                  {station.status.toLowerCase() === 'operational' ? '🟢' : '🔴'}
                </span>
              </div>
              {stationOwnerDisplay && <span className="station-owner">{stationOwnerDisplay}</span>}
              {station.port_class !== undefined && (
                <span className="station-class">Class {station.port_class}: {portClassNames[station.port_class] || 'Unknown'}</span>
              )}
              <span className="station-type">{station.type.replace(/_/g, ' ')}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PlanetPortPair;
