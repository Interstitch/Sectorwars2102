import React, { useState, useEffect } from 'react';
import PageHeader from '../ui/PageHeader';
import './colonization-overview.css';

interface ColonizationStats {
  total_planets: number;
  colonized_planets: number;
  uninhabited_planets: number;
  colonizing_planets: number;
  total_population: number;
  average_production: number;
}

const ColonizationOverview: React.FC = () => {
  const [stats, setStats] = useState<ColonizationStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchColonizationData();
  }, []);

  const fetchColonizationData = async () => {
    try {
      setLoading(true);
      // Simulated API calls - replace with actual endpoints
      
      const statsData = {
        total_planets: 150,
        colonized_planets: 89,
        uninhabited_planets: 45,
        colonizing_planets: 16,
        total_population: 125000000,
        average_production: 67.5
      };
      
      setStats(statsData);
    } catch (error) {
      console.error('Failed to fetch colonization data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="colonization-overview">
      <PageHeader 
        title="Colonization Overview" 
        subtitle="Monitor planetary colonization and production"
      />
      
      {loading ? (
        <div className="loading-spinner">Loading colonization data...</div>
      ) : (
        <>
          {/* Stats Grid */}
          <div className="stats-grid">
            {stats && (
              <>
                <div className="stat-card">
                  <h3>Total Planets</h3>
                  <span className="stat-value">{stats.total_planets}</span>
                  <span className="stat-label">In Galaxy</span>
                </div>
                <div className="stat-card">
                  <h3>Colonized</h3>
                  <span className="stat-value">{stats.colonized_planets}</span>
                  <span className="stat-label">Inhabited</span>
                </div>
                <div className="stat-card">
                  <h3>Population</h3>
                  <span className="stat-value">{(stats.total_population / 1000000).toFixed(1)}M</span>
                  <span className="stat-label">Total Citizens</span>
                </div>
                <div className="stat-card">
                  <h3>Avg Production</h3>
                  <span className="stat-value">{stats.average_production.toFixed(1)}%</span>
                  <span className="stat-label">Efficiency</span>
                </div>
              </>
            )}
          </div>

          <div className="feature-placeholder">
            <h3>🌍 Planet Management Interface</h3>
            <p>This component would include:</p>
            <ul>
              <li>Interactive galaxy map showing all planets</li>
              <li>Planet details with population, production, and resources</li>
              <li>Colonization progress tracking</li>
              <li>Genesis device usage monitoring</li>
              <li>Planetary defense management</li>
              <li>Production optimization tools</li>
            </ul>
          </div>
        </>
      )}
    </div>
  );
};

export default ColonizationOverview;