/**
 * CombatLog Component
 * 
 * Displays detailed combat history and analytics for past engagements.
 * Provides filtering, searching, and detailed round-by-round analysis.
 */

import React, { useState, useEffect, useMemo } from 'react';
import { InputValidator, XSSPrevention } from '../../utils/security/inputValidation';
import './combat-log.css';

export interface CombatRecord {
  id: string;
  timestamp: string;
  opponent: {
    id: string;
    name: string;
    type: 'ship' | 'planet' | 'port';
  };
  outcome: 'victory' | 'defeat' | 'retreat';
  rounds: number;
  damageDealt: number;
  damageTaken: number;
  dronesLost: number;
  dronesDestroyed: number;
  loot?: {
    credits: number;
    resources?: Record<string, number>;
  };
  sector: {
    id: string;
    name: string;
  };
}

interface CombatLogProps {
  records?: CombatRecord[];
  onRecordSelect?: (record: CombatRecord) => void;
  maxRecords?: number;
}

export const CombatLog: React.FC<CombatLogProps> = ({
  records = [],
  onRecordSelect,
  maxRecords = 50
}) => {
  // State
  const [filter, setFilter] = useState<'all' | 'victory' | 'defeat' | 'retreat'>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<'date' | 'outcome' | 'damage'>('date');
  const [sortAsc, setSortAsc] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<CombatRecord | null>(null);
  
  const [combatRecords, setCombatRecords] = useState<CombatRecord[]>([]);

  useEffect(() => {
    setCombatRecords(records.slice(0, maxRecords));
  }, [records, maxRecords]);
  
  // Filter and sort records
  const filteredRecords = useMemo(() => {
    let filtered = combatRecords;
    
    // Apply outcome filter
    if (filter !== 'all') {
      filtered = filtered.filter(r => r.outcome === filter);
    }
    
    // Apply search filter
    if (searchTerm) {
      const sanitized = InputValidator.sanitizeSearchQuery(searchTerm).toLowerCase();
      filtered = filtered.filter(r => 
        r.opponent.name.toLowerCase().includes(sanitized) ||
        r.sector.name.toLowerCase().includes(sanitized)
      );
    }
    
    // Sort records
    filtered.sort((a, b) => {
      let comparison = 0;
      
      switch (sortBy) {
        case 'date':
          comparison = new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
          break;
        case 'outcome':
          comparison = a.outcome.localeCompare(b.outcome);
          break;
        case 'damage':
          comparison = b.damageDealt - a.damageDealt;
          break;
      }
      
      return sortAsc ? -comparison : comparison;
    });
    
    return filtered;
  }, [combatRecords, filter, searchTerm, sortBy, sortAsc]);
  
  // Calculate statistics
  const stats = useMemo(() => {
    const total = combatRecords.length;
    const victories = combatRecords.filter(r => r.outcome === 'victory').length;
    const defeats = combatRecords.filter(r => r.outcome === 'defeat').length;
    const retreats = combatRecords.filter(r => r.outcome === 'retreat').length;
    
    const totalDamageDealt = combatRecords.reduce((sum, r) => sum + r.damageDealt, 0);
    const totalDamageTaken = combatRecords.reduce((sum, r) => sum + r.damageTaken, 0);
    const totalLoot = combatRecords.reduce((sum, r) => sum + (r.loot?.credits || 0), 0);
    
    return {
      total,
      victories,
      defeats,
      retreats,
      winRate: total > 0 ? (victories / total * 100).toFixed(1) : '0',
      avgDamageDealt: total > 0 ? Math.round(totalDamageDealt / total) : 0,
      avgDamageTaken: total > 0 ? Math.round(totalDamageTaken / total) : 0,
      totalLoot
    };
  }, [combatRecords]);
  
  // Handle search input
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);
  };
  
  // Handle record selection
  const handleRecordClick = (record: CombatRecord) => {
    setSelectedRecord(record);
    if (onRecordSelect) {
      onRecordSelect(record);
    }
  };
  
  // Toggle sort direction
  const toggleSort = (newSortBy: typeof sortBy) => {
    if (sortBy === newSortBy) {
      setSortAsc(!sortAsc);
    } else {
      setSortBy(newSortBy);
      setSortAsc(false);
    }
  };
  
  // Format timestamp
  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };
  
  // Get outcome icon
  const getOutcomeIcon = (outcome: string) => {
    switch (outcome) {
      case 'victory': return '✅';
      case 'defeat': return '❌';
      case 'retreat': return '🏃';
      default: return '❓';
    }
  };
  
  return (
    <div className="combat-log">
      <div className="combat-log-header">
        <h3>COMBAT HISTORY</h3>
        <div className="log-stats">
          <span className="stat victory">Victories: {stats.victories}</span>
          <span className="stat defeat">Defeats: {stats.defeats}</span>
          <span className="stat retreat">Retreats: {stats.retreats}</span>
          <span className="stat rate">Win Rate: {stats.winRate}%</span>
        </div>
      </div>
      
      <div className="log-controls">
        <div className="filter-group">
          <button
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All ({stats.total})
          </button>
          <button
            className={`filter-btn victory ${filter === 'victory' ? 'active' : ''}`}
            onClick={() => setFilter('victory')}
          >
            Victories
          </button>
          <button
            className={`filter-btn defeat ${filter === 'defeat' ? 'active' : ''}`}
            onClick={() => setFilter('defeat')}
          >
            Defeats
          </button>
          <button
            className={`filter-btn retreat ${filter === 'retreat' ? 'active' : ''}`}
            onClick={() => setFilter('retreat')}
          >
            Retreats
          </button>
        </div>
        
        <div className="search-group">
          <input
            type="text"
            placeholder="Search opponent or sector..."
            value={searchTerm}
            onChange={handleSearchChange}
            className="search-input"
            maxLength={50}
          />
        </div>
        
        <div className="sort-group">
          <button
            className={`sort-btn ${sortBy === 'date' ? 'active' : ''}`}
            onClick={() => toggleSort('date')}
          >
            Date {sortBy === 'date' && (sortAsc ? '↑' : '↓')}
          </button>
          <button
            className={`sort-btn ${sortBy === 'outcome' ? 'active' : ''}`}
            onClick={() => toggleSort('outcome')}
          >
            Outcome {sortBy === 'outcome' && (sortAsc ? '↑' : '↓')}
          </button>
          <button
            className={`sort-btn ${sortBy === 'damage' ? 'active' : ''}`}
            onClick={() => toggleSort('damage')}
          >
            Damage {sortBy === 'damage' && (sortAsc ? '↑' : '↓')}
          </button>
        </div>
      </div>
      
      <div className="log-summary">
        <div className="summary-item">
          <span className="label">Total Damage Dealt:</span>
          <span className="value">{stats.avgDamageDealt.toLocaleString()} avg</span>
        </div>
        <div className="summary-item">
          <span className="label">Total Damage Taken:</span>
          <span className="value">{stats.avgDamageTaken.toLocaleString()} avg</span>
        </div>
        <div className="summary-item">
          <span className="label">Total Loot Earned:</span>
          <span className="value">{stats.totalLoot.toLocaleString()} credits</span>
        </div>
      </div>
      
      <div className="log-entries">
        {filteredRecords.length === 0 ? (
          <div className="no-records">
            <p>{combatRecords.length === 0 ? 'No combat history yet. Engage in combat to see your battle records here.' : 'No combat records match your filters.'}</p>
            {searchTerm && <p className="hint">Try adjusting your search</p>}
          </div>
        ) : (
          filteredRecords.map(record => (
            <div 
              key={record.id}
              className={`log-entry ${record.outcome} ${selectedRecord?.id === record.id ? 'selected' : ''}`}
              onClick={() => handleRecordClick(record)}
            >
              <div className="entry-header">
                <span className="outcome-icon">{getOutcomeIcon(record.outcome)}</span>
                <span className="opponent-name">{record.opponent.name}</span>
                <span className="opponent-type">({record.opponent.type})</span>
                <span className="timestamp">{formatDate(record.timestamp)}</span>
              </div>
              
              <div className="entry-details">
                <div className="detail-row">
                  <span className="sector">📍 {record.sector.name}</span>
                  <span className="rounds">⏱️ {record.rounds} rounds</span>
                </div>
                
                <div className="detail-row">
                  <span className="damage dealt">⚔️ {record.damageDealt} dealt</span>
                  <span className="damage taken">🛡️ {record.damageTaken} taken</span>
                </div>
                
                {(record.dronesLost > 0 || record.dronesDestroyed > 0) && (
                  <div className="detail-row">
                    <span className="drones">
                      🤖 {record.dronesDestroyed} destroyed / {record.dronesLost} lost
                    </span>
                  </div>
                )}
                
                {record.loot && (
                  <div className="loot-info">
                    <span className="loot-credits">💰 {record.loot.credits} credits</span>
                    {record.loot.resources && (
                      <span className="loot-resources">
                        📦 {Object.entries(record.loot.resources)
                          .map(([type, amount]) => `${amount} ${type}`)
                          .join(', ')}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
      
      {selectedRecord && (
        <div className="selected-record-details">
          <h4>Combat Details</h4>
          <div className="detail-grid">
            <div className="detail-item">
              <span className="label">Combat ID:</span>
              <span className="value">{selectedRecord.id}</span>
            </div>
            <div className="detail-item">
              <span className="label">Duration:</span>
              <span className="value">{selectedRecord.rounds} rounds</span>
            </div>
            <div className="detail-item">
              <span className="label">Efficiency:</span>
              <span className="value">
                {selectedRecord.damageTaken > 0 
                  ? (selectedRecord.damageDealt / selectedRecord.damageTaken).toFixed(2)
                  : '∞'
                } ratio
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};