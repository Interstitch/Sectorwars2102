import React, { createContext, useContext, useEffect, useState, useCallback, useRef } from 'react';
import websocketService, { 
  WebSocketMessage, 
  ChatMessage, 
  PlayerMovementMessage, 
  SectorPlayersMessage,
  NotificationMessage 
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
  const [sectorPlayers, setSectorPlayers] = useState<Array<{
    user_id: string;
    username: string;
    connected_at: string;
    last_heartbeat: string;
  }>>([]);
  const [notifications, setNotifications] = useState<NotificationMessage[]>([]);
  const [recentMovements, setRecentMovements] = useState<PlayerMovementMessage[]>([]);
  
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

    // Handle other message types
    const generalHandler = (message: WebSocketMessage) => {
      switch (message.type) {
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
          console.log('WebSocket: Unhandled message type:', message.type);
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