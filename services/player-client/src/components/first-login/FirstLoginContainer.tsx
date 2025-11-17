import React, { useState, useEffect } from 'react';
import { useFirstLogin } from '../../contexts/FirstLoginContext';
import ShipSelection from './ShipSelection';
import DialogueExchange from './DialogueExchange';
import OutcomeDisplay from './OutcomeDisplay';
import TrustMeter from './TrustMeter';
import { getGuardForSession, GuardPersonality } from '../../utils/guardPersonalities';
import './first-login.css';

/**
 * FirstLoginContainer serves as the main component for the first login experience.
 * It manages the overall flow between ship selection, dialogue exchanges, and outcome display.
 */
const FirstLoginContainer: React.FC = () => {
  const {
    isLoading,
    error,
    session,
    startSession,
    resetError,
    resetSession,
    requiresFirstLogin,
    dialogueOutcome,
    dialogueHistory
  } = useFirstLogin();

  // Track which step of the first login experience we're on
  const [currentStep, setCurrentStep] = useState<'ship_selection' | 'dialogue' | 'completion'>(
    'ship_selection'
  );

  // Guard personality (generated once per session)
  const [guardPersonality, setGuardPersonality] = useState<GuardPersonality | null>(null);

  // Trust level (0-1) that updates with each response
  const [currentTrust, setCurrentTrust] = useState<number>(0.5);

  // Update trust level based on dialogue history (simple heuristic)
  useEffect(() => {
    if (dialogueHistory && dialogueHistory.length > 1) {
      // Count completed player responses
      const completedExchanges = dialogueHistory.filter(ex => ex.player).length;
      if (completedExchanges > 0) {
        // Gradually adjust trust based on number of exchanges
        // More exchanges without failure = increasing trust
        const trustAdjustment = completedExchanges * 0.1;
        const newTrust = Math.min(1.0, (guardPersonality?.baseSuspicion ? 1 - guardPersonality.baseSuspicion : 0.5) + trustAdjustment);
        setCurrentTrust(newTrust);
      }
    }
  }, [dialogueHistory, guardPersonality]);

  // Development logging (reduced verbosity)
  // console.log('FirstLoginContainer: Current step:', currentStep);
  // console.log('FirstLoginContainer: Session:', session);

  // Initialize the first login session when the component mounts
  useEffect(() => {
    if (requiresFirstLogin && !session && !isLoading) {
      startSession();
    }

    // Update the current step based on the session state
    if (session) {
      setCurrentStep(session.current_step);

      // Generate guard personality for this session (deterministic based on session ID)
      if (!guardPersonality && session.session_id) {
        const guard = getGuardForSession(session.session_id);
        setGuardPersonality(guard);
        // Set initial trust based on guard's base suspicion (inverted)
        setCurrentTrust(1 - guard.baseSuspicion);
        console.log(`[FirstLogin:Guard] ${guard.title} ${guard.name} | Trait: ${guard.trait} | Base Trust: ${(1 - guard.baseSuspicion).toFixed(2)}`);
      }
    }
  }, [requiresFirstLogin, session, isLoading, guardPersonality]);

  // If the player doesn't need first login, don't show this component
  if (!requiresFirstLogin) {
    return null;
  }

  return (
    <div className="first-login-container">
      {/* Always show some content so the container is visible */}
      <div className="dialogue-box">
        <div className="game-title-header">
          <h1 className="game-title">SECTOR WARS 2102</h1>
          <p className="game-subtitle">Welcome to the Galaxy - Security Registration</p>
          {guardPersonality && (
            <div style={{
              margin: '10px 0',
              padding: '10px',
              background: 'rgba(0, 0, 0, 0.3)',
              borderRadius: '4px',
              fontSize: '0.9em',
              color: '#bbb'
            }}>
              <div style={{fontWeight: 'bold', color: '#fff'}}>
                {guardPersonality.title} {guardPersonality.name}
              </div>
              <div style={{fontSize: '0.85em', fontStyle: 'italic', marginTop: '4px'}}>
                {guardPersonality.description}
              </div>
            </div>
          )}
          <button onClick={resetSession} style={{padding: '5px 10px', margin: '10px', background: '#ff6b6b', color: 'white', border: 'none', borderRadius: '4px'}}>
            Reset Session (Debug)
          </button>
        </div>

        {/* Trust Meter - shows during dialogue phase */}
        {currentStep === 'dialogue' && guardPersonality && (
          <TrustMeter trustLevel={currentTrust} guardName={guardPersonality.name} />
        )}

        {isLoading && (
          <div className="loading-message">
            <div className="loading-spinner"></div>
            <p>Initializing security protocols...</p>
          </div>
        )}

        {error && (
          <div className="error-message">
            <p>{error}</p>
            <button onClick={resetError}>Try Again</button>
          </div>
        )}

        {!isLoading && !error && !session && (
          <div className="waiting-message">
            <p>Preparing your arrival at the spaceport...</p>
            <button onClick={startSession}>Begin Registration</button>
          </div>
        )}

        {currentStep === 'ship_selection' && session && (
          <ShipSelection />
        )}

        {currentStep === 'dialogue' && session && (
          <DialogueExchange />
        )}

        {(currentStep === 'completion' || dialogueOutcome) && (
          <OutcomeDisplay />
        )}
      </div>
    </div>
  );
};

export default FirstLoginContainer;