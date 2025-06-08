# Quantum Trading API Documentation
**Enterprise-Grade Quantum Trading Backend Integration**

## Overview

The Quantum Trading API provides both REST endpoints and WebSocket connections for real-time quantum-enhanced space trading. Built with enterprise security, the API supports quantum superposition trades, ghost trading simulations, and ARIA AI integration.

## Base URL

- **Production**: `https://api.sectorwars2102.com/api/v1/quantum-trading`
- **Development**: `http://localhost:8080/api/v1/quantum-trading`
- **GitHub Codespaces**: `https://{workspace}-8080.app.github.dev/api/v1/quantum-trading`

## Authentication

All API endpoints require JWT authentication via Bearer token:

```http
Authorization: Bearer {jwt_token}
```

Obtain JWT token via the authentication endpoints:
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/oauth/google`
- `POST /api/v1/auth/oauth/paypal`

## WebSocket Connection

### Connection URL
```
ws://localhost:8080/api/v1/ws/connect?token={jwt_token}
```

### Message Format
```json
{
  "type": "quantum_trading",
  "action": "create_quantum_trade",
  "params": {
    "commodity": "ORE",
    "action": "buy",
    "quantity": 100,
    "price": 50.0
  },
  "timestamp": "2025-06-08T12:00:00Z",
  "signature": "abc123..."
}
```

## REST API Endpoints

### Create Quantum Trade
Creates a trade in quantum superposition with multiple probability states.

**Endpoint**: `POST /create-quantum-trade`

**Request Body**:
```json
{
  "commodity": "ORE",
  "action": "buy",
  "quantity": 100,
  "price": 50.0,
  "max_price": 55.0,
  "min_price": 45.0
}
```

**Response**:
```json
{
  "trade_id": "quantum_20250608_abc123",
  "commodity": "ORE",
  "action": "buy", 
  "quantity": 100,
  "superposition_states": [
    {
      "state_id": "optimistic",
      "probability": 0.3,
      "price": 52.0,
      "profit": 500,
      "risk": "low"
    },
    {
      "state_id": "likely", 
      "probability": 0.4,
      "price": 50.0,
      "profit": 300,
      "risk": "medium"
    },
    {
      "state_id": "pessimistic",
      "probability": 0.3, 
      "price": 48.0,
      "profit": 100,
      "risk": "high"
    }
  ],
  "probability": 0.85,
  "manipulation_warning": false,
  "dna_sequence": "ATCG...",
  "message": "Quantum trade created successfully"
}
```

### Execute Ghost Trade
Runs a risk-free simulation of a trade without affecting your portfolio.

**Endpoint**: `POST /ghost-trade`

**Request Body**:
```json
{
  "commodity": "ORGANICS",
  "action": "sell",
  "quantity": 200,
  "price": 75.0
}
```

**Response**:
```json
{
  "trade_id": "ghost_20250608_def456",
  "expected_profit": 750,
  "recommendation": "STRONG SELL - High profit potential with low risk",
  "outcomes": [
    {
      "outcome": "Best Case",
      "probability": 0.25,
      "profit": 1200
    },
    {
      "outcome": "Likely Case", 
      "probability": 0.50,
      "profit": 750
    },
    {
      "outcome": "Worst Case",
      "probability": 0.25, 
      "profit": 300
    }
  ],
  "message": "Ghost trade simulation completed"
}
```

### Collapse Quantum Trade
Executes a quantum trade by collapsing the superposition to reality.

**Endpoint**: `POST /collapse-quantum-trade/{trade_id}`

**Response**:
```json
{
  "trade_id": "quantum_20250608_abc123",
  "status": "executed",
  "final_state": "likely",
  "profit": 300,
  "price": 50.0,
  "message": "Quantum trade collapsed and executed successfully"
}
```

### Get Quantum State
Returns current quantum trading engine status and statistics.

**Endpoint**: `GET /quantum-state`

**Response**:
```json
{
  "status": "active",
  "active_trades": 3,
  "total_volume": 1500,
  "success_rate": 0.73,
  "quantum_field_strength": 0.68,
  "manipulation_alerts": 0,
  "player_statistics": {
    "total_trades": 47,
    "profit_loss": 12500,
    "best_trade": 2300,
    "trading_dna_evolution": 0.89
  },
  "message": "Quantum engine operational"
}
```

### Get AI Recommendations
Returns ARIA AI-powered trading recommendations based on personal patterns.

**Endpoint**: `GET /recommendations`

**Response**:
```json
{
  "recommendations": [
    {
      "commodity": "TECHNOLOGY",
      "action": "buy",
      "confidence": 0.92,
      "reasoning": "High quantum field resonance detected in tech sectors",
      "quantum_advantage": "67% probability of optimistic quantum state",
      "expected_profit": 850,
      "risk_assessment": "low"
    }
  ],
  "market_sentiment": "bullish_quantum_enhanced",
  "manipulation_alerts": [
    "Unusual EQUIPMENT trading volume in Sector 15 - proceed with caution"
  ],
  "personal_insights": "Based on your trading DNA, you perform 23% better with morning trades",
  "message": "AI recommendations generated successfully"
}
```

### Create Trade Cascade
Creates a complex multi-step quantum trading strategy.

**Endpoint**: `POST /create-cascade`

**Request Body**:
```json
{
  "cascade_name": "Resource Arbitrage Strategy",
  "trades": [
    {
      "commodity": "ORE",
      "action": "buy", 
      "quantity": 100,
      "trigger_condition": "immediate"
    },
    {
      "commodity": "EQUIPMENT",
      "action": "sell",
      "quantity": 50,
      "trigger_condition": "first_trade_profit > 200"
    }
  ]
}
```

**Response**:
```json
{
  "cascade_id": "cascade_20250608_ghi789",
  "status": "created",
  "expected_steps": 2,
  "estimated_completion": "2025-06-08T14:30:00Z",
  "risk_assessment": "medium",
  "message": "Trade cascade created successfully"
}
```

## WebSocket Events

### Outgoing Messages (Client → Server)

#### Quantum Trading Message
```json
{
  "type": "quantum_trading",
  "action": "create_quantum_trade",
  "params": {
    "commodity": "FUEL",
    "action": "buy",
    "quantity": 150
  },
  "timestamp": "2025-06-08T12:00:00Z",
  "signature": "..."
}
```

#### ARIA Chat Message
```json
{
  "type": "aria_chat", 
  "content": "What's the best quantum trade right now?",
  "context": "quantum_trading",
  "conversation_id": "conv_123",
  "timestamp": "2025-06-08T12:00:00Z",
  "signature": "..."
}
```

### Incoming Messages (Server → Client)

#### Quantum Trade Created
```json
{
  "type": "quantum_trade_created",
  "data": {
    "trade_id": "quantum_20250608_jkl012",
    "commodity": "FUEL",
    "action": "buy",
    "quantity": 150,
    "superposition_states": [...],
    "probability": 0.78,
    "manipulation_warning": false
  },
  "timestamp": "2025-06-08T12:00:00Z"
}
```

#### Ghost Trade Result
```json
{
  "type": "ghost_trade_result",
  "data": {
    "trade_id": "ghost_20250608_mno345", 
    "expected_profit": 950,
    "recommendation": "MODERATE BUY - Good profit potential",
    "outcomes": [...]
  },
  "timestamp": "2025-06-08T12:00:00Z"
}
```

#### Quantum Trade Collapsed
```json
{
  "type": "quantum_trade_collapsed",
  "data": {
    "trade_id": "quantum_20250608_jkl012",
    "status": "success",
    "trade": {
      "id": "quantum_20250608_jkl012",
      "commodity": "FUEL",
      "profit": 450,
      "final_price": 52.5
    }
  },
  "timestamp": "2025-06-08T12:00:00Z"
}
```

#### ARIA Response
```json
{
  "type": "aria_response",
  "conversation_id": "conv_123",
  "data": {
    "message": "I recommend buying TECHNOLOGY in Sector 12 - quantum field strength is 82%",
    "confidence": 0.91,
    "context_used": "quantum_trading", 
    "actions": [
      {
        "type": "quantum_trade_suggestion",
        "commodity": "TECHNOLOGY",
        "action": "buy",
        "quantity": 75
      }
    ],
    "suggestions": [
      "Run ghost simulation first",
      "Check market manipulation indicators",
      "Consider quantum field timing"
    ]
  },
  "timestamp": "2025-06-08T12:00:00Z"
}
```

## Error Handling

### HTTP Status Codes

- `200` - Success
- `201` - Created (new quantum trade)
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (invalid/expired JWT)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (trade ID not found)
- `409` - Conflict (trade already collapsed)
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error

### Error Response Format
```json
{
  "error": {
    "code": "INVALID_QUANTUM_PARAMETERS",
    "message": "Quantum trade parameters exceed safe uncertainty limits",
    "details": {
      "field": "quantity",
      "max_allowed": 1000,
      "provided": 1500
    }
  },
  "timestamp": "2025-06-08T12:00:00Z",
  "request_id": "req_abc123"
}
```

### Common Error Codes

- `INVALID_QUANTUM_PARAMETERS` - Trade parameters invalid
- `INSUFFICIENT_FUNDS` - Not enough credits for trade
- `QUANTUM_FIELD_UNSTABLE` - Sector quantum field too unstable
- `MANIPULATION_DETECTED` - Potential market manipulation
- `TRADE_NOT_FOUND` - Quantum trade ID not found
- `ALREADY_COLLAPSED` - Trade already executed
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `UNAUTHORIZED_ACCESS` - Invalid authentication

## Rate Limiting

### REST API Limits
- **Standard Users**: 100 requests/minute
- **Premium Users**: 500 requests/minute
- **Enterprise**: 2000 requests/minute

### WebSocket Limits
- **Message Rate**: 30 messages/minute
- **Quantum Trades**: 10 trades/minute
- **ARIA Chat**: 20 messages/minute

Rate limit headers included in responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1683518400
```

