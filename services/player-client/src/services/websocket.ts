export interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

export interface ChatMessage {
  type: 'chat_message';
  from_user_id: string;
  from_username: string;
  content: string;
  target_type: 'sector' | 'team' | 'global';
  timestamp: string;
  sector_id?: number;
  team_id?: string;
}

export interface PlayerMovementMessage {
  type: 'player_entered_sector' | 'player_left_sector';
  user_id: string;
  username: string;
  sector_id: number;
  timestamp: string;
}

export interface SectorPlayersMessage {
  type: 'sector_players';
  sector_id: number;
  players: Array<{
    user_id: string;
    username: string;
    connected_at: string;
    last_heartbeat: string;
  }>;
  timestamp: string;
}

export interface NotificationMessage {
  type: 'notification';
  title: string;
  content: string;
  level: 'info' | 'success' | 'warning' | 'error';
  timestamp: string;
}

export interface ARIAChatMessage {
  type: 'aria_chat';
  content: string;
  conversation_id?: string;
  context?: string;
  timestamp: string;
  session_id: string;
  signature?: string;
}

export interface ARIAResponseMessage {
  type: 'aria_response';
  conversation_id: string;
  data: {
    message: string;
    confidence: number;
    context_used: string;
    actions: Array<{
      type: string;
      [key: string]: any;
    }>;
    suggestions: string[];
    learning_note?: string;
  };
  timestamp: string;
  server_version: string;
  signature?: string;
}

// Quantum Trading Message Types
export interface QuantumTradingMessage {
  type: 'quantum_trading';
  action: 'create_quantum_trade' | 'collapse_trade' | 'execute_ghost_trade' | 'cancel_quantum_trade';
  params: {
    trade_type: 'buy' | 'sell';
    commodity: string;
    quantity: number;
    sector_id?: number;
    port_id?: number;
    max_price?: number;
    min_price?: number;
    trade_id?: string;
    superposition_states?: number;
  };
  timestamp: string;
  session_id: string;
  signature?: string;
}

export interface QuantumTradingResponse {
  type: 'quantum_trading_response';
  action: string;
  success: boolean;
  data?: {
    trade_id: string;
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
    ghost_results?: {
      expected_profit: number;
      success_probability: number;
      risk_assessment: string;
    };
  };
  error?: string;
  timestamp: string;
  signature?: string;
}

export interface QuantumMarketDataMessage {
  type: 'quantum_market_data';
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
}

type MessageHandler = (message: WebSocketMessage) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private token: string | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private messageHandlers: Set<MessageHandler> = new Set();
  private isConnected = false;
  private shouldReconnect = true;

  constructor() {
    this.setupEventListeners();
  }

  private setupEventListeners() {
    // Handle page visibility changes
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible' && !this.isConnected && this.token) {
        this.connect();
      }
    });

    // Handle online/offline events
    window.addEventListener('online', () => {
      if (!this.isConnected && this.token) {
        this.connect();
      }
    });

    window.addEventListener('offline', () => {
      this.disconnect();
    });
  }

  private getWebSocketUrl(): string {
    // For Docker environments, always use localhost:8080 for WebSocket
    // This works because the Docker ports are mapped to the host
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    
    // In Docker/Codespaces, use the external port mapping
    if (window.location.host.includes('.app.github.dev')) {
      console.log('WebSocket: GitHub Codespaces detected - using external gameserver WebSocket');
      // Use the external gameserver URL for WebSocket
      const gameserverHost = window.location.host.replace('-3000.app.github.dev', '-8080.app.github.dev');
      return `${protocol}//${gameserverHost}/api/v1/ws/connect`;
    }
    
    // For local development, use localhost
    return `ws://localhost:8080/api/v1/ws/connect`;
  }

  connect(token?: string): void {
    if (token) {
      this.token = token;
    }

    if (!this.token) {
      console.error('WebSocket: No authentication token provided');
      return;
    }

    if (this.ws && (this.ws.readyState === WebSocket.CONNECTING || this.ws.readyState === WebSocket.OPEN)) {
      console.log('WebSocket: Already connected or connecting');
      return;
    }

    try {
      const wsUrl = `${this.getWebSocketUrl()}?token=${encodeURIComponent(this.token)}`;
      console.log('WebSocket: Connecting to', wsUrl.replace(this.token, '[TOKEN]'));
      
      this.ws = new WebSocket(wsUrl);
      this.setupWebSocketHandlers();
    } catch (error) {
      console.error('WebSocket: Failed to create connection', error);
      this.scheduleReconnect();
    }
  }

  private setupWebSocketHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log('WebSocket: Connected successfully');
      this.isConnected = true;
      this.reconnectAttempts = 0;
      this.reconnectDelay = 1000;
      this.startHeartbeat();
      
      // Notify handlers about connection
      this.notifyHandlers({
        type: 'connection_status',
        connected: true,
        timestamp: new Date().toISOString()
      });
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        console.log('WebSocket: Received message', message.type);
        this.notifyHandlers(message);
      } catch (error) {
        console.error('WebSocket: Failed to parse message', error);
      }
    };

    this.ws.onclose = (event) => {
      console.log('WebSocket: Connection closed', event.code, event.reason);
      this.isConnected = false;
      this.stopHeartbeat();
      
      // Notify handlers about disconnection
      this.notifyHandlers({
        type: 'connection_status',
        connected: false,
        code: event.code,
        reason: event.reason,
        timestamp: new Date().toISOString()
      });

      if (this.shouldReconnect && event.code !== 4001 && event.code !== 4002) {
        this.scheduleReconnect();
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket: Connection error', error);
      
      // Notify handlers about error
      this.notifyHandlers({
        type: 'connection_error',
        error: 'WebSocket connection error',
        timestamp: new Date().toISOString()
      });
    };
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('WebSocket: Max reconnection attempts reached');
      this.notifyHandlers({
        type: 'connection_failed',
        message: 'Failed to reconnect after maximum attempts',
        timestamp: new Date().toISOString()
      });
      return;
    }

    console.log(`WebSocket: Scheduling reconnect attempt ${this.reconnectAttempts + 1} in ${this.reconnectDelay}ms`);
    
    setTimeout(() => {
      this.reconnectAttempts++;
      this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000); // Max 30 seconds
      this.connect();
    }, this.reconnectDelay);
  }

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected) {
        this.send({
          type: 'heartbeat',
          timestamp: new Date().toISOString()
        });
      }
    }, 30000); // Send heartbeat every 30 seconds
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  send(message: WebSocketMessage): boolean {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket: Cannot send message - not connected');
      return false;
    }

    try {
      this.ws.send(JSON.stringify(message));
      return true;
    } catch (error) {
      console.error('WebSocket: Failed to send message', error);
      return false;
    }
  }

  // Chat methods
  sendChatMessage(content: string, targetType: 'sector' | 'team' | 'global' = 'sector'): boolean {
    return this.send({
      type: 'chat_message',
      content: content.trim(),
      target_type: targetType,
      timestamp: new Date().toISOString()
    });
  }

  // Player info requests
  requestSectorPlayers(): boolean {
    return this.send({
      type: 'request_sector_players',
      timestamp: new Date().toISOString()
    });
  }

  requestTeamPlayers(): boolean {
    return this.send({
      type: 'request_team_players',
      timestamp: new Date().toISOString()
    });
  }

  // ARIA AI Chat methods
  sendARIAMessage(content: string, conversationId?: string, context?: string): boolean {
    // Generate session ID (could be stored in localStorage or state)
    const sessionId = localStorage.getItem('aria_session_id') || 'session_' + Date.now();
    localStorage.setItem('aria_session_id', sessionId);

    const message: ARIAChatMessage = {
      type: 'aria_chat',
      content: content.trim(),
      conversation_id: conversationId,
      context: context || 'general',
      timestamp: new Date().toISOString(),
      session_id: sessionId
    };

    // Add signature for security (simplified client-side signing)
    message.signature = this.generateMessageSignature(message);

    return this.send(message);
  }

  // Quantum Trading methods
  createQuantumTrade(
    tradeType: 'buy' | 'sell',
    commodity: string,
    quantity: number,
    sectorId?: number,
    portId?: number,
    maxPrice?: number,
    minPrice?: number,
    superpositionStates?: number
  ): boolean {
    const sessionId = localStorage.getItem('aria_session_id') || 'session_' + Date.now();

    const message: QuantumTradingMessage = {
      type: 'quantum_trading',
      action: 'create_quantum_trade',
      params: {
        trade_type: tradeType,
        commodity,
        quantity,
        sector_id: sectorId,
        port_id: portId,
        max_price: maxPrice,
        min_price: minPrice,
        superposition_states: superpositionStates || 3
      },
      timestamp: new Date().toISOString(),
      session_id: sessionId
    };

    // Add signature for security
    message.signature = this.generateQuantumSignature(message);

    return this.send(message);
  }

  collapseQuantumTrade(tradeId: string): boolean {
    const sessionId = localStorage.getItem('aria_session_id') || 'session_' + Date.now();

    const message: QuantumTradingMessage = {
      type: 'quantum_trading',
      action: 'collapse_trade',
      params: {
        trade_id: tradeId,
        trade_type: 'buy', // Required but not used for collapse
        commodity: '', // Required but not used for collapse
        quantity: 0 // Required but not used for collapse
      },
      timestamp: new Date().toISOString(),
      session_id: sessionId
    };

    message.signature = this.generateQuantumSignature(message);
    return this.send(message);
  }

  executeGhostTrade(
    tradeType: 'buy' | 'sell',
    commodity: string,
    quantity: number,
    sectorId?: number,
    portId?: number
  ): boolean {
    const sessionId = localStorage.getItem('aria_session_id') || 'session_' + Date.now();

    const message: QuantumTradingMessage = {
      type: 'quantum_trading',
      action: 'execute_ghost_trade',
      params: {
        trade_type: tradeType,
        commodity,
        quantity,
        sector_id: sectorId,
        port_id: portId
      },
      timestamp: new Date().toISOString(),
      session_id: sessionId
    };

    message.signature = this.generateQuantumSignature(message);
    return this.send(message);
  }

  cancelQuantumTrade(tradeId: string): boolean {
    const sessionId = localStorage.getItem('aria_session_id') || 'session_' + Date.now();

    const message: QuantumTradingMessage = {
      type: 'quantum_trading',
      action: 'cancel_quantum_trade',
      params: {
        trade_id: tradeId,
        trade_type: 'buy', // Required but not used for cancel
        commodity: '', // Required but not used for cancel
        quantity: 0 // Required but not used for cancel
      },
      timestamp: new Date().toISOString(),
      session_id: sessionId
    };

    message.signature = this.generateQuantumSignature(message);
    return this.send(message);
  }

  private generateMessageSignature(message: ARIAChatMessage): string {
    // Simple client-side signature - server will validate properly
    const content = JSON.stringify({
      type: message.type,
      timestamp: message.timestamp,
      session_id: message.session_id
    });
    
    // Use a simple hash - real signature would use proper crypto
    return btoa(content).slice(0, 16);
  }

  private generateQuantumSignature(message: QuantumTradingMessage): string {
    // Simple client-side signature for quantum trading - server will validate properly
    const content = JSON.stringify({
      type: message.type,
      action: message.action,
      timestamp: message.timestamp,
      session_id: message.session_id
    });
    
    // Use a simple hash - real signature would use proper crypto
    return btoa(content).slice(0, 16);
  }

  // Message handler management
  addMessageHandler(handler: MessageHandler): void {
    this.messageHandlers.add(handler);
  }

  removeMessageHandler(handler: MessageHandler): void {
    this.messageHandlers.delete(handler);
  }

  private notifyHandlers(message: WebSocketMessage): void {
    this.messageHandlers.forEach(handler => {
      try {
        handler(message);
      } catch (error) {
        console.error('WebSocket: Error in message handler', error);
      }
    });
  }

  disconnect(): void {
    this.shouldReconnect = false;
    this.stopHeartbeat();
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    
    this.isConnected = false;
  }

  getConnectionStatus(): {
    connected: boolean;
    reconnectAttempts: number;
    hasToken: boolean;
  } {
    return {
      connected: this.isConnected,
      reconnectAttempts: this.reconnectAttempts,
      hasToken: !!this.token
    };
  }

  // Helper methods for common message types
  onChatMessage(callback: (message: ChatMessage) => void): () => void {
    const handler = (message: WebSocketMessage) => {
      if (message.type === 'chat_message') {
        callback(message as ChatMessage);
      }
    };
    this.addMessageHandler(handler);
    return () => this.removeMessageHandler(handler);
  }

  onPlayerMovement(callback: (message: PlayerMovementMessage) => void): () => void {
    const handler = (message: WebSocketMessage) => {
      if (message.type === 'player_entered_sector' || message.type === 'player_left_sector') {
        callback(message as PlayerMovementMessage);
      }
    };
    this.addMessageHandler(handler);
    return () => this.removeMessageHandler(handler);
  }

  onSectorPlayers(callback: (message: SectorPlayersMessage) => void): () => void {
    const handler = (message: WebSocketMessage) => {
      if (message.type === 'sector_players') {
        callback(message as SectorPlayersMessage);
      }
    };
    this.addMessageHandler(handler);
    return () => this.removeMessageHandler(handler);
  }

  onNotification(callback: (message: NotificationMessage) => void): () => void {
    const handler = (message: WebSocketMessage) => {
      if (message.type === 'notification') {
        callback(message as NotificationMessage);
      }
    };
    this.addMessageHandler(handler);
    return () => this.removeMessageHandler(handler);
  }

  onConnectionStatus(callback: (connected: boolean, details?: any) => void): () => void {
    const handler = (message: WebSocketMessage) => {
      if (message.type === 'connection_status') {
        callback(message.connected, message);
      }
    };
    this.addMessageHandler(handler);
    return () => this.removeMessageHandler(handler);
  }

  // ARIA AI callback handlers
  onARIAResponse(callback: (message: ARIAResponseMessage) => void): () => void {
    const handler = (message: WebSocketMessage) => {
      if (message.type === 'aria_response') {
        callback(message as ARIAResponseMessage);
      }
    };
    this.addMessageHandler(handler);
    return () => this.removeMessageHandler(handler);
  }

  // Quantum Trading callback handlers
  onQuantumTradingResponse(callback: (message: QuantumTradingResponse) => void): () => void {
    const handler = (message: WebSocketMessage) => {
      if (message.type === 'quantum_trading_response') {
        callback(message as QuantumTradingResponse);
      }
    };
    this.addMessageHandler(handler);
    return () => this.removeMessageHandler(handler);
  }

  onQuantumMarketData(callback: (message: QuantumMarketDataMessage) => void): () => void {
    const handler = (message: WebSocketMessage) => {
      if (message.type === 'quantum_market_data') {
        callback(message as QuantumMarketDataMessage);
      }
    };
    this.addMessageHandler(handler);
    return () => this.removeMessageHandler(handler);
  }
}

// Export singleton instance
export const websocketService = new WebSocketService();
export default websocketService;