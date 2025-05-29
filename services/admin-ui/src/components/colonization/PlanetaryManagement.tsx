import React, { useState, useEffect } from 'react';
import { Bar, Radar } from 'react-chartjs-2';
import { useAuth } from '../../contexts/AuthContext';
import './planetary-management.css';

interface Planet {
  id: string;
  name: string;
  sectorId: string;
  sectorName: string;
  type: 'Terran' | 'Desert' | 'Ice' | 'Gas Giant' | 'Volcanic' | 'Ocean';
  size: 'Small' | 'Medium' | 'Large' | 'Massive';
  atmosphere: 'None' | 'Toxic' | 'Thin' | 'Breathable' | 'Dense';
  temperature: number; // in Celsius
  gravity: number; // relative to Earth (1.0)
  resources: {
    energy: number;
    minerals: number;
    water: number;
    rareMaterials: number;
  };
  habitability: number; // 0-100
  population: number;
  maxPopulation: number;
  colonies: number;
  infrastructure: {
    spaceports: number;
    defenses: number;
    factories: number;
    research: number;
  };
  ownership: {
    playerId?: string;
    playerName?: string;
    teamId?: string;
    teamName?: string;
    contested: boolean;
  };
  discovered: boolean;
  colonizable: boolean;
  hasGenesisDevice: boolean;
}

interface PlanetStats {
  totalPlanets: number;
  discoveredPlanets: number;
  colonizedPlanets: number;
  contestedPlanets: number;
  totalPopulation: number;
  averageHabitability: number;
  resourceDistribution: {
    energy: number;
    minerals: number;
    water: number;
    rareMaterials: number;
  };
}

interface TerraformingProject {
  id: string;
  planetId: string;
  planetName: string;
  type: 'atmosphere' | 'temperature' | 'water' | 'soil';
  progress: number;
  duration: number; // in hours
  cost: {
    energy: number;
    minerals: number;
  };
  impact: {
    habitability: number;
    resourceBonus: string;
  };
}

