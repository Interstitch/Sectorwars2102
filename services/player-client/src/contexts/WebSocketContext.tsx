import React, { createContext, useContext, useEffect, useState, useCallback, useRef } from 'react';
import websocketService, { 
  WebSocketMessage, 
  ChatMessage, 
  PlayerMovementMessage, 
  SectorPlayersMessage,
  NotificationMessage,
  ARIAResponseMessage,
  QuantumTradingResponse,
  QuantumMarketDataMessage
} from '../services/websocket';
import { useAuth } from './AuthContext';

interface WebSocketContextType {
  // Connection status
  isConnected: boolean;
  connectionStatus: string;
  
  // Chat functionality
  chatMessages: ChatMessage[];
  sendChatMessage: (content: string, targetType?: 'sector' | 'team' | 'global') => boolean;
  clearChatMessages: () => void;
  
  // ARIA AI Chat functionality
  sendARIAMessage: (content: string, conversationId?: string, context?: string) => boolean;
  ariaMessages: Array<{
    id: string;
    type: 'user' | 'ai';
    content: string;
    timestamp: string;
    conversationId?: string;
    confidence?: number;
    actions?: Array<{
      type: string;
      [key: string]: any;
    }>;
    suggestions?: string[];
  }>;
  clearARIAMessages: () => void;
  
  // Player presence
  sectorPlayers: Array<{
    user_id: string;
    username: string;
    connected_at: string;
    last_heartbeat: string;
  }>;
  requestSectorPlayers: () => void;
  
  // Notifications
  notifications: NotificationMessage[];
  addNotification: (notification: Omit<NotificationMessage, 'type' | 'timestamp'>) => void;
  removeNotification: (index: number) => void;
  clearNotifications: () => void;
  
  // Player movement tracking
  recentMovements: PlayerMovementMessage[];
  
  // Quantum Trading functionality
  quantumTrades: Array<{
    trade_id: string;
    trade_type: 'buy' | 'sell';
    commodity: string;
    quantity: number;
    superposition_states: Array<{
      price: number;
      profit: number;
      probability: number;
      outcome: string;
    }>;
    manipulation_warning: boolean;
    risk_score: number;
    confidence_interval: [number, number];
    dna_sequence?: string;
    timestamp: string;
  }>;
  
  ghostTrades: Array<{
    trade_id: string;
    trade_type: 'buy' | 'sell';
    commodity: string;
    quantity: number;
    expected_profit: number;
    success_probability: number;
    risk_assessment: string;
    timestamp: string;
  }>;
  
  quantumMarketData: Array<{
    sector_id: number;
    commodity_prices: Array<{
      commodity: string;
      current_price: number;
      quantum_volatility: number;
      manipulation_probability: number;
      ai_recommendation: 'buy' | 'sell' | 'hold';
      aria_insights: string[];
    }>;
    timestamp: string;
  }>;
  
  // Quantum Trading methods
  createQuantumTrade: (
    tradeType: 'buy' | 'sell',
    commodity: string,
    quantity: number,
    sectorId?: number,
    portId?: number,
    maxPrice?: number,
    minPrice?: number,
    superpositionStates?: number
  ) => boolean;
  
  collapseQuantumTrade: (tradeId: string) => boolean;
  executeGhostTrade: (
    tradeType: 'buy' | 'sell',
    commodity: string,
    quantity: number,
    sectorId?: number,
    portId?: number
  ) => boolean;
  
  cancelQuantumTrade: (tradeId: string) => boolean;
  clearQuantumTrades: () => void;
  clearGhostTrades: () => void;
  
  // Connection management
  connect: () => void;
  disconnect: () => void;
  reconnect: () => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

interface WebSocketProviderProps {
  children: React.ReactNode;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const { user } = useAuth();
  const token = localStorage.getItem('accessToken');
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('Disconnected');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [ariaMessages, setAriaMessages] = useState<Array<{
    id: string;
    type: 'user' | 'ai';
    content: string;
    timestamp: string;
    conversationId?: string;
    confidence?: number;
    actions?: Array<{
      type: string;
      [key: string]: any;
    }>;
    suggestions?: string[];
  }>>([]);
  const [sectorPlayers, setSectorPlayers] = useState<Array<{
    user_id: string;
    username: string;
    connected_at: string;
    last_heartbeat: string;
  }>>([]);
  const [notifications, setNotifications] = useState<NotificationMessage[]>([]);
  const [recentMovements, setRecentMovements] = useState<PlayerMovementMessage[]>([]);
  
