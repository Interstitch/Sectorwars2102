// AI Trading Intelligence Service
import { 
  TradingRecommendation, 
  MarketAnalysis, 
  PlayerTradingProfile, 
  AIPreferences,
  RecommendationFeedback,
  OptimalRoute,
  AIPerformanceStats
} from '../components/ai/types';

class AITradingService {
  private baseUrl = '/api/v1/ai';

  private getAuthHeaders() {
    const token = localStorage.getItem('accessToken');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  }

  // Recommendations
  async getRecommendations(limit: number = 5, includeExpired: boolean = false): Promise<TradingRecommendation[]> {
    const response = await fetch(`${this.baseUrl}/recommendations?limit=${limit}&include_expired=${includeExpired}`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch recommendations: ${response.statusText}`);
    }

    return response.json();
  }

  async getRecommendationHistory(daysBack: number = 7, type?: string): Promise<TradingRecommendation[]> {
    let url = `${this.baseUrl}/recommendations/history?days_back=${daysBack}`;
    if (type) {
      url += `&recommendation_type=${type}`;
    }

    const response = await fetch(url, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch recommendation history: ${response.statusText}`);
    }

    return response.json();
  }

  async submitRecommendationFeedback(recommendationId: string, feedback: RecommendationFeedback): Promise<void> {
    const response = await fetch(`${this.baseUrl}/recommendations/${recommendationId}/feedback`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(feedback)
    });

    if (!response.ok) {
      throw new Error(`Failed to submit feedback: ${response.statusText}`);
    }
  }

  // Market Analysis
  async getMarketAnalysis(commodityId: string, sectorId?: string): Promise<MarketAnalysis> {
    let url = `${this.baseUrl}/market-analysis/${commodityId}`;
    if (sectorId) {
      url += `?sector_id=${sectorId}`;
    }

    const response = await fetch(url, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch market analysis: ${response.statusText}`);
    }

    return response.json();
  }

  // Route Optimization
  async optimizeRoute(startSector: string, cargoCapacity: number, maxStops: number = 5): Promise<OptimalRoute> {
    const response = await fetch(`${this.baseUrl}/optimize-route`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        start_sector: startSector,
        cargo_capacity: cargoCapacity,
        max_stops: maxStops
      })
    });

    if (!response.ok) {
      throw new Error(`Failed to optimize route: ${response.statusText}`);
    }

    return response.json();
  }

  // Profile Management
  async getTradingProfile(): Promise<PlayerTradingProfile> {
    const response = await fetch(`${this.baseUrl}/profile`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch trading profile: ${response.statusText}`);
    }

    return response.json();
  }

  async updateAIPreferences(preferences: AIPreferences): Promise<void> {
    const response = await fetch(`${this.baseUrl}/profile`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(preferences)
    });

    if (!response.ok) {
      throw new Error(`Failed to update AI preferences: ${response.statusText}`);
    }
  }

  async updateTradingData(tradeData: {
    trade_type: string;
    commodity_id?: string;
    sector_id?: string;
    profit?: number;
    risk_taken?: number;
    additional_data?: Record<string, any>;
  }): Promise<void> {
    const response = await fetch(`${this.baseUrl}/profile/trade-update`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(tradeData)
    });

    if (!response.ok) {
      throw new Error(`Failed to update trading data: ${response.statusText}`);
    }
  }

  // Performance Statistics
  async getPerformanceStats(daysBack: number = 7): Promise<AIPerformanceStats> {
    const response = await fetch(`${this.baseUrl}/performance?days_back=${daysBack}`, {
      headers: this.getAuthHeaders()
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch performance stats: ${response.statusText}`);
    }

    return response.json();
  }

  // Utility Methods
  async checkAIAvailability(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/performance`, {
        headers: this.getAuthHeaders()
      });
      return response.ok;
    } catch {
      return false;
    }
  }
}

// Export singleton instance
export const aiTradingService = new AITradingService();
export default aiTradingService;