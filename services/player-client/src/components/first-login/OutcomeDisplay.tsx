import React, { useState } from 'react';
import { useFirstLogin } from '../../contexts/FirstLoginContext';
import { useGame } from '../../contexts/GameContext';
import { useNavigate } from 'react-router-dom';
import './first-login.css';

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
 * OutcomeDisplay shows the final result of the first login experience,
 * including the awarded ship, credits, and any bonuses or penalties.
 */
const OutcomeDisplay: React.FC = () => {
  const {
    dialogueOutcome,
    completeFirstLogin,
    isLoading
  } = useFirstLogin();

  const { onFirstLoginComplete } = useGame();
  const navigate = useNavigate();
  const [isCompleting, setIsCompleting] = useState(false);
  const [completionResult, setCompletionResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  console.log('🎬 OutcomeDisplay: Rendered with dialogueOutcome:', dialogueOutcome);

  if (!dialogueOutcome) {
    console.log('⚠️ OutcomeDisplay: No dialogueOutcome, not rendering');
    return null;
  }

  console.log('✨ OutcomeDisplay: Displaying final outcome screen');

  const handleStartGame = async () => {
    console.log('🎮 OutcomeDisplay: Player clicked "Begin Your Journey"');
    setIsCompleting(true);
    setError(null);

    try {
      console.log('🏁 OutcomeDisplay: Calling completeFirstLogin()...');
      const result = await completeFirstLogin();
      console.log('✅ OutcomeDisplay: First Login marked complete in database:', result);
      setCompletionResult(result);

      // Refresh all game data in GameContext
      console.log('🔄 OutcomeDisplay: Refreshing game data...');
      await onFirstLoginComplete();

      // Redirect to the game dashboard after a short delay
      console.log('🚀 OutcomeDisplay: Redirecting to /game in 1.5 seconds...');
      setTimeout(() => {
        navigate('/game');
      }, 1500);
    } catch (err) {
      console.error('❌ OutcomeDisplay: Failed to complete first login:', err);
      setError('Failed to complete registration. Please try again.');
      setIsCompleting(false);
    }
  };

  // Helper function to get outcome message based on outcome type
  const getOutcomeMessage = () => {
    switch (dialogueOutcome.outcome) {
      case 'SUCCESS':
        return "Authentication successful. Welcome aboard, captain!";
      case 'PARTIAL_SUCCESS':
        return "Your story has inconsistencies, but you're cleared to proceed.";
      case 'FAILURE':
        return "Your story doesn't check out. You're limited to basic resources.";
      default:
        return "Processing complete. You may now enter the sector.";
    }
  };

  return (
    <div className="outcome-container">
      <h2 className="outcome-header">{getOutcomeMessage()}</h2>
      
      <div className="outcome-ship">
        <div className={`ship-image-large ${dialogueOutcome.awarded_ship.toLowerCase().replace(/_/g, '-')}`}>
          <div className="fallback">{SHIP_NAMES[dialogueOutcome.awarded_ship] || dialogueOutcome.awarded_ship}</div>
        </div>
        <div className="ship-name">{SHIP_NAMES[dialogueOutcome.awarded_ship] || dialogueOutcome.awarded_ship}</div>
      </div>
      
      <div className="outcome-details">
        <div className="outcome-item">
          <div className="outcome-icon">💰</div>
          <div className="outcome-value">{dialogueOutcome.starting_credits}</div>
          <div className="outcome-label">Credits</div>
        </div>
        
        <div className="outcome-item">
          <div className="outcome-icon">🔍</div>
          <div className="outcome-value">{dialogueOutcome.negotiation_skill}</div>
          <div className="outcome-label">Negotiation Skill</div>
        </div>
        
        {dialogueOutcome.negotiation_bonus && (
          <div className="outcome-item">
            <div className="outcome-icon">⭐</div>
            <div className="outcome-value">Trade Bonus</div>
            <div className="outcome-label">Special Ability</div>
          </div>
        )}
        
        {dialogueOutcome.notoriety_penalty && (
          <div className="outcome-item">
            <div className="outcome-icon">⚠️</div>
            <div className="outcome-value">Notoriety</div>
            <div className="outcome-label">Reputation Penalty</div>
          </div>
        )}
      </div>
      
      <div className="guard-final-message dialogue-text">
        <div className="dialogue-header">
          <div className="speaker-name">Security Guard:</div>
          {/* Debug indicator for final response */}
          {dialogueOutcome.guard_response.includes('[RULE-BASED]') && (
            <div className="debug-indicator debug-fallback">🤖 FALLBACK</div>
          )}
          {dialogueOutcome.guard_response.includes('[AI-ANTHROPIC]') && (
            <div className="debug-indicator debug-ai-anthropic">🧠 AI-CLAUDE</div>
          )}
          {dialogueOutcome.guard_response.includes('[AI-OPENAI]') && (
            <div className="debug-indicator debug-ai-openai">🧠 AI-GPT</div>
          )}
        </div>
        <div style={{marginTop: '10px'}}>
          {dialogueOutcome.guard_response.replace(/\[(RULE-BASED|AI-ANTHROPIC|AI-OPENAI)\]\s*/, '')}
        </div>
      </div>
      
      {error && <div className="error-message">{error}</div>}
      
      <button 
        className="outcome-start-button"
        onClick={handleStartGame}
        disabled={isLoading || isCompleting}
      >
        {isCompleting ? 'Initializing...' : 'Begin Your Journey'}
      </button>
    </div>
  );
};

export default OutcomeDisplay;