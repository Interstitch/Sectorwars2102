import React, { useState, useEffect } from 'react';
import { api } from '../../utils/auth';
import './universe-detail.css';

interface SectorDetailProps {
  sector: any;
  onBack: () => void;
  onPortClick: (port: any) => void;
  onPlanetClick: (planet: any) => void;
  onUpdate?: (updatedSector: any) => void;
}

const SectorDetail: React.FC<SectorDetailProps> = ({ sector, onBack, onPortClick, onPlanetClick, onUpdate }) => {
  const [portData, setPortData] = useState<any>(null);
  const [planetData, setPlanetData] = useState<any>(null);
  const [shipsInSector, setShipsInSector] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingField, setEditingField] = useState<string | null>(null);
  const [editValues, setEditValues] = useState<any>({});
  const [isUpdating, setIsUpdating] = useState(false);

  useEffect(() => {
    loadSectorDetails();
  }, [sector]);

  const loadSectorDetails = async () => {
    setLoading(true);
    try {
      // Load port data if sector has port
      if (sector.has_port) {
        const portResponse = await api.get(`/api/v1/admin/sectors/${sector.sector_id}/port`);
        setPortData(portResponse.data);
      }

      // Load planet data if sector has planet
      if (sector.has_planet) {
        const planetResponse = await api.get(`/api/v1/admin/sectors/${sector.sector_id}/planet`);
        setPlanetData(planetResponse.data);
      }

      // Load ships in sector
      const shipsResponse = await api.get(`/api/v1/admin/sectors/${sector.sector_id}/ships`);
      setShipsInSector((shipsResponse.data as any)?.ships || []);

    } catch (error) {
      console.error('Error loading sector details:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (field: string, currentValue: any) => {
    setEditingField(field);
    setEditValues({ ...editValues, [field]: currentValue });
  };

  const handleSave = async (field: string) => {
    try {
      setIsUpdating(true);
      const value = editValues[field];
      
      // Update sector via API
      await api.patch(`/api/v1/admin/sectors/${sector.id}`, {
        [field]: value
      });
      
      // Update local state
      const updatedSector = { ...sector, [field]: value };
      if (onUpdate) {
        onUpdate(updatedSector);
      }
      
      setEditingField(null);
    } catch (error) {
      console.error(`Failed to update ${field}:`, error);
      alert(`Failed to update ${field}`);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleCancel = () => {
    setEditingField(null);
    setEditValues({});
  };

  const EditableField: React.FC<{
    field: string;
    value: any;
    type?: 'text' | 'number' | 'select' | 'boolean';
    options?: string[];
  }> = ({ field, value, type = 'text', options }) => {
    const isEditing = editingField === field;
    
    if (isEditing) {
      return (
        <div className="editable-field editing">
          {type === 'select' && options ? (
            <select
              value={editValues[field] || value}
              onChange={(e) => setEditValues({ ...editValues, [field]: e.target.value })}
              disabled={isUpdating}
            >
              {options.map(option => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          ) : type === 'boolean' ? (
            <select
              value={editValues[field] !== undefined ? editValues[field] : value}
              onChange={(e) => setEditValues({ ...editValues, [field]: e.target.value === 'true' })}
              disabled={isUpdating}
            >
              <option value="true">Yes</option>
              <option value="false">No</option>
            </select>
          ) : (
            <input
              type={type}
              value={editValues[field] !== undefined ? editValues[field] : value}
              onChange={(e) => setEditValues({ 
                ...editValues, 
                [field]: type === 'number' ? parseFloat(e.target.value) || 0 : e.target.value 
              })}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleSave(field);
                if (e.key === 'Escape') handleCancel();
              }}
              disabled={isUpdating}
              autoFocus
            />
          )}
          <div className="edit-actions">
            <button 
              onClick={() => handleSave(field)} 
              disabled={isUpdating}
              className="save-btn"
            >
              ✓
            </button>
            <button 
              onClick={handleCancel} 
              disabled={isUpdating}
              className="cancel-btn"
            >
              ✕
            </button>
          </div>
        </div>
      );
    }

    return (
      <span 
        className="editable-field clickable" 
        onClick={() => handleEdit(field, value)}
        title="Click to edit"
      >
        {type === 'boolean' ? (value ? 'Yes' : 'No') : value}
      </span>
    );
  };

  const getSectorTypeColor = (type: string) => {
    switch (type.toUpperCase()) {
      case 'NEBULA': return '#8B4D8B';
      case 'ASTEROID_FIELD': return '#A67B5B';
      case 'RADIATION_ZONE': return '#FFB347';
      case 'WARP_STORM': return '#6B8BFF';
      default: return '#4B7C4B';
    }
  };

  return (
    <div className="sector-detail">
      <div className="detail-header">
        <button className="back-button" onClick={onBack}>
          ← Back to Universe
        </button>
        <h2>Sector {sector.sector_id}: {sector.name}</h2>
      </div>

      {loading ? (
        <div className="loading">Loading sector details...</div>
      ) : (
        <div className="detail-content">
          <div className="sector-info-panel">
            <h3>Sector Information</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="label">Name:</span>
                <span className="value">
                  <EditableField field="name" value={sector.name} type="text" />
                </span>
              </div>
              <div className="info-item">
                <span className="label">Type:</span>
                <span className="value" style={{ color: getSectorTypeColor(sector.type) }}>
                  <EditableField 
                    field="type" 
                    value={sector.type} 
                    type="select"
                    options={['NORMAL', 'NEBULA', 'ASTEROID_FIELD', 'RADIATION_ZONE', 'WARP_STORM']}
                  />
                </span>
              </div>
              <div className="info-item">
                <span className="label">X Coordinate:</span>
                <span className="value">
                  <EditableField field="x_coord" value={sector.x_coord} type="number" />
                </span>
              </div>
              <div className="info-item">
                <span className="label">Y Coordinate:</span>
                <span className="value">
                  <EditableField field="y_coord" value={sector.y_coord} type="number" />
                </span>
              </div>
              <div className="info-item">
                <span className="label">Z Coordinate:</span>
                <span className="value">
                  <EditableField field="z_coord" value={sector.z_coord} type="number" />
                </span>
              </div>
              <div className="info-item">
                <span className="label">Hazard Level:</span>
                <span className="value hazard-level" data-level={Math.floor(sector.hazard_level)}>
                  <EditableField field="hazard_level" value={sector.hazard_level} type="number" /> / 10
                </span>
              </div>
              <div className="info-item">
                <span className="label">Discovered:</span>
                <span className="value">
                  <EditableField field="is_discovered" value={sector.is_discovered} type="boolean" />
                </span>
              </div>
              <div className="info-item">
                <span className="label">Controlling Faction:</span>
                <span className="value">
                  <EditableField field="controlling_faction" value={sector.controlling_faction || 'None'} type="text" />
                </span>
              </div>
              <div className="info-item">
                <span className="label">Ships in Sector:</span>
                <span className="value">{shipsInSector.length}</span>
              </div>
            </div>
          </div>

          <div className="sector-features">
            {sector.has_port && portData && (
              <div className="feature-card port-card" onClick={() => onPortClick(portData)}>
                <h3>🏪 Port: {portData.name}</h3>
                <div className="feature-info">
                  <p>Class {portData.port_class} Trading Post</p>
                  <p>Tax Rate: {portData.tax_rate}%</p>
                  <p>Defense Drones: {portData.defense_fighters}</p>
                  <button className="view-details">View Port Details →</button>
                </div>
              </div>
            )}

            {sector.has_planet && planetData && (
              <div className="feature-card planet-card" onClick={() => onPlanetClick(planetData)}>
                <h3>🌍 Planet: {planetData.name}</h3>
                <div className="feature-info">
                  <p>Type: {planetData.planet_type}</p>
                  <p>Owner: {planetData.owner_name || 'Uncolonized'}</p>
                  <p>Citadel Level: {planetData.citadel_level}</p>
                  <button className="view-details">View Planet Details →</button>
                </div>
              </div>
            )}

            {sector.has_warp_tunnel && (
              <div className="feature-card warp-card">
                <h3>🌀 Warp Tunnels</h3>
                <div className="feature-info">
                  <p>Connected sectors via quantum tunnels</p>
                  <p className="warp-note">Use navigation computer to view connections</p>
                </div>
              </div>
            )}
          </div>

          {shipsInSector.length > 0 && (
            <div className="ships-panel">
              <h3>Ships in Sector</h3>
              <div className="ships-list">
                {shipsInSector.map((ship: any) => (
                  <div key={ship.id} className="ship-item">
                    <span className="ship-name">{ship.name}</span>
                    <span className="ship-type">{ship.type}</span>
                    <span className="ship-owner">{ship.owner_name}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SectorDetail;