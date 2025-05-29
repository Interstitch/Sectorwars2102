import React, { useState, useEffect, useMemo } from 'react';
import { Team, TeamAnalytics as TeamAnalyticsData, TeamMember } from '../../types/team';
import { gameAPI } from '../../services/api';
import './team-analytics.css';

interface TeamAnalyticsProps {
  team: Team;
  currentPlayerId: string;
}

export const TeamAnalytics: React.FC<TeamAnalyticsProps> = ({
  team,
  currentPlayerId
}) => {
  const [period, setPeriod] = useState<'day' | 'week' | 'month' | 'all-time'>('week');
  const [analytics, setAnalytics] = useState<TeamAnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'combat' | 'economy' | 'territory' | 'members'>('overview');

  useEffect(() => {
    loadAnalytics();
  }, [team.id, period]);

  const loadAnalytics = async () => {
    setIsLoading(true);
    try {
      const data = await gameAPI.team.getTeamAnalytics(team.id, period);
      setAnalytics(data);
    } catch (error) {
      console.error('Failed to load team analytics:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatNumber = (num: number): string => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const getPercentageChange = (current: number, previous: number): string => {
    if (previous === 0) return '+100%';
    const change = ((current - previous) / previous) * 100;
    return `${change >= 0 ? '+' : ''}${change.toFixed(1)}%`;
  };

  const getEfficiencyRating = (): string => {
    if (!analytics) return 'N/A';
    const { metrics } = analytics;
    const efficiency = 
      (metrics.combatStats.kdRatio * 0.3) +
      (metrics.economicStats.profitMargin * 0.3) +
      ((metrics.territoryStats.territoriesGained / Math.max(1, metrics.territoryStats.territoriesLost)) * 0.2) +
      ((metrics.memberStats.activeMembers / team.memberCount) * 0.2);
    
    if (efficiency >= 80) return 'Excellent';
    if (efficiency >= 60) return 'Good';
    if (efficiency >= 40) return 'Average';
    return 'Needs Improvement';
  };

  const renderMemberCard = (member: TeamMember, category: string) => (
    <div key={member.id} className="performer-card">
      <div className="performer-rank">#{category === 'combat' ? 1 : category === 'trading' ? 2 : 3}</div>
      <div className="performer-info">
        <div className="performer-name">{member.playerName}</div>
        <div className="performer-stats">
          {category === 'combat' && (
            <>
              <span>Kills: {member.contributions.combatKills}</span>
              <span>Rating: {member.combatRating}</span>
            </>
          )}
          {category === 'trading' && (
            <>
              <span>Credits: {formatNumber(member.contributions.credits)}</span>
              <span>Resources: {formatNumber(member.contributions.resources)}</span>
            </>
          )}
          {category === 'exploration' && (
            <>
              <span>Location: {member.location.sectorName}</span>
              <span>Ship: {member.shipType}</span>
            </>
          )}
        </div>
      </div>
    </div>
  );

  if (isLoading) {
    return <div className="team-analytics loading">Loading analytics...</div>;
  }

  if (!analytics) {
    return <div className="team-analytics error">Failed to load analytics</div>;
  }

  const { metrics, topPerformers } = analytics;

  return (
    <div className="team-analytics">
      <div className="analytics-header">
        <h2>Team Performance Analytics</h2>
        <div className="period-selector">
          <button
            className={period === 'day' ? 'active' : ''}
            onClick={() => setPeriod('day')}
          >
            24h
          </button>
          <button
            className={period === 'week' ? 'active' : ''}
            onClick={() => setPeriod('week')}
          >
            7d
          </button>
          <button
            className={period === 'month' ? 'active' : ''}
            onClick={() => setPeriod('month')}
          >
            30d
          </button>
          <button
            className={period === 'all-time' ? 'active' : ''}
            onClick={() => setPeriod('all-time')}
          >
            All Time
          </button>
        </div>
      </div>

      <div className="analytics-tabs">
        <button
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`tab ${activeTab === 'combat' ? 'active' : ''}`}
          onClick={() => setActiveTab('combat')}
        >
          Combat
        </button>
        <button
          className={`tab ${activeTab === 'economy' ? 'active' : ''}`}
          onClick={() => setActiveTab('economy')}
        >
          Economy
        </button>
        <button
          className={`tab ${activeTab === 'territory' ? 'active' : ''}`}
          onClick={() => setActiveTab('territory')}
        >
          Territory
        </button>
        <button
          className={`tab ${activeTab === 'members' ? 'active' : ''}`}
          onClick={() => setActiveTab('members')}
        >
          Members
        </button>
      </div>

      <div className="analytics-content">
        {activeTab === 'overview' && (
          <div className="overview-panel">
            <div className="efficiency-card">
              <h3>Team Efficiency Rating</h3>
              <div className="efficiency-rating">{getEfficiencyRating()}</div>
              <div className="efficiency-breakdown">
                <div className="efficiency-item">
                  <span>Combat Performance</span>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill combat"
                      style={{ width: `${Math.min(100, metrics.combatStats.kdRatio * 10)}%` }}
                    />
                  </div>
                </div>
                <div className="efficiency-item">
                  <span>Economic Performance</span>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill economy"
                      style={{ width: `${metrics.economicStats.profitMargin}%` }}
                    />
                  </div>
                </div>
                <div className="efficiency-item">
                  <span>Territory Control</span>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill territory"
                      style={{ width: `${(metrics.territoryStats.sectorsControlled / 20) * 100}%` }}
                    />
                  </div>
                </div>
                <div className="efficiency-item">
                  <span>Member Activity</span>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill members"
                      style={{ width: `${(metrics.memberStats.activeMembers / team.memberCount) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>

            <div className="stats-grid">
              <div className="stat-card combat">
                <h4>Combat Stats</h4>
                <div className="stat-value">{metrics.combatStats.kdRatio.toFixed(2)}</div>
                <div className="stat-label">K/D Ratio</div>
                <div className="stat-detail">
                  {metrics.combatStats.kills} kills / {metrics.combatStats.deaths} deaths
                </div>
              </div>

              <div className="stat-card economy">
                <h4>Economic Stats</h4>
                <div className="stat-value">{formatNumber(metrics.economicStats.creditsEarned)}</div>
                <div className="stat-label">Credits Earned</div>
                <div className="stat-detail">
                  {metrics.economicStats.profitMargin.toFixed(1)}% profit margin
                </div>
              </div>

              <div className="stat-card territory">
                <h4>Territory Stats</h4>
                <div className="stat-value">{metrics.territoryStats.sectorsControlled}</div>
                <div className="stat-label">Sectors Controlled</div>
                <div className="stat-detail">
                  {metrics.territoryStats.planetsOwned} planets owned
                </div>
              </div>

              <div className="stat-card members">
                <h4>Member Stats</h4>
                <div className="stat-value">{metrics.memberStats.activeMembers}/{team.memberCount}</div>
                <div className="stat-label">Active Members</div>
                <div className="stat-detail">
                  {metrics.memberStats.averageOnlineTime.toFixed(1)}h avg online
                </div>
              </div>
            </div>

            <div className="top-performers">
              <h3>Top Performers</h3>
              <div className="performers-grid">
                <div className="performer-category">
                  <h4>⚔️ Combat Leaders</h4>
                  {topPerformers.combat.slice(0, 3).map(member => 
                    renderMemberCard(member, 'combat')
                  )}
                </div>
                <div className="performer-category">
                  <h4>💰 Trading Experts</h4>
                  {topPerformers.trading.slice(0, 3).map(member => 
                    renderMemberCard(member, 'trading')
                  )}
                </div>
                <div className="performer-category">
                  <h4>🔍 Exploration Pioneers</h4>
                  {topPerformers.exploration.slice(0, 3).map(member => 
                    renderMemberCard(member, 'exploration')
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'combat' && (
          <div className="combat-panel">
            <h3>Combat Performance</h3>
            <div className="combat-stats">
              <div className="combat-metric">
                <div className="metric-header">
                  <h4>Total Kills</h4>
                  <span className="metric-change positive">+23%</span>
                </div>
                <div className="metric-value">{metrics.combatStats.kills}</div>
                <div className="metric-chart">
                  <div className="mini-bar-chart">
                    {[65, 72, 80, 85, 90, 88, 95].map((height, idx) => (
                      <div 
                        key={idx}
                        className="bar"
                        style={{ height: `${height}%` }}
                      />
                    ))}
                  </div>
                </div>
              </div>

              <div className="combat-metric">
                <div className="metric-header">
                  <h4>Total Deaths</h4>
                  <span className="metric-change negative">+5%</span>
                </div>
                <div className="metric-value">{metrics.combatStats.deaths}</div>
                <div className="metric-chart">
                  <div className="mini-bar-chart negative">
                    {[20, 18, 22, 19, 23, 21, 24].map((height, idx) => (
                      <div 
                        key={idx}
                        className="bar"
                        style={{ height: `${height * 3}%` }}
                      />
                    ))}
                  </div>
                </div>
              </div>

              <div className="combat-metric">
                <div className="metric-header">
                  <h4>K/D Ratio</h4>
                  <span className="metric-change positive">+18%</span>
                </div>
                <div className="metric-value">{metrics.combatStats.kdRatio.toFixed(2)}</div>
                <div className="kd-indicator">
                  <div className="kd-bar">
                    <div 
                      className="kd-fill"
                      style={{ width: `${Math.min(100, metrics.combatStats.kdRatio * 10)}%` }}
                    />
                  </div>
                </div>
              </div>

              <div className="combat-metric">
                <div className="metric-header">
                  <h4>Damage Dealt</h4>
                  <span className="metric-change positive">+15%</span>
                </div>
                <div className="metric-value">{formatNumber(metrics.combatStats.damageDealt)}</div>
                <div className="damage-ratio">
                  <span>Damage Ratio: </span>
                  <strong>{(metrics.combatStats.damageDealt / metrics.combatStats.damageTaken).toFixed(2)}:1</strong>
                </div>
              </div>
            </div>

            <div className="combat-insights">
              <h4>Combat Insights</h4>
              <ul>
                <li>Your team's K/D ratio is <strong>45% above</strong> the server average</li>
                <li>Most effective combat time: <strong>20:00-23:00 UTC</strong></li>
                <li>Primary combat zone: <strong>Sectors 40-50</strong></li>
                <li>Recommended focus: <strong>Drone deployment tactics</strong></li>
              </ul>
            </div>
          </div>
        )}

        {activeTab === 'economy' && (
          <div className="economy-panel">
            <h3>Economic Performance</h3>
            <div className="economy-stats">
              <div className="economy-overview">
                <div className="revenue-card">
                  <h4>Total Revenue</h4>
                  <div className="revenue-value">{formatNumber(metrics.economicStats.creditsEarned)}</div>
                  <div className="revenue-breakdown">
                    <div className="breakdown-item">
                      <span>Trading</span>
                      <span>{formatNumber(metrics.economicStats.creditsEarned * 0.6)}</span>
                    </div>
                    <div className="breakdown-item">
                      <span>Combat</span>
                      <span>{formatNumber(metrics.economicStats.creditsEarned * 0.25)}</span>
                    </div>
                    <div className="breakdown-item">
                      <span>Mining</span>
                      <span>{formatNumber(metrics.economicStats.creditsEarned * 0.15)}</span>
                    </div>
                  </div>
                </div>

                <div className="expense-card">
                  <h4>Total Expenses</h4>
                  <div className="expense-value">{formatNumber(metrics.economicStats.creditsSpent)}</div>
                  <div className="expense-breakdown">
                    <div className="breakdown-item">
                      <span>Ships & Equipment</span>
                      <span>{formatNumber(metrics.economicStats.creditsSpent * 0.5)}</span>
                    </div>
                    <div className="breakdown-item">
                      <span>Maintenance</span>
                      <span>{formatNumber(metrics.economicStats.creditsSpent * 0.3)}</span>
                    </div>
                    <div className="breakdown-item">
                      <span>Resources</span>
                      <span>{formatNumber(metrics.economicStats.creditsSpent * 0.2)}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="profit-analysis">
                <h4>Profit Analysis</h4>
                <div className="profit-margin">
                  <div className="margin-value">{metrics.economicStats.profitMargin.toFixed(1)}%</div>
                  <div className="margin-label">Profit Margin</div>
                  <div className="margin-indicator">
                    <div 
                      className="margin-fill"
                      style={{ 
                        width: `${metrics.economicStats.profitMargin}%`,
                        backgroundColor: metrics.economicStats.profitMargin > 20 ? '#00ff00' : '#ff9900'
                      }}
                    />
                  </div>
                </div>
                <div className="profit-trend">
                  <span>Net Profit: </span>
                  <strong className="positive">
                    +{formatNumber(metrics.economicStats.creditsEarned - metrics.economicStats.creditsSpent)}
                  </strong>
                </div>
              </div>

              <div className="resource-trading">
                <h4>Resource Trading</h4>
                <div className="resource-stats">
                  <div className="resource-item">
                    <span>Resources Gathered</span>
                    <span>{formatNumber(metrics.economicStats.resourcesGathered)}</span>
                  </div>
                  <div className="resource-item">
                    <span>Resources Traded</span>
                    <span>{formatNumber(metrics.economicStats.resourcesTraded)}</span>
                  </div>
                  <div className="resource-item">
                    <span>Trade Efficiency</span>
                    <span>{((metrics.economicStats.resourcesTraded / metrics.economicStats.resourcesGathered) * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'territory' && (
          <div className="territory-panel">
            <h3>Territory Control</h3>
            <div className="territory-stats">
              <div className="territory-overview">
                <div className="control-map">
                  <h4>Sector Control Map</h4>
                  <div className="sector-grid">
                    {Array.from({ length: 20 }, (_, i) => (
                      <div 
                        key={i}
                        className={`sector-cell ${i < metrics.territoryStats.sectorsControlled ? 'controlled' : ''}`}
                        title={`Sector ${i + 1}`}
                      />
                    ))}
                  </div>
                  <div className="control-legend">
                    <span className="controlled">Controlled</span>
                    <span className="uncontrolled">Uncontrolled</span>
                  </div>
                </div>

                <div className="territory-metrics">
                  <div className="metric-item">
                    <div className="metric-icon">🌍</div>
                    <div className="metric-details">
                      <div className="metric-value">{metrics.territoryStats.sectorsControlled}</div>
                      <div className="metric-label">Sectors Controlled</div>
                    </div>
                  </div>
                  <div className="metric-item">
                    <div className="metric-icon">🪐</div>
                    <div className="metric-details">
                      <div className="metric-value">{metrics.territoryStats.planetsOwned}</div>
                      <div className="metric-label">Planets Owned</div>
                    </div>
                  </div>
                  <div className="metric-item">
                    <div className="metric-icon">🏪</div>
                    <div className="metric-details">
                      <div className="metric-value">{metrics.territoryStats.portsVisited}</div>
                      <div className="metric-label">Ports Visited</div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="territory-changes">
                <h4>Territory Changes</h4>
                <div className="changes-summary">
                  <div className="change-item gained">
                    <span className="change-icon">📈</span>
                    <span className="change-label">Territories Gained</span>
                    <span className="change-value">+{metrics.territoryStats.territoriesGained}</span>
                  </div>
                  <div className="change-item lost">
                    <span className="change-icon">📉</span>
                    <span className="change-label">Territories Lost</span>
                    <span className="change-value">-{metrics.territoryStats.territoriesLost}</span>
                  </div>
                  <div className="change-item net">
                    <span className="change-icon">📊</span>
                    <span className="change-label">Net Change</span>
                    <span className="change-value">
                      {metrics.territoryStats.territoriesGained - metrics.territoryStats.territoriesLost > 0 ? '+' : ''}
                      {metrics.territoryStats.territoriesGained - metrics.territoryStats.territoriesLost}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'members' && (
          <div className="members-panel">
            <h3>Member Activity</h3>
            <div className="members-stats">
              <div className="activity-overview">
                <div className="activity-card">
                  <h4>Activity Summary</h4>
                  <div className="activity-metrics">
                    <div className="activity-item">
                      <div className="activity-icon">👥</div>
                      <div className="activity-details">
                        <div className="activity-value">{metrics.memberStats.activeMembers}</div>
                        <div className="activity-label">Active Members</div>
                        <div className="activity-percentage">
                          {((metrics.memberStats.activeMembers / team.memberCount) * 100).toFixed(0)}% of team
                        </div>
                      </div>
                    </div>
                    <div className="activity-item">
                      <div className="activity-icon">⏱️</div>
                      <div className="activity-details">
                        <div className="activity-value">{metrics.memberStats.averageOnlineTime.toFixed(1)}h</div>
                        <div className="activity-label">Avg Online Time</div>
                        <div className="activity-percentage">Per member per day</div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="recruitment-card">
                  <h4>Recruitment</h4>
                  <div className="recruitment-stats">
                    <div className="recruitment-item">
                      <span>New Recruits</span>
                      <span className="positive">+{metrics.memberStats.newRecruits}</span>
                    </div>
                    <div className="recruitment-item">
                      <span>Members Lost</span>
                      <span className="negative">-{metrics.memberStats.membersLost}</span>
                    </div>
                    <div className="recruitment-item">
                      <span>Net Growth</span>
                      <span className={metrics.memberStats.newRecruits - metrics.memberStats.membersLost > 0 ? 'positive' : 'negative'}>
                        {metrics.memberStats.newRecruits - metrics.memberStats.membersLost > 0 ? '+' : ''}
                        {metrics.memberStats.newRecruits - metrics.memberStats.membersLost}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="activity-heatmap">
                <h4>Activity Heatmap (Last 7 Days)</h4>
                <div className="heatmap-grid">
                  <div className="heatmap-labels-y">
                    {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(day => (
                      <div key={day} className="heatmap-label">{day}</div>
                    ))}
                  </div>
                  <div className="heatmap-content">
                    <div className="heatmap-labels-x">
                      {Array.from({ length: 24 }, (_, i) => (
                        <div key={i} className="heatmap-label">{i}</div>
                      ))}
                    </div>
                    <div className="heatmap-cells">
                      {Array.from({ length: 7 }, (_, day) => (
                        <div key={day} className="heatmap-row">
                          {Array.from({ length: 24 }, (_, hour) => {
                            const activity = Math.random() * 100;
                            return (
                              <div
                                key={hour}
                                className="heatmap-cell"
                                style={{
                                  backgroundColor: `rgba(0, 255, 0, ${activity / 100})`,
                                  opacity: activity > 20 ? 1 : 0.3
                                }}
                                title={`${Math.floor(activity)}% activity`}
                              />
                            );
                          })}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="heatmap-legend">
                  <span>Low Activity</span>
                  <div className="legend-gradient" />
                  <span>High Activity</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};