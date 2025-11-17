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

  // Only log once when component mounts with valid outcome
  React.useEffect(() => {
    if (dialogueOutcome) {
      console.log(`[FirstLogin:UI] Outcome screen displayed | ${dialogueOutcome.outcome}`);
    }
  }, [dialogueOutcome]);

  if (!dialogueOutcome) {
    return null;
  }

  const handleStartGame = async () => {
    setIsCompleting(true);
    setError(null);

    try {
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

      {/* Score Breakdown - shows why player passed/failed */}
      {dialogueOutcome.final_persuasion_score !== undefined && (
        <div className="score-breakdown" style={{
          margin: '20px 0',
          padding: '15px',
          background: dialogueOutcome.outcome === 'SUCCESS' ? 'rgba(0, 200, 100, 0.1)' : 'rgba(200, 100, 0, 0.1)',
          borderRadius: '8px',
          border: dialogueOutcome.outcome === 'SUCCESS' ? '1px solid rgba(0, 200, 100, 0.3)' : '1px solid rgba(200, 100, 0, 0.3)'
        }}>
          <div style={{fontWeight: 'bold', marginBottom: '10px', color: '#aaa'}}>
            Evaluation Results:
          </div>
          <div style={{fontSize: '0.9em', lineHeight: '1.6'}}>
            <div>Your Persuasion Score: <strong>{dialogueOutcome.final_persuasion_score.toFixed(4)}</strong></div>
            <div>Negotiation Level: <strong>{dialogueOutcome.negotiation_skill}</strong></div>
            <div style={{marginTop: '8px', paddingTop: '8px', borderTop: '1px solid rgba(255, 255, 255, 0.1)'}}>
              {dialogueOutcome.outcome === 'SUCCESS' ? (
                <span style={{color: '#0c0'}}>
                  ✓ Your score met the threshold for {SHIP_NAMES[dialogueOutcome.awarded_ship] || dialogueOutcome.awarded_ship}
                </span>
              ) : (
                <span style={{color: '#c80'}}>
                  ✗ Your score didn't meet the required threshold. Keep practicing your negotiation skills!
                </span>
              )}
            </div>
          </div>
        </div>
      )}

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