## Security Features

### Authentication Security
- **JWT Tokens**: Signed with RS256 algorithm
- **Token Expiry**: 24 hours for standard, 7 days for "remember me"
- **Refresh Tokens**: Secure token rotation
- **Multi-Factor Authentication**: Optional TOTP support

### Quantum Trading Security
- **Input Validation**: All parameters validated against quantum physics constraints
- **Manipulation Detection**: Real-time monitoring for suspicious patterns
- **Trade Signing**: Cryptographic signatures prevent trade tampering
- **Rate Limiting**: Prevents abuse and market manipulation

### WebSocket Security
- **Connection Authentication**: JWT required for WebSocket connection
- **Message Signing**: All messages cryptographically signed
- **Replay Protection**: Timestamp validation prevents replay attacks
- **Connection Limits**: Maximum 3 concurrent connections per user

## SDK Examples

### JavaScript/TypeScript
```typescript
import { QuantumTradingAPI } from '@sectorwars/quantum-trading-sdk';

const api = new QuantumTradingAPI({
  baseURL: 'http://localhost:8080/api/v1/quantum-trading',
  token: 'your_jwt_token'
});

// Create quantum trade
const trade = await api.createQuantumTrade({
  commodity: 'ORE',
  action: 'buy',
  quantity: 100
});

// Run ghost simulation
const ghost = await api.executeGhostTrade({
  commodity: 'ORE', 
  action: 'sell',
  quantity: 100
});

// Collapse to reality
const result = await api.collapseQuantumTrade(trade.trade_id);
```

### Python
```python
from sectorwars_quantum import QuantumTradingClient

client = QuantumTradingClient(
    base_url='http://localhost:8080/api/v1/quantum-trading',
    token='your_jwt_token'
)

# Create quantum trade
trade = client.create_quantum_trade(
    commodity='ORGANICS',
    action='sell', 
    quantity=200
)

# Execute ghost trade
ghost = client.execute_ghost_trade(
    commodity='ORGANICS',
    action='buy',
    quantity=150
)

# Get recommendations
recs = client.get_ai_recommendations()
```

## Testing

### Sandbox Environment
- **URL**: `http://localhost:8080/api/v1/quantum-trading`
- **Test Data**: Pre-populated with sample quantum trades
- **Rate Limits**: Relaxed for testing (1000 requests/minute)
- **Authentication**: Test JWT tokens available

### Test Quantum Trades
The API provides test quantum trades for development:
```json
{
  "test_trades": [
    {
      "trade_id": "test_quantum_001",
      "commodity": "ORE", 
      "action": "buy",
      "quantity": 100,
      "status": "superposition"
    }
  ]
}
```

## Support

### Documentation
- **Full API Docs**: `/docs/api/quantum-trading`
- **WebSocket Guide**: `/docs/websocket/quantum-trading`
- **ARIA Integration**: `/docs/features/aria-ai-quantum-integration`

### Community
- **Discord**: #quantum-trading-api
- **Forums**: community.sectorwars2102.com
- **GitHub**: github.com/sectorwars2102/quantum-trading-api

### Enterprise Support
- **Email**: enterprise@sectorwars2102.com
- **SLA**: 99.9% uptime guarantee
- **Custom Integration**: Available for large deployments

---

## 🚀 Welcome to Quantum Trading

The Quantum Trading API represents a breakthrough in gaming technology - the first API to implement real quantum mechanics for virtual trading. With enterprise-grade security, real-time WebSocket communication, and ARIA AI integration, developers can create revolutionary quantum trading experiences.

**Happy Quantum Coding!** ⚛️💻

---
**Last Updated**: June 8, 2025  
**API Version**: v1.0  
**OpenAPI Spec**: Available at `/api/v1/quantum-trading/openapi.json`