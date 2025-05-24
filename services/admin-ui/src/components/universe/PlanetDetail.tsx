import React from 'react';
import './universe-detail.css';

interface PlanetDetailProps {
  planet: any;
  onBack: () => void;
}

const PlanetDetail: React.FC<PlanetDetailProps> = ({ planet, onBack }) => {
  const getPlanetTypeInfo = (type: string) => {
    const typeInfo: { [key: string]: { name: string; description: string; color: string; icon: string } } = {
      'TERRA': { 
        name: 'Terra', 
        description: 'Earth-like planet, optimal for all production', 
        color: '#4a7c59',
        icon: '🌍'
      },
      'M_CLASS': { 
        name: 'M-Class', 
        description: 'Standard habitable planet, good for organics', 
        color: '#6b8e23',
        icon: '🌏'
      },
      'L_CLASS': { 
        name: 'L-Class', 
        description: 'Rocky planet with thin atmosphere, good for ore', 
        color: '#8b7355',
        icon: '🪨'
      },
      'O_CLASS': { 
        name: 'O-Class', 
        description: 'Ocean planet, excellent for organics', 
        color: '#4682b4',
        icon: '🌊'
      },
      'K_CLASS': { 
        name: 'K-Class', 
        description: 'Desert/arid planet, moderate for ore', 
        color: '#daa520',
        icon: '🏜️'
      },
      'H_CLASS': { 
        name: 'H-Class', 
        description: 'Harsh environment, good for equipment', 
        color: '#cd5c5c',
        icon: '🌋'
      },
      'D_CLASS': { 
        name: 'D-Class', 
        description: 'Barren/dead world, minimal production', 
        color: '#696969',
        icon: '☄️'
      },
      'C_CLASS': { 
        name: 'C-Class', 
        description: 'Cold/ice planet, challenging colonization', 
        color: '#b0e0e6',
        icon: '❄️'
      }
    };
    return typeInfo[type] || typeInfo['TERRA'];
  };

  const typeInfo = getPlanetTypeInfo(planet.planet_type);
  const colonists = planet.colonists || { fuel: 0, organics: 0, equipment: 0 };
  const production = planet.production || { fuel: 0, organics: 0, equipment: 0 };
  const totalColonists = colonists.fuel + colonists.organics + colonists.equipment;

  return (
    <div className="planet-detail">
      <div className="detail-header">
        <button className="back-button" onClick={onBack}>
          ← Back to Sector
        </button>
        <h2>{typeInfo.icon} {planet.name}</h2>
        <div className="planet-type" style={{ backgroundColor: typeInfo.color }}>
          {typeInfo.name} Planet
        </div>
      </div>

      <div className="detail-content">
        <div className="planet-overview">
          <h3>Planet Overview</h3>
          <div className="info-grid">
            <div className="info-item">
              <span className="label">Owner:</span>
              <span className="value">{planet.owner_name || 'Uncolonized'}</span>
            </div>
            <div className="info-item">
              <span className="label">Total Colonists:</span>
              <span className="value">{totalColonists.toLocaleString()}</span>
            </div>
            <div className="info-item">
              <span className="label">Citadel Level:</span>
              <span className="value">{planet.citadel_level} / 5</span>
            </div>
            <div className="info-item">
              <span className="label">Shield Level:</span>
              <span className="value">{planet.shield_level} / 3</span>
            </div>
            <div className="info-item">
              <span className="label">Defense Fighters:</span>
              <span className="value">{planet.fighters || 0}</span>
            </div>
            <div className="info-item">
              <span className="label">Breeding Rate:</span>
              <span className="value">{planet.breeding_rate}% per day</span>
            </div>
          </div>
          <p className="planet-description">{typeInfo.description}</p>
        </div>

        <div className="colonist-section">
          <h3>Colonist Distribution</h3>
          <div className="colonist-grid">
            <div className="colonist-card fuel">
              <h4>⚡ Fuel Colonists</h4>
              <div className="colonist-info">
                <div className="count">{colonists.fuel.toLocaleString()}</div>
                <div className="capacity">Max: {(planet.colonistCapacity?.fuel || 5000).toLocaleString()}</div>
                <div className="percentage">
                  {Math.round((colonists.fuel / (planet.colonistCapacity?.fuel || 5000)) * 100)}% capacity
                </div>
              </div>
            </div>
            <div className="colonist-card organics">
              <h4>🌿 Organics Colonists</h4>
              <div className="colonist-info">
                <div className="count">{colonists.organics.toLocaleString()}</div>
                <div className="capacity">Max: {(planet.colonistCapacity?.organics || 5000).toLocaleString()}</div>
                <div className="percentage">
                  {Math.round((colonists.organics / (planet.colonistCapacity?.organics || 5000)) * 100)}% capacity
                </div>
              </div>
            </div>
            <div className="colonist-card equipment">
              <h4>⚙️ Equipment Colonists</h4>
              <div className="colonist-info">
                <div className="count">{colonists.equipment.toLocaleString()}</div>
                <div className="capacity">Max: {(planet.colonistCapacity?.equipment || 5000).toLocaleString()}</div>
                <div className="percentage">
                  {Math.round((colonists.equipment / (planet.colonistCapacity?.equipment || 5000)) * 100)}% capacity
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="production-section">
          <h3>Production Rates</h3>
          <div className="production-grid">
            <div className="production-item">
              <span className="resource-icon">⛏️</span>
              <span className="resource-name">Ore</span>
              <div className="production-bar">
                <div className="bar-fill" style={{ width: `${production.ore * 10}%` }}></div>
              </div>
              <span className="production-value">{production.ore}/10</span>
            </div>
            <div className="production-item">
              <span className="resource-icon">🌾</span>
              <span className="resource-name">Organics</span>
              <div className="production-bar">
                <div className="bar-fill" style={{ width: `${production.organics * 10}%` }}></div>
              </div>
              <span className="production-value">{production.organics}/10</span>
            </div>
            <div className="production-item">
              <span className="resource-icon">🔧</span>
              <span className="resource-name">Equipment</span>
              <div className="production-bar">
                <div className="bar-fill" style={{ width: `${production.equipment * 10}%` }}></div>
              </div>
              <span className="production-value">{production.equipment}/10</span>
            </div>
          </div>
        </div>

        <div className="planet-defenses">
          <h3>Planetary Defenses</h3>
          <div className="defense-grid">
            <div className="defense-item">
              <div className="defense-icon">🏰</div>
              <div className="defense-info">
                <h4>Citadel</h4>
                <p>Level {planet.citadel_level}</p>
                <p className="defense-desc">
                  {getCitadelDescription(planet.citadel_level)}
                </p>
              </div>
            </div>
            <div className="defense-item">
              <div className="defense-icon">🛡️</div>
              <div className="defense-info">
                <h4>Shields</h4>
                <p>Level {planet.shield_level}</p>
                <p className="defense-desc">
                  {getShieldDescription(planet.shield_level)}
                </p>
              </div>
            </div>
            <div className="defense-item">
              <div className="defense-icon">🤖</div>
              <div className="defense-info">
                <h4>Fighters</h4>
                <p>{planet.fighters || 0} deployed</p>
                <p className="defense-desc">
                  Automated defense drones protect the planet
                </p>
              </div>
            </div>
          </div>
        </div>

        {!planet.owner_id && (
          <div className="colonization-info">
            <h3>Colonization Requirements</h3>
            <ul>
              <li>Transport colonists from Terra (Sol System)</li>
              <li>Minimum 50 colonists of any type to establish colony</li>
              <li>Different planet types have varying production capabilities</li>
              <li>Build citadels and shields to protect your investment</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

// Helper functions
const getCitadelDescription = (level: number): string => {
  const descriptions = [
    'No citadel - planet is undefended',
    'Basic fortification provides minimal defense',
    'Standard citadel with improved defensive capabilities',
    'Advanced citadel with strong defensive systems',
    'Fortress citadel with powerful defensive arrays',
    'Maximum citadel - nearly impregnable defenses'
  ];
  return descriptions[level] || descriptions[0];
};

const getShieldDescription = (level: number): string => {
  const descriptions = [
    'No shields - vulnerable to all attacks',
    'Basic shields provide 33% damage reduction',
    'Improved shields provide 66% damage reduction',
    'Maximum shields provide 99% damage reduction'
  ];
  return descriptions[level] || descriptions[0];
};

export default PlanetDetail;