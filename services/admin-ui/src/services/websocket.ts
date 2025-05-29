import { io, Socket } from 'socket.io-client';

interface WebSocketConfig {
  url: string;
  path?: string;
  reconnection?: boolean;
  reconnectionAttempts?: number;
  reconnectionDelay?: number;
}

interface WebSocketEvents {
  // Economy events
  'economy:market-update': (data: any) => void;
  'economy:price-change': (data: any) => void;
  'economy:intervention': (data: any) => void;
  
  // Combat events
  'combat:new-event': (data: any) => void;
  'combat:dispute-filed': (data: any) => void;
  'combat:stats-update': (data: any) => void;
  
  // Fleet events
  'fleet:status-change': (data: any) => void;
  'fleet:maintenance-alert': (data: any) => void;
  'fleet:emergency': (data: any) => void;
  
  // Team events
  'team:update': (data: any) => void;
  'team:alliance-change': (data: any) => void;
  'team:member-change': (data: any) => void;
  
  // Colony events
  'colony:production-update': (data: any) => void;
  'colony:alert': (data: any) => void;
  'colony:genesis-event': (data: any) => void;
  
  // System events
  'system:alert': (data: any) => void;
  'system:performance': (data: any) => void;
  'system:security-event': (data: any) => void;
  
  // AI Trading events
  'ai:model-update': (data: any) => void;
  'ai:prediction-made': (data: any) => void;
  'ai:recommendation-sent': (data: any) => void;
  'ai:profile-updated': (data: any) => void;
  'ai:training-complete': (data: any) => void;
  'ai:accuracy-update': (data: any) => void;
  'ai:route-update': (data: any) => void;
  'ai:route-stats-update': (data: any) => void;
  'ai:segment-update': (data: any) => void;
  'ai:trend-update': (data: any) => void;
}

class WebSocketService {
  private socket: Socket | null = null;
  private config: WebSocketConfig;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private eventHandlers: Map<string, Set<Function>> = new Map();
  private connectionPromise: Promise<void> | null = null;

  constructor() {
    // Default configuration
    this.config = {
      url: import.meta.env.VITE_WS_URL || 'http://localhost:8080',
      path: '/ws/admin',
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 5000
    };
  }

  async connect(token: string): Promise<void> {
    if (this.socket?.connected) {
      return Promise.resolve();
    }

    if (this.connectionPromise) {
      return this.connectionPromise;
    }

    this.connectionPromise = new Promise((resolve, reject) => {
      try {
        this.socket = io(this.config.url, {
          path: this.config.path,
          reconnection: this.config.reconnection,
          reconnectionAttempts: this.config.reconnectionAttempts,
          reconnectionDelay: this.config.reconnectionDelay,
          auth: {
            token
          },
          transports: ['websocket', 'polling']
        });

        this.socket.on('connect', () => {
          console.log('WebSocket connected to admin channel');
          this.clearReconnectTimer();
          
          // Subscribe to admin-specific rooms
          this.socket?.emit('admin:subscribe', {
            rooms: ['economy', 'combat', 'fleet', 'team', 'colony', 'system']
          });
          
          resolve();
        });

        this.socket.on('disconnect', (reason) => {
          console.log('WebSocket disconnected:', reason);
          if (reason === 'io server disconnect') {
            // Server initiated disconnect, attempt reconnect
            this.attemptReconnect(token);
          }
        });

        this.socket.on('error', (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        });

        // Set up event forwarding
        this.setupEventForwarding();
        
      } catch (error) {
        console.error('Failed to create WebSocket connection:', error);
        reject(error);
      }
    });

    return this.connectionPromise;
  }

  private setupEventForwarding(): void {
    if (!this.socket) return;

    // Forward all typed events to registered handlers
    const events: (keyof WebSocketEvents)[] = [
      'economy:market-update',
      'economy:price-change',
      'economy:intervention',
      'combat:new-event',
      'combat:dispute-filed',
      'combat:stats-update',
      'fleet:status-change',
      'fleet:maintenance-alert',
      'fleet:emergency',
      'team:update',
      'team:alliance-change',
      'team:member-change',
      'colony:production-update',
      'colony:alert',
      'colony:genesis-event',
      'system:alert',
      'system:performance',
      'system:security-event',
      'ai:model-update',
      'ai:prediction-made',
      'ai:recommendation-sent',
      'ai:profile-updated',
      'ai:training-complete',
      'ai:accuracy-update',
      'ai:route-update',
      'ai:route-stats-update',
      'ai:segment-update',
      'ai:trend-update'
    ];

    events.forEach(event => {
      this.socket?.on(event, (data: any) => {
        this.emit(event, data);
      });
    });
  }

  disconnect(): void {
    this.clearReconnectTimer();
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
    this.connectionPromise = null;
  }

  on<K extends keyof WebSocketEvents>(
    event: K,
    handler: WebSocketEvents[K]
  ): () => void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set());
    }
    
    this.eventHandlers.get(event)!.add(handler);
    
    // Return unsubscribe function
    return () => {
      const handlers = this.eventHandlers.get(event);
      if (handlers) {
        handlers.delete(handler);
        if (handlers.size === 0) {
          this.eventHandlers.delete(event);
        }
      }
    };
  }

  off<K extends keyof WebSocketEvents>(
    event: K,
    handler?: WebSocketEvents[K]
  ): void {
    if (!handler) {
      // Remove all handlers for this event
      this.eventHandlers.delete(event);
    } else {
      // Remove specific handler
      const handlers = this.eventHandlers.get(event);
      if (handlers) {
        handlers.delete(handler);
        if (handlers.size === 0) {
          this.eventHandlers.delete(event);
        }
      }
    }
  }

  emit(event: string, data: any): void {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`Error in WebSocket event handler for ${event}:`, error);
        }
      });
    }
  }

  send(event: string, data: any): void {
    if (this.socket?.connected) {
      this.socket.emit(event, data);
    } else {
      console.warn('WebSocket not connected, cannot send event:', event);
    }
  }

  private attemptReconnect(token: string): void {
    if (this.reconnectTimer) return;

    this.reconnectTimer = setTimeout(() => {
      console.log('Attempting WebSocket reconnection...');
      this.connect(token).catch(error => {
        console.error('Reconnection failed:', error);
      });
    }, this.config.reconnectionDelay);
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  isConnected(): boolean {
    return this.socket?.connected || false;
  }

  getSocket(): Socket | null {
    return this.socket;
  }
}

// Export singleton instance
export const websocketService = new WebSocketService();

// Export types
export type { WebSocketEvents };