  // Quantum Trading state
  const [quantumTrades, setQuantumTrades] = useState<Array<{
    trade_id: string;
    trade_type: 'buy' | 'sell';
    commodity: string;
    quantity: number;
    superposition_states: Array<{
      price: number;
      profit: number;
      probability: number;
      outcome: string;
    }>;
    manipulation_warning: boolean;
    risk_score: number;
    confidence_interval: [number, number];
    dna_sequence?: string;
    timestamp: string;
  }>>([]);

  const [ghostTrades, setGhostTrades] = useState<Array<{
    trade_id: string;
    trade_type: 'buy' | 'sell';
    commodity: string;
    quantity: number;
    expected_profit: number;
    success_probability: number;
    risk_assessment: string;
    timestamp: string;
  }>>([]);

  const [quantumMarketData, setQuantumMarketData] = useState<Array<{
    sector_id: number;
    commodity_prices: Array<{
      commodity: string;
      current_price: number;
      quantum_volatility: number;
      manipulation_probability: number;
      ai_recommendation: 'buy' | 'sell' | 'hold';
      aria_insights: string[];
    }>;
    timestamp: string;
  }>>([]);
  
  // Keep track of cleanup functions
  const cleanupFunctions = useRef<Array<() => void>>([]);

  // Connection management
  const connect = useCallback(() => {
    if (token) {
      console.log('WebSocket: Initiating connection with token');
      websocketService.connect(token);
    } else {
      console.warn('WebSocket: No token available for connection');
    }
  }, [token]);

  const disconnect = useCallback(() => {
    console.log('WebSocket: Disconnecting');
    websocketService.disconnect();
  }, []);

  const reconnect = useCallback(() => {
    console.log('WebSocket: Reconnecting');
    disconnect();
    setTimeout(connect, 1000);
  }, [connect, disconnect]);

  // Chat functionality
  const sendChatMessage = useCallback((content: string, targetType: 'sector' | 'team' | 'global' = 'sector') => {
    return websocketService.sendChatMessage(content, targetType);
  }, []);

  const clearChatMessages = useCallback(() => {
    setChatMessages([]);
  }, []);

  // ARIA functionality
  const sendARIAMessage = useCallback((content: string, conversationId?: string, context?: string) => {
    const success = websocketService.sendARIAMessage(content, conversationId, context);
    
    if (success) {
      // Add user message immediately to the local state
      const userMessage = {
        id: `user-${Date.now()}`,
        type: 'user' as const,
        content: content,
        timestamp: new Date().toISOString(),
        conversationId: conversationId
      };
      setAriaMessages(prev => [...prev, userMessage]);
    }
    
    return success;
  }, []);

  const clearARIAMessages = useCallback(() => {
    setAriaMessages([]);
  }, []);

  // Quantum Trading functionality
  const createQuantumTrade = useCallback((
    tradeType: 'buy' | 'sell',
    commodity: string,
    quantity: number,
    sectorId?: number,
    portId?: number,
    maxPrice?: number,
    minPrice?: number,
    superpositionStates?: number
  ) => {
    const success = websocketService.createQuantumTrade(
      tradeType, commodity, quantity, sectorId, portId, maxPrice, minPrice, superpositionStates
    );
    
    if (success) {
      // Notify ARIA about the quantum trade creation
      websocketService.sendARIAMessage(
        `Creating quantum ${tradeType} trade: ${quantity} ${commodity} with ${superpositionStates || 3} superposition states`,
        undefined,
        'quantum_trading'
      );
    }
    
    return success;
  }, []);

  const collapseQuantumTrade = useCallback((tradeId: string) => {
    const success = websocketService.collapseQuantumTrade(tradeId);
    
    if (success) {
      // Notify ARIA about the quantum trade collapse
      websocketService.sendARIAMessage(
        `Collapsing quantum trade ${tradeId} to reality`,
        undefined,
        'quantum_trading'
      );
    }
    
    return success;
  }, []);

  const executeGhostTrade = useCallback((
    tradeType: 'buy' | 'sell',
    commodity: string,
    quantity: number,
    sectorId?: number,
    portId?: number
  ) => {
    const success = websocketService.executeGhostTrade(tradeType, commodity, quantity, sectorId, portId);
    
    if (success) {
      // Notify ARIA about the ghost trade
      websocketService.sendARIAMessage(
        `Running ghost ${tradeType} simulation: ${quantity} ${commodity}`,
        undefined,
        'quantum_trading'
      );
    }
    
    return success;
  }, []);

