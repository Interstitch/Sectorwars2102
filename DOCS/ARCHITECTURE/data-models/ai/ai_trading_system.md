# AI Trading Intelligence System - Data Definitions

*Created: May 24, 2025*  
*Last Updated: May 24, 2025*  
*System Version: 1.0.0*

## Overview

The AI Trading Intelligence System provides personalized trading recommendations, market analysis, and route optimization using machine learning algorithms. This document defines all data structures, database schemas, and API interfaces for the system.

## Database Schema

### AI Market Predictions (`ai_market_predictions`)

Stores AI-generated market price predictions with confidence intervals.

```sql
CREATE TABLE ai_market_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    commodity_id UUID NOT NULL,
    sector_id UUID NOT NULL REFERENCES sectors(id) ON DELETE CASCADE,
    predicted_price DECIMAL(10,2) NOT NULL,
    confidence_interval DECIMAL(3,2) NOT NULL,
    prediction_horizon INTEGER NOT NULL, -- hours ahead
    model_version VARCHAR(50) NOT NULL,
    training_data_points INTEGER NOT NULL,
    prediction_factors JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    actual_price DECIMAL(10,2), -- For accuracy tracking
    accuracy_score DECIMAL(3,2), -- How accurate was this prediction
    
    INDEX ix_ai_market_predictions_commodity_sector (commodity_id, sector_id),
    INDEX ix_ai_market_predictions_expires_at (expires_at),
    INDEX ix_ai_market_predictions_created_at (created_at)
);
```

**Key Fields:**
- `prediction_horizon`: How many hours in the future this prediction is for
- `confidence_interval`: 0.0 to 1.0 confidence score
- `prediction_factors`: JSON array of factors influencing the prediction
- `actual_price`: Set after the prediction period to calculate accuracy

### Player Trading Profiles (`player_trading_profiles`)

Stores AI-learned player trading patterns and preferences.

```sql
CREATE TABLE player_trading_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID UNIQUE NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    risk_tolerance DECIMAL(3,2) NOT NULL DEFAULT 0.5, -- 0.0 = conservative, 1.0 = aggressive
    preferred_commodities JSONB, -- List of commodity IDs and preference scores
    avoided_sectors JSONB, -- Sectors the player tends to avoid
    trading_patterns JSONB, -- Learned behavioral patterns
    performance_metrics JSONB, -- Historical performance data
    ai_assistance_level VARCHAR(20) DEFAULT 'medium', -- 'minimal', 'medium', 'full'
    notification_preferences JSONB, -- When and how to notify
    learning_data JSONB, -- ML model training data specific to this player
    last_active_sector UUID REFERENCES sectors(id) ON DELETE SET NULL,
    average_profit_per_trade DECIMAL(10,2) DEFAULT 0,
    total_trades_analyzed INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX ix_player_trading_profiles_player_id (player_id),
    INDEX ix_player_trading_profiles_updated_at (updated_at)
);
```

**Key Fields:**
- `risk_tolerance`: 0.0 (conservative) to 1.0 (aggressive)
- `preferred_commodities`: `{"commodity_uuid": preference_score}`
- `trading_patterns`: Learned behaviors like preferred trade times, route patterns
- `ai_assistance_level`: How much AI help the player wants

### AI Recommendations (`ai_recommendations`)

Stores AI-generated trading recommendations for players.

```sql
CREATE TABLE ai_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    recommendation_type VARCHAR(50) NOT NULL, -- 'buy', 'sell', 'route', 'avoid'
    recommendation_data JSONB NOT NULL, -- Structured recommendation details
    confidence_score DECIMAL(3,2) NOT NULL, -- 0.0 to 1.0
    expected_profit DECIMAL(10,2),
    risk_assessment VARCHAR(20) NOT NULL, -- 'low', 'medium', 'high'
    reasoning TEXT, -- Human-readable explanation
    priority_level INTEGER DEFAULT 3, -- 1-5 scale (5 = urgent)
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    accepted BOOLEAN, -- NULL = pending, True/False = user decision
    acceptance_timestamp TIMESTAMP WITH TIME ZONE,
    outcome_profit DECIMAL(10,2), -- Actual profit if recommendation was followed
    outcome_timestamp TIMESTAMP WITH TIME ZONE,
    feedback_score INTEGER, -- 1-5 user feedback rating
    feedback_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX ix_ai_recommendations_player_id (player_id),
    INDEX ix_ai_recommendations_type_priority (recommendation_type, priority_level),
    INDEX ix_ai_recommendations_expires_at (expires_at),
    INDEX ix_ai_recommendations_accepted (accepted)
);
```

**Recommendation Types:**
- `buy`: Suggests purchasing a commodity
- `sell`: Suggests selling a commodity
- `route`: Suggests a trading route
- `avoid`: Warns against risky actions

### AI Model Performance (`ai_model_performance`)

Tracks performance metrics for AI models.

```sql
CREATE TABLE ai_model_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    performance_date DATE NOT NULL,
    total_predictions INTEGER NOT NULL,
    correct_predictions INTEGER NOT NULL,
    accuracy_percentage DECIMAL(5,2) NOT NULL,
    average_confidence DECIMAL(3,2) NOT NULL,
    user_acceptance_rate DECIMAL(3,2) NOT NULL,
    average_user_satisfaction DECIMAL(3,2),
    profit_improvement_rate DECIMAL(5,2), -- How much AI improves user profits
    performance_metrics JSONB, -- Additional detailed metrics
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE INDEX ix_ai_model_performance_date_model (performance_date, model_name),
    INDEX ix_ai_model_performance_accuracy (accuracy_percentage)
);
```

### AI Training Data (`ai_training_data`)

Stores market data for AI model training.

```sql
CREATE TABLE ai_training_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    data_type VARCHAR(50) NOT NULL, -- 'market_price', 'trade_volume', 'player_behavior'
    sector_id UUID REFERENCES sectors(id) ON DELETE CASCADE,
    commodity_id UUID, -- References commodities when that table exists
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    data_value DECIMAL(12,4) NOT NULL,
    contextual_data JSONB, -- Additional context like market conditions
    quality_score DECIMAL(3,2) DEFAULT 1.0, -- Data quality for training (0.0-1.0)
    used_in_training BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    INDEX ix_ai_training_data_type_timestamp (data_type, timestamp),
    INDEX ix_ai_training_data_sector_commodity (sector_id, commodity_id),
    INDEX ix_ai_training_data_quality_training (quality_score, used_in_training)
);
```

## API Data Structures

### TradingRecommendation

```typescript
interface TradingRecommendation {
  id: string;
  type: 'buy' | 'sell' | 'route' | 'avoid' | 'wait';
  commodity_id?: string;
  sector_id?: string;
  target_price?: number;
  expected_profit?: number;
  confidence: number; // 0-1
  risk_level: 'low' | 'medium' | 'high';
  reasoning: string;
  priority: number; // 1-5
  expires_at: string; // ISO datetime
}
```

### MarketAnalysis

```typescript
interface MarketAnalysis {
  commodity_id: string;
  current_price: number;
  predicted_price: number;
  price_trend: 'rising' | 'falling' | 'stable';
  volatility: number;
  confidence: number;
  factors: string[];
  time_horizon: number; // hours
}
```

### PlayerTradingProfile

```typescript
interface PlayerTradingProfile {
  player_id: string;
  risk_tolerance: number; // 0-1
  ai_assistance_level: 'minimal' | 'medium' | 'full';
  average_profit_per_trade: number;
  total_trades_analyzed: number;
  preferred_commodities?: Record<string, number>;
  trading_patterns?: Record<string, any>;
  performance_metrics?: Record<string, any>;
  last_active_sector?: string;
}
```

### OptimalRoute

```typescript
interface OptimalRoute {
  sectors: string[];
  total_profit: number;
  total_distance: number;
  estimated_time: number; // minutes
  risk_score: number;
  commodity_chain: Array<{
    sector: string;
    commodity: string;
    action: 'buy' | 'sell';
    price: number;
    quantity: number;
  }>;
}
```

## API Endpoints

### Recommendations

- `GET /api/v1/ai/recommendations` - Get current recommendations
- `GET /api/v1/ai/recommendations/history` - Get recommendation history
- `POST /api/v1/ai/recommendations/{id}/feedback` - Submit feedback

### Market Analysis

- `GET /api/v1/ai/market-analysis/{commodity_id}` - Get market analysis
- `POST /api/v1/ai/optimize-route` - Get optimal route recommendations

### Profile Management

- `GET /api/v1/ai/profile` - Get player trading profile
- `PUT /api/v1/ai/profile` - Update AI preferences
- `POST /api/v1/ai/profile/trade-update` - Update with new trade data

### Performance

- `GET /api/v1/ai/performance` - Get AI performance statistics

## Business Logic

### Recommendation Generation

1. **Market Opportunities**: Analyze price predictions vs current prices
2. **Route Optimization**: Calculate multi-sector profit paths
3. **Risk Warnings**: Identify high-risk situations
4. **Personalization**: Factor in player's risk tolerance and patterns

### Learning Algorithm

1. **Data Collection**: Gather trade data, market prices, player actions
2. **Pattern Recognition**: Identify successful trading patterns
3. **Model Training**: Update prediction models with new data
4. **Validation**: Test model accuracy against historical data

### Performance Tracking

- **Accuracy**: Compare predictions to actual outcomes
- **User Satisfaction**: Track recommendation acceptance rates
- **Profit Impact**: Measure improvement in player profits
- **Continuous Improvement**: Adjust models based on performance

## Security Considerations

### Data Protection
- All player data encrypted at rest
- API endpoints require authentication
- Rate limiting on AI requests
- Audit logging for all AI actions

### Privacy
- Player trading patterns anonymized for model training
- Optional data sharing preferences
- GDPR compliance for data export/deletion

### Anti-Gaming
- Detect and prevent AI manipulation
- Monitor for unusual recommendation patterns
- Validate all trade data before training

## Integration Points

### Existing Systems
- **Player Management**: Trading profiles linked to player accounts
- **Market Data**: Real-time price feeds for predictions
- **Trading System**: Integration with existing trade mechanics
- **WebSocket Service**: Real-time recommendation delivery

### External Dependencies
- **Scikit-learn**: Machine learning algorithms
- **Prophet**: Time series forecasting
- **Pandas**: Data manipulation
- **NumPy**: Numerical computations

## Monitoring & Metrics

### Key Performance Indicators
- Prediction accuracy rate (target: >70%)
- User acceptance rate (target: >40%)
- Profit improvement (target: 20% increase)
- Response time (target: <200ms)

### Alerts
- Model accuracy drops below 60%
- High user rejection rate (>80%)
- API response time exceeds 500ms
- Database query timeouts

## Future Enhancements

### Phase 2 Features
- Natural language interaction with AI assistant
- Multi-player intelligence sharing
- Advanced risk modeling
- Economic scenario simulation

### Machine Learning Improvements
- Deep learning for complex pattern recognition
- Reinforcement learning for strategy optimization
- Ensemble methods for improved accuracy
- Real-time model adaptation

---

*This document serves as the complete data definition for the AI Trading Intelligence System and should be updated whenever schema or API changes are made.*