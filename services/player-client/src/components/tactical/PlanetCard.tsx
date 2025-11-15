import React from 'react';
import './planet-card.css';

interface PlanetCardProps {
  planet: {
    id: string;
    name: string;
    type: string;
    status: string;
    sector_id: number;
    owner_id?: string | null;
    resources?: {
      [key: string]: any;
    };
    population?: number;
    max_population?: number;
    habitability_score?: number;
  };
}

const PlanetCard: React.FC<PlanetCardProps> = ({ planet }) => {
  // Planet type configurations
  const planetTypeInfo: {
    [key: string]: { icon: string; color: string; climate: string };
  } = {
    'terran': { icon: '🌍', color: '#00ff41', climate: 'Earth-like' },
    'ice': { icon: '🧊', color: '#00d9ff', climate: 'Frozen' },
    'volcanic': { icon: '🌋', color: '#ff6b00', climate: 'Volcanic' },
    'gas_giant': { icon: '🪐', color: '#c961de', climate: 'Gas Giant' },
    'barren': { icon: '🌑', color: '#8b4513', climate: 'Barren' },
    'oceanic': { icon: '🌊', color: '#0088ff', climate: 'Oceanic' },
    'desert': { icon: '🏜️', color: '#ffb000', climate: 'Desert' },
    'jungle': { icon: '🌴', color: '#22c55e', climate: 'Jungle' }
  };

  // Resource icons
  const resourceIcons: { [key: string]: string } = {
    'ore': '⛏️',
    'fuel': '⛽',
    'organics': '🌱',
    'equipment': '⚙️',
    'water': '💧',
    'minerals': '💎',
    'energy': '⚡',
    'exotic': '✨'
  };

  const typeInfo = planetTypeInfo[planet.type?.toLowerCase()] || planetTypeInfo['barren'];

  // Calculate population percentage
  const populationPercent = planet.max_population
    ? ((planet.population || 0) / planet.max_population) * 100
    : 0;

  // Format population for display
  const formatPopulation = (pop: number | undefined) => {
    if (!pop) return '0';
    if (pop >= 1000000000) return `${(pop / 1000000000).toFixed(1)}B`;
    if (pop >= 1000000) return `${(pop / 1000000).toFixed(1)}M`;
    if (pop >= 1000) return `${(pop / 1000).toFixed(1)}K`;
    return pop.toString();
  };

  // Get habitability level
  const getHabitabilityLevel = (score: number | undefined) => {
    if (!score) return { label: 'Uninhabitable', color: '#6b7280' };
    if (score >= 80) return { label: 'Excellent', color: '#00ff41' };
    if (score >= 60) return { label: 'Good', color: '#00d9ff' };
    if (score >= 40) return { label: 'Fair', color: '#ffb000' };
    if (score >= 20) return { label: 'Poor', color: '#ff6b00' };
    return { label: 'Harsh', color: '#ef4444' };
  };

  const habitability = getHabitabilityLevel(planet.habitability_score);

  // Get available resources
  const availableResources = planet.resources
    ? Object.entries(planet.resources)
        .filter(([_, value]) => value && (typeof value === 'boolean' || value > 0))
        .map(([resource, _]) => resource)
    : [];

  return (
    <div className="planet-card">
      {/* Planet Header */}
      <div className="planet-card-header">
        <div className="planet-icon" style={{ filter: `drop-shadow(0 0 12px ${typeInfo.color})` }}>
          {typeInfo.icon}
        </div>
        <div className="planet-info">
          <div className="planet-name">{planet.name}</div>
          <div className="planet-climate-badge" style={{ borderColor: typeInfo.color, color: typeInfo.color }}>
            {typeInfo.climate}
          </div>
        </div>
        <div className="planet-status">
          {planet.owner_id ? (
            <span className="status-owned">👤 Owned</span>
          ) : (
            <span className="status-unclaimed">○ Unclaimed</span>
          )}
        </div>
      </div>

      {/* Planet Body */}
      <div className="planet-card-body">
        {/* Habitability */}
        {planet.habitability_score !== undefined && (
          <div className="planet-habitability">
            <div className="habitability-header">
              <span className="habitability-label">Habitability</span>
              <span className="habitability-value" style={{ color: habitability.color }}>
                {habitability.label}
              </span>
            </div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{
                  width: `${planet.habitability_score}%`,
                  background: `linear-gradient(90deg, ${habitability.color} 0%, ${typeInfo.color} 100%)`
                }}
              ></div>
            </div>
            <div className="habitability-score">{planet.habitability_score}%</div>
          </div>
        )}

        {/* Population */}
        {planet.population !== undefined && planet.max_population !== undefined && (
          <div className="planet-population">
            <div className="population-header">
              <span className="population-icon">👥</span>
              <span className="population-label">Population</span>
            </div>
            <div className="population-bar-container">
              <div className="progress-bar">
                <div
                  className="progress-fill population-fill"
                  style={{ width: `${populationPercent}%` }}
                ></div>
              </div>
              <div className="population-stats">
                {formatPopulation(planet.population)} / {formatPopulation(planet.max_population)}
              </div>
            </div>
          </div>
        )}

        {/* Resources */}
        {availableResources.length > 0 && (
          <div className="planet-resources">
            <div className="resources-label">📦 Available Resources:</div>
            <div className="resources-grid">
              {availableResources.map(resource => (
                <div key={resource} className="resource-item" title={resource}>
                  <span className="resource-icon">{resourceIcons[resource] || '•'}</span>
                  <span className="resource-name">{resource}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Planet Status */}
        {planet.status && planet.status !== 'normal' && (
          <div className="planet-status-info">
            <span className="status-icon">⚠️</span>
            <span className="status-text">{planet.status}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default PlanetCard;
