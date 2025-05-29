import React, { useState, useEffect, useMemo } from 'react';
import { playerAPI } from '../../services/api';
import './progress-visualizer.css';

interface ProgressData {
  timeline: TimelineEntry[];
  milestones: Milestone[];
  trends: {
    category: string;
    data: TrendPoint[];
    improvement: number;
    projection: number;
  }[];
  comparisons: {
    metric: string;
    personal: number;
    average: number;
    top10: number;
    percentile: number;
  }[];
}

interface TimelineEntry {
  date: string;
  event: string;
  category: 'combat' | 'trading' | 'exploration' | 'social' | 'achievement';
  significance: 'minor' | 'moderate' | 'major' | 'legendary';
  details?: string;
}

interface Milestone {
  id: string;
  name: string;
  description: string;
  achieved: boolean;
  achievedDate?: string;
  nextTarget?: string;
  progress: number;
  icon: string;
}

interface TrendPoint {
  timestamp: string;
  value: number;
  label?: string;
}

export const ProgressVisualizer: React.FC = () => {
  const [progressData, setProgressData] = useState<ProgressData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [chartType, setChartType] = useState<'line' | 'bar' | 'radar'>('line');

  useEffect(() => {
    const fetchProgressData = async () => {
      try {
        setLoading(true);
        setError(null);
        const playerId = localStorage.getItem('playerId');
        if (!playerId) throw new Error('Player ID not found');
        
        const response = await playerAPI.getProgressData(playerId, selectedTimeRange);
        setProgressData(response);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load progress data');
      } finally {
        setLoading(false);
      }
    };

    fetchProgressData();
    const interval = setInterval(fetchProgressData, 60000); // Update every minute
    return () => clearInterval(interval);
  }, [selectedTimeRange]);

  const filteredTimeline = useMemo(() => {
    if (!progressData) return [];
    if (selectedCategory === 'all') return progressData.timeline;
    return progressData.timeline.filter(entry => entry.category === selectedCategory);
  }, [progressData, selectedCategory]);

  const significantMilestones = useMemo(() => {
    if (!progressData) return [];
    return progressData.milestones
      .filter(m => m.achieved || m.progress > 75)
      .sort((a, b) => b.progress - a.progress);
  }, [progressData]);

  const renderTrendChart = (trend: typeof progressData.trends[0]) => {
    const maxValue = Math.max(...trend.data.map(d => d.value));
    const minValue = Math.min(...trend.data.map(d => d.value));
    const range = maxValue - minValue || 1;

    return (
      <div className="trend-chart">
        <h4>{trend.category}</h4>
        <div className="chart-container">
          {chartType === 'line' && (
            <svg viewBox="0 0 400 200" className="line-chart">
              <polyline
                points={trend.data.map((point, index) => {
                  const x = (index / (trend.data.length - 1)) * 380 + 10;
                  const y = 190 - ((point.value - minValue) / range) * 180;
                  return `${x},${y}`;
                }).join(' ')}
                fill="none"
                stroke="var(--primary-color)"
                strokeWidth="2"
              />
              {trend.data.map((point, index) => {
                const x = (index / (trend.data.length - 1)) * 380 + 10;
                const y = 190 - ((point.value - minValue) / range) * 180;
                return (
                  <circle
                    key={index}
                    cx={x}
                    cy={y}
                    r="4"
                    fill="var(--primary-color)"
                    className="data-point"
                  >
                    <title>{`${point.timestamp}: ${point.value.toFixed(2)}`}</title>
                  </circle>
                );
              })}
            </svg>
          )}
          {chartType === 'bar' && (
            <div className="bar-chart">
              {trend.data.map((point, index) => (
                <div key={index} className="bar-container">
                  <div 
                    className="bar"
                    style={{ 
                      height: `${((point.value - minValue) / range) * 100}%`,
                      backgroundColor: 'var(--primary-color)'
                    }}
                  >
                    <span className="bar-label">{point.value.toFixed(0)}</span>
                  </div>
                  <span className="bar-time">{point.label || point.timestamp}</span>
                </div>
              ))}
            </div>
          )}
        </div>
        <div className="trend-stats">
          <span className={`improvement ${trend.improvement >= 0 ? 'positive' : 'negative'}`}>
            {trend.improvement >= 0 ? '↑' : '↓'} {Math.abs(trend.improvement).toFixed(1)}%
          </span>
          <span className="projection">
            Projected: {trend.projection.toFixed(0)}
          </span>
        </div>
      </div>
    );
  };

  if (loading) return <div className="progress-visualizer loading">Loading progress data...</div>;
  if (error) return <div className="progress-visualizer error">Error: {error}</div>;
  if (!progressData) return <div className="progress-visualizer empty">No progress data available</div>;

  return (
    <div className="progress-visualizer">
      <div className="visualizer-header">
        <h2>Progress Tracker</h2>
        <div className="controls">
          <select 
            value={selectedTimeRange} 
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            className="time-range-selector"
          >
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="all">All Time</option>
          </select>
          <select 
            value={chartType} 
            onChange={(e) => setChartType(e.target.value as typeof chartType)}
            className="chart-type-selector"
          >
            <option value="line">Line Chart</option>
            <option value="bar">Bar Chart</option>
            <option value="radar">Radar Chart</option>
          </select>
        </div>
      </div>

      <div className="timeline-section">
        <h3>Activity Timeline</h3>
        <div className="category-filter">
          <button 
            className={selectedCategory === 'all' ? 'active' : ''}
            onClick={() => setSelectedCategory('all')}
          >
            All
          </button>
          <button 
            className={selectedCategory === 'combat' ? 'active' : ''}
            onClick={() => setSelectedCategory('combat')}
          >
            Combat
          </button>
          <button 
            className={selectedCategory === 'trading' ? 'active' : ''}
            onClick={() => setSelectedCategory('trading')}
          >
            Trading
          </button>
          <button 
            className={selectedCategory === 'exploration' ? 'active' : ''}
            onClick={() => setSelectedCategory('exploration')}
          >
            Exploration
          </button>
          <button 
            className={selectedCategory === 'social' ? 'active' : ''}
            onClick={() => setSelectedCategory('social')}
          >
            Social
          </button>
        </div>
        <div className="timeline">
          {filteredTimeline.map((entry, index) => (
            <div key={index} className={`timeline-entry ${entry.significance}`}>
              <div className="timeline-date">{new Date(entry.date).toLocaleDateString()}</div>
              <div className={`timeline-content ${entry.category}`}>
                <span className="timeline-event">{entry.event}</span>
                {entry.details && <span className="timeline-details">{entry.details}</span>}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="milestones-section">
        <h3>Milestones & Progress</h3>
        <div className="milestones-grid">
          {significantMilestones.map(milestone => (
            <div key={milestone.id} className={`milestone ${milestone.achieved ? 'achieved' : 'in-progress'}`}>
              <div className="milestone-icon">{milestone.icon}</div>
              <div className="milestone-content">
                <h4>{milestone.name}</h4>
                <p>{milestone.description}</p>
                <div className="milestone-progress">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${milestone.progress}%` }}
                    />
                  </div>
                  <span className="progress-text">{milestone.progress}%</span>
                </div>
                {milestone.achievedDate && (
                  <span className="achieved-date">
                    Achieved: {new Date(milestone.achievedDate).toLocaleDateString()}
                  </span>
                )}
                {milestone.nextTarget && !milestone.achieved && (
                  <span className="next-target">Next: {milestone.nextTarget}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="trends-section">
        <h3>Performance Trends</h3>
        <div className="trends-grid">
          {progressData.trends.map((trend, index) => (
            <div key={index} className="trend-item">
              {renderTrendChart(trend)}
            </div>
          ))}
        </div>
      </div>

      <div className="comparisons-section">
        <h3>How You Compare</h3>
        <div className="comparisons-grid">
          {progressData.comparisons.map((comparison, index) => (
            <div key={index} className="comparison-item">
              <h4>{comparison.metric}</h4>
              <div className="comparison-bars">
                <div className="comparison-row">
                  <span className="label">You</span>
                  <div className="bar-wrapper">
                    <div 
                      className="comparison-bar personal"
                      style={{ width: `${(comparison.personal / comparison.top10) * 100}%` }}
                    />
                    <span className="value">{comparison.personal.toFixed(0)}</span>
                  </div>
                </div>
                <div className="comparison-row">
                  <span className="label">Average</span>
                  <div className="bar-wrapper">
                    <div 
                      className="comparison-bar average"
                      style={{ width: `${(comparison.average / comparison.top10) * 100}%` }}
                    />
                    <span className="value">{comparison.average.toFixed(0)}</span>
                  </div>
                </div>
                <div className="comparison-row">
                  <span className="label">Top 10%</span>
                  <div className="bar-wrapper">
                    <div 
                      className="comparison-bar top10"
                      style={{ width: '100%' }}
                    />
                    <span className="value">{comparison.top10.toFixed(0)}</span>
                  </div>
                </div>
              </div>
              <div className="percentile">
                Top {comparison.percentile.toFixed(0)}% of players
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};