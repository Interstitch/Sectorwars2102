import React, { useState } from 'react';
import { useFirstLogin } from '../../contexts/FirstLoginContext';
import './first-login.css';

// Ship descriptions for display
const SHIP_DESCRIPTIONS: Record<string, string> = {
  SCOUT_SHIP: "Fast ship with excellent sensors and moderate cargo capacity. Great for exploration and reconnaissance missions.",
  CARGO_FREIGHTER: "Large vessel with extensive cargo holds. Slower but ideal for trade routes with high volume goods.",
  ESCAPE_POD: "Small, basic ship with minimal features but good maneuverability. Built for survival, not comfort.",
  LIGHT_FREIGHTER: "Balanced ship with decent speed and cargo capacity. A popular choice for new traders in the sector.",
  DEFENDER: "Combat-focused vessel with reinforced hull and weapon hardpoints. Lower cargo capacity but high survivability.",
  FAST_COURIER: "Extremely fast ship designed for rapid transit between sectors. Limited cargo space but excellent for high-value, low-volume goods."
};

// Ship display names
const SHIP_NAMES: Record<string, string> = {
  SCOUT_SHIP: "Scout Ship",
  CARGO_FREIGHTER: "Cargo Freighter",
  ESCAPE_POD: "Escape Pod",
  LIGHT_FREIGHTER: "Light Freighter",
  DEFENDER: "Defender",
  FAST_COURIER: "Fast Courier"
};

/**
 * ShipSelection component allows players to choose a ship and provide an initial dialogue response.
 */
const ShipSelection: React.FC = () => {
  const {
    session,
    availableShips,
    claimShip,
    currentPrompt,
    isLoading
  } = useFirstLogin();

  const [selectedShip, setSelectedShip] = useState<string | null>(null);
  const [response, setResponse] = useState('');
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (selectedShip && response.trim()) {
      await claimShip(selectedShip, response);
    }
  };

  return (
    <div className="dialogue-box">
      <div className="dialogue-header">
        <div className="npc-avatar"></div>
        <div className="speaker-name">Security Guard</div>
      </div>
      
      <div className="dialogue-text">
        {currentPrompt || "Hold it right there! This area is restricted to registered pilots only. Which of these vessels belongs to you?"}
      </div>
      
      {/* Ship selection grid */}
      <div className="ship-selection">
        {availableShips.map(ship => (
          <div 
            key={ship}
            className={`ship-option ${selectedShip === ship ? 'selected' : ''}`}
            onClick={() => setSelectedShip(ship)}
          >
            <div className={`ship-image ${ship.toLowerCase().replace(/_/g, '-')}`}>
              <div className="fallback">{SHIP_NAMES[ship]}</div>
            </div>
            <div className="ship-name">{SHIP_NAMES[ship]}</div>
            <div className="ship-description">{SHIP_DESCRIPTIONS[ship]}</div>
          </div>
        ))}
      </div>
      
      <form onSubmit={handleSubmit} className="dialogue-response">
        <textarea
          className="response-input"
          placeholder="Type your response here..."
          value={response}
          onChange={(e) => setResponse(e.target.value)}
          disabled={isLoading}
        />
        
        <div className="response-buttons">
          <button 
            type="submit" 
            className="submit-response"
            disabled={!selectedShip || !response.trim() || isLoading}
          >
            Submit
          </button>
        </div>
      </form>
    </div>
  );
};

export default ShipSelection;