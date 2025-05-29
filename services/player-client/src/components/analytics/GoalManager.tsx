import React, { useState, useEffect, useMemo } from 'react';
import { playerAPI } from '../../services/api';
import './goal-manager.css';

interface Goal {
  id: string;
  title: string;
  description: string;
  category: 'combat' | 'trading' | 'exploration' | 'social' | 'personal';
  type: 'daily' | 'weekly' | 'monthly' | 'custom';
  status: 'active' | 'completed' | 'failed' | 'paused';
  priority: 'low' | 'medium' | 'high' | 'critical';
  progress: number;
  target: number;
  unit: string;
  deadline: string;
  rewards: {
    credits?: number;
    experience?: number;
    achievement?: string;
    customReward?: string;
  };
  milestones: {
    threshold: number;
    description: string;
    completed: boolean;
  }[];
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
}

interface GoalTemplate {
  id: string;
  title: string;
  description: string;
  category: Goal['category'];
  suggestedTarget: number;
  unit: string;
  difficulty: 'easy' | 'medium' | 'hard' | 'extreme';
  estimatedTime: string;
  tips: string[];
}

interface GoalStats {
  totalGoals: number;
  completedGoals: number;
  failedGoals: number;
  successRate: number;
  currentStreak: number;
  bestStreak: number;
  averageCompletionTime: number;
  categoryBreakdown: Record<Goal['category'], number>;
}

