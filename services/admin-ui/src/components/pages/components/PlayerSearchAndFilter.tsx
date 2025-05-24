import React, { useState, useCallback } from 'react';
import { PlayerFilters } from '../../../types/playerManagement';
import './PlayerSearchAndFilter.css';

interface PlayerSearchAndFilterProps {
  filters: PlayerFilters;
  onFiltersChange: (filters: PlayerFilters) => void;
  loading?: boolean;
}

const PlayerSearchAndFilter: React.FC<PlayerSearchAndFilterProps> = ({
  filters,
  onFiltersChange,
  loading = false
}) => {
  const [showAdvanced, setShowAdvanced] = useState(false);

  const updateFilter = useCallback((field: keyof PlayerFilters, value: any) => {
    onFiltersChange({
      ...filters,
      [field]: value
    });
  }, [filters, onFiltersChange]);

  const clearAllFilters = useCallback(() => {
    onFiltersChange({
      search: '',
      status: 'all',
      team: null,
      minCredits: null,
      maxCredits: null,
      lastLoginAfter: null,
      lastLoginBefore: null,
      reputationFilter: null,
      hasShips: null,
      hasPlanets: null,
      hasPorts: null,
      onlineOnly: false,
      suspiciousActivity: false
    });
  }, [onFiltersChange]);

  const hasActiveFilters = React.useMemo(() => {
    return filters.search !== '' ||
           filters.status !== 'all' ||
           filters.team !== null ||
           filters.minCredits !== null ||
           filters.maxCredits !== null ||
           filters.lastLoginAfter !== null ||
           filters.lastLoginBefore !== null ||
           filters.reputationFilter !== null ||
           filters.hasShips !== null ||
           filters.hasPlanets !== null ||
           filters.hasPorts !== null ||
           filters.onlineOnly ||
           filters.suspiciousActivity;
  }, [filters]);

  return (
    <div className="player-search-filter">
      {/* Basic Search and Filters */}
      <div className="basic-filters">
        <div className="search-group">
          <div className="search-input-wrapper">
            <input
              type="text"
              placeholder="Search players by username, email, or ID..."
              value={filters.search}
              onChange={(e) => updateFilter('search', e.target.value)}
              className="search-input"
              disabled={loading}
            />
            <div className="search-icon">🔍</div>
          </div>
        </div>

        <div className="filter-group">
          <select 
            value={filters.status} 
            onChange={(e) => updateFilter('status', e.target.value)}
            className="filter-select"
            disabled={loading}
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="banned">Banned</option>
          </select>

          <div className="quick-filters">
            <label className="quick-filter">
              <input
                type="checkbox"
                checked={filters.onlineOnly}
                onChange={(e) => updateFilter('onlineOnly', e.target.checked)}
                disabled={loading}
              />
              Online Only
            </label>
            
            <label className="quick-filter warning">
              <input
                type="checkbox"
                checked={filters.suspiciousActivity}
                onChange={(e) => updateFilter('suspiciousActivity', e.target.checked)}
                disabled={loading}
              />
              🚨 Suspicious Activity
            </label>
          </div>
        </div>

        <div className="filter-actions">
          <button 
            onClick={() => setShowAdvanced(!showAdvanced)}
            className={`advanced-toggle ${showAdvanced ? 'active' : ''}`}
            disabled={loading}
          >
            ⚙️ {showAdvanced ? 'Hide' : 'Show'} Advanced
          </button>
          
          {hasActiveFilters && (
            <button 
              onClick={clearAllFilters}
              className="clear-filters"
              disabled={loading}
            >
              ✖️ Clear All
            </button>
          )}
          
          {hasActiveFilters && (
            <div className="active-filters-indicator">
              <span className="filter-count">{Object.values(filters).filter(v => 
                v !== null && v !== '' && v !== 'all' && v !== false
              ).length} filters active</span>
            </div>
          )}
        </div>
      </div>

      {/* Advanced Filters */}
      {showAdvanced && (
        <div className="advanced-filters">
          <div className="advanced-section">
            <h4>Credit Range</h4>
            <div className="range-inputs">
              <input
                type="number"
                placeholder="Min credits"
                value={filters.minCredits || ''}
                onChange={(e) => updateFilter('minCredits', e.target.value ? parseInt(e.target.value) : null)}
                className="range-input"
                disabled={loading}
              />
              <span className="range-separator">to</span>
              <input
                type="number"
                placeholder="Max credits"
                value={filters.maxCredits || ''}
                onChange={(e) => updateFilter('maxCredits', e.target.value ? parseInt(e.target.value) : null)}
                className="range-input"
                disabled={loading}
              />
            </div>
          </div>

          <div className="advanced-section">
            <h4>Last Login Range</h4>
            <div className="date-inputs">
              <input
                type="date"
                value={filters.lastLoginAfter ? new Date(filters.lastLoginAfter).toISOString().split('T')[0] : ''}
                onChange={(e) => updateFilter('lastLoginAfter', e.target.value ? new Date(e.target.value) : null)}
                className="date-input"
                disabled={loading}
              />
              <span className="range-separator">to</span>
              <input
                type="date"
                value={filters.lastLoginBefore ? new Date(filters.lastLoginBefore).toISOString().split('T')[0] : ''}
                onChange={(e) => updateFilter('lastLoginBefore', e.target.value ? new Date(e.target.value) : null)}
                className="date-input"
                disabled={loading}
              />
            </div>
          </div>

          <div className="advanced-section">
            <h4>Asset Ownership</h4>
            <div className="asset-filters">
              <select 
                value={filters.hasShips === null ? 'any' : filters.hasShips ? 'yes' : 'no'} 
                onChange={(e) => updateFilter('hasShips', e.target.value === 'any' ? null : e.target.value === 'yes')}
                className="asset-select"
                disabled={loading}
              >
                <option value="any">Any Ships</option>
                <option value="yes">Has Ships</option>
                <option value="no">No Ships</option>
              </select>

              <select 
                value={filters.hasPlanets === null ? 'any' : filters.hasPlanets ? 'yes' : 'no'} 
                onChange={(e) => updateFilter('hasPlanets', e.target.value === 'any' ? null : e.target.value === 'yes')}
                className="asset-select"
                disabled={loading}
              >
                <option value="any">Any Planets</option>
                <option value="yes">Has Planets</option>
                <option value="no">No Planets</option>
              </select>

              <select 
                value={filters.hasPorts === null ? 'any' : filters.hasPorts ? 'yes' : 'no'} 
                onChange={(e) => updateFilter('hasPorts', e.target.value === 'any' ? null : e.target.value === 'yes')}
                className="asset-select"
                disabled={loading}
              >
                <option value="any">Any Ports</option>
                <option value="yes">Has Ports</option>
                <option value="no">No Ports</option>
              </select>
            </div>
          </div>

          <div className="advanced-section">
            <h4>Team Affiliation</h4>
            <div className="team-filter">
              <input
                type="text"
                placeholder="Team ID or name"
                value={filters.team || ''}
                onChange={(e) => updateFilter('team', e.target.value || null)}
                className="team-input"
                disabled={loading}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PlayerSearchAndFilter;