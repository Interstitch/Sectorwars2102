import React, { useState, useEffect } from 'react';
import { api } from '../../utils/auth';
import { PlayerModel } from '../../types/playerManagement';
import './player-asset-manager.css';

interface PlayerAssetManagerProps {
  player: PlayerModel;
  onClose: () => void;
  onUpdate: (updatedPlayer: PlayerModel) => void;
}

interface AssetData {
  ships: any[];
  planets: any[];
  ports: any[];
  availableShips: any[];
  availablePlanets: any[];
  availablePorts: any[];
}

const PlayerAssetManager: React.FC<PlayerAssetManagerProps> = ({ 
  player, 
  onClose, 
  onUpdate 
}) => {
  const [assets, setAssets] = useState<AssetData>({
    ships: [],
    planets: [],
    ports: [],
    availableShips: [],
    availablePlanets: [],
    availablePorts: []
  });
  
  const [activeTab, setActiveTab] = useState<'ships' | 'planets' | 'ports'>('ships');
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [selectedAssets, setSelectedAssets] = useState<string[]>([]);

  useEffect(() => {
    loadPlayerAssets();
  }, [player.id]);

  const loadPlayerAssets = async () => {
    setLoading(true);
    try {
      // Load player's current assets using existing admin endpoints with owner_id filter
      const [shipsRes, planetsRes, portsRes] = await Promise.all([
        api.get(`/api/v1/admin/ships?ownerId=${player.id}`),
        api.get(`/api/v1/admin/planets?owner_id=${player.id}`),
        api.get(`/api/v1/admin/ports?owner_id=${player.id}`)
      ]);

      // Load unowned assets (assets available for assignment)
      const [availableShipsRes, availablePlanetsRes, availablePortsRes] = await Promise.all([
        // For ships, get all ships and filter client-side for unowned (TODO: add backend support)
        api.get('/api/v1/admin/ships?limit=100'),
        // For planets, use filter_colonized=false to get uncolonized planets
        api.get('/api/v1/admin/planets?filter_colonized=false&limit=100'),
        // For ports, get all and filter client-side (TODO: add backend support)
        api.get('/api/v1/admin/ports?limit=100')
      ]);

      // Filter unowned ships and ports client-side
      const allShips = (availableShipsRes.data as any)?.ships || [];
      const unownedShips = allShips.filter((ship: any) => !ship.owner || ship.owner.id === null || ship.owner.id === 'null');

      const allPorts = (availablePortsRes.data as any)?.ports || [];
      const unownedPorts = allPorts.filter((port: any) => !port.owner_id || port.owner_id === null);

      setAssets({
        ships: (shipsRes.data as any)?.ships || [],
        planets: (planetsRes.data as any)?.planets || [],
        ports: (portsRes.data as any)?.ports || [],
        availableShips: unownedShips,
        availablePlanets: (availablePlanetsRes.data as any)?.planets || [],
        availablePorts: unownedPorts
      });
    } catch (error) {
      console.error('Failed to load player assets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAssetAction = async (action: 'assign' | 'remove', assetType: string, assetIds: string[]) => {
    if (assetIds.length === 0) {
      alert('Please select assets to ' + action);
      return;
    }

    if (!confirm(`Are you sure you want to ${action} ${assetIds.length} ${assetType}(s)?`)) {
      return;
    }

    setActionLoading(true);
    try {
      const endpoint = action === 'assign' 
        ? `/api/v1/admin/players/${player.id}/assets/assign`
        : `/api/v1/admin/players/${player.id}/assets/remove`;

      await api.post(endpoint, {
        asset_type: assetType,
        asset_ids: assetIds
      });

      // Reload assets after action
      await loadPlayerAssets();
      setSelectedAssets([]);

      // Update player data if needed
      const updatedPlayer = { ...player };
      if (assetType === 'ships') {
        updatedPlayer.assets.ships_count += action === 'assign' ? assetIds.length : -assetIds.length;
      } else if (assetType === 'planets') {
        updatedPlayer.assets.planets_count += action === 'assign' ? assetIds.length : -assetIds.length;
      } else if (assetType === 'ports') {
        updatedPlayer.assets.ports_count += action === 'assign' ? assetIds.length : -assetIds.length;
      }
      onUpdate(updatedPlayer);

      alert(`Successfully ${action}ed ${assetIds.length} ${assetType}(s)`);
    } catch (error: any) {
      console.error(`Failed to ${action} assets:`, error);
      alert(`Failed to ${action} assets: ${error.response?.data?.detail || 'Unknown error'}`);
    } finally {
      setActionLoading(false);
    }
  };

  const toggleAssetSelection = (assetId: string) => {
    setSelectedAssets(prev => 
      prev.includes(assetId) 
        ? prev.filter(id => id !== assetId)
        : [...prev, assetId]
    );
  };

  const selectAllAssets = (assetList: any[]) => {
    const allIds = assetList.map(asset => asset.id);
    setSelectedAssets(allIds);
  };

  const clearSelection = () => {
    setSelectedAssets([]);
  };

  const renderAssetList = (assetList: any[], isOwned: boolean = true) => {
    if (assetList.length === 0) {
      return (
        <div className="empty-state">
          <p>No {activeTab} {isOwned ? 'owned' : 'available'}</p>
        </div>
      );
    }

    return (
      <div className="asset-list">
        {assetList.map((asset) => (
          <div 
            key={asset.id} 
            className={`asset-item ${selectedAssets.includes(asset.id) ? 'selected' : ''}`}
            onClick={() => toggleAssetSelection(asset.id)}
          >
            <div className="asset-checkbox">
              <input 
                type="checkbox" 
                checked={selectedAssets.includes(asset.id)}
                onChange={() => toggleAssetSelection(asset.id)}
                onClick={(e) => e.stopPropagation()}
              />
            </div>
            
            <div className="asset-info">
              <div className="asset-header">
                <h4>{asset.name}</h4>
                <span className="asset-type">
                  {activeTab === 'ships' && asset.ship_type}
                  {activeTab === 'planets' && asset.planet_type}
                  {activeTab === 'ports' && `Class ${asset.port_class}`}
                </span>
              </div>
              
              <div className="asset-details">
                {activeTab === 'ships' && (
                  <>
                    <span>Location: Sector {asset.current_sector_id || 'Unknown'}</span>
                    <span>Condition: {asset.condition || 100}%</span>
                    <span>Cargo: {asset.cargo_used || 0}/{asset.cargo_capacity || 0}</span>
                  </>
                )}
                
                {activeTab === 'planets' && (
                  <>
                    <span>Sector: {asset.sector_id || 'Unknown'}</span>
                    <span>Citadel: Level {asset.citadel_level || 0}</span>
                    <span>Population: {(asset.total_colonists || 0).toLocaleString()}</span>
                  </>
                )}
                
                {activeTab === 'ports' && (
                  <>
                    <span>Sector: {asset.sector_id || 'Unknown'}</span>
                    <span>Tax Rate: {asset.tax_rate || 0}%</span>
                    <span>Fighters: {asset.defense_fighters || 0}</span>
                  </>
                )}
              </div>
            </div>
            
            <div className="asset-value">
              {asset.estimated_value && (
                <span className="value">{asset.estimated_value.toLocaleString()} credits</span>
              )}
            </div>
          </div>
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="player-asset-manager loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <span>Loading player assets...</span>
        </div>
      </div>
    );
  }

  const currentAssets = assets[activeTab];
  const availableAssets = assets[`available${activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}` as keyof AssetData] as any[];

  return (
    <div className="player-asset-manager">
      <div className="manager-header">
        <h3>Asset Manager: {player.username}</h3>
        <button onClick={onClose} className="close-btn">×</button>
      </div>

      <div className="asset-tabs">
        <button 
          className={`tab ${activeTab === 'ships' ? 'active' : ''}`}
          onClick={() => {
            setActiveTab('ships');
            setSelectedAssets([]);
          }}
        >
          🚀 Ships ({assets.ships.length})
        </button>
        <button 
          className={`tab ${activeTab === 'planets' ? 'active' : ''}`}
          onClick={() => {
            setActiveTab('planets');
            setSelectedAssets([]);
          }}
        >
          🌍 Planets ({assets.planets.length})
        </button>
        <button 
          className={`tab ${activeTab === 'ports' ? 'active' : ''}`}
          onClick={() => {
            setActiveTab('ports');
            setSelectedAssets([]);
          }}
        >
          🏪 Ports ({assets.ports.length})
        </button>
      </div>

      <div className="asset-sections">
        <div className="owned-section">
          <div className="section-header">
            <h4>Owned {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}</h4>
            <div className="section-actions">
              {selectedAssets.length > 0 && (
                <>
                  <span className="selection-count">{selectedAssets.length} selected</span>
                  <button 
                    onClick={() => handleAssetAction('remove', activeTab, selectedAssets)}
                    className="btn btn-danger"
                    disabled={actionLoading}
                  >
                    Remove Selected
                  </button>
                  <button onClick={clearSelection} className="btn btn-secondary">
                    Clear Selection
                  </button>
                </>
              )}
              <button 
                onClick={() => selectAllAssets(currentAssets)}
                className="btn btn-outline"
                disabled={currentAssets.length === 0}
              >
                Select All
              </button>
            </div>
          </div>
          {renderAssetList(currentAssets, true)}
        </div>

        <div className="available-section">
          <div className="section-header">
            <h4>Available {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}</h4>
            <div className="section-actions">
              {selectedAssets.length > 0 && (
                <>
                  <span className="selection-count">{selectedAssets.length} selected</span>
                  <button 
                    onClick={() => handleAssetAction('assign', activeTab, selectedAssets)}
                    className="btn btn-primary"
                    disabled={actionLoading}
                  >
                    Assign Selected
                  </button>
                  <button onClick={clearSelection} className="btn btn-secondary">
                    Clear Selection
                  </button>
                </>
              )}
              <button 
                onClick={() => selectAllAssets(availableAssets)}
                className="btn btn-outline"
                disabled={availableAssets.length === 0}
              >
                Select All
              </button>
            </div>
          </div>
          {renderAssetList(availableAssets, false)}
        </div>
      </div>

      <div className="manager-footer">
        <div className="asset-summary">
          <div className="summary-item">
            <span className="label">Total Assets:</span>
            <span className="value">
              {assets.ships.length + assets.planets.length + assets.ports.length}
            </span>
          </div>
          <div className="summary-item">
            <span className="label">Estimated Value:</span>
            <span className="value">
              {(
                [...assets.ships, ...assets.planets, ...assets.ports]
                  .reduce((sum, asset) => sum + (asset.estimated_value || 0), 0)
              ).toLocaleString()} credits
            </span>
          </div>
        </div>
        
        <button onClick={onClose} className="btn btn-primary">
          Close
        </button>
      </div>
    </div>
  );
};

export default PlayerAssetManager;