export const GoalManager: React.FC = () => {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [templates, setTemplates] = useState<GoalTemplate[]>([]);
  const [stats, setStats] = useState<GoalStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<Goal['category'] | 'all'>('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingGoal, setEditingGoal] = useState<Goal | null>(null);

  useEffect(() => {
    const fetchGoalsData = async () => {
      try {
        setLoading(true);
        setError(null);
        const playerId = localStorage.getItem('playerId');
        if (!playerId) throw new Error('Player ID not found');
        
        const [goalsResponse, templatesResponse] = await Promise.all([
          playerAPI.getGoals(playerId),
          playerAPI.getGoalTemplates()
        ]);
        
        setGoals(goalsResponse.goals);
        setStats(goalsResponse.stats);
        setTemplates(templatesResponse);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load goals');
      } finally {
        setLoading(false);
      }
    };

    fetchGoalsData();
    const interval = setInterval(fetchGoalsData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const filteredGoals = useMemo(() => {
    if (selectedCategory === 'all') return goals;
    return goals.filter(goal => goal.category === selectedCategory);
  }, [goals, selectedCategory]);

  const activeGoals = useMemo(() => {
    return filteredGoals.filter(g => g.status === 'active');
  }, [filteredGoals]);

  const completedGoals = useMemo(() => {
    return filteredGoals.filter(g => g.status === 'completed');
  }, [filteredGoals]);

  const handleCreateGoal = async (goalData: Partial<Goal>) => {
    try {
      const playerId = localStorage.getItem('playerId');
      if (!playerId) throw new Error('Player ID not found');
      
      const newGoal = await playerAPI.createGoal(playerId, goalData);
      setGoals([...goals, newGoal]);
      setShowCreateModal(false);
    } catch (err) {
      console.error('Failed to create goal:', err);
    }
  };

  const handleUpdateGoal = async (goalId: string, updates: Partial<Goal>) => {
    try {
      const playerId = localStorage.getItem('playerId');
      if (!playerId) throw new Error('Player ID not found');
      
      const updatedGoal = await playerAPI.updateGoal(playerId, goalId, updates);
      setGoals(goals.map(g => g.id === goalId ? updatedGoal : g));
      setEditingGoal(null);
    } catch (err) {
      console.error('Failed to update goal:', err);
    }
  };

  const handleDeleteGoal = async (goalId: string) => {
    try {
      const playerId = localStorage.getItem('playerId');
      if (!playerId) throw new Error('Player ID not found');
      
      await playerAPI.deleteGoal(playerId, goalId);
      setGoals(goals.filter(g => g.id !== goalId));
    } catch (err) {
      console.error('Failed to delete goal:', err);
    }
  };

  const renderGoalCard = (goal: Goal) => {
    const progressPercentage = (goal.progress / goal.target) * 100;
    const timeRemaining = new Date(goal.deadline).getTime() - Date.now();
    const daysRemaining = Math.ceil(timeRemaining / (1000 * 60 * 60 * 24));
    
    return (
      <div key={goal.id} className={`goal-card ${goal.status} priority-${goal.priority}`}>
        <div className="goal-header">
          <h4>{goal.title}</h4>
          <div className="goal-actions">
            <button 
              className="edit-btn"
              onClick={() => setEditingGoal(goal)}
              disabled={goal.status !== 'active'}
            >
              ✏️
            </button>
            <button 
              className="delete-btn"
              onClick={() => handleDeleteGoal(goal.id)}
            >
              🗑️
            </button>
          </div>
        </div>
        
        <p className="goal-description">{goal.description}</p>
        
        <div className="goal-progress">
          <div className="progress-info">
            <span className="progress-text">
              {goal.progress} / {goal.target} {goal.unit}
            </span>
            <span className="progress-percentage">{progressPercentage.toFixed(0)}%</span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${Math.min(progressPercentage, 100)}%` }}
            />
          </div>
        </div>
        
        {goal.milestones.length > 0 && (
          <div className="goal-milestones">
            {goal.milestones.map((milestone, index) => (
              <div 
                key={index} 
                className={`milestone-dot ${milestone.completed ? 'completed' : ''}`}
                title={milestone.description}
                style={{ left: `${(milestone.threshold / goal.target) * 100}%` }}
              />
            ))}
          </div>
        )}
        
        <div className="goal-footer">
          <div className="goal-deadline">
            {goal.status === 'active' && daysRemaining > 0 ? (
              <span className={daysRemaining <= 3 ? 'urgent' : ''}>
                {daysRemaining} days remaining
              </span>
            ) : goal.status === 'completed' ? (
              <span className="completed">Completed!</span>
            ) : goal.status === 'failed' ? (
              <span className="failed">Failed</span>
            ) : (
              <span className="paused">Paused</span>
            )}
          </div>
          
          {goal.rewards && Object.keys(goal.rewards).length > 0 && (
            <div className="goal-rewards">
              {goal.rewards.credits && <span>💰 {goal.rewards.credits}</span>}
              {goal.rewards.experience && <span>⭐ {goal.rewards.experience} XP</span>}
              {goal.rewards.achievement && <span>🏆 {goal.rewards.achievement}</span>}
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderCreateModal = () => {
    if (!showCreateModal) return null;
    
    return (
      <div className="goal-modal-overlay" onClick={() => setShowCreateModal(false)}>
        <div className="goal-modal" onClick={(e) => e.stopPropagation()}>
          <h3>Create New Goal</h3>
          
          <div className="template-section">
            <h4>Choose from Templates</h4>
            <div className="template-grid">
              {templates.map(template => (
                <div 
                  key={template.id} 
                  className={`template-card difficulty-${template.difficulty}`}
                  onClick={() => {
                    // Populate form with template data
                  }}
                >
                  <h5>{template.title}</h5>
                  <p>{template.description}</p>
                  <div className="template-info">
                    <span>{template.category}</span>
                    <span>{template.estimatedTime}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="divider">OR</div>
          
          <form className="goal-form" onSubmit={(e) => {
            e.preventDefault();
            // Handle form submission
          }}>
            <h4>Create Custom Goal</h4>
            {/* Form fields would go here */}
            <div className="form-actions">
              <button type="button" onClick={() => setShowCreateModal(false)}>
                Cancel
              </button>
              <button type="submit">Create Goal</button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  if (loading) return <div className="goal-manager loading">Loading goals...</div>;
  if (error) return <div className="goal-manager error">Error: {error}</div>;

  return (
    <div className="goal-manager">
      <div className="manager-header">
        <h2>Goal Manager</h2>
        <button 
          className="create-goal-btn"
          onClick={() => setShowCreateModal(true)}
        >
          + Create New Goal
        </button>
      </div>

      {stats && (
        <div className="goal-stats">
          <div className="stat-card">
            <span className="stat-value">{stats.successRate.toFixed(0)}%</span>
            <span className="stat-label">Success Rate</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{stats.currentStreak}</span>
            <span className="stat-label">Current Streak</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{stats.completedGoals}</span>
            <span className="stat-label">Completed</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{stats.totalGoals}</span>
            <span className="stat-label">Total Goals</span>
          </div>
        </div>
      )}

      <div className="category-tabs">
        <button 
          className={selectedCategory === 'all' ? 'active' : ''}
          onClick={() => setSelectedCategory('all')}
        >
          All ({goals.length})
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
        <button 
          className={selectedCategory === 'personal' ? 'active' : ''}
          onClick={() => setSelectedCategory('personal')}
        >
          Personal
        </button>
      </div>

      <div className="goals-sections">
        {activeGoals.length > 0 && (
          <div className="active-goals-section">
            <h3>Active Goals ({activeGoals.length})</h3>
            <div className="goals-grid">
              {activeGoals.map(renderGoalCard)}
            </div>
          </div>
        )}

        {completedGoals.length > 0 && (
          <div className="completed-goals-section">
            <h3>Recently Completed ({completedGoals.length})</h3>
            <div className="goals-grid">
              {completedGoals.slice(0, 6).map(renderGoalCard)}
            </div>
          </div>
        )}

        {filteredGoals.length === 0 && (
          <div className="empty-state">
            <p>No goals found in this category.</p>
            <button onClick={() => setShowCreateModal(true)}>
              Create Your First Goal
            </button>
          </div>
        )}
      </div>

      {renderCreateModal()}
      {editingGoal && (
        <div className="goal-modal-overlay" onClick={() => setEditingGoal(null)}>
          <div className="goal-modal" onClick={(e) => e.stopPropagation()}>
            <h3>Edit Goal</h3>
            {/* Edit form would go here */}
            <div className="form-actions">
              <button onClick={() => setEditingGoal(null)}>Cancel</button>
              <button onClick={() => handleUpdateGoal(editingGoal.id, editingGoal)}>
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};