  const cancelQuantumTrade = useCallback((tradeId: string) => {
    const success = websocketService.cancelQuantumTrade(tradeId);
    
    if (success) {
      // Remove from local state
      setQuantumTrades(prev => prev.filter(trade => trade.trade_id !== tradeId));
      
      // Notify ARIA about the cancellation
      websocketService.sendARIAMessage(
        `Cancelled quantum trade ${tradeId}`,
        undefined,
        'quantum_trading'
      );
    }
    
    return success;
  }, []);

  const clearQuantumTrades = useCallback(() => {
    setQuantumTrades([]);
  }, []);

  const clearGhostTrades = useCallback(() => {
    setGhostTrades([]);
  }, []);

  // Player presence
  const requestSectorPlayers = useCallback(() => {
    websocketService.requestSectorPlayers();
  }, []);

  // Notifications
  const addNotification = useCallback((notification: Omit<NotificationMessage, 'type' | 'timestamp'>) => {
    const newNotification: NotificationMessage = {
      ...notification,
      type: 'notification',
      timestamp: new Date().toISOString()
    };
    
    setNotifications(prev => [newNotification, ...prev].slice(0, 10)); // Keep only last 10
    
    // Auto-remove notification after 5 seconds for non-error messages
    if (notification.level !== 'error') {
      setTimeout(() => {
        setNotifications(prev => prev.filter(n => n.timestamp !== newNotification.timestamp));
      }, 5000);
    }
  }, []);