export const PlanetaryManagement: React.FC = () => {
  const { user } = useAuth();
  const [planets, setPlanets] = useState<Planet[]>([]);
  const [stats, setStats] = useState<PlanetStats | null>(null);
  const [terraformingProjects, setTerraformingProjects] = useState<TerraformingProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPlanet, setSelectedPlanet] = useState<Planet | null>(null);
  const [filterType, setFilterType] = useState<string>('all');
  const [filterOwnership, setFilterOwnership] = useState<string>('all');
  const [showOnlyColonizable, setShowOnlyColonizable] = useState(false);
  const [sortBy, setSortBy] = useState<string>('habitability');

  useEffect(() => {
    loadPlanetaryData();
    const interval = setInterval(loadPlanetaryData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const loadPlanetaryData = async () => {
    try {
      const response = await fetch('/api/admin/planets', {
        headers: {
          'Authorization': `Bearer ${user?.token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load planetary data');
      }

      const data = await response.json();
      setPlanets(data.planets);
      setStats(data.stats);
      setTerraformingProjects(data.terraformingProjects);
    } catch (err) {
      console.error('Error loading planetary data:', err);
      // Use mock data for development
      generateMockData();
    } finally {
      setLoading(false);
    }
  };

  const generateMockData = () => {
    const types: Planet['type'][] = ['Terran', 'Desert', 'Ice', 'Gas Giant', 'Volcanic', 'Ocean'];
    const sizes: Planet['size'][] = ['Small', 'Medium', 'Large', 'Massive'];
    const atmospheres: Planet['atmosphere'][] = ['None', 'Toxic', 'Thin', 'Breathable', 'Dense'];
    
    const mockPlanets: Planet[] = [];
    for (let i = 1; i <= 100; i++) {
      const type = types[Math.floor(Math.random() * types.length)];
      const isColonized = Math.random() > 0.6;
      const isDiscovered = isColonized || Math.random() > 0.3;
      
      mockPlanets.push({
        id: `planet-${i}`,
        name: `Planet ${i}`,
        sectorId: `sector-${Math.floor(Math.random() * 20) + 1}`,
        sectorName: `Sector ${Math.floor(Math.random() * 20) + 1}`,
        type,
        size: sizes[Math.floor(Math.random() * sizes.length)],
        atmosphere: atmospheres[Math.floor(Math.random() * atmospheres.length)],
        temperature: Math.floor(Math.random() * 200) - 100,
        gravity: Math.random() * 2 + 0.1,
        resources: {
          energy: Math.floor(Math.random() * 100),
          minerals: Math.floor(Math.random() * 100),
          water: Math.floor(Math.random() * 100),
          rareMaterials: Math.floor(Math.random() * 50),
        },
        habitability: type === 'Terran' ? Math.floor(Math.random() * 40) + 60 :
          type === 'Gas Giant' ? 0 : Math.floor(Math.random() * 80),
        population: isColonized ? Math.floor(Math.random() * 10000000) : 0,
        maxPopulation: Math.floor(Math.random() * 50000000) + 1000000,
        colonies: isColonized ? Math.floor(Math.random() * 10) + 1 : 0,
        infrastructure: {
          spaceports: isColonized ? Math.floor(Math.random() * 5) : 0,
          defenses: isColonized ? Math.floor(Math.random() * 10) : 0,
          factories: isColonized ? Math.floor(Math.random() * 20) : 0,
          research: isColonized ? Math.floor(Math.random() * 5) : 0,
        },
        ownership: isColonized ? {
          playerId: `player-${Math.floor(Math.random() * 50) + 1}`,
          playerName: `Player ${Math.floor(Math.random() * 50) + 1}`,
          teamId: Math.random() > 0.3 ? `team-${Math.floor(Math.random() * 10) + 1}` : undefined,
          teamName: Math.random() > 0.3 ? `Team ${Math.floor(Math.random() * 10) + 1}` : undefined,
          contested: Math.random() > 0.9,
        } : {
          contested: false,
        },
        discovered: isDiscovered,
        colonizable: type !== 'Gas Giant' && !isColonized,
        hasGenesisDevice: Math.random() > 0.95,
      });
    }
    setPlanets(mockPlanets);

    // Calculate stats
    const discovered = mockPlanets.filter(p => p.discovered);
    const colonized = mockPlanets.filter(p => p.colonies > 0);
    const contested = mockPlanets.filter(p => p.ownership.contested);
    
    setStats({
      totalPlanets: mockPlanets.length,
      discoveredPlanets: discovered.length,
      colonizedPlanets: colonized.length,
      contestedPlanets: contested.length,
      totalPopulation: colonized.reduce((sum, p) => sum + p.population, 0),
      averageHabitability: discovered.reduce((sum, p) => sum + p.habitability, 0) / discovered.length,
      resourceDistribution: {
        energy: mockPlanets.reduce((sum, p) => sum + p.resources.energy, 0),
        minerals: mockPlanets.reduce((sum, p) => sum + p.resources.minerals, 0),
        water: mockPlanets.reduce((sum, p) => sum + p.resources.water, 0),
        rareMaterials: mockPlanets.reduce((sum, p) => sum + p.resources.rareMaterials, 0),
      },
    });

    // Generate terraforming projects
    const projects: TerraformingProject[] = [];
    const projectTypes: TerraformingProject['type'][] = ['atmosphere', 'temperature', 'water', 'soil'];
    
    for (let i = 0; i < 10; i++) {
      const planet = colonized[Math.floor(Math.random() * colonized.length)];
      if (planet) {
        projects.push({
          id: `project-${i}`,
          planetId: planet.id,
          planetName: planet.name,
          type: projectTypes[Math.floor(Math.random() * projectTypes.length)],
          progress: Math.floor(Math.random() * 100),
          duration: Math.floor(Math.random() * 720) + 24,
          cost: {
            energy: Math.floor(Math.random() * 10000) + 1000,
            minerals: Math.floor(Math.random() * 5000) + 500,
          },
          impact: {
            habitability: Math.floor(Math.random() * 20) + 5,
            resourceBonus: ['energy', 'minerals', 'water'][Math.floor(Math.random() * 3)],
          },
        });
      }
    }
    setTerraformingProjects(projects);
  };

  const filteredPlanets = planets.filter(planet => {
    if (!planet.discovered) return false;
    
    const matchesType = filterType === 'all' || planet.type === filterType;
    const matchesOwnership = filterOwnership === 'all' ||
      (filterOwnership === 'colonized' && planet.colonies > 0) ||
      (filterOwnership === 'uncolonized' && planet.colonies === 0) ||
      (filterOwnership === 'contested' && planet.ownership.contested);
    const matchesColonizable = !showOnlyColonizable || planet.colonizable;
    
    return matchesType && matchesOwnership && matchesColonizable;
  });

  const sortedPlanets = [...filteredPlanets].sort((a, b) => {
    switch (sortBy) {
      case 'habitability':
        return b.habitability - a.habitability;
      case 'population':
        return b.population - a.population;
      case 'resources':
        const aTotal = a.resources.energy + a.resources.minerals + a.resources.water + a.resources.rareMaterials;
        const bTotal = b.resources.energy + b.resources.minerals + b.resources.water + b.resources.rareMaterials;
        return bTotal - aTotal;
      case 'name':
        return a.name.localeCompare(b.name);
      default:
        return 0;
    }
  });

  const getResourceChartData = () => {
    if (!stats) return { labels: [], datasets: [] };

    return {
      labels: ['Energy', 'Minerals', 'Water', 'Rare Materials'],
      datasets: [{
        label: 'Total Resources',
        data: [
          stats.resourceDistribution.energy,
          stats.resourceDistribution.minerals,
          stats.resourceDistribution.water,
          stats.resourceDistribution.rareMaterials,
        ],
        backgroundColor: [
          'rgba(255, 206, 86, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(153, 102, 255, 0.8)',
        ],
        borderWidth: 0,
      }],
    };
  };

  const getPlanetRadarData = (planet: Planet) => {
    return {
      labels: ['Habitability', 'Energy', 'Minerals', 'Water', 'Infrastructure', 'Defense'],
      datasets: [{
        label: planet.name,
        data: [
          planet.habitability,
          planet.resources.energy,
          planet.resources.minerals,
          planet.resources.water,
          (planet.infrastructure.spaceports + planet.infrastructure.factories + planet.infrastructure.research) * 5,
          planet.infrastructure.defenses * 10,
        ],
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 2,
      }],
    };
  };

  const getTypeIcon = (type: Planet['type']) => {
    switch (type) {
      case 'Terran': return '🌍';
      case 'Desert': return '🏜️';
      case 'Ice': return '❄️';
      case 'Gas Giant': return '🌀';
      case 'Volcanic': return '🌋';
      case 'Ocean': return '🌊';
      default: return '🪐';
    }
  };

  const getAtmosphereColor = (atmosphere: Planet['atmosphere']) => {
    switch (atmosphere) {
      case 'Breathable': return 'var(--success-color)';
      case 'Thin': return 'var(--warning-color)';
      case 'Dense': return 'var(--info-color)';
      case 'Toxic': return 'var(--error-color)';
      case 'None': return 'var(--text-secondary)';
      default: return 'var(--text-primary)';
    }
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(num);
  };

  if (loading) {
    return <div className="planetary-management loading">Loading planetary data...</div>;
  }

  return (
    <div className="planetary-management">
      <div className="management-header">
        <h2>Planetary Management</h2>
        <div className="header-stats">
          <div className="stat-card">
            <span className="stat-label">Total Planets</span>
            <span className="stat-value">{stats?.totalPlanets || 0}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Discovered</span>
            <span className="stat-value">{stats?.discoveredPlanets || 0}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Colonized</span>
            <span className="stat-value success">{stats?.colonizedPlanets || 0}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Contested</span>
            <span className="stat-value error">{stats?.contestedPlanets || 0}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Avg Habitability</span>
            <span className="stat-value">{Math.round(stats?.averageHabitability || 0)}%</span>
          </div>
        </div>
      </div>

      <div className="management-controls">
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="filter-select"
        >
          <option value="all">All Types</option>
          <option value="Terran">Terran</option>
          <option value="Desert">Desert</option>
          <option value="Ice">Ice</option>
          <option value="Gas Giant">Gas Giant</option>
          <option value="Volcanic">Volcanic</option>
          <option value="Ocean">Ocean</option>
        </select>
        <select
          value={filterOwnership}
          onChange={(e) => setFilterOwnership(e.target.value)}
          className="filter-select"
        >
          <option value="all">All Planets</option>
          <option value="colonized">Colonized</option>
          <option value="uncolonized">Uncolonized</option>
          <option value="contested">Contested</option>
        </select>
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="sort-select"
        >
          <option value="habitability">Sort by Habitability</option>
          <option value="population">Sort by Population</option>
          <option value="resources">Sort by Resources</option>
          <option value="name">Sort by Name</option>
        </select>
        <label className="colonizable-toggle">
          <input
            type="checkbox"
            checked={showOnlyColonizable}
            onChange={(e) => setShowOnlyColonizable(e.target.checked)}
          />
          Show only colonizable
        </label>
      </div>

      <div className="management-content">
        <div className="planets-section">
          <div className="planets-grid">
            {sortedPlanets.map(planet => (
              <div
                key={planet.id}
                className={`planet-card ${planet.ownership.contested ? 'contested' : ''}`}
                onClick={() => setSelectedPlanet(planet)}
              >
                <div className="planet-header">
                  <span className="planet-icon">{getTypeIcon(planet.type)}</span>
                  <div className="planet-title">
                    <h4>{planet.name}</h4>
                    <span className="planet-sector">{planet.sectorName}</span>
                  </div>
                  {planet.hasGenesisDevice && <span className="genesis-indicator">🧬</span>}
                </div>
                
                <div className="planet-stats">
                  <div className="stat-row">
                    <span>Type:</span>
                    <span>{planet.type}</span>
                  </div>
                  <div className="stat-row">
                    <span>Size:</span>
                    <span>{planet.size}</span>
                  </div>
                  <div className="stat-row">
                    <span>Atmosphere:</span>
                    <span style={{ color: getAtmosphereColor(planet.atmosphere) }}>
                      {planet.atmosphere}
                    </span>
                  </div>
                  <div className="stat-row">
                    <span>Habitability:</span>
                    <span className={planet.habitability > 60 ? 'good' : planet.habitability > 30 ? 'medium' : 'poor'}>
                      {planet.habitability}%
                    </span>
                  </div>
                  {planet.colonies > 0 && (
                    <>
                      <div className="stat-row">
                        <span>Population:</span>
                        <span>{formatNumber(planet.population)}</span>
                      </div>
                      <div className="stat-row">
                        <span>Owner:</span>
                        <span>{planet.ownership.playerName || 'Unowned'}</span>
                      </div>
                    </>
                  )}
                </div>

                <div className="planet-resources">
                  <div className="resource" title="Energy">
                    <span className="resource-icon">⚡</span>
                    <span className="resource-value">{planet.resources.energy}</span>
                  </div>
                  <div className="resource" title="Minerals">
                    <span className="resource-icon">💎</span>
                    <span className="resource-value">{planet.resources.minerals}</span>
                  </div>
                  <div className="resource" title="Water">
                    <span className="resource-icon">💧</span>
                    <span className="resource-value">{planet.resources.water}</span>
                  </div>
                  <div className="resource" title="Rare Materials">
                    <span className="resource-icon">✨</span>
                    <span className="resource-value">{planet.resources.rareMaterials}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="sidebar">
          <div className="resource-chart">
            <h3>Resource Distribution</h3>
            <Bar
              data={getResourceChartData()}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    display: false,
                  },
                },
              }}
            />
          </div>

          <div className="terraforming-section">
            <h3>Active Terraforming Projects</h3>
            <div className="projects-list">
              {terraformingProjects.map(project => (
                <div key={project.id} className="project-card">
                  <div className="project-header">
                    <span className="project-planet">{project.planetName}</span>
                    <span className="project-type">{project.type}</span>
                  </div>
                  <div className="project-progress">
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{ width: `${project.progress}%` }}
                      />
                    </div>
                    <span className="progress-text">{project.progress}%</span>
                  </div>
                  <div className="project-details">
                    <span>+{project.impact.habitability}% Habitability</span>
                    <span>{Math.round(project.duration * (100 - project.progress) / 100)}h remaining</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {selectedPlanet && (
        <div className="planet-detail-modal" onClick={() => setSelectedPlanet(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>{selectedPlanet.name} Details</h2>
            <button className="close-button" onClick={() => setSelectedPlanet(null)}>×</button>
            
            <div className="detail-grid">
              <div className="detail-section">
                <h3>Physical Properties</h3>
                <div className="properties-grid">
                  <div className="property">
                    <span className="property-label">Temperature</span>
                    <span className="property-value">{selectedPlanet.temperature}°C</span>
                  </div>
                  <div className="property">
                    <span className="property-label">Gravity</span>
                    <span className="property-value">{selectedPlanet.gravity.toFixed(2)}g</span>
                  </div>
                  <div className="property">
                    <span className="property-label">Max Population</span>
                    <span className="property-value">{formatNumber(selectedPlanet.maxPopulation)}</span>
                  </div>
                  <div className="property">
                    <span className="property-label">Colonies</span>
                    <span className="property-value">{selectedPlanet.colonies}</span>
                  </div>
                </div>
              </div>

              <div className="detail-section">
                <h3>Infrastructure</h3>
                <div className="infrastructure-grid">
                  <div className="infrastructure-item">
                    <span className="infra-icon">🚀</span>
                    <span className="infra-count">{selectedPlanet.infrastructure.spaceports}</span>
                    <span className="infra-label">Spaceports</span>
                  </div>
                  <div className="infrastructure-item">
                    <span className="infra-icon">🛡️</span>
                    <span className="infra-count">{selectedPlanet.infrastructure.defenses}</span>
                    <span className="infra-label">Defenses</span>
                  </div>
                  <div className="infrastructure-item">
                    <span className="infra-icon">🏭</span>
                    <span className="infra-count">{selectedPlanet.infrastructure.factories}</span>
                    <span className="infra-label">Factories</span>
                  </div>
                  <div className="infrastructure-item">
                    <span className="infra-icon">🔬</span>
                    <span className="infra-count">{selectedPlanet.infrastructure.research}</span>
                    <span className="infra-label">Research</span>
                  </div>
                </div>
              </div>

              <div className="detail-section radar-section">
                <h3>Planet Overview</h3>
                <Radar
                  data={getPlanetRadarData(selectedPlanet)}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        display: false,
                      },
                    },
                    scales: {
                      r: {
                        beginAtZero: true,
                        max: 100,
                      },
                    },
                  }}
                />
              </div>

              <div className="detail-section">
                <h3>Actions</h3>
                <div className="action-buttons">
                  <button className="action-button primary">View Colonies</button>
                  <button className="action-button">Monitor Resources</button>
                  {selectedPlanet.colonizable && (
                    <button className="action-button success">Mark for Colonization</button>
                  )}
                  {selectedPlanet.ownership.contested && (
                    <button className="action-button error">Resolve Conflict</button>
                  )}
                  <button className="action-button warning">Start Terraforming</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};