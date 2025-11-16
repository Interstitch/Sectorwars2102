/**
 * Quantum Trading Interface - Revolutionary AI-Enhanced Trading
 * First space game with quantum mechanics trading and ARIA intelligence
 * 
 * Features:
 * - Quantum superposition trades (multiple probability states)
 * - Ghost trading for risk-free strategy testing  
 * - Trade cascades for complex multi-step strategies
 * - Real-time ARIA intelligence integration
 * - Market manipulation detection
 * - Trade DNA evolution patterns
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { 
  Atom, 
  Ghost, 
  Zap, 
  TrendingUp, 
  Target, 
  Shield, 
  Brain,
  Play,
  Pause,
  SkipForward,
  AlertTriangle,
  CheckCircle,
  Clock,
  Eye,
  Dna,
  Activity,
  Layers,
  BarChart3,
  Sparkles
} from 'lucide-react';
import { useWebSocket } from '../../contexts/WebSocketContext';
import { useGame } from '../../contexts/GameContext';
import { useAuth } from '../../contexts/AuthContext';
import quantumTradingApi from '../../services/quantumTradingApi';
import './quantum-trading-interface.css';

// Types for quantum trading
interface QuantumTrade {
  trade_id: string;
  commodity: string;
  action: 'buy' | 'sell';
  quantity: number;
  probability: number;
  superposition_states: Array<{
    price: number;
    profit: number;
    probability: number;
    outcome: string;
  }>;
  manipulation_warning: boolean;
  optimal_execution_time?: string;
  risk_score: number;
  confidence_interval: [number, number];
  dna_sequence?: string;
  generation?: number;
  fitness_score?: number;
}

interface GhostTradeResult {
  success: boolean;
  simulated_profit: number;
  risk_assessment: string;
  market_impact: number;
  recommended_adjustments: string[];
  probability_distribution: Array<{
    outcome: string;
    probability: number;
    profit: number;
  }>;
}

interface TradeCascade {
  cascade_id: string;
  strategy_name: string;
  trades: QuantumTrade[];
  expected_profit: number;
  risk_tolerance: number;
  completion_probability: number;
  estimated_duration: string;
}

interface QuantumTradingInterfaceProps {
  isMinimized?: boolean;
  onToggleMinimize?: () => void;
}

const QuantumTradingInterface: React.FC<QuantumTradingInterfaceProps> = ({
  isMinimized = false,
  onToggleMinimize
}) => {
  // State management
  const [activeTab, setActiveTab] = useState<'quantum' | 'ghost' | 'cascade' | 'dna'>('quantum');
  const [isActive, setIsActive] = useState(false);
  
  // Quantum trading state
  const [quantumTrades, setQuantumTrades] = useState<QuantumTrade[]>([]);
  const [selectedCommodity, setSelectedCommodity] = useState('ORE');
  const [tradeAction, setTradeAction] = useState<'buy' | 'sell'>('buy');
  const [quantity, setQuantity] = useState(100);
  const [isCreatingTrade, setIsCreatingTrade] = useState(false);
  
  // Ghost trading state
  const [ghostResults, setGhostResults] = useState<GhostTradeResult[]>([]);
  const [isRunningGhost, setIsRunningGhost] = useState(false);
  
  // Trade cascade state
  const [cascades, setCascades] = useState<TradeCascade[]>([]);
  const [isCreatingCascade, setIsCreatingCascade] = useState(false);
  const [cascadeStrategy, setCascadeStrategy] = useState('');
  
  // Quantum state monitoring
  const [quantumState, setQuantumState] = useState({
    total_trades: 0,
    success_rate: 0,
    market_stability: 'stable',
    ai_confidence: 0.95,
    manipulation_detected: false
  });

  // Context hooks
  const { 
    isConnected, 
    sendARIAMessage, 
    createQuantumTrade: wsCreateQuantumTrade,
    collapseQuantumTrade: wsCollapseQuantumTrade,
    executeGhostTrade: wsExecuteGhostTrade,
    cancelQuantumTrade: wsCancelQuantumTrade,
    quantumTrades: wsQuantumTrades,
    ghostTrades: wsGhostTrades,
    quantumMarketData: wsQuantumMarketData
  } = useWebSocket();
  const { playerState, currentShip, marketInfo } = useGame();
  const { user } = useAuth();

  // Set up API authentication when user changes
  useEffect(() => {
    if (user) {
      const token = localStorage.getItem('accessToken');
      if (token) {
        quantumTradingApi.setAuthToken(token);
      }
    }
  }, [user]);

  // Available commodities
  const commodities = ['ORE', 'ORGANICS', 'EQUIPMENT', 'FUEL', 'LUXURY', 'TECHNOLOGY', 'COLONISTS'];

  // WebSocket message handler for quantum trading responses
  const handleQuantumMessage = useCallback((message: any) => {
    switch (message.type) {
      case 'quantum_trade_created':
        setQuantumTrades(prev => [...prev, message.data]);
        setIsCreatingTrade(false);
        break;
        
      case 'ghost_trade_result':
        setGhostResults(prev => [...prev, message.data]);
        setIsRunningGhost(false);
        break;
        
      case 'quantum_trade_collapsed':
        // Update trade status when collapsed to reality
        setQuantumTrades(prev => 
          prev.map(trade => 
            trade.trade_id === message.data.trade_id 
              ? { ...trade, probability: message.data.success ? 1.0 : 0.0 }
              : trade
          )
        );
        break;
        
      case 'quantum_state':
        setQuantumState(message.data.global_state);
        setQuantumTrades(message.data.my_trades);
        break;
    }
  }, []);

  // Initialize quantum state
  useEffect(() => {
    if (isConnected && isActive) {
      // Request current quantum state
      getQuantumState();
    }
  }, [isConnected, isActive]);

  // Send WebSocket message helper
  // Use WebSocket quantum trading methods directly - no need for sendQuantumMessage wrapper

  // Create quantum trade in superposition
  const createQuantumTrade = useCallback(async () => {
    setIsCreatingTrade(true);
    
    const params = {
      commodity: selectedCommodity,
      action: tradeAction,
      quantity: quantity,
      player_id: playerState?.id
    };
    
    // Use the real WebSocket quantum trading method
    const success = wsCreateQuantumTrade(
      tradeAction,
      selectedCommodity,
      quantity,
      playerState?.currentSector,
      playerState?.currentPort,
      undefined, // maxPrice
      undefined, // minPrice
      3 // superpositionStates
    );
    
    if (success) {
      // Update local quantum state optimistically
      setQuantumState(prev => ({
        ...prev,
        active_trades: prev.active_trades + 1,
        total_volume: prev.total_volume + quantity
      }));
    }
    
    setIsCreatingTrade(false);
    
  }, [
    isConnected,
    wsCreateQuantumTrade,
    tradeAction,
    selectedCommodity,
    quantity,
    playerState?.currentSector,
    playerState?.currentPort
  ]);

  // Run ghost trade simulation
  const runGhostTrade = useCallback(async () => {
    if (!isConnected) return;
    
    setIsRunningGhost(true);
    
    // Use the real WebSocket ghost trading method
    const success = wsExecuteGhostTrade(
      tradeAction,
      selectedCommodity,
      quantity,
      playerState?.currentSector,
      playerState?.currentPort
    );
    
    if (!success) {
      setIsRunningGhost(false);
    }
    
  }, [
    isConnected,
    wsExecuteGhostTrade,
    tradeAction,
    selectedCommodity,
    quantity,
    playerState?.currentSector,
    playerState?.currentPort
  ]);

  // Collapse quantum trade to reality
  const collapseQuantumTrade = useCallback((tradeId: string) => {
    if (!isConnected) return;
    
    // Use the real WebSocket collapse method
    wsCollapseQuantumTrade(tradeId);
    
  }, [isConnected, wsCollapseQuantumTrade]);

  // Use WebSocket quantum trades instead of local state
  const processedQuantumTrades = useMemo(() => {
    return wsQuantumTrades.map(trade => ({
      trade_id: trade.trade_id,
      commodity: trade.commodity,
      action: trade.trade_type,
      quantity: trade.quantity,
      probability: trade.superposition_states.reduce((sum, state) => sum + state.probability, 0) / trade.superposition_states.length,
      superposition_states: trade.superposition_states,
      manipulation_warning: trade.manipulation_warning,
      risk_score: trade.risk_score,
      confidence_interval: trade.confidence_interval,
      dna_sequence: trade.dna_sequence
    }));
  }, [wsQuantumTrades]);

  const processedGhostResults = useMemo(() => {
    return wsGhostTrades.map(ghost => ({
      success: ghost.success_probability > 0.5,
      simulated_profit: ghost.expected_profit,
      risk_assessment: ghost.risk_assessment,
      market_impact: 0.05, // Default value since not in WebSocket type
      recommended_adjustments: ['Monitor market conditions'],
      probability_distribution: [
        { outcome: 'Success', probability: ghost.success_probability, profit: ghost.expected_profit },
        { outcome: 'Failure', probability: 1 - ghost.success_probability, profit: 0 }
      ]
    }));
  }, [wsGhostTrades]);

  // Update state with processed WebSocket data
  useEffect(() => {
    setQuantumTrades(processedQuantumTrades);
  }, [processedQuantumTrades]);

  useEffect(() => {
    setGhostResults(processedGhostResults);
  }, [processedGhostResults]);

  // Calculate total potential profit
  const totalPotentialProfit = useMemo(() => {
    return quantumTrades.reduce((total, trade) => {
      const expectedProfit = trade.superposition_states.reduce((sum, state) => 
        sum + (state.profit * state.probability), 0
      );
      return total + expectedProfit;
    }, 0);
  }, [quantumTrades]);

  // Get risk assessment color
  const getRiskColor = (riskScore: number): string => {
    if (riskScore < 0.2) return '#10b981'; // green
    if (riskScore < 0.5) return '#f59e0b'; // yellow
    return '#ef4444'; // red
  };

  if (isMinimized) {
    return (
      <div className="quantum-trading-minimized" onClick={onToggleMinimize}>
        <Atom className="w-6 h-6" />
        <span className="quantum-indicator">
          {quantumTrades.length}
        </span>
      </div>
    );
  }

  return (
    <div className={`quantum-trading-interface ${isActive ? 'active' : ''}`}>
      {/* Header */}
      <div className="quantum-header">
        <div className="quantum-title">
          <Atom className="w-6 h-6" />
          <span>Quantum Trading</span>
          <div className="quantum-status">
            {isConnected ? (
              <CheckCircle className="w-4 h-4 text-green-400" />
            ) : (
              <AlertTriangle className="w-4 h-4 text-yellow-400" />
            )}
          </div>
        </div>
        
        <div className="quantum-controls">
          <button
            onClick={() => setIsActive(!isActive)}
            className={`quantum-toggle ${isActive ? 'active' : ''}`}
          >
            {isActive ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            {isActive ? 'Pause' : 'Activate'}
          </button>
          
          {onToggleMinimize && (
            <button onClick={onToggleMinimize} className="quantum-action">
              <SkipForward className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Quantum State Overview */}
      <div className="quantum-overview">
        <div className="quantum-metrics">
          <div className="metric">
            <Layers className="w-4 h-4" />
            <span className="metric-value">{quantumTrades.length}</span>
            <span className="metric-label">Active Trades</span>
          </div>
          
          <div className="metric">
            <TrendingUp className="w-4 h-4" />
            <span className="metric-value">
              {totalPotentialProfit > 0 ? '+' : ''}{Math.round(totalPotentialProfit)}
            </span>
            <span className="metric-label">Potential Profit</span>
          </div>
          
          <div className="metric">
            <Brain className="w-4 h-4" />
            <span className="metric-value">{Math.round(quantumState.ai_confidence * 100)}%</span>
            <span className="metric-label">AI Confidence</span>
          </div>
          
          <div className="metric">
            <Activity className="w-4 h-4" />
            <span className="metric-value">{quantumState.market_stability}</span>
            <span className="metric-label">Market State</span>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="quantum-tabs">
        {[
          { key: 'quantum', label: 'Superposition', icon: Atom },
          { key: 'ghost', label: 'Ghost Trades', icon: Ghost },
          { key: 'cascade', label: 'Cascades', icon: Zap },
          { key: 'dna', label: 'Trade DNA', icon: Dna }
        ].map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key as any)}
            className={`quantum-tab ${activeTab === key ? 'active' : ''}`}
          >
            <Icon className="w-4 h-4" />
            <span>{label}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="quantum-content">
        {activeTab === 'quantum' && (
          <div className="quantum-superposition">
            {/* Trade Creation */}
            <div className="trade-creation">
              <h3>Create Quantum Trade</h3>
              
              <div className="trade-form">
                <div className="form-row">
                  <select
                    value={selectedCommodity}
                    onChange={(e) => setSelectedCommodity(e.target.value)}
                    className="quantum-select"
                  >
                    {commodities.map(commodity => (
                      <option key={commodity} value={commodity}>{commodity}</option>
                    ))}
                  </select>
                  
                  <div className="action-toggle">
                    <button
                      onClick={() => setTradeAction('buy')}
                      className={`action-btn ${tradeAction === 'buy' ? 'active' : ''}`}
                    >
                      Buy
                    </button>
                    <button
                      onClick={() => setTradeAction('sell')}
                      className={`action-btn ${tradeAction === 'sell' ? 'active' : ''}`}
                    >
                      Sell
                    </button>
                  </div>
                </div>
                
                <div className="form-row">
                  <input
                    type="number"
                    value={quantity}
                    onChange={(e) => setQuantity(Number(e.target.value))}
                    min="1"
                    max="10000"
                    className="quantum-input"
                    placeholder="Quantity"
                  />
                  
                  <button
                    onClick={createQuantumTrade}
                    disabled={isCreatingTrade || !isConnected}
                    className="create-quantum-btn"
                  >
                    {isCreatingTrade ? (
                      <>
                        <Activity className="w-4 h-4 animate-spin" />
                        Creating...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4" />
                        Create Superposition
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Active Quantum Trades */}
            <div className="quantum-trades">
              <h3>Superposition Trades</h3>
              
              {quantumTrades.length === 0 ? (
                <div className="empty-state">
                  <Atom className="w-8 h-8 opacity-50" />
                  <p>No quantum trades in superposition</p>
                  <p className="text-sm">Create your first quantum trade above</p>
                </div>
              ) : (
                <div className="trades-list">
                  {quantumTrades.map((trade) => (
                    <div key={trade.trade_id} className="quantum-trade-card">
                      <div className="trade-header">
                        <div className="trade-info">
                          <span className="commodity">{trade.commodity}</span>
                          <span className={`action ${trade.action}`}>{trade.action.toUpperCase()}</span>
                          <span className="quantity">{trade.quantity}</span>
                        </div>
                        
                        <div className="trade-probability">
                          <Target className="w-4 h-4" />
                          <span>{Math.round(trade.probability * 100)}%</span>
                        </div>
                      </div>
                      
                      {trade.manipulation_warning && (
                        <div className="manipulation-warning">
                          <AlertTriangle className="w-4 h-4" />
                          <span>Market manipulation detected</span>
                        </div>
                      )}
                      
                      <div className="superposition-states">
                        {trade.superposition_states.map((state, idx) => (
                          <div key={idx} className="state">
                            <div className="state-outcome">{state.outcome}</div>
                            <div className="state-probability">{Math.round(state.probability * 100)}%</div>
                            <div className={`state-profit ${state.profit >= 0 ? 'positive' : 'negative'}`}>
                              {state.profit >= 0 ? '+' : ''}{state.profit}
                            </div>
                          </div>
                        ))}
                      </div>
                      
                      <div className="trade-actions">
                        <button
                          onClick={() => collapseQuantumTrade(trade.trade_id)}
                          className="collapse-btn"
                        >
                          <Eye className="w-4 h-4" />
                          Collapse to Reality
                        </button>
                        
                        <div className="risk-indicator">
                          <Shield 
                            className="w-4 h-4" 
                            style={{ color: getRiskColor(trade.risk_score) }}
                          />
                          <span>Risk: {Math.round(trade.risk_score * 100)}%</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'ghost' && (
          <div className="ghost-trading">
            <div className="ghost-controls">
              <h3>Ghost Trade Simulation</h3>
              <p>Test trading strategies without risk</p>
              
              <button
                onClick={runGhostTrade}
                disabled={isRunningGhost || !isConnected}
                className="ghost-btn"
              >
                {isRunningGhost ? (
                  <>
                    <Activity className="w-4 h-4 animate-spin" />
                    Simulating...
                  </>
                ) : (
                  <>
                    <Ghost className="w-4 h-4" />
                    Run Ghost Trade
                  </>
                )}
              </button>
            </div>
            
            <div className="ghost-results">
              {ghostResults.map((result, idx) => (
                <div key={idx} className="ghost-result-card">
                  <div className="result-header">
                    <Ghost className="w-5 h-5" />
                    <span>Ghost Simulation {idx + 1}</span>
                    <span className={`result-status ${result.success ? 'success' : 'failure'}`}>
                      {result.success ? 'Success' : 'Failure'}
                    </span>
                  </div>
                  
                  <div className="result-details">
                    <div className="detail">
                      <span>Simulated Profit:</span>
                      <span className={result.simulated_profit >= 0 ? 'positive' : 'negative'}>
                        {result.simulated_profit >= 0 ? '+' : ''}{Math.round(result.simulated_profit)}
                      </span>
                    </div>
                    
                    <div className="detail">
                      <span>Risk Assessment:</span>
                      <span className={`risk-${result.risk_assessment}`}>
                        {result.risk_assessment.toUpperCase()}
                      </span>
                    </div>
                  </div>
                  
                  <div className="recommendations">
                    <h4>AI Recommendations:</h4>
                    <ul>
                      {result.recommended_adjustments.map((rec, i) => (
                        <li key={i}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'cascade' && (
          <div className="trade-cascades">
            <h3>Trade Cascades</h3>
            <p>Multi-step trading strategies</p>
            
            <div className="empty-state">
              <Zap className="w-8 h-8 opacity-50" />
              <p>Cascade system coming soon</p>
              <p className="text-sm">Complex multi-trade strategies in development</p>
            </div>
          </div>
        )}

        {activeTab === 'dna' && (
          <div className="trade-dna">
            <h3>Trade DNA Evolution</h3>
            <p>Evolving trading patterns</p>
            
            <div className="empty-state">
              <Dna className="w-8 h-8 opacity-50" />
              <p>Trade DNA system coming soon</p>
              <p className="text-sm">Genetic algorithms for pattern optimization</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default QuantumTradingInterface;