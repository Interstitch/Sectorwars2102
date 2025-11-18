import React, { useState } from 'react';
import { useFirstLogin } from '../../contexts/FirstLoginContext';
import './first-login.css';

// Ship descriptions for display
const SHIP_DESCRIPTIONS: Record<string, string> = {
  SCOUT_SHIP: "Fast ship with excellent sensors and moderate cargo capacity. Great for exploration and reconnaissance missions.",
  CARGO_HAULER: "Large vessel with extensive cargo holds. Slower but ideal for trade routes with high volume goods.",
  ESCAPE_POD: "Small, basic ship with minimal features but good maneuverability. Built for survival, not comfort.",
  LIGHT_FREIGHTER: "Balanced ship with decent speed and cargo capacity. A popular choice for new traders in the sector.",
  DEFENDER: "Combat-focused vessel with reinforced hull and weapon hardpoints. Lower cargo capacity but high survivability.",
  FAST_COURIER: "Extremely fast ship designed for rapid transit between sectors. Limited cargo space but excellent for high-value, low-volume goods.",
  COLONY_SHIP: "Specialized vessel designed for colonization missions. Equipped with terraforming modules and space for many colonists.",
  CARRIER: "Massive military vessel with multiple drone bays and fleet coordination capabilities. The backbone of any serious fleet operation."
};

// Ship display names
const SHIP_NAMES: Record<string, string> = {
  SCOUT_SHIP: "Scout Ship",
  CARGO_HAULER: "Cargo Hauler",
  ESCAPE_POD: "Escape Pod",
  LIGHT_FREIGHTER: "Light Freighter",
  DEFENDER: "Defender",
  FAST_COURIER: "Fast Courier",
  COLONY_SHIP: "Colony Ship",
  CARRIER: "Carrier"
};

/**
 * ShipSelection component allows players to choose a ship and provide an initial dialogue response.
 */
const ShipSelection: React.FC = () => {
  const {
    session,
    availableShips,
    sessionLoaded,
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

  // Development logging
  console.log('[ShipSelection] Rendering with:', {
    availableShips,
    availableShipsLength: availableShips?.length,
    currentPrompt: currentPrompt?.substring(0, 100),
    sessionLoaded,
    session: session?.session_id
  });

  return (
    <div className="ship-selection-content">
      <div className="location-context">Callisto Colony Shipyard</div>
      
      <div className="dialogue-header">
        <div className="npc-avatar"></div>
        <div className="speaker-name">Security Guard</div>
        {/* Debug indicator for ship selection prompt */}
        {currentPrompt && currentPrompt.includes('[RULE-BASED]') && (
          <div className="debug-indicator debug-fallback">🤖 FALLBACK</div>
        )}
        {currentPrompt && currentPrompt.includes('[AI-ANTHROPIC]') && (
          <div className="debug-indicator debug-ai-anthropic">🧠 AI-CLAUDE</div>
        )}
        {currentPrompt && currentPrompt.includes('[AI-OPENAI]') && (
          <div className="debug-indicator debug-ai-openai">🧠 AI-GPT</div>
        )}
      </div>
      
      <div className="dialogue-text">
        {currentPrompt?.replace(/\[(RULE-BASED|AI-ANTHROPIC|AI-OPENAI)\]\s*/, '') || `The year is 2102. You find yourself in a bustling shipyard on the outskirts of the Callisto Colony. Your memory is hazy—a side effect of the cryo-sleep required for the journey here. A small orange cat darts between the landing gear of nearby ships, disappearing into the shadows. You're approaching what appears to be your escape pod when a stern-looking Security Guard blocks your path.

Guard: "Hold it right there! This area is restricted to registered pilots only. Which of these vessels belongs to you?"`}
      </div>
      
      {/* Ship selection grid */}
      <div className="ship-selection">
        {availableShips && availableShips.length > 0 ? availableShips.map(ship => (
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
        )) : (
          <div className="no-ships-message">
            {!sessionLoaded ? (
              <p>Loading available ships...</p>
            ) : (
              <div>
                <p>No ships available at this time.</p>
                <p>Session: {session ? 'Loaded' : 'Not loaded'}</p>
                <p>Available ships data: {JSON.stringify(availableShips)}</p>
              </div>
            )}
          </div>
        )}
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