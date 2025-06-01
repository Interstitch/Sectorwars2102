import React, { useState, useEffect, useRef } from 'react';
import { useFirstLogin } from '../../contexts/FirstLoginContext';
import './first-login.css';

/**
 * DialogueExchange component handles the ongoing conversation between the player
 * and the security guard during the first login experience.
 */
const DialogueExchange: React.FC = () => {
  const {
    currentPrompt,
    dialogueHistory,
    submitResponse,
    isLoading,
    dialogueOutcome,
    session
  } = useFirstLogin();

  const [response, setResponse] = useState('');
  
  console.log('DialogueExchange: Rendered with session:', session);
  console.log('DialogueExchange: Current prompt:', currentPrompt);
  console.log('DialogueExchange: Dialogue history:', dialogueHistory);
  const dialogueHistoryRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll to the bottom of the dialogue history when it updates
  useEffect(() => {
    if (dialogueHistoryRef.current) {
      dialogueHistoryRef.current.scrollTop = dialogueHistoryRef.current.scrollHeight;
    }
  }, [dialogueHistory]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (response.trim() && !isLoading && !dialogueOutcome) {
      try {
        await submitResponse(response);
        setResponse('');
      } catch (error) {
        console.error('Error submitting response:', error);
      }
    }
  };

  return (
    <div className="dialogue-exchange-content">
      {/* Display dialogue history */}
      <div className="dialogue-history" ref={dialogueHistoryRef}>
        {dialogueHistory && dialogueHistory.length > 0 ? (
          dialogueHistory.map((exchange, index) => (
            <div key={index} className="history-item">
              {exchange.npc && (
                <div className="npc-message">
                  <div className="dialogue-header">
                    <div className="speaker-name">Security Guard:</div>
                    {/* Debug indicator */}
                    {exchange.npc.includes('[RULE-BASED]') && (
                      <div className="debug-indicator debug-fallback">🤖 FALLBACK</div>
                    )}
                    {exchange.npc.includes('[AI-ANTHROPIC]') && (
                      <div className="debug-indicator debug-ai-anthropic">🧠 AI-CLAUDE</div>
                    )}
                    {exchange.npc.includes('[AI-OPENAI]') && (
                      <div className="debug-indicator debug-ai-openai">🧠 AI-GPT</div>
                    )}
                  </div>
                  <div className="dialogue-text">{exchange.npc.replace(/\[(RULE-BASED|AI-ANTHROPIC|AI-OPENAI)\]\s*/, '')}</div>
                </div>
              )}
              {exchange.player && (
                <div className="player-message">
                  <div className="dialogue-text">{exchange.player}</div>
                </div>
              )}
            </div>
          ))
        ) : (
          <div className="loading-message">
            <p>Loading dialogue history...</p>
            <p>Current prompt: {currentPrompt || 'None'}</p>
            <p>Session ID: {session?.session_id || 'None'}</p>
          </div>
        )}
      </div>

      {/* Current prompt and response input */}
      {!dialogueOutcome && (
        <form onSubmit={handleSubmit} className="dialogue-response">
          <textarea
            className="response-input"
            placeholder="Type your response to the guard..."
            value={response}
            onChange={(e) => setResponse(e.target.value)}
            disabled={isLoading || !!dialogueOutcome}
          />
          
          <div className="response-buttons">
            <button 
              type="submit" 
              className="submit-response"
              disabled={!response.trim() || isLoading || !!dialogueOutcome}
            >
              Submit
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export default DialogueExchange;