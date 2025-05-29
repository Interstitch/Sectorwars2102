import React, { useState, useMemo, useCallback } from 'react';
import { Ship } from '../../types/game';
import { InputValidator } from '../../utils/security/inputValidation';
import './maintenance-manager.css';

interface MaintenanceItem {
  id: string;
  component: 'hull' | 'shields' | 'engines' | 'weapons' | 'systems';
  name: string;
  condition: number; // 0-100
  repairCost: number;
  repairTime: number; // hours
  priority: 'critical' | 'high' | 'medium' | 'low';
  description: string;
}

interface MaintenanceSchedule {
  lastMaintenance: string;
  nextScheduled: string;
  maintenanceInterval: number; // days
  totalMaintenanceCost: number;
}

interface MaintenanceManagerProps {
  ship: Ship;
  playerCredits: number;
  onRepair?: (items: string[], totalCost: number) => void;
  onScheduleMaintenance?: (schedule: MaintenanceSchedule) => void;
  onEmergencyRepair?: () => void;
}

const MaintenanceManager: React.FC<MaintenanceManagerProps> = ({
  ship,
  playerCredits,
  onRepair,
  onScheduleMaintenance,
  onEmergencyRepair
}) => {
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
  const [showScheduler, setShowScheduler] = useState(false);
  const [maintenanceInterval, setMaintenanceInterval] = useState(30);
  const [lastAction, setLastAction] = useState<number>(0);

  // Rate limiting
  const RATE_LIMIT_MS = 1000;
  const canPerformAction = useCallback(() => {
    const now = Date.now();
    if (now - lastAction < RATE_LIMIT_MS) {
      return false;
    }
    setLastAction(now);
    return true;
  }, [lastAction]);

  // Generate maintenance items based on ship condition
  const maintenanceItems: MaintenanceItem[] = useMemo(() => {
    const items: MaintenanceItem[] = [];
    
    // Hull maintenance
    const shipHealth = (ship as any).health || 100;
    if (shipHealth < 100) {
      items.push({
        id: 'hull_repair',
        component: 'hull',
        name: 'Hull Integrity Repair',
        condition: shipHealth,
        repairCost: Math.floor((100 - shipHealth) * 100),
        repairTime: Math.ceil((100 - shipHealth) / 10),
        priority: shipHealth < 30 ? 'critical' : shipHealth < 60 ? 'high' : 'medium',
        description: `Repair hull damage and restore structural integrity. Current: ${shipHealth}%`
      });
    }

    // Shield maintenance
    const shipShields = (ship as any).shields || 100;
    if (shipShields < 100) {
      items.push({
        id: 'shield_repair',
        component: 'shields',
        name: 'Shield Generator Maintenance',
        condition: shipShields,
        repairCost: Math.floor((100 - shipShields) * 80),
        repairTime: Math.ceil((100 - shipShields) / 15),
        priority: shipShields < 50 ? 'high' : 'medium',
        description: `Recalibrate shield generators and replace depleted cells. Current: ${shipShields}%`
      });
    }

    // Engine maintenance (simulated)
    const engineCondition = 85;
    items.push({
      id: 'engine_tune',
      component: 'engines',
      name: 'Engine Optimization',
      condition: engineCondition,
      repairCost: 500,
      repairTime: 2,
      priority: 'low',
      description: 'Tune engine performance and clean intake manifolds'
    });

    // Weapons maintenance (simulated)
    const weaponsCondition = 92;
    items.push({
      id: 'weapons_calibration',
      component: 'weapons',
      name: 'Weapons Calibration',
      condition: weaponsCondition,
      repairCost: 300,
      repairTime: 1,
      priority: 'low',
      description: 'Calibrate targeting systems and clean weapon barrels'
    });

    // Systems maintenance (simulated)
    const systemsCondition = 78;
    items.push({
      id: 'systems_update',
      component: 'systems',
      name: 'Computer Systems Update',
      condition: systemsCondition,
      repairCost: 750,
      repairTime: 3,
      priority: 'medium',
      description: 'Update navigation software and repair sensor arrays'
    });

    return items;
  }, [ship]);

  // Calculate total repair cost and time
  const repairSummary = useMemo(() => {
    let totalCost = 0;
    let totalTime = 0;
    const itemsToRepair: MaintenanceItem[] = [];

    selectedItems.forEach(itemId => {
      const item = maintenanceItems.find(i => i.id === itemId);
      if (item) {
        totalCost += item.repairCost;
        totalTime = Math.max(totalTime, item.repairTime);
        itemsToRepair.push(item);
      }
    });

    return { totalCost, totalTime, itemsToRepair };
  }, [selectedItems, maintenanceItems]);

  // Calculate maintenance schedule cost
  const scheduleCost = useMemo(() => {
    const baseCost = 1000;
    const intervalMultiplier = 30 / maintenanceInterval; // More frequent = more expensive
    return Math.floor(baseCost * intervalMultiplier);
  }, [maintenanceInterval]);

  const toggleItemSelection = useCallback((itemId: string) => {
    setSelectedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(itemId)) {
        newSet.delete(itemId);
      } else {
        newSet.add(itemId);
      }
      return newSet;
    });
  }, []);

  const selectAllCritical = useCallback(() => {
    const criticalItems = maintenanceItems
      .filter(item => item.priority === 'critical' || item.priority === 'high')
      .map(item => item.id);
    setSelectedItems(new Set(criticalItems));
  }, [maintenanceItems]);

  const performRepairs = useCallback(() => {
    if (!canPerformAction() || !onRepair) return;

    if (repairSummary.totalCost > playerCredits) {
      alert('Insufficient credits for repairs!');
      return;
    }

    if (selectedItems.size === 0) {
      alert('No items selected for repair!');
      return;
    }

    onRepair(Array.from(selectedItems), repairSummary.totalCost);
    setSelectedItems(new Set());
  }, [canPerformAction, onRepair, selectedItems, repairSummary.totalCost, playerCredits]);

  const scheduleMaintenance = useCallback(() => {
    if (!canPerformAction() || !onScheduleMaintenance) return;

    if (scheduleCost > playerCredits) {
      alert('Insufficient credits for maintenance schedule!');
      return;
    }

    const schedule: MaintenanceSchedule = {
      lastMaintenance: new Date().toISOString(),
      nextScheduled: new Date(Date.now() + maintenanceInterval * 24 * 60 * 60 * 1000).toISOString(),
      maintenanceInterval,
      totalMaintenanceCost: scheduleCost
    };

    onScheduleMaintenance(schedule);
    setShowScheduler(false);
  }, [canPerformAction, onScheduleMaintenance, maintenanceInterval, scheduleCost, playerCredits]);

  const getConditionColor = (condition: number) => {
    if (condition >= 90) return '#44ff44';
    if (condition >= 70) return '#88ff88';
    if (condition >= 50) return '#ffaa44';
    if (condition >= 30) return '#ff8844';
    return '#ff4444';
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return '#ff4444';
      case 'high': return '#ff8844';
      case 'medium': return '#ffaa44';
      case 'low': return '#88ff88';
      default: return '#ffffff';
    }
  };

  const shipHealth = (ship as any).health || 100;
  const shipShields = (ship as any).shields || 100;

  return (
    <div className="maintenance-manager">
      <div className="manager-header">
        <h3>Ship Maintenance</h3>
        <div className="ship-status">
          <span className="ship-name">{ship.name}</span>
          <span className="ship-type">{ship.type}</span>
        </div>
      </div>

      <div className="maintenance-overview">
        <div className="overview-card">
          <h4>Overall Condition</h4>
          <div className="condition-meter">
            <div 
              className="condition-fill"
              style={{ 
                width: `${((shipHealth + shipShields) / 2)}%`,
                backgroundColor: getConditionColor((shipHealth + shipShields) / 2)
              }}
            />
            <span className="condition-value">{((shipHealth + shipShields) / 2).toFixed(0)}%</span>
          </div>
        </div>
        
        <div className="overview-card">
          <h4>Maintenance Required</h4>
          <div className="maintenance-count">
            <span className="count-value">{maintenanceItems.length}</span>
            <span className="count-label">items</span>
          </div>
        </div>
        
        <div className="overview-card">
          <h4>Estimated Cost</h4>
          <div className="cost-estimate">
            <span className="cost-value">
              {maintenanceItems.reduce((sum, item) => sum + item.repairCost, 0).toLocaleString()}
            </span>
            <span className="cost-label">credits</span>
          </div>
        </div>
      </div>

      <div className="maintenance-items">
        <div className="items-header">
          <h4>Maintenance Items</h4>
          <button 
            className="select-critical-btn"
            onClick={selectAllCritical}
          >
            Select Critical
          </button>
        </div>

        <div className="items-list">
          {maintenanceItems.map(item => (
            <div 
              key={item.id} 
              className={`maintenance-item ${selectedItems.has(item.id) ? 'selected' : ''}`}
              onClick={() => toggleItemSelection(item.id)}
            >
              <div className="item-checkbox">
                <input 
                  type="checkbox"
                  checked={selectedItems.has(item.id)}
                  onChange={() => {}}
                  onClick={(e) => e.stopPropagation()}
                />
              </div>
              
              <div className="item-info">
                <div className="item-header">
                  <h5>{item.name}</h5>
                  <span 
                    className="item-priority"
                    style={{ color: getPriorityColor(item.priority) }}
                  >
                    {item.priority.toUpperCase()}
                  </span>
                </div>
                <p className="item-description">{item.description}</p>
                <div className="item-stats">
                  <span className="stat-item">
                    <span className="stat-label">Condition:</span>
                    <span 
                      className="stat-value"
                      style={{ color: getConditionColor(item.condition) }}
                    >
                      {item.condition}%
                    </span>
                  </span>
                  <span className="stat-item">
                    <span className="stat-label">Cost:</span>
                    <span className="stat-value">{item.repairCost.toLocaleString()} cr</span>
                  </span>
                  <span className="stat-item">
                    <span className="stat-label">Time:</span>
                    <span className="stat-value">{item.repairTime}h</span>
                  </span>
                </div>
              </div>
              
              <div className="item-condition">
                <div className="condition-bar">
                  <div 
                    className="condition-bar-fill"
                    style={{ 
                      height: `${item.condition}%`,
                      backgroundColor: getConditionColor(item.condition)
                    }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {selectedItems.size > 0 && (
        <div className="repair-summary">
          <h4>Repair Summary</h4>
          <div className="summary-stats">
            <div className="summary-item">
              <span className="summary-label">Selected Items:</span>
              <span className="summary-value">{selectedItems.size}</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Total Cost:</span>
              <span className="summary-value">{repairSummary.totalCost.toLocaleString()} cr</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Repair Time:</span>
              <span className="summary-value">{repairSummary.totalTime}h</span>
            </div>
          </div>
          
          <div className="repair-actions">
            <button 
              className="repair-btn"
              onClick={performRepairs}
              disabled={repairSummary.totalCost > playerCredits}
            >
              Perform Repairs
            </button>
            <button 
              className="clear-btn"
              onClick={() => setSelectedItems(new Set())}
            >
              Clear Selection
            </button>
          </div>
          
          {repairSummary.totalCost > playerCredits && (
            <div className="insufficient-funds">
              ⚠️ Insufficient credits! You need {(repairSummary.totalCost - playerCredits).toLocaleString()} more credits.
            </div>
          )}
        </div>
      )}

      <div className="maintenance-options">
        <button 
          className="schedule-btn"
          onClick={() => setShowScheduler(!showScheduler)}
        >
          {showScheduler ? 'Cancel Scheduling' : 'Schedule Maintenance'}
        </button>
        
        {onEmergencyRepair && (
          <button 
            className="emergency-btn"
            onClick={onEmergencyRepair}
          >
            Emergency Repair (2x Cost)
          </button>
        )}
      </div>

      {showScheduler && (
        <div className="maintenance-scheduler">
          <h4>Schedule Regular Maintenance</h4>
          <p>Set up automatic maintenance to keep your ship in top condition.</p>
          
          <div className="scheduler-options">
            <label>Maintenance Interval</label>
            <div className="interval-selector">
              <input 
                type="range"
                min="7"
                max="90"
                value={maintenanceInterval}
                onChange={(e) => setMaintenanceInterval(parseInt(e.target.value))}
              />
              <span className="interval-value">{maintenanceInterval} days</span>
            </div>
            
            <div className="schedule-cost">
              <span className="cost-label">Monthly Cost:</span>
              <span className="cost-value">{scheduleCost.toLocaleString()} cr</span>
            </div>
            
            <div className="schedule-benefits">
              <h5>Benefits:</h5>
              <ul>
                <li>10% discount on all repairs</li>
                <li>Priority service at all stations</li>
                <li>Free emergency diagnostics</li>
                <li>Extended warranty on parts</li>
              </ul>
            </div>
            
            <button 
              className="confirm-schedule-btn"
              onClick={scheduleMaintenance}
              disabled={scheduleCost > playerCredits}
            >
              Confirm Schedule
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default MaintenanceManager;