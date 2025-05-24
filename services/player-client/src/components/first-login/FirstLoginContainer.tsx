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
    requiresFirstLogin,
    dialogueOutcome
  } = useFirstLogin();

  // Track which step of the first login experience we're on
  const [currentStep, setCurrentStep] = useState<'ship_selection' | 'dialogue' | 'completion'>(
    'ship_selection'
  );

  // Initialize the first login session when the component mounts
  useEffect(() => {
    if (requiresFirstLogin && !session) {
      startSession();
    }
    
    // Update the current step based on the session state
    if (session) {
      setCurrentStep(session.current_step);
    }
  }, [requiresFirstLogin, session, startSession]);

  // If the player doesn't need first login, don't show this component
  if (!requiresFirstLogin) {
    return null;
  }

  return (
    <div className="first-login-container">
      {isLoading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
        </div>
      )}

      {error && (
        <div className="error-message">
          {error}
          <button onClick={resetError}>Dismiss</button>
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
  );
};

export default FirstLoginContainer;