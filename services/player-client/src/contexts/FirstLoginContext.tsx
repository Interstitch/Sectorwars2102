import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';
import { useAuth } from './AuthContext';

// Create an axios instance that uses the Vite proxy
const api = axios.create({
  baseURL: '', // Empty baseURL to use current origin and proxy
  withCredentials: false
});

// Add interceptor to include auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Types for first login state
export interface FirstLoginSession {
  session_id: string;
  player_id: string;
  available_ships: string[];
  current_step: 'ship_selection' | 'dialogue' | 'completion';
  npc_prompt: string;
  exchange_id?: string;
  sequence_number?: number;
}

export interface DialogueAnalysis {
  exchange_id: string;
  analysis: {
    persuasiveness: number;
    confidence: number;
    consistency: number;
  };
  is_final: boolean;
  outcome?: {
    outcome: string;
    awarded_ship: string;
    starting_credits: number;
    negotiation_skill: string;
    final_persuasion_score: number;
    negotiation_bonus: boolean;
    notoriety_penalty: boolean;
    guard_response: string;
  };
  next_question?: string;
  next_exchange_id?: string;
}

export interface CompleteFirstLoginResult {
  player_id: string;
  nickname?: string;
  credits: number;
  ship: {
    id: string;
    name: string;
    type: string;
  };
  negotiation_bonus: boolean;
  notoriety_penalty: boolean;
}

interface FirstLoginContextType {
  requiresFirstLogin: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Session data
  session: FirstLoginSession | null;
  startSession: () => Promise<void>;
  
  // Dialogue state
  currentPrompt: string;
  exchangeId: string | null;
  dialogueHistory: {
    npc: string;
    player: string;
  }[];
  
  // Ship selection
  availableShips: string[];
  sessionLoaded: boolean;
  claimShip: (shipType: string, response: string) => Promise<void>;
  
  // Dialogue interaction
  submitResponse: (response: string) => Promise<DialogueAnalysis>;
  
  // Dialogue outcome
  dialogueOutcome: DialogueAnalysis['outcome'] | null;
  completeFirstLogin: () => Promise<CompleteFirstLoginResult>;
  
  // UI state helpers
  resetError: () => void;
  resetSession: () => void;
}

const FirstLoginContext = createContext<FirstLoginContextType | undefined>(undefined);

export const FirstLoginProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  
  // Basic state
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [requiresFirstLogin, setRequiresFirstLogin] = useState<boolean>(false);
  
  // Session state
  const [session, setSession] = useState<FirstLoginSession | null>(null);
  const [dialogueHistory, setDialogueHistory] = useState<{ npc: string; player: string; }[]>([]);
  const [currentPrompt, setCurrentPrompt] = useState<string>('');
  const [exchangeId, setExchangeId] = useState<string | null>(null);
  const [dialogueOutcome, setDialogueOutcome] = useState<DialogueAnalysis['outcome'] | null>(null);
  
  // Use the axios instance configured at the top of the file (with proxy)
  
  // Rate limiting state
  const [lastCheckTime, setLastCheckTime] = useState<number>(0);
  const [lastSessionTime, setLastSessionTime] = useState<number>(0);
  const CHECK_COOLDOWN = 5000; // 5 seconds between checks
  const SESSION_COOLDOWN = 5000; // 5 seconds between session starts

  // Check if first login is required when user logs in
  useEffect(() => {
    if (isAuthenticated && user) {
      const now = Date.now();
      if (now - lastCheckTime > CHECK_COOLDOWN) {
        setLastCheckTime(now);
        checkFirstLoginStatus();
      }
    }
  }, [isAuthenticated, user, lastCheckTime]);
  
  // Check if the player needs to go through first login
  const checkFirstLoginStatus = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.get('/api/v1/first-login/status');
      setRequiresFirstLogin((response.data as any).requires_first_login);
      
      // If first login is required and there's an active session, load it
      if ((response.data as any).requires_first_login && (response.data as any).session_id) {
        await startSession();
      }
    } catch (error) {
      console.error('Error checking first login status:', error);
      setError('Failed to check first login status.');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Start or resume a first login session
  const startSession = async () => {
    // Rate limiting check
    const now = Date.now();
    if (now - lastSessionTime < SESSION_COOLDOWN) {
      console.log('FirstLoginContext: Skipping startSession due to rate limiting');
      return;
    }
    setLastSessionTime(now);
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.post('/api/v1/first-login/session');
      console.log('FirstLogin: Session response:', response.data);
      setSession(response.data as FirstLoginSession);
      
      // Set initial prompt and exchange ID
      setCurrentPrompt((response.data as any).npc_prompt);
      setExchangeId((response.data as any).exchange_id || null);
      
      // Initialize dialogue history with the first NPC prompt
      setDialogueHistory([{ npc: (response.data as any).npc_prompt, player: '' }]);
    } catch (error: any) {
      console.error('Error starting first login session:', error);
      
      // Handle specific error types
      if (error.response?.status === 429) {
        console.log('FirstLoginContext: Rate limited, will retry in 10 seconds');
        setError('Too many requests. Please wait a moment.');
        // Retry after a longer delay for rate limiting
        setTimeout(() => {
          console.log('FirstLoginContext: Retrying after rate limit');
          startSession();
        }, 10000); // 10 seconds
        return;
      } else if (error.response?.status === 500) {
        setError('Server error. Please try again in a few moments.');
      } else {
        setError('Failed to start first login session.');
      }
    } finally {
      setIsLoading(false);
    }
  };
  
  // Claim a ship and submit initial dialogue response
  const claimShip = async (shipType: string, response: string) => {
    setIsLoading(true);
    setError(null);

    console.log('🚀 FirstLogin: Claiming ship:', shipType);
    console.log('💬 FirstLogin: Initial dialogue response:', response);
    console.log('📋 FirstLogin: Current session:', session);

    try {
      const payload = {
        ship_type: shipType,
        dialogue_response: response
      };
      console.log('📤 FirstLogin: Sending claim payload:', payload);

      const result = await api.post('/api/v1/first-login/claim-ship', payload);

      console.log('✅ FirstLogin: Ship claimed successfully, moving to dialogue phase');
      console.log('❓ FirstLogin: First guard question:', result.data.npc_prompt);

      setSession(result.data);

      // Update dialogue history
      setDialogueHistory(prev => [
        ...prev,
        { npc: '', player: response },
        { npc: result.data.npc_prompt, player: '' }
      ]);

      // Set new prompt and exchange ID
      setCurrentPrompt(result.data.npc_prompt);
      setExchangeId(result.data.exchange_id || null);
    } catch (error: any) {
      console.error('❌ FirstLogin: Error claiming ship:', error);
      console.error('Error response:', error.response);
      console.error('Error response data:', error.response?.data);
      console.error('Error response status:', error.response?.status);
      console.error('Error response headers:', error.response?.headers);
      
      // More specific error messages
      if (error.response?.status === 401) {
        setError('Authentication failed. Please log in again.');
      } else if (error.response?.status === 400) {
        setError(error.response?.data?.detail || 'Invalid ship selection or response.');
      } else if (error.response?.status === 500) {
        console.error('500 Error details:', error.response?.data);
        setError('Server error. Please try again later.');
      } else if (error.code === 'ERR_NETWORK') {
        setError('Network error. Please check your connection.');
      } else {
        setError('Failed to claim ship. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };
  
  // Submit a dialogue response
  const submitResponse = async (response: string): Promise<DialogueAnalysis> => {
    setIsLoading(true);
    setError(null);

    try {
      if (!exchangeId) {
        throw new Error('No active dialogue exchange.');
      }

      console.log('🎯 FirstLogin: Submitting dialogue response:', {
        exchangeId,
        response: response.substring(0, 100) + (response.length > 100 ? '...' : '')
      });

      const result = await api.post(`/api/v1/first-login/dialogue/${exchangeId}`, {
        response
      });

      console.log('📊 FirstLogin: Dialogue analysis received:', {
        is_final: result.data.is_final,
        has_outcome: !!result.data.outcome,
        has_next_question: !!result.data.next_question,
        analysis: result.data.analysis
      });

      // Log the scoring details
      if (result.data.analysis) {
        console.log('⭐ FirstLogin: Response Scores:', {
          persuasiveness: result.data.analysis.persuasiveness,
          confidence: result.data.analysis.confidence,
          consistency: result.data.analysis.consistency,
          negotiation_skill: result.data.analysis.negotiation_skill,
          believability: result.data.analysis.believability,
          guard_mood: result.data.analysis.guard_mood,
          inconsistencies: result.data.analysis.inconsistencies
        });
      }

      // Update dialogue history
      setDialogueHistory(prev => [
        ...prev.slice(0, prev.length - 1),
        { ...prev[prev.length - 1], player: response }
      ]);

      // If there's a next question, add it to history and update state
      if (result.data.next_question) {
        console.log('❓ FirstLogin: Guard asks another question');
        setDialogueHistory(prev => [
          ...prev,
          { npc: result.data.next_question, player: '' }
        ]);
        setCurrentPrompt(result.data.next_question);
        setExchangeId(result.data.next_exchange_id || null);
      }

      // If this is the final response, store the outcome
      if (result.data.is_final && result.data.outcome) {
        console.log('🎉 FirstLogin: DIALOGUE COMPLETE! Final outcome:', {
          outcome: result.data.outcome.outcome,
          awarded_ship: result.data.outcome.awarded_ship,
          starting_credits: result.data.outcome.starting_credits,
          negotiation_skill: result.data.outcome.negotiation_skill,
          negotiation_bonus: result.data.outcome.negotiation_bonus,
          notoriety_penalty: result.data.outcome.notoriety_penalty
        });

        setDialogueOutcome(result.data.outcome);

        // Add the guard's final response to the history
        setDialogueHistory(prev => [
          ...prev,
          { npc: result.data.outcome.guard_response, player: '' }
        ]);

        // Update the current prompt
        setCurrentPrompt(result.data.outcome.guard_response);

        console.log('✅ FirstLogin: OutcomeDisplay should now render');
      }

      return result.data;
    } catch (error) {
      console.error('❌ FirstLogin: Error submitting dialogue response:', error);
      setError('Failed to submit dialogue response.');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };
  
  // Complete the first login process
  const completeFirstLogin = async (): Promise<CompleteFirstLoginResult> => {
    setIsLoading(true);
    setError(null);

    try {
      console.log('🏁 FirstLogin: Calling /complete endpoint to finalize First Login');
      const result = await api.post('/api/v1/first-login/complete');

      console.log('✅ FirstLogin: Completion successful:', result.data);

      // First login is now complete
      setRequiresFirstLogin(false);

      return result.data;
    } catch (error) {
      console.error('❌ FirstLogin: Error completing first login:', error);
      setError('Failed to complete first login process.');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };
  
  // Reset error state
  const resetError = () => setError(null);
  
  const resetSession = async () => {
    try {
      // Clear frontend state first
      setSession(null);
      setDialogueHistory([]);
      setCurrentPrompt('');
      setExchangeId(null);
      setDialogueOutcome(null);
      setError(null);
      
      // Try to reset server-side session
      await api.delete('/api/v1/first-login/session');
      console.log('FirstLogin: Server session reset successfully');
    } catch (error) {
      console.log('FirstLogin: Could not reset server session (this is okay):', error);
      // Don't show error to user as this is just a cleanup attempt
    }
  };
  
  // Context value
  const value = {
    requiresFirstLogin,
    isLoading,
    error,
    
    session,
    startSession,
    
    currentPrompt,
    exchangeId,
    dialogueHistory,
    
    availableShips: session?.available_ships || [],
    sessionLoaded: !!session,
    claimShip,
    
    submitResponse,
    
    dialogueOutcome,
    completeFirstLogin,
    
    resetError,
    resetSession
  };
  
  return <FirstLoginContext.Provider value={value}>{children}</FirstLoginContext.Provider>;
};

// Hook for using the first login context
export const useFirstLogin = () => {
  const context = useContext(FirstLoginContext);
  if (context === undefined) {
    throw new Error('useFirstLogin must be used within a FirstLoginProvider');
  }
  return context;
};