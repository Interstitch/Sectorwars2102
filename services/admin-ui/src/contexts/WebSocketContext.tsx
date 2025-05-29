import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { useAuth } from './AuthContext';
import { websocketService, WebSocketEvents } from '../services/websocket';

interface WebSocketContextValue {
  isConnected: boolean;
  subscribe: <K extends keyof WebSocketEvents>(
    event: K,
    handler: WebSocketEvents[K]
  ) => () => void;
  unsubscribe: <K extends keyof WebSocketEvents>(
    event: K,
    handler?: WebSocketEvents[K]
  ) => void;
  send: (event: string, data: any) => void;
}

const WebSocketContext = createContext<WebSocketContextValue | null>(null);

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within WebSocketProvider');
  }
  return context;
};

interface WebSocketProviderProps {
  children: React.ReactNode;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const { user, token } = useAuth();
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (user && token) {
      // Connect to WebSocket when user is authenticated
      websocketService.connect(token)
        .then(() => {
          setIsConnected(true);
          console.log('WebSocket connected successfully');
        })
        .catch(error => {
          console.error('Failed to connect WebSocket:', error);
          setIsConnected(false);
        });

      // Set up connection status monitoring
      const checkConnection = setInterval(() => {
        setIsConnected(websocketService.isConnected());
      }, 5000);

      return () => {
        clearInterval(checkConnection);
        websocketService.disconnect();
        setIsConnected(false);
      };
    } else {
      // Disconnect when user logs out
      websocketService.disconnect();
      setIsConnected(false);
    }
  }, [user, token]);

  const subscribe = useCallback(<K extends keyof WebSocketEvents>(
    event: K,
    handler: WebSocketEvents[K]
  ) => {
    return websocketService.on(event, handler);
  }, []);

  const unsubscribe = useCallback(<K extends keyof WebSocketEvents>(
    event: K,
    handler?: WebSocketEvents[K]
  ) => {
    websocketService.off(event, handler);
  }, []);

  const send = useCallback((event: string, data: any) => {
    websocketService.send(event, data);
  }, []);

  const value: WebSocketContextValue = {
    isConnected,
    subscribe,
    unsubscribe,
    send
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

// Custom hooks for specific event types
export const useEconomyUpdates = (
  onMarketUpdate?: (data: any) => void,
  onPriceChange?: (data: any) => void,
  onIntervention?: (data: any) => void
) => {
  const { subscribe } = useWebSocket();

  useEffect(() => {
    const unsubscribers: (() => void)[] = [];

    if (onMarketUpdate) {
      unsubscribers.push(subscribe('economy:market-update', onMarketUpdate));
    }
    if (onPriceChange) {
      unsubscribers.push(subscribe('economy:price-change', onPriceChange));
    }
    if (onIntervention) {
      unsubscribers.push(subscribe('economy:intervention', onIntervention));
    }

    return () => {
      unsubscribers.forEach(unsub => unsub());
    };
  }, [subscribe, onMarketUpdate, onPriceChange, onIntervention]);
};

export const useCombatUpdates = (
  onNewEvent?: (data: any) => void,
  onDisputeFiled?: (data: any) => void,
  onStatsUpdate?: (data: any) => void
) => {
  const { subscribe } = useWebSocket();

  useEffect(() => {
    const unsubscribers: (() => void)[] = [];

    if (onNewEvent) {
      unsubscribers.push(subscribe('combat:new-event', onNewEvent));
    }
    if (onDisputeFiled) {
      unsubscribers.push(subscribe('combat:dispute-filed', onDisputeFiled));
    }
    if (onStatsUpdate) {
      unsubscribers.push(subscribe('combat:stats-update', onStatsUpdate));
    }

    return () => {
      unsubscribers.forEach(unsub => unsub());
    };
  }, [subscribe, onNewEvent, onDisputeFiled, onStatsUpdate]);
};

export const useFleetUpdates = (
  onStatusChange?: (data: any) => void,
  onMaintenanceAlert?: (data: any) => void,
  onEmergency?: (data: any) => void
) => {
  const { subscribe } = useWebSocket();

  useEffect(() => {
    const unsubscribers: (() => void)[] = [];

    if (onStatusChange) {
      unsubscribers.push(subscribe('fleet:status-change', onStatusChange));
    }
    if (onMaintenanceAlert) {
      unsubscribers.push(subscribe('fleet:maintenance-alert', onMaintenanceAlert));
    }
    if (onEmergency) {
      unsubscribers.push(subscribe('fleet:emergency', onEmergency));
    }

    return () => {
      unsubscribers.forEach(unsub => unsub());
    };
  }, [subscribe, onStatusChange, onMaintenanceAlert, onEmergency]);
};

export const useTeamUpdates = (
  onTeamUpdate?: (data: any) => void,
  onAllianceChange?: (data: any) => void,
  onMemberChange?: (data: any) => void
) => {
  const { subscribe } = useWebSocket();

  useEffect(() => {
    const unsubscribers: (() => void)[] = [];

    if (onTeamUpdate) {
      unsubscribers.push(subscribe('team:update', onTeamUpdate));
    }
    if (onAllianceChange) {
      unsubscribers.push(subscribe('team:alliance-change', onAllianceChange));
    }
    if (onMemberChange) {
      unsubscribers.push(subscribe('team:member-change', onMemberChange));
    }

    return () => {
      unsubscribers.forEach(unsub => unsub());
    };
  }, [subscribe, onTeamUpdate, onAllianceChange, onMemberChange]);
};

export const useSystemAlerts = (
  onAlert?: (data: any) => void,
  onPerformance?: (data: any) => void,
  onSecurityEvent?: (data: any) => void
) => {
  const { subscribe } = useWebSocket();

  useEffect(() => {
    const unsubscribers: (() => void)[] = [];

    if (onAlert) {
      unsubscribers.push(subscribe('system:alert', onAlert));
    }
    if (onPerformance) {
      unsubscribers.push(subscribe('system:performance', onPerformance));
    }
    if (onSecurityEvent) {
      unsubscribers.push(subscribe('system:security-event', onSecurityEvent));
    }

    return () => {
      unsubscribers.forEach(unsub => unsub());
    };
  }, [subscribe, onAlert, onPerformance, onSecurityEvent]);
};

export const useAIUpdates = (
  onModelUpdate?: (data: any) => void,
  onPredictionMade?: (data: any) => void,
  onRecommendationSent?: (data: any) => void,
  onProfileUpdated?: (data: any) => void,
  onTrainingComplete?: (data: any) => void,
  onAccuracyUpdate?: (data: any) => void,
  onRouteUpdate?: (data: any) => void,
  onRouteStatsUpdate?: (data: any) => void,
  onSegmentUpdate?: (data: any) => void,
  onTrendUpdate?: (data: any) => void
) => {
  const { subscribe } = useWebSocket();

  useEffect(() => {
    const unsubscribers: (() => void)[] = [];

    if (onModelUpdate) {
      unsubscribers.push(subscribe('ai:model-update', onModelUpdate));
    }
    if (onPredictionMade) {
      unsubscribers.push(subscribe('ai:prediction-made', onPredictionMade));
    }
    if (onRecommendationSent) {
      unsubscribers.push(subscribe('ai:recommendation-sent', onRecommendationSent));
    }
    if (onProfileUpdated) {
      unsubscribers.push(subscribe('ai:profile-updated', onProfileUpdated));
    }
    if (onTrainingComplete) {
      unsubscribers.push(subscribe('ai:training-complete', onTrainingComplete));
    }
    if (onAccuracyUpdate) {
      unsubscribers.push(subscribe('ai:accuracy-update', onAccuracyUpdate));
    }
    if (onRouteUpdate) {
      unsubscribers.push(subscribe('ai:route-update', onRouteUpdate));
    }
    if (onRouteStatsUpdate) {
      unsubscribers.push(subscribe('ai:route-stats-update', onRouteStatsUpdate));
    }
    if (onSegmentUpdate) {
      unsubscribers.push(subscribe('ai:segment-update', onSegmentUpdate));
    }
    if (onTrendUpdate) {
      unsubscribers.push(subscribe('ai:trend-update', onTrendUpdate));
    }

    return () => {
      unsubscribers.forEach(unsub => unsub());
    };
  }, [subscribe, onModelUpdate, onPredictionMade, onRecommendationSent, onProfileUpdated, onTrainingComplete, onAccuracyUpdate, onRouteUpdate, onRouteStatsUpdate, onSegmentUpdate, onTrendUpdate]);
};