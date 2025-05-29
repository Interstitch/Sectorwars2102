import React, { useState, useEffect, useMemo } from 'react';
import { playerAPI } from '../../services/api';
import './leaderboards.css';

interface LeaderboardEntry {
  rank: number;
  playerId: string;
  username: string;
  avatar?: string;
  value: number;
  secondaryValue?: number;
  change: number; // Position change since last update
  trend: 'up' | 'down' | 'stable';
  isCurrentPlayer: boolean;
  teamId?: string;
  teamName?: string;
  additionalInfo?: Record<string, any>;
}

interface LeaderboardCategory {
  id: string;
  name: string;
  description: string;
  icon: string;
  unit: string;
  secondaryUnit?: string;
  refreshInterval: number;
  subcategories?: {
    id: string;
    name: string;
  }[];
}

interface LeaderboardData {
  category: string;
  subcategory?: string;
  timeRange: string;
  entries: LeaderboardEntry[];
  lastUpdated: string;
  totalPlayers: number;
  currentPlayerRank?: number;
}

interface LeaderboardFilter {
  friends: boolean;
  team: boolean;
  region: boolean;
}

const CATEGORIES: LeaderboardCategory[] = [
  {
    id: 'overall',
    name: 'Overall',
    description: 'Combined player ranking',
    icon: '👑',
    unit: 'points',
    refreshInterval: 300000,
  },
  {
    id: 'combat',
    name: 'Combat',
    description: 'Battle prowess rankings',
    icon: '⚔️',
    unit: 'victories',
    secondaryUnit: 'K/D ratio',
    refreshInterval: 60000,
    subcategories: [
      { id: 'pvp', name: 'PvP Kills' },
      { id: 'siege', name: 'Siege Victories' },
      { id: 'drone', name: 'Drone Efficiency' },
    ],
  },
  {
    id: 'trading',
    name: 'Trading',
    description: 'Economic mastery rankings',
    icon: '💰',
    unit: 'credits',
    secondaryUnit: 'profit/turn',
    refreshInterval: 120000,
    subcategories: [
      { id: 'profit', name: 'Total Profit' },
      { id: 'efficiency', name: 'Trade Efficiency' },
      { id: 'routes', name: 'Routes Discovered' },
    ],
  },
  {
    id: 'exploration',
    name: 'Exploration',
    description: 'Discovery achievements',
    icon: '🔭',
    unit: 'sectors',
    refreshInterval: 180000,
    subcategories: [
      { id: 'sectors', name: 'Sectors Visited' },
      { id: 'planets', name: 'Planets Discovered' },
      { id: 'wormholes', name: 'Wormholes Found' },
    ],
  },
  {
    id: 'colonization',
    name: 'Colonization',
    description: 'Empire building rankings',
    icon: '🏛️',
    unit: 'colonies',
    secondaryUnit: 'population',
    refreshInterval: 300000,
    subcategories: [
      { id: 'colonies', name: 'Total Colonies' },
      { id: 'population', name: 'Total Population' },
      { id: 'production', name: 'Production Output' },
    ],
  },
  {
    id: 'team',
    name: 'Team',
    description: 'Team performance rankings',
    icon: '🤝',
    unit: 'points',
    refreshInterval: 300000,
  },
];

export const Leaderboards: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState('overall');
  const [selectedSubcategory, setSelectedSubcategory] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState('all');
  const [leaderboardData, setLeaderboardData] = useState<LeaderboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<LeaderboardFilter>({
    friends: false,
    team: false,
    region: false,
  });
  const [searchQuery, setSearchQuery] = useState('');

  const currentCategory = useMemo(
    () => CATEGORIES.find(cat => cat.id === selectedCategory),
    [selectedCategory]
  );

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const params = {
          subcategory: selectedSubcategory,
          timeRange,
          filters,
        };
        
        const response = await playerAPI.getLeaderboards(selectedCategory, params);
        setLeaderboardData(response);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load leaderboard');
      } finally {
        setLoading(false);
      }
    };

    fetchLeaderboard();
    
    // Set up refresh interval based on category
    const interval = setInterval(
      fetchLeaderboard,
      currentCategory?.refreshInterval || 300000
    );
    
    return () => clearInterval(interval);
  }, [selectedCategory, selectedSubcategory, timeRange, filters, currentCategory]);

  const filteredEntries = useMemo(() => {
    if (!leaderboardData || !searchQuery) return leaderboardData?.entries || [];
    
    return leaderboardData.entries.filter(entry =>
      entry.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
      entry.teamName?.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [leaderboardData, searchQuery]);

  const renderTrendIndicator = (entry: LeaderboardEntry) => {
    if (entry.change === 0) return <span className="trend stable">-</span>;
    if (entry.change > 0) {
      return <span className="trend up">↑{entry.change}</span>;
    }
    return <span className="trend down">↓{Math.abs(entry.change)}</span>;
  };

  const renderLeaderboardEntry = (entry: LeaderboardEntry, index: number) => {
    const isTop3 = entry.rank <= 3;
    const rankEmoji = isTop3 ? ['🥇', '🥈', '🥉'][entry.rank - 1] : '';

    return (
      <div 
        key={entry.playerId}
        className={`leaderboard-entry ${entry.isCurrentPlayer ? 'current-player' : ''} ${isTop3 ? 'top-3' : ''}`}
      >
        <div className="rank-section">
          <span className="rank">{rankEmoji || `#${entry.rank}`}</span>
          {renderTrendIndicator(entry)}
        </div>
        
        <div className="player-info">
          {entry.avatar && (
            <img src={entry.avatar} alt={entry.username} className="player-avatar" />
          )}
          <div className="player-details">
            <span className="player-name">{entry.username}</span>
            {entry.teamName && (
              <span className="team-name">[{entry.teamName}]</span>
            )}
          </div>
        </div>
        
        <div className="score-section">
          <span className="primary-value">
            {entry.value.toLocaleString()} {currentCategory?.unit}
          </span>
          {entry.secondaryValue !== undefined && currentCategory?.secondaryUnit && (
            <span className="secondary-value">
              {entry.secondaryValue.toFixed(2)} {currentCategory.secondaryUnit}
            </span>
          )}
        </div>
      </div>
    );
  };

  if (loading && !leaderboardData) {
    return <div className="leaderboards loading">Loading leaderboard...</div>;
  }

  if (error) {
    return <div className="leaderboards error">Error: {error}</div>;
  }

  return (
    <div className="leaderboards">
      <div className="leaderboards-header">
        <h2>Leaderboards</h2>
        <div className="header-controls">
          <input
            type="text"
            placeholder="Search players..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(e.target.value)}
            className="time-range-selector"
          >
            <option value="daily">Today</option>
            <option value="weekly">This Week</option>
            <option value="monthly">This Month</option>
            <option value="all">All Time</option>
          </select>
        </div>
      </div>

      <div className="categories-bar">
        {CATEGORIES.map(category => (
          <button
            key={category.id}
            className={`category-btn ${selectedCategory === category.id ? 'active' : ''}`}
            onClick={() => {
              setSelectedCategory(category.id);
              setSelectedSubcategory(null);
            }}
          >
            <span className="category-icon">{category.icon}</span>
            <span className="category-name">{category.name}</span>
          </button>
        ))}
      </div>

      {currentCategory?.subcategories && (
        <div className="subcategories-bar">
          <button
            className={`subcategory-btn ${!selectedSubcategory ? 'active' : ''}`}
            onClick={() => setSelectedSubcategory(null)}
          >
            All
          </button>
          {currentCategory.subcategories.map(sub => (
            <button
              key={sub.id}
              className={`subcategory-btn ${selectedSubcategory === sub.id ? 'active' : ''}`}
              onClick={() => setSelectedSubcategory(sub.id)}
            >
              {sub.name}
            </button>
          ))}
        </div>
      )}

      <div className="filters-bar">
        <label className="filter-checkbox">
          <input
            type="checkbox"
            checked={filters.friends}
            onChange={(e) => setFilters({ ...filters, friends: e.target.checked })}
          />
          <span>Friends Only</span>
        </label>
        <label className="filter-checkbox">
          <input
            type="checkbox"
            checked={filters.team}
            onChange={(e) => setFilters({ ...filters, team: e.target.checked })}
          />
          <span>Team Only</span>
        </label>
        <label className="filter-checkbox">
          <input
            type="checkbox"
            checked={filters.region}
            onChange={(e) => setFilters({ ...filters, region: e.target.checked })}
          />
          <span>My Region</span>
        </label>
      </div>

      {leaderboardData && (
        <>
          <div className="leaderboard-info">
            <span className="total-players">
              {leaderboardData.totalPlayers.toLocaleString()} players ranked
            </span>
            {leaderboardData.currentPlayerRank && (
              <span className="current-rank">
                Your rank: #{leaderboardData.currentPlayerRank}
              </span>
            )}
            <span className="last-updated">
              Updated: {new Date(leaderboardData.lastUpdated).toLocaleTimeString()}
            </span>
          </div>

          <div className="leaderboard-list">
            {filteredEntries.length > 0 ? (
              filteredEntries.map((entry, index) => renderLeaderboardEntry(entry, index))
            ) : (
              <div className="empty-state">
                No players found matching your criteria.
              </div>
            )}
          </div>

          {leaderboardData.currentPlayerRank && leaderboardData.currentPlayerRank > 50 && (
            <div className="player-position-callout">
              <h3>Your Position</h3>
              {leaderboardData.entries
                .filter(e => e.isCurrentPlayer)
                .map((entry, index) => renderLeaderboardEntry(entry, index))}
            </div>
          )}
        </>
      )}
    </div>
  );
};