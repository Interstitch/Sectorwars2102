import React, { useState, useEffect, useCallback } from 'react';
import { citadelAPI } from '../../services/api';
import './citadel.css';

interface CitadelInfo {
  level: number;
  level_name: string;
  max_level: number;
  safe_storage: number;
  safe_storage_capacity: number;
  drone_capacity: number;
  upgrade_cost: number | null;
  upgrade_time_hours: number | null;
  upgrading: boolean;
  upgrade_complete_at: string | null;
}

interface CitadelManagerProps {
  planetId: string;
  playerCredits: number;
  onUpdate?: () => void;
}

const CITADEL_LEVEL_NAMES = [
  'No Citadel',
  'Outpost Bunker',
  'Fortified Base',
  'Command Center',
  'War Fortress',
  'Planetary Stronghold',
];

const CitadelManager: React.FC<CitadelManagerProps> = ({
  planetId,
  playerCredits,
  onUpdate,
}) => {
  const [citadel, setCitadel] = useState<CitadelInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [depositAmount, setDepositAmount] = useState('');
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  const fetchCitadel = useCallback(async () => {
    try {
      setLoading(true);
      const data = await citadelAPI.getInfo(planetId);
      setCitadel(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load citadel info');
    } finally {
      setLoading(false);
    }
  }, [planetId]);

  useEffect(() => {
    fetchCitadel();
  }, [fetchCitadel]);

  const handleUpgrade = async () => {
    if (!citadel || actionLoading) return;
    try {
      setActionLoading(true);
      setActionMessage(null);
      await citadelAPI.upgrade(planetId);
      setActionMessage('Citadel upgrade initiated!');
      await fetchCitadel();
      onUpdate?.();
    } catch (err: any) {
      setActionMessage(err.message || 'Upgrade failed');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeposit = async () => {
    const amount = parseInt(depositAmount);
    if (!amount || amount <= 0 || actionLoading) return;
    try {
      setActionLoading(true);
      setActionMessage(null);
      await citadelAPI.deposit(planetId, amount);
      setActionMessage(`Deposited ${amount.toLocaleString()} credits`);
      setDepositAmount('');
      await fetchCitadel();
      onUpdate?.();
    } catch (err: any) {
      setActionMessage(err.message || 'Deposit failed');
    } finally {
      setActionLoading(false);
    }
  };

  const handleWithdraw = async () => {
    const amount = parseInt(withdrawAmount);
    if (!amount || amount <= 0 || actionLoading) return;
    try {
      setActionLoading(true);
      setActionMessage(null);
      await citadelAPI.withdraw(planetId, amount);
      setActionMessage(`Withdrew ${amount.toLocaleString()} credits`);
      setWithdrawAmount('');
      await fetchCitadel();
      onUpdate?.();
    } catch (err: any) {
      setActionMessage(err.message || 'Withdraw failed');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="citadel-manager citadel-loading">
        <div className="citadel-spinner" />
        <span>Loading citadel...</span>
      </div>
    );
  }

  if (error || !citadel) {
    return (
      <div className="citadel-manager citadel-error">
        <span>{error || 'Citadel unavailable'}</span>
        <button onClick={fetchCitadel} className="citadel-retry-btn">Retry</button>
      </div>
    );
  }

  const storagePercent = citadel.safe_storage_capacity > 0
    ? (citadel.safe_storage / citadel.safe_storage_capacity) * 100
    : 0;

  return (
    <div className="citadel-manager">
      <div className="citadel-header">
        <h3>Citadel</h3>
        <span className="citadel-level-badge">Level {citadel.level}</span>
      </div>

      <div className="citadel-level-name">
        {citadel.level_name || CITADEL_LEVEL_NAMES[citadel.level] || `Level ${citadel.level}`}
      </div>

      <div className="citadel-stats">
        <div className="citadel-stat">
          <span className="stat-label">Safe Storage</span>
          <div className="storage-bar">
            <div
              className="storage-fill"
              style={{ width: `${Math.min(100, storagePercent)}%` }}
            />
          </div>
          <span className="stat-value">
            {citadel.safe_storage.toLocaleString()} / {citadel.safe_storage_capacity.toLocaleString()}
          </span>
        </div>
        <div className="citadel-stat">
          <span className="stat-label">Drone Capacity</span>
          <span className="stat-value">{citadel.drone_capacity}</span>
        </div>
      </div>

      {/* Safe Storage Controls */}
      <div className="citadel-storage-controls">
        <div className="storage-action">
          <input
            type="number"
            placeholder="Amount"
            value={depositAmount}
            onChange={(e) => setDepositAmount(e.target.value)}
            min="1"
            className="storage-input"
          />
          <button
            onClick={handleDeposit}
            disabled={actionLoading || !depositAmount}
            className="citadel-btn deposit-btn"
          >
            Deposit
          </button>
        </div>
        <div className="storage-action">
          <input
            type="number"
            placeholder="Amount"
            value={withdrawAmount}
            onChange={(e) => setWithdrawAmount(e.target.value)}
            min="1"
            max={citadel.safe_storage.toString()}
            className="storage-input"
          />
          <button
            onClick={handleWithdraw}
            disabled={actionLoading || !withdrawAmount}
            className="citadel-btn withdraw-btn"
          >
            Withdraw
          </button>
        </div>
      </div>

      {/* Upgrade Section */}
      {citadel.level < citadel.max_level && !citadel.upgrading && citadel.upgrade_cost && (
        <div className="citadel-upgrade">
          <div className="upgrade-info">
            <span className="upgrade-label">
              Upgrade to Level {citadel.level + 1}
            </span>
            <span className="upgrade-cost">
              {citadel.upgrade_cost.toLocaleString()} credits
            </span>
            {citadel.upgrade_time_hours && (
              <span className="upgrade-time">
                {citadel.upgrade_time_hours}h build time
              </span>
            )}
          </div>
          <button
            onClick={handleUpgrade}
            disabled={actionLoading || playerCredits < citadel.upgrade_cost}
            className="citadel-btn upgrade-btn"
          >
            {playerCredits < citadel.upgrade_cost ? 'Insufficient Credits' : 'Upgrade'}
          </button>
        </div>
      )}

      {citadel.upgrading && citadel.upgrade_complete_at && (
        <div className="citadel-upgrading">
          Upgrading... Completes at{' '}
          {new Date(citadel.upgrade_complete_at).toLocaleString()}
        </div>
      )}

      {citadel.level >= citadel.max_level && (
        <div className="citadel-max-level">Maximum Level Reached</div>
      )}

      {actionMessage && (
        <div className="citadel-message">{actionMessage}</div>
      )}
    </div>
  );
};

export default CitadelManager;
