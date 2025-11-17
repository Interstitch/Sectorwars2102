import React, { useState, useEffect } from 'react';
import { useFirstLogin } from '../../contexts/FirstLoginContext';
import ShipSelection from './ShipSelection';
import DialogueExchange from './DialogueExchange';
import OutcomeDisplay from './OutcomeDisplay';
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
    dialogueOutcome
  } = useFirstLogin();

  // Track which step of the first login experience we're on
  const [currentStep, setCurrentStep] = useState<'ship_selection' | 'dialogue' | 'completion'>(
    'ship_selection'
  );

  // Development logging (reduced verbosity)
  // console.log('FirstLoginContainer: Current step:', currentStep);
  // console.log('FirstLoginContainer: Session:', session);

  // Initialize the first login session when the component mounts
  useEffect(() => {
    if (requiresFirstLogin && !session && !isLoading) {
      // console.log('FirstLoginContainer: Starting session');
      startSession();
    }

    // Update the current step based on the session state
    if (session) {
      // console.log('FirstLoginContainer: Updating step from session:', session.current_step);
      setCurrentStep(session.current_step);
    }
  }, [requiresFirstLogin, session, isLoading]); // Remove startSession from deps to prevent loops

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
          <button onClick={resetSession} style={{padding: '5px 10px', margin: '10px', background: '#ff6b6b', color: 'white', border: 'none', borderRadius: '4px'}}>
            Reset Session (Debug)
          </button>
        </div>

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