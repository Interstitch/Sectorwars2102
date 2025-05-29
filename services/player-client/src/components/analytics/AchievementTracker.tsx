import React, { useState, useEffect, useMemo } from 'react';
import { gameAPI } from '../../services/api';
import './achievement-tracker.css';

interface Achievement {
  id: string;
  name: string;
  description: string;
  category: 'combat' | 'trading' | 'exploration' | 'social' | 'special';
  tier: 'bronze' | 'silver' | 'gold' | 'platinum' | 'legendary';
  icon: string;
  progress: number;
  maxProgress: number;
  completed: boolean;
  completedAt?: string;
  rewards: {
    credits?: number;
    experience?: number;
    title?: string;
    badge?: string;
    special?: string;
  };
  secret?: boolean;
}

interface AchievementCategory {
  name: string;
  icon: string;
  color: string;
  totalAchievements: number;
  completedAchievements: number;
  totalPoints: number;
  earnedPoints: number;
}

interface AchievementStats {
  totalAchievements: number;
  completedAchievements: number;
  completionRate: number;
  totalPoints: number;
  earnedPoints: number;
  recentAchievements: Achievement[];
  rareAchievements: Achievement[];
  nearCompletion: Achievement[];
}

interface AchievementTrackerProps {
  playerId: string;
  onAchievementSelect?: (achievement: Achievement) => void;
}

const AchievementTracker: React.FC<AchievementTrackerProps> = ({
  playerId,
  onAchievementSelect
}) => {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [filterMode, setFilterMode] = useState<'all' | 'completed' | 'in-progress' | 'locked'>('all');
  const [sortBy, setSortBy] = useState<'name' | 'progress' | 'tier' | 'recent'>('progress');
  const [showSecret, setShowSecret] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch achievements data
  useEffect(() => {
    const fetchAchievements = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        const response = await gameAPI.player.getAchievements(playerId);
        setAchievements(response.achievements || []);
      } catch (err) {
        setError('Failed to load achievements. Please try again.');
        console.error('Achievements fetch error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAchievements();
  }, [playerId]);

  // Calculate achievement statistics
  const stats: AchievementStats = useMemo(() => {
    const completed = achievements.filter(a => a.completed);
    const totalPoints = achievements.reduce((sum, a) => sum + (a.maxProgress || 0), 0);
    const earnedPoints = achievements.reduce((sum, a) => sum + (a.progress || 0), 0);
    
    const recent = completed
      .filter(a => a.completedAt)
      .sort((a, b) => new Date(b.completedAt!).getTime() - new Date(a.completedAt!).getTime())
      .slice(0, 5);
    
    const rare = completed
      .filter(a => a.tier === 'legendary' || a.tier === 'platinum')
      .slice(0, 5);
    
    const nearCompletion = achievements
      .filter(a => !a.completed && a.progress / a.maxProgress >= 0.8)
      .sort((a, b) => (b.progress / b.maxProgress) - (a.progress / a.maxProgress))
      .slice(0, 5);
    
    return {
      totalAchievements: achievements.length,
      completedAchievements: completed.length,
      completionRate: achievements.length > 0 ? (completed.length / achievements.length) * 100 : 0,
      totalPoints,
      earnedPoints,
      recentAchievements: recent,
      rareAchievements: rare,
      nearCompletion
    };
  }, [achievements]);

  // Group achievements by category
  const categories: AchievementCategory[] = useMemo(() => {
    const categoryMap: Record<string, AchievementCategory> = {
      all: {
        name: 'All',
        icon: '🏆',
        color: '#4a9eff',
        totalAchievements: achievements.length,
        completedAchievements: achievements.filter(a => a.completed).length,
        totalPoints: stats.totalPoints,
        earnedPoints: stats.earnedPoints
      }
    };

    const categoryInfo = {
      combat: { name: 'Combat', icon: '⚔️', color: '#ff4444' },
      trading: { name: 'Trading', icon: '💰', color: '#44ff44' },
      exploration: { name: 'Exploration', icon: '🌍', color: '#4a9eff' },
      social: { name: 'Social', icon: '👥', color: '#ffaa44' },
      special: { name: 'Special', icon: '✨', color: '#ff44ff' }
    };

    achievements.forEach(achievement => {
      if (!categoryMap[achievement.category]) {
        categoryMap[achievement.category] = {
          ...categoryInfo[achievement.category],
          totalAchievements: 0,
          completedAchievements: 0,
          totalPoints: 0,
          earnedPoints: 0
        };
      }
      
      categoryMap[achievement.category].totalAchievements++;
      if (achievement.completed) {
        categoryMap[achievement.category].completedAchievements++;
      }
      categoryMap[achievement.category].totalPoints += achievement.maxProgress;
      categoryMap[achievement.category].earnedPoints += achievement.progress;
    });

    return Object.values(categoryMap);
  }, [achievements, stats]);

  // Filter and sort achievements
  const filteredAchievements = useMemo(() => {
    let filtered = [...achievements];

    // Category filter
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(a => a.category === selectedCategory);
    }

    // Completion filter
    switch (filterMode) {
      case 'completed':
        filtered = filtered.filter(a => a.completed);
        break;
      case 'in-progress':
        filtered = filtered.filter(a => !a.completed && a.progress > 0);
        break;
      case 'locked':
        filtered = filtered.filter(a => !a.completed && a.progress === 0);
        break;
    }

    // Secret filter
    if (!showSecret) {
      filtered = filtered.filter(a => !a.secret || a.completed);
    }

    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'progress':
          return (b.progress / b.maxProgress) - (a.progress / a.maxProgress);
        case 'tier':
          const tierOrder = { legendary: 5, platinum: 4, gold: 3, silver: 2, bronze: 1 };
          return tierOrder[b.tier] - tierOrder[a.tier];
        case 'recent':
          if (a.completedAt && b.completedAt) {
            return new Date(b.completedAt).getTime() - new Date(a.completedAt).getTime();
          }
          return a.completed ? -1 : 1;
        default:
          return 0;
      }
    });

    return filtered;
  }, [achievements, selectedCategory, filterMode, sortBy, showSecret]);

  const getTierColor = (tier: Achievement['tier']) => {
    switch (tier) {
      case 'bronze': return '#cd7f32';
      case 'silver': return '#c0c0c0';
      case 'gold': return '#ffd700';
      case 'platinum': return '#e5e4e2';
      case 'legendary': return '#ff44ff';
      default: return '#888';
    }
  };

  const formatReward = (rewards: Achievement['rewards']) => {
    const parts = [];
    if (rewards.credits) parts.push(`${rewards.credits.toLocaleString()} cr`);
    if (rewards.experience) parts.push(`${rewards.experience} XP`);
    if (rewards.title) parts.push(`Title: "${rewards.title}"`);
    if (rewards.badge) parts.push(`Badge: ${rewards.badge}`);
    if (rewards.special) parts.push(rewards.special);
    return parts.join(' • ');
  };

  if (isLoading) {
    return (
      <div className="achievement-tracker loading">
        <div className="loading-spinner">Loading achievements...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="achievement-tracker error">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  return (
    <div className="achievement-tracker">
      <div className="tracker-header">
        <h3>Achievements</h3>
        <div className="achievement-summary">
          <div className="summary-stat">
            <span className="stat-value">{stats.completedAchievements}/{stats.totalAchievements}</span>
            <span className="stat-label">Completed</span>
          </div>
          <div className="summary-stat">
            <span className="stat-value">{stats.completionRate.toFixed(0)}%</span>
            <span className="stat-label">Progress</span>
          </div>
          <div className="summary-stat">
            <span className="stat-value">{stats.earnedPoints.toLocaleString()}</span>
            <span className="stat-label">Points</span>
          </div>
        </div>
      </div>

      <div className="category-selector">
        {categories.map(category => (
          <button
            key={category.name}
            className={`category-btn ${selectedCategory === (category.name === 'All' ? 'all' : category.name.toLowerCase()) ? 'active' : ''}`}
            onClick={() => setSelectedCategory(category.name === 'All' ? 'all' : category.name.toLowerCase())}
            style={{ borderColor: category.color }}
          >
            <span className="category-icon">{category.icon}</span>
            <span className="category-name">{category.name}</span>
            <span className="category-progress">
              {category.completedAchievements}/{category.totalAchievements}
            </span>
          </button>
        ))}
      </div>

      <div className="tracker-controls">
        <div className="filter-controls">
          {(['all', 'completed', 'in-progress', 'locked'] as const).map(mode => (
            <button
              key={mode}
              className={`filter-btn ${filterMode === mode ? 'active' : ''}`}
              onClick={() => setFilterMode(mode)}
            >
              {mode.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
            </button>
          ))}
        </div>

        <div className="sort-controls">
          <select 
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
            className="sort-select"
          >
            <option value="progress">Sort by Progress</option>
            <option value="name">Sort by Name</option>
            <option value="tier">Sort by Tier</option>
            <option value="recent">Sort by Recent</option>
          </select>
          
          <label className="secret-toggle">
            <input
              type="checkbox"
              checked={showSecret}
              onChange={(e) => setShowSecret(e.target.checked)}
            />
            Show Secret
          </label>
        </div>
      </div>

      <div className="achievements-highlights">
        {stats.nearCompletion.length > 0 && (
          <div className="highlight-section">
            <h4>🔥 Almost There!</h4>
            <div className="highlight-list">
              {stats.nearCompletion.map(achievement => (
                <div key={achievement.id} className="highlight-item">
                  <span className="achievement-icon">{achievement.icon}</span>
                  <span className="achievement-name">{achievement.name}</span>
                  <span className="achievement-progress">
                    {Math.floor((achievement.progress / achievement.maxProgress) * 100)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {stats.recentAchievements.length > 0 && (
          <div className="highlight-section">
            <h4>🎉 Recently Earned</h4>
            <div className="highlight-list">
              {stats.recentAchievements.map(achievement => (
                <div key={achievement.id} className="highlight-item">
                  <span className="achievement-icon">{achievement.icon}</span>
                  <span className="achievement-name">{achievement.name}</span>
                  <span className="achievement-date">
                    {new Date(achievement.completedAt!).toLocaleDateString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="achievements-grid">
        {filteredAchievements.map(achievement => (
          <div 
            key={achievement.id}
            className={`achievement-card ${achievement.completed ? 'completed' : ''} ${achievement.secret && !achievement.completed ? 'secret' : ''}`}
            onClick={() => onAchievementSelect?.(achievement)}
          >
            <div 
              className="achievement-tier"
              style={{ backgroundColor: getTierColor(achievement.tier) }}
            >
              {achievement.tier.toUpperCase()}
            </div>

            <div className="achievement-icon">{achievement.icon}</div>
            
            <div className="achievement-info">
              <h4>{achievement.secret && !achievement.completed ? '???' : achievement.name}</h4>
              <p>{achievement.secret && !achievement.completed ? 'Hidden achievement' : achievement.description}</p>
              
              {!achievement.completed && (
                <div className="achievement-progress">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill"
                      style={{ width: `${(achievement.progress / achievement.maxProgress) * 100}%` }}
                    />
                  </div>
                  <span className="progress-text">
                    {achievement.progress}/{achievement.maxProgress}
                  </span>
                </div>
              )}
              
              {achievement.completed && achievement.completedAt && (
                <div className="completion-date">
                  ✅ {new Date(achievement.completedAt).toLocaleDateString()}
                </div>
              )}
              
              {(achievement.completed || !achievement.secret) && achievement.rewards && (
                <div className="achievement-rewards">
                  <span className="rewards-label">Rewards:</span>
                  <span className="rewards-text">{formatReward(achievement.rewards)}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {filteredAchievements.length === 0 && (
        <div className="no-achievements">
          No achievements found matching your filters.
        </div>
      )}
    </div>
  );
};

export default AchievementTracker;