  const removeNotification = useCallback((index: number) => {
    setNotifications(prev => prev.filter((_, i) => i !== index));
  }, []);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  // Set up message handlers when component mounts
  useEffect(() => {
    const cleanups: Array<() => void> = [];

    // Connection status handler
    const connectionHandler = websocketService.onConnectionStatus((connected, details) => {
      setIsConnected(connected);
      if (connected) {
        setConnectionStatus('Connected');
        console.log('WebSocket: Connection established');
      } else {
        setConnectionStatus(details?.reason || 'Disconnected');
        console.log('WebSocket: Connection lost');
        
        // Clear real-time data when disconnected
        setSectorPlayers([]);
      }
    });
    cleanups.push(connectionHandler);

    // Chat message handler
    const chatHandler = websocketService.onChatMessage((message) => {
      setChatMessages(prev => [...prev, message].slice(-50)); // Keep last 50 messages
    });
    cleanups.push(chatHandler);

    // Player movement handler
    const movementHandler = websocketService.onPlayerMovement((message) => {
      setRecentMovements(prev => [message, ...prev].slice(0, 20)); // Keep last 20 movements
      
      // Update sector players list based on movement
      if (message.type === 'player_entered_sector') {
        setSectorPlayers(prev => {
          // Check if player is already in the list
          const exists = prev.some(p => p.user_id === message.user_id);
          if (!exists) {
            return [...prev, {
              user_id: message.user_id,
              username: message.username,
              connected_at: message.timestamp,
              last_heartbeat: message.timestamp
            }];
          }
          return prev;
        });
      } else if (message.type === 'player_left_sector') {
        setSectorPlayers(prev => prev.filter(p => p.user_id !== message.user_id));
      }
    });
    cleanups.push(movementHandler);

    // Sector players handler
    const sectorPlayersHandler = websocketService.onSectorPlayers((message) => {
      setSectorPlayers(message.players);
    });
    cleanups.push(sectorPlayersHandler);

    // Notification handler
    const notificationHandler = websocketService.onNotification((message) => {
      setNotifications(prev => [message, ...prev].slice(0, 10));
      
      // Auto-remove notification after 5 seconds for non-error messages
      if (message.level !== 'error') {
        setTimeout(() => {
          setNotifications(prev => prev.filter(n => n.timestamp !== message.timestamp));
        }, 5000);
      }
    });
    cleanups.push(notificationHandler);

    // ARIA response handler
    const ariaHandler = websocketService.onARIAResponse((message) => {
      const aiMessage = {
        id: `ai-${Date.now()}`,
        type: 'ai' as const,
        content: message.data.message,
        timestamp: message.timestamp,
        conversationId: message.conversation_id,
        confidence: message.data.confidence,
        actions: message.data.actions,
        suggestions: message.data.suggestions
      };
      
      setAriaMessages(prev => [...prev, aiMessage]);
      
      // Show notification for important ARIA responses
      if (message.data.actions && message.data.actions.length > 0) {
        addNotification({
          title: 'ARIA Recommendation',
          content: `ARIA has ${message.data.actions.length} suggestion(s) for you`,
          level: 'info'
        });
      }
    });
    cleanups.push(ariaHandler);

    // Backend Quantum Trading message handlers (matching actual backend format)
    const quantumTradeCreatedHandler = (message: WebSocketMessage) => {
      if (message.type === 'quantum_trade_created' && message.data) {
        // Add new quantum trade to state
        const newTrade = {
          trade_id: message.data.trade_id,
          trade_type: message.data.action as 'buy' | 'sell',
          commodity: message.data.commodity,
          quantity: message.data.quantity,
          superposition_states: message.data.superposition_states,
          manipulation_warning: message.data.manipulation_warning,
          risk_score: message.data.probability < 0.7 ? 0.3 : 0.1, // Convert probability to risk
          confidence_interval: [message.data.probability - 0.1, message.data.probability + 0.1] as [number, number],
          dna_sequence: message.data.dna_sequence,
          timestamp: message.timestamp || new Date().toISOString()
        };
        
        setQuantumTrades(prev => [...prev, newTrade]);
        
        addNotification({
          title: 'Quantum Trade Created',
          content: `Created quantum ${message.data.action} trade for ${message.data.quantity} ${message.data.commodity}`,
          level: 'success'
        });
      }
    };
    websocketService.addMessageHandler(quantumTradeCreatedHandler);
    cleanups.push(() => websocketService.removeMessageHandler(quantumTradeCreatedHandler));

    const ghostTradeResultHandler = (message: WebSocketMessage) => {
      if (message.type === 'ghost_trade_result' && message.data) {
        // Add ghost trade result to state
        const ghostResult = {
          trade_id: message.data.trade_id || `ghost_${Date.now()}`,
          trade_type: message.data.action as 'buy' | 'sell',
          commodity: message.data.commodity || 'ORE',
          quantity: message.data.quantity || 100,
          expected_profit: message.data.expected_profit,
          success_probability: message.data.outcomes?.reduce((sum: number, outcome: any) => 
            sum + (outcome.profit > 0 ? outcome.probability : 0), 0) || 0.5,
          risk_assessment: message.data.recommendation?.includes('HIGH') ? 'high' : 
                          message.data.recommendation?.includes('MEDIUM') ? 'medium' : 'low',
          timestamp: message.timestamp || new Date().toISOString()
        };
        
        setGhostTrades(prev => [...prev, ghostResult]);
        
        addNotification({
          title: 'Ghost Trade Completed',
          content: `Simulation: ${message.data.recommendation}`,
          level: 'info'
        });
      }
    };
    websocketService.addMessageHandler(ghostTradeResultHandler);
    cleanups.push(() => websocketService.removeMessageHandler(ghostTradeResultHandler));

    const quantumTradeCollapsedHandler = (message: WebSocketMessage) => {
      if (message.type === 'quantum_trade_collapsed' && message.data) {
        // Remove quantum trade from superposition
        setQuantumTrades(prev => prev.filter(trade => trade.trade_id !== message.data.trade?.id));
        
        const profit = message.data.trade?.profit || 0;
        addNotification({
          title: 'Quantum Trade Collapsed',
          content: `Trade executed with ${profit > 0 ? '+' : ''}${profit} credits`,
          level: profit > 0 ? 'success' : 'warning'
        });
      }
    };
    websocketService.addMessageHandler(quantumTradeCollapsedHandler);
    cleanups.push(() => websocketService.removeMessageHandler(quantumTradeCollapsedHandler));

    // Legacy quantum trading response handler (for backward compatibility)
    const quantumTradingHandler = websocketService.onQuantumTradingResponse((message) => {
      if (message.success && message.data) {
        if (message.action === 'create_quantum_trade') {
          // Handle legacy format
          const newTrade = {
            trade_id: message.data.trade_id,
            trade_type: message.data.superposition_states?.[0]?.outcome?.includes('buy') ? 'buy' as const : 'sell' as const,
            commodity: 'ORE', // This should come from the original request, stored temporarily
            quantity: 100, // This should come from the original request
            superposition_states: message.data.superposition_states || [],
            manipulation_warning: message.data.manipulation_warning || false,
            risk_score: message.data.risk_score || 0.5,
            confidence_interval: message.data.confidence_interval || [0.6, 0.9],
            dna_sequence: message.data.dna_sequence,
            timestamp: message.timestamp || new Date().toISOString()
          };
          
          setQuantumTrades(prev => [...prev, newTrade]);
          
          addNotification({
            title: 'Quantum Trade Created',
            content: `Created quantum trade with ${message.data.superposition_states?.length || 0} probability states`,
            level: 'success'
          });
        }
      } else if (!message.success) {
        addNotification({
          title: 'Quantum Trade Error',
          content: message.error || 'Quantum trading operation failed',
          level: 'error'
        });
      }
    });
    cleanups.push(quantumTradingHandler);

    // Quantum Market Data handler
    const quantumMarketHandler = websocketService.onQuantumMarketData((message) => {
      setQuantumMarketData(prev => {
        // Replace data for the same sector or add new sector data
        const filtered = prev.filter(data => data.sector_id !== message.sector_id);
        return [...filtered, message].slice(-10); // Keep last 10 sectors
      });
      
      // Check for important market events
      const highVolatilityCommodities = message.commodity_prices.filter(
        price => price.quantum_volatility > 0.7
      );
      
      if (highVolatilityCommodities.length > 0) {
        addNotification({
          title: 'Quantum Market Alert',
          content: `High volatility detected in ${highVolatilityCommodities.length} commodities`,
          level: 'warning'
        });
      }
      
      // Check for manipulation warnings
      const manipulationRisk = message.commodity_prices.filter(
        price => price.manipulation_probability > 0.5
      );
      
      if (manipulationRisk.length > 0) {
        addNotification({
          title: 'Market Manipulation Alert',
          content: `Manipulation risk detected in ${manipulationRisk.map(p => p.commodity).join(', ')}`,
          level: 'error'
        });
      }
    });
    cleanups.push(quantumMarketHandler);

    // Handle other message types
    const generalHandler = (message: WebSocketMessage) => {
      switch (message.type) {
        case 'connection_status':
          // This is handled by the websocketService's onConnectionStatus
          // No additional handling needed here
          break;
          
        case 'heartbeat_ack':
          // Handle heartbeat acknowledgment
          break;
          
        case 'trade_completed':
          addNotification({
            title: 'Trade Completed',
            content: 'A trade was completed in your area',
            level: 'info'
          });
          break;
          
        case 'combat_event':
          addNotification({
            title: 'Combat Activity',
            content: 'Combat activity detected in your sector',
            level: 'warning'
          });
          break;
          
        case 'admin_broadcast':
          addNotification({
            title: message.title || 'System Message',
            content: message.content || 'Administrative broadcast',
            level: 'info'
          });
          break;
          
        case 'connection_error':
          addNotification({
            title: 'Connection Error',
            content: message.error || 'WebSocket connection error',
            level: 'error'
          });
          break;
          
        case 'connection_failed':
          addNotification({
            title: 'Connection Failed',
            content: message.message || 'Failed to maintain connection',
            level: 'error'
          });
          break;
          
        default:
          // Only log truly unhandled message types, not ones handled by specific handlers
          if (!['sector_players', 'connection_status', 'chat_message', 'player_entered_sector', 'player_left_sector', 'notification'].includes(message.type)) {
            console.log('WebSocket: Unhandled message type:', message.type);
          }
      }
    };
    
    websocketService.addMessageHandler(generalHandler);
    cleanups.push(() => websocketService.removeMessageHandler(generalHandler));

    // Store cleanup functions
    cleanupFunctions.current = cleanups;

    return () => {
      cleanups.forEach(cleanup => cleanup());
    };
  }, [addNotification]);

  // Auto-connect when user is authenticated
  useEffect(() => {
    if (user && token) {
      console.log('WebSocket: User authenticated, connecting...');
      connect();
    } else {
      console.log('WebSocket: User not authenticated, disconnecting...');
      disconnect();
    }

    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, [user, token, connect, disconnect]);

  // Auto-request sector players when connected
  useEffect(() => {
    if (isConnected) {
      // Request sector players after a short delay to ensure we're fully connected
      setTimeout(() => {
        requestSectorPlayers();
      }, 1000);
    }
  }, [isConnected, requestSectorPlayers]);

  const contextValue: WebSocketContextType = {
    // Connection status
    isConnected,
    connectionStatus,
    
    // Chat functionality
    chatMessages,
    sendChatMessage,
    clearChatMessages,
    
    // ARIA AI Chat functionality
    sendARIAMessage,
    ariaMessages,
    clearARIAMessages,
    
    // Player presence
    sectorPlayers,
    requestSectorPlayers,
    
    // Notifications
    notifications,
    addNotification,
    removeNotification,
    clearNotifications,
    
    // Player movement tracking
    recentMovements,
    
    // Quantum Trading functionality
    quantumTrades,
    ghostTrades,
    quantumMarketData,
    createQuantumTrade,
    collapseQuantumTrade,
    executeGhostTrade,
    cancelQuantumTrade,
    clearQuantumTrades,
    clearGhostTrades,
    
    // Connection management
    connect,
    disconnect,
    reconnect
  };

  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  );
};

export default WebSocketProvider;