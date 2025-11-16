/**
 * Quantum Trading API Service
 * REST API integration for quantum trading when WebSocket is unavailable
 * Connects to backend QuantumTradingEngine via HTTP endpoints
 */

import axios from 'axios';

// Types matching backend models
export interface QuantumTradeRequest {
  commodity: string;
  action: 'buy' | 'sell';
  quantity: number;
  price?: number;
  max_price?: number;
  min_price?: number;
}

export interface GhostTradeRequest {
  commodity: string;
  action: 'buy' | 'sell';
  quantity: number;
  price?: number;
}

export interface QuantumTradeResponse {
  trade_id: string;
  commodity: string;
  action: 'buy' | 'sell';
  quantity: number;
  superposition_states: Array<{
    state_id: string;
    probability: number;
    price: number;
    profit: number;
    risk: string;
  }>;
  probability: number;
  manipulation_warning: boolean;
  dna_sequence?: string;
  message: string;
}

export interface GhostTradeResponse {
  trade_id: string;
  expected_profit: number;
  recommendation: string;
  outcomes: Array<{
    outcome: string;
    probability: number;
    profit: number;
  }>;
  message: string;
}

export interface QuantumStateResponse {
  status: string;
  active_trades: number;
  total_volume: number;
  success_rate: number;
  message: string;
}

export interface AIRecommendationResponse {
  recommendations: Array<{
    commodity: string;
    action: 'buy' | 'sell';
    confidence: number;
    reasoning: string;
    quantum_advantage: string;
  }>;
  market_sentiment: string;
  manipulation_alerts: string[];
}

class QuantumTradingApiService {
  private baseURL: string;
  private token: string | null = null;

  constructor() {
    // Auto-detect API URL based on environment
    if (typeof window !== 'undefined') {
      const protocol = window.location.protocol;
      const hostname = window.location.hostname;
      
      // Detect GitHub Codespaces
      if (hostname.includes('app.github.dev')) {
        this.baseURL = `${protocol}//${hostname.replace('-3000', '-8080')}/api/v1/quantum-trading`;
      }
      // Detect Replit
      else if (hostname.includes('repl.co')) {
        this.baseURL = `${protocol}//${hostname}:8080/api/v1/quantum-trading`;
      }
      // Local development
      else {
        this.baseURL = 'http://localhost:8080/api/v1/quantum-trading';
      }
    } else {
      this.baseURL = 'http://localhost:8080/api/v1/quantum-trading';
    }
  }

  setAuthToken(token: string) {
    this.token = token;
  }

  private getAuthHeaders() {
    return this.token ? { Authorization: `Bearer ${this.token}` } : {};
  }

  /**
   * Create a quantum trade in superposition
   */
  async createQuantumTrade(request: QuantumTradeRequest): Promise<QuantumTradeResponse> {
    try {
      const response = await axios.post(
        `${this.baseURL}/create-quantum-trade`,
        request,
        { headers: this.getAuthHeaders() }
      );
      return response.data;
    } catch (error) {
      console.error('Failed to create quantum trade:', error);
      throw new Error('Failed to create quantum trade');
    }
  }

  /**
   * Execute a ghost trade simulation
   */
  async executeGhostTrade(request: GhostTradeRequest): Promise<GhostTradeResponse> {
    try {
      const response = await axios.post(
        `${this.baseURL}/ghost-trade`,
        request,
        { headers: this.getAuthHeaders() }
      );
      return response.data;
    } catch (error) {
      console.error('Failed to execute ghost trade:', error);
      throw new Error('Failed to execute ghost trade');
    }
  }

  /**
   * Collapse a quantum trade to reality (execute)
   */
  async collapseQuantumTrade(tradeId: string): Promise<{ message: string; profit: number }> {
    try {
      const response = await axios.post(
        `${this.baseURL}/collapse-quantum-trade/${tradeId}`,
        {},
        { headers: this.getAuthHeaders() }
      );
      return response.data;
    } catch (error) {
      console.error('Failed to collapse quantum trade:', error);
      throw new Error('Failed to collapse quantum trade');
    }
  }

  /**
   * Get current quantum trading engine state
   */
  async getQuantumState(): Promise<QuantumStateResponse> {
    try {
      const response = await axios.get(
        `${this.baseURL}/quantum-state`,
        { headers: this.getAuthHeaders() }
      );
      return response.data;
    } catch (error) {
      console.error('Failed to get quantum state:', error);
      throw new Error('Failed to get quantum state');
    }
  }

  /**
   * Get AI-powered trading recommendations
   */
  async getAIRecommendations(): Promise<AIRecommendationResponse> {
    try {
      const response = await axios.get(
        `${this.baseURL}/recommendations`,
        { headers: this.getAuthHeaders() }
      );
      return response.data;
    } catch (error) {
      console.error('Failed to get AI recommendations:', error);
      throw new Error('Failed to get AI recommendations');
    }
  }

  /**
   * Create a trade cascade (complex multi-step strategy)
   */
  async createTradeCascade(trades: QuantumTradeRequest[]): Promise<{ cascade_id: string; message: string }> {
    try {
      const response = await axios.post(
        `${this.baseURL}/create-cascade`,
        { trades },
        { headers: this.getAuthHeaders() }
      );
      return response.data;
    } catch (error) {
      console.error('Failed to create trade cascade:', error);
      throw new Error('Failed to create trade cascade');
    }
  }

  /**
   * Health check for quantum trading API
   */
  async healthCheck(): Promise<{ status: string; message: string }> {
    try {
      const response = await axios.get(`${this.baseURL.replace('/quantum-trading', '')}/health`);
      return { status: 'healthy', message: 'Quantum Trading API is operational' };
    } catch (error) {
      return { status: 'unhealthy', message: 'Quantum Trading API is not responding' };
    }
  }
}

// Export singleton instance
export const quantumTradingApi = new QuantumTradingApiService();
export default quantumTradingApi;