import React, { useState, useEffect, useCallback } from 'react';
import { rankingAPI } from '../../services/api';
import './ranking.css';

interface LeaderboardEntry {
  position: number;
  player_id: string;
  nickname: string;
  military_rank: string;
  score: number;
}

interface LeaderboardData {
  category: string;
  entries: LeaderboardEntry[];
  player_position: number | null;
  total_players: number;
}

type Category = 'rank_points' | 'combat' | 'trading' | 'exploration';

const CATEGORY_LABELS: Record<Category, { label: string; icon: string; scoreLabel: string }> = {
  rank_points: { label: 'Rank Points', icon: '\u2B50', scoreLabel: 'Points' },
  combat:      { label: 'Combat',      icon: '\u2694\uFE0F', scoreLabel: 'Victories' },
  trading:     { label: 'Trading',     icon: '\uD83D\uDCB0', scoreLabel: 'Volume' },
  exploration: { label: 'Exploration', icon: '\uD83C\uDF0C', scoreLabel: 'Activity' },
};

const CATEGORIES: Category[] = ['rank_points', 'combat', 'trading', 'exploration'];

interface LeaderboardProps {
  category?: Category;
}

const Leaderboard: React.FC<LeaderboardProps> = ({ category: initialCategory = 'rank_points' }) => {
  const [activeCategory, setActiveCategory] = useState<Category>(initialCategory);
  const [data, setData] = useState<LeaderboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const currentPlayerId = localStorage.getItem('playerId');

  const fetchLeaderboard = useCallback(async (cat: Category) => {
    try {
      setLoading(true);
      setError(null);
      const result = await rankingAPI.getPublicLeaderboard(cat, 20);
      setData(result);
    } catch (err: any) {
      setError(err.message || 'Failed to load leaderboard');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLeaderboard(activeCategory);
  }, [activeCategory, fetchLeaderboard]);

  const handleCategoryChange = (cat: Category) => {
    setActiveCategory(cat);
  };

  const meta = CATEGORY_LABELS[activeCategory];

  return (
    <div className="leaderboard">
      <div className="leaderboard-header">
        <h3>Leaderboard</h3>
        {data && <span className="leaderboard-total">{data.total_players} players</span>}
      </div>

      <div className="medal-categories">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            className={`medal-cat-btn ${activeCategory === cat ? 'active' : ''}`}
            onClick={() => handleCategoryChange(cat)}
          >
            {CATEGORY_LABELS[cat].icon} {CATEGORY_LABELS[cat].label}
          </button>
        ))}
      </div>

      {loading && (
        <div className="leaderboard-body leaderboard-loading">
          <div className="rank-spinner" />
          <span>Loading leaderboard...</span>
        </div>
      )}

      {error && (
        <div className="leaderboard-body leaderboard-error">
          <span>{error}</span>
        </div>
      )}

      {!loading && !error && data && (
        <>
          <table className="leaderboard-table">
            <thead>
              <tr>
                <th className="col-pos">#</th>
                <th className="col-name">Player</th>
                <th className="col-rank">Rank</th>
                <th className="col-score">{meta.scoreLabel}</th>
              </tr>
            </thead>
            <tbody>
              {data.entries.map((entry) => (
                <tr
                  key={entry.player_id}
                  className={entry.player_id === currentPlayerId ? 'current-player' : ''}
                >
                  <td className="col-pos">{entry.position}</td>
                  <td className="col-name">{entry.nickname}</td>
                  <td className="col-rank">{entry.military_rank}</td>
                  <td className="col-score">{entry.score.toLocaleString()}</td>
                </tr>
              ))}
              {data.entries.length === 0 && (
                <tr>
                  <td colSpan={4} className="leaderboard-empty">No entries yet</td>
                </tr>
              )}
            </tbody>
          </table>

          {data.player_position !== null && !data.entries.some((e) => e.player_id === currentPlayerId) && (
            <div className="leaderboard-your-rank">
              Your position: <strong>#{data.player_position}</strong> of {data.total_players}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default Leaderboard;
