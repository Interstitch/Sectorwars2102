/**
 * Smart Trading Automation Assistant - ARIA-Powered Automated Trading
 * Part of Foundation Sprint: Revolutionary Trading Automation with AI
 * OWASP Compliant • Real-Time Execution • Risk Management
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { realtimeWebSocket, TradingAutomationRule, TradingCondition } from '../../services/realtimeWebSocket';
import './smart-trading-automation.css';

// Security-first interfaces
interface AutomationStatus {
  isActive: boolean;
  totalProfitToday: number;
  tradesExecuted: number;
  rulesActive: number;
  lastAction: {
    type: 'buy' | 'sell';
    commodity: string;
    amount: number;
    profit: number;
    timestamp: string;
    reasoning: string;
  } | null;
}

interface TradeDecision {
  shouldExecute: boolean;
  confidence: number;
  reasoning: string;
  estimatedProfit: number;
  riskScore: number;
}

interface SecurityLimits {
  maxTradesPerHour: number;
  maxConcurrentRules: number;
  cooldownBetweenTrades: number;
  maxInvestmentPerTrade: number;
  dailyLossLimit: number;
}

interface RuleTemplate {
  name: string;
  description: string;
  conditions: Partial<TradingCondition>[];
  riskLevel: 'conservative' | 'moderate' | 'aggressive';
  maxInvestment: number;
}

// OWASP A04: Security limits configuration
const SECURITY_LIMITS: SecurityLimits = {
  maxTradesPerHour: 20,
  maxConcurrentRules: 10,
  cooldownBetweenTrades: 30000, // 30 seconds
  maxInvestmentPerTrade: 100000, // Credits
  dailyLossLimit: 500000 // Credits
};

// Pre-defined rule templates for safety
const RULE_TEMPLATES: RuleTemplate[] = [
  {
    name: "Conservative Profit Lock",
    description: "Buy low, sell when 10% profit is achieved",
    conditions: [
      { type: 'price_below', value: 0, comparison: 'less_than' },
      { type: 'margin_exceeds', value: 10, comparison: 'greater_than' }
    ],
    riskLevel: 'conservative',
    maxInvestment: 50000
  },
  {
    name: "AI Confidence Trading",
    description: "Trade based on high AI confidence predictions",
    conditions: [
      { type: 'ai_confidence', value: 0.8, comparison: 'greater_than' }
    ],
    riskLevel: 'moderate',
    maxInvestment: 75000
  },
  {
    name: "Market Momentum",
    description: "Follow strong market trends with stop-loss",
    conditions: [
      { type: 'price_above', value: 0, comparison: 'greater_than' }
    ],
    riskLevel: 'aggressive',
    maxInvestment: 100000
  }
];

// Input validation utility
const validateTradingRule = (rule: Partial<TradingAutomationRule>): { isValid: boolean; errors: string[] } => {
  const errors: string[] = [];

  // OWASP A03: Input validation
  if (!rule.name || rule.name.length < 3 || rule.name.length > 50) {
    errors.push('Rule name must be 3-50 characters');
  }

  if (!rule.commodity || !/^[a-zA-Z0-9_-]+$/.test(rule.commodity)) {
    errors.push('Invalid commodity name');
  }

  if (!rule.maxInvestment || rule.maxInvestment <= 0 || rule.maxInvestment > SECURITY_LIMITS.maxInvestmentPerTrade) {
    errors.push(`Max investment must be 1-${SECURITY_LIMITS.maxInvestmentPerTrade} credits`);
  }

  if (!rule.buyConditions?.length && !rule.sellConditions?.length) {
    errors.push('At least one trading condition is required');
  }

  return { isValid: errors.length === 0, errors };
};

export const SmartTradingAutomation: React.FC = () => {
  // State management
  const [automationStatus, setAutomationStatus] = useState<AutomationStatus>({
    isActive: false,
    totalProfitToday: 0,
    tradesExecuted: 0,
    rulesActive: 0,
    lastAction: null
  });

  const [tradingRules, setTradingRules] = useState<TradingAutomationRule[]>([]);
  const [newRule, setNewRule] = useState<Partial<TradingAutomationRule>>({
    name: '',
    commodity: 'organics',
    buyConditions: [],
    sellConditions: [],
    riskLevel: 'moderate',
    maxInvestment: 10000,
    isActive: false
  });

  const [showRuleBuilder, setShowRuleBuilder] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<RuleTemplate | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const [recentTrades, setRecentTrades] = useState<any[]>([]);
  const [performanceMetrics, setPerformanceMetrics] = useState({
    successRate: 0,
    averageProfit: 0,
    totalVolume: 0,
    bestPerformingRule: null as string | null
  });

  // Available commodities
  const availableCommodities = useMemo(() => [
    'organics', 'equipment', 'energy', 'technology', 'luxury', 'minerals'
  ], []);

  // Initialize automation system
  useEffect(() => {
    const initializeAutomation = async () => {
      try {
        setIsLoading(true);
        
        // Load existing rules from backend
        await loadTradingRules();
        
        // Subscribe to trading signals for automation
        await realtimeWebSocket.subscribeToTradingSignals();
        
        // Load automation status
        await loadAutomationStatus();
        
      } catch (error) {
        console.error('❌ Failed to initialize automation system:', error);
        setErrors(['Failed to initialize automation system']);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAutomation();
  }, []);

  // WebSocket event handlers
  useEffect(() => {
    const handleTradingSignal = (message: any) => {
      if (message.data.type === 'automation_update') {
        setAutomationStatus(prev => ({
          ...prev,
          ...message.data.status
        }));
      }

      if (message.data.type === 'trade_executed') {
        const trade = message.data.trade;
        setRecentTrades(prev => [trade, ...prev.slice(0, 9)]); // Keep last 10 trades
        
        // Update metrics
        updatePerformanceMetrics(trade);
      }
    };

    realtimeWebSocket.on('trading_signal', handleTradingSignal);

    return () => {
      realtimeWebSocket.off('trading_signal', handleTradingSignal);
    };
  }, []);

  // Load trading rules from backend
  const loadTradingRules = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/trading/automation/rules', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const rules = await response.json();
        setTradingRules(rules);
      }
    } catch (error) {
      console.error('❌ Failed to load trading rules:', error);
    }
  }, []);

  // Load automation status
  const loadAutomationStatus = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/trading/automation/status', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const status = await response.json();
        setAutomationStatus(status);
      }
    } catch (error) {
      console.error('❌ Failed to load automation status:', error);
    }
  }, []);

  // Update performance metrics
  const updatePerformanceMetrics = useCallback((trade: any) => {
    setPerformanceMetrics(prev => {
      const newTotalVolume = prev.totalVolume + trade.amount;
      const newAverageProfit = ((prev.averageProfit * prev.totalVolume) + trade.profit) / newTotalVolume;
      
      return {
        ...prev,
        totalVolume: newTotalVolume,
        averageProfit: newAverageProfit,
        successRate: trade.profit > 0 ? prev.successRate + 1 : prev.successRate
      };
    });
  }, []);

  // Toggle automation
  const toggleAutomation = useCallback(async () => {
    try {
      setIsLoading(true);
      
      const newStatus = !automationStatus.isActive;
      
      const response = await fetch('/api/v1/trading/automation/toggle', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ active: newStatus })
      });

      if (response.ok) {
        setAutomationStatus(prev => ({ ...prev, isActive: newStatus }));
        
        // Send WebSocket message for real-time updates
        await realtimeWebSocket.sendChannelMessage('trading_signal', {
          action: 'toggle_automation',
          active: newStatus,
          timestamp: new Date().toISOString()
        });
      } else {
        throw new Error('Failed to toggle automation');
      }
    } catch (error) {
      console.error('❌ Failed to toggle automation:', error);
      setErrors(['Failed to toggle automation']);
    } finally {
      setIsLoading(false);
    }
  }, [automationStatus.isActive]);

  // Create new trading rule
  const createTradingRule = useCallback(async () => {
    const validation = validateTradingRule(newRule);
    if (!validation.isValid) {
      setErrors(validation.errors);
      return;
    }

    try {
      setIsLoading(true);
      setErrors([]);

      // OWASP A04: Security checks
      if (tradingRules.length >= SECURITY_LIMITS.maxConcurrentRules) {
        throw new Error(`Maximum ${SECURITY_LIMITS.maxConcurrentRules} rules allowed`);
      }

      const ruleData: TradingAutomationRule = {
        id: `rule_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        name: newRule.name!.slice(0, 50), // Truncate for security
        commodity: newRule.commodity!,
        buyConditions: newRule.buyConditions || [],
        sellConditions: newRule.sellConditions || [],
        riskLevel: newRule.riskLevel!,
        maxInvestment: Math.min(newRule.maxInvestment!, SECURITY_LIMITS.maxInvestmentPerTrade),
        isActive: false // Start inactive for safety
      };

      const response = await fetch('/api/v1/trading/automation/rules', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(ruleData)
      });

      if (response.ok) {
        const createdRule = await response.json();
        setTradingRules(prev => [...prev, createdRule]);
        
        // Reset form
        setNewRule({
          name: '',
          commodity: 'organics',
          buyConditions: [],
          sellConditions: [],
          riskLevel: 'moderate',
          maxInvestment: 10000,
          isActive: false
        });
        
        setShowRuleBuilder(false);
      } else {
        throw new Error('Failed to create trading rule');
      }
    } catch (error) {
      console.error('❌ Failed to create trading rule:', error);
      setErrors([error instanceof Error ? error.message : 'Failed to create trading rule']);
    } finally {
      setIsLoading(false);
    }
  }, [newRule, tradingRules.length]);

  // Toggle rule active status
  const toggleRule = useCallback(async (ruleId: string) => {
    try {
      const response = await fetch(`/api/v1/trading/automation/rules/${ruleId}/toggle`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        setTradingRules(prev => prev.map(rule => 
          rule.id === ruleId ? { ...rule, isActive: !rule.isActive } : rule
        ));
      }
    } catch (error) {
      console.error('❌ Failed to toggle rule:', error);
    }
  }, []);

  // Delete trading rule
  const deleteRule = useCallback(async (ruleId: string) => {
    if (!confirm('Are you sure you want to delete this trading rule?')) {
      return;
    }

    try {
      const response = await fetch(`/api/v1/trading/automation/rules/${ruleId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        setTradingRules(prev => prev.filter(rule => rule.id !== ruleId));
      }
    } catch (error) {
      console.error('❌ Failed to delete rule:', error);
    }
  }, []);

  // Apply rule template
  const applyTemplate = useCallback((template: RuleTemplate) => {
    setNewRule({
      name: template.name,
      commodity: 'organics',
      buyConditions: template.conditions as TradingCondition[],
      sellConditions: [],
      riskLevel: template.riskLevel,
      maxInvestment: template.maxInvestment,
      isActive: false
    });
    setSelectedTemplate(template);
  }, []);

  // Add trading condition
  const addCondition = useCallback((type: 'buy' | 'sell') => {
    const newCondition: TradingCondition = {
      type: 'price_below',
      value: 0,
      comparison: 'less_than'
    };

    setNewRule(prev => ({
      ...prev,
      [type === 'buy' ? 'buyConditions' : 'sellConditions']: [
        ...(prev[type === 'buy' ? 'buyConditions' : 'sellConditions'] || []),
        newCondition
      ]
    }));
  }, []);

  // Remove trading condition
  const removeCondition = useCallback((type: 'buy' | 'sell', index: number) => {
    setNewRule(prev => ({
      ...prev,
      [type === 'buy' ? 'buyConditions' : 'sellConditions']: 
        (prev[type === 'buy' ? 'buyConditions' : 'sellConditions'] || []).filter((_, i) => i !== index)
    }));
  }, []);

  // Update trading condition
  const updateCondition = useCallback((type: 'buy' | 'sell', index: number, field: keyof TradingCondition, value: any) => {
    setNewRule(prev => {
      const conditions = [...(prev[type === 'buy' ? 'buyConditions' : 'sellConditions'] || [])];
      conditions[index] = { ...conditions[index], [field]: value };
      
      return {
        ...prev,
        [type === 'buy' ? 'buyConditions' : 'sellConditions']: conditions
      };
    });
  }, []);

  return (
    <div className="smart-trading-automation">
      {/* Header */}
      <div className="automation-header">
        <div className="header-title">
          <h2>🤖 Smart Trading Automation Assistant</h2>
          <div className="automation-status">
            <span className={`status-badge ${automationStatus.isActive ? 'active' : 'inactive'}`}>
              {automationStatus.isActive ? '🟢 ACTIVE' : '🔴 INACTIVE'}
            </span>
            <span className="rules-count">
              {automationStatus.rulesActive} of {tradingRules.length} rules active
            </span>
          </div>
        </div>

        <div className="header-controls">
          <button
            className={`master-toggle ${automationStatus.isActive ? 'active' : ''}`}
            onClick={toggleAutomation}
            disabled={isLoading || tradingRules.length === 0}
          >
            {isLoading ? '⏳' : automationStatus.isActive ? '⏸️ Stop' : '▶️ Start'} Automation
          </button>

          <button
            className="new-rule-btn"
            onClick={() => setShowRuleBuilder(!showRuleBuilder)}
          >
            ➕ New Rule
          </button>
        </div>
      </div>

      {/* Error Display */}
      {errors.length > 0 && (
        <div className="error-banner">
          {errors.map((error, index) => (
            <div key={index} className="error-message">
              ❌ {error}
            </div>
          ))}
          <button onClick={() => setErrors([])} className="dismiss-btn">✕</button>
        </div>
      )}

      {/* Performance Dashboard */}
      <div className="performance-dashboard">
        <div className="performance-grid">
          <div className="metric-card profit">
            <div className="metric-label">Today's Profit</div>
            <div className={`metric-value ${automationStatus.totalProfitToday >= 0 ? 'positive' : 'negative'}`}>
              {automationStatus.totalProfitToday >= 0 ? '+' : ''}
              {automationStatus.totalProfitToday.toLocaleString()} credits
            </div>
          </div>

          <div className="metric-card trades">
            <div className="metric-label">Trades Executed</div>
            <div className="metric-value">{automationStatus.tradesExecuted}</div>
          </div>

          <div className="metric-card success">
            <div className="metric-label">Success Rate</div>
            <div className="metric-value">{performanceMetrics.successRate.toFixed(1)}%</div>
          </div>

          <div className="metric-card volume">
            <div className="metric-label">Total Volume</div>
            <div className="metric-value">{performanceMetrics.totalVolume.toLocaleString()}</div>
          </div>
        </div>

        {automationStatus.lastAction && (
          <div className="last-action">
            <div className="action-header">🤖 Last ARIA Action</div>
            <div className="action-details">
              <span className={`action-type ${automationStatus.lastAction.type}`}>
                {automationStatus.lastAction.type.toUpperCase()}
              </span>
              <span className="action-commodity">{automationStatus.lastAction.commodity}</span>
              <span className="action-amount">{automationStatus.lastAction.amount} units</span>
              <span className={`action-profit ${automationStatus.lastAction.profit >= 0 ? 'positive' : 'negative'}`}>
                {automationStatus.lastAction.profit >= 0 ? '+' : ''}{automationStatus.lastAction.profit} credits
              </span>
            </div>
            <div className="action-reasoning">{automationStatus.lastAction.reasoning}</div>
          </div>
        )}
      </div>

      {/* Rule Builder */}
      {showRuleBuilder && (
        <div className="rule-builder">
          <div className="builder-header">
            <h3>Create New Trading Rule</h3>
            <button
              className="close-builder"
              onClick={() => setShowRuleBuilder(false)}
            >
              ✕
            </button>
          </div>

          {/* Templates */}
          <div className="rule-templates">
            <h4>Quick Templates</h4>
            <div className="template-grid">
              {RULE_TEMPLATES.map((template, index) => (
                <div
                  key={index}
                  className={`template-card ${selectedTemplate === template ? 'selected' : ''}`}
                  onClick={() => applyTemplate(template)}
                >
                  <div className="template-name">{template.name}</div>
                  <div className="template-description">{template.description}</div>
                  <div className="template-meta">
                    <span className={`risk-level ${template.riskLevel}`}>
                      {template.riskLevel}
                    </span>
                    <span className="max-investment">
                      Max: {template.maxInvestment.toLocaleString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Rule Configuration */}
          <div className="rule-config">
            <div className="config-row">
              <label>
                Rule Name:
                <input
                  type="text"
                  value={newRule.name || ''}
                  onChange={(e) => setNewRule(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="Enter rule name"
                  maxLength={50}
                />
              </label>

              <label>
                Commodity:
                <select
                  value={newRule.commodity || 'organics'}
                  onChange={(e) => setNewRule(prev => ({ ...prev, commodity: e.target.value }))}
                >
                  {availableCommodities.map(commodity => (
                    <option key={commodity} value={commodity}>
                      {commodity.charAt(0).toUpperCase() + commodity.slice(1)}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <div className="config-row">
              <label>
                Risk Level:
                <select
                  value={newRule.riskLevel || 'moderate'}
                  onChange={(e) => setNewRule(prev => ({ 
                    ...prev, 
                    riskLevel: e.target.value as 'conservative' | 'moderate' | 'aggressive'
                  }))}
                >
                  <option value="conservative">Conservative</option>
                  <option value="moderate">Moderate</option>
                  <option value="aggressive">Aggressive</option>
                </select>
              </label>

              <label>
                Max Investment:
                <input
                  type="number"
                  value={newRule.maxInvestment || 10000}
                  onChange={(e) => setNewRule(prev => ({ 
                    ...prev, 
                    maxInvestment: Math.min(parseInt(e.target.value) || 0, SECURITY_LIMITS.maxInvestmentPerTrade)
                  }))}
                  min="1"
                  max={SECURITY_LIMITS.maxInvestmentPerTrade}
                />
              </label>
            </div>

            {/* Buy Conditions */}
            <div className="conditions-section">
              <div className="conditions-header">
                <h4>Buy Conditions</h4>
                <button
                  className="add-condition-btn"
                  onClick={() => addCondition('buy')}
                >
                  ➕ Add
                </button>
              </div>

              {(newRule.buyConditions || []).map((condition, index) => (
                <div key={index} className="condition-row">
                  <select
                    value={condition.type}
                    onChange={(e) => updateCondition('buy', index, 'type', e.target.value)}
                  >
                    <option value="price_below">Price Below</option>
                    <option value="price_above">Price Above</option>
                    <option value="margin_exceeds">Margin Exceeds</option>
                    <option value="ai_confidence">AI Confidence</option>
                  </select>

                  <input
                    type="number"
                    value={condition.value}
                    onChange={(e) => updateCondition('buy', index, 'value', parseFloat(e.target.value) || 0)}
                    step="0.01"
                  />

                  <select
                    value={condition.comparison}
                    onChange={(e) => updateCondition('buy', index, 'comparison', e.target.value)}
                  >
                    <option value="less_than">Less Than</option>
                    <option value="greater_than">Greater Than</option>
                    <option value="equals">Equals</option>
                  </select>

                  <button
                    className="remove-condition-btn"
                    onClick={() => removeCondition('buy', index)}
                  >
                    🗑️
                  </button>
                </div>
              ))}
            </div>

            {/* Sell Conditions */}
            <div className="conditions-section">
              <div className="conditions-header">
                <h4>Sell Conditions</h4>
                <button
                  className="add-condition-btn"
                  onClick={() => addCondition('sell')}
                >
                  ➕ Add
                </button>
              </div>

              {(newRule.sellConditions || []).map((condition, index) => (
                <div key={index} className="condition-row">
                  <select
                    value={condition.type}
                    onChange={(e) => updateCondition('sell', index, 'type', e.target.value)}
                  >
                    <option value="price_below">Price Below</option>
                    <option value="price_above">Price Above</option>
                    <option value="margin_exceeds">Margin Exceeds</option>
                    <option value="ai_confidence">AI Confidence</option>
                  </select>

                  <input
                    type="number"
                    value={condition.value}
                    onChange={(e) => updateCondition('sell', index, 'value', parseFloat(e.target.value) || 0)}
                    step="0.01"
                  />

                  <select
                    value={condition.comparison}
                    onChange={(e) => updateCondition('sell', index, 'comparison', e.target.value)}
                  >
                    <option value="less_than">Less Than</option>
                    <option value="greater_than">Greater Than</option>
                    <option value="equals">Equals</option>
                  </select>

                  <button
                    className="remove-condition-btn"
                    onClick={() => removeCondition('sell', index)}
                  >
                    🗑️
                  </button>
                </div>
              ))}
            </div>

            <button
              className="create-rule-btn"
              onClick={createTradingRule}
              disabled={isLoading || !newRule.name}
            >
              {isLoading ? '⏳ Creating...' : '✅ Create Rule'}
            </button>
          </div>
        </div>
      )}

      {/* Trading Rules List */}
      <div className="trading-rules">
        <h3>Trading Rules ({tradingRules.length}/{SECURITY_LIMITS.maxConcurrentRules})</h3>
        
        {tradingRules.length === 0 ? (
          <div className="no-rules">
            <p>No trading rules configured. Create your first rule to start automated trading.</p>
          </div>
        ) : (
          <div className="rules-grid">
            {tradingRules.map(rule => (
              <div key={rule.id} className={`rule-card ${rule.isActive ? 'active' : 'inactive'}`}>
                <div className="rule-header">
                  <div className="rule-name">{rule.name}</div>
                  <div className="rule-controls">
                    <button
                      className={`toggle-rule ${rule.isActive ? 'active' : 'inactive'}`}
                      onClick={() => toggleRule(rule.id)}
                    >
                      {rule.isActive ? '⏸️' : '▶️'}
                    </button>
                    <button
                      className="delete-rule"
                      onClick={() => deleteRule(rule.id)}
                    >
                      🗑️
                    </button>
                  </div>
                </div>

                <div className="rule-details">
                  <div className="rule-commodity">{rule.commodity}</div>
                  <div className={`rule-risk ${rule.riskLevel}`}>
                    {rule.riskLevel}
                  </div>
                  <div className="rule-investment">
                    Max: {rule.maxInvestment.toLocaleString()}
                  </div>
                </div>

                <div className="rule-conditions">
                  {rule.buyConditions.length > 0 && (
                    <div className="conditions-summary">
                      <span className="condition-type">Buy:</span>
                      <span className="condition-count">{rule.buyConditions.length} conditions</span>
                    </div>
                  )}
                  {rule.sellConditions.length > 0 && (
                    <div className="conditions-summary">
                      <span className="condition-type">Sell:</span>
                      <span className="condition-count">{rule.sellConditions.length} conditions</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Recent Trades */}
      {recentTrades.length > 0 && (
        <div className="recent-trades">
          <h3>Recent Automated Trades</h3>
          <div className="trades-list">
            {recentTrades.map((trade, index) => (
              <div key={index} className="trade-item">
                <div className="trade-meta">
                  <span className={`trade-type ${trade.type}`}>
                    {trade.type.toUpperCase()}
                  </span>
                  <span className="trade-commodity">{trade.commodity}</span>
                  <span className="trade-time">
                    {new Date(trade.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <div className="trade-details">
                  <span className="trade-amount">{trade.amount} units</span>
                  <span className={`trade-profit ${trade.profit >= 0 ? 'positive' : 'negative'}`}>
                    {trade.profit >= 0 ? '+' : ''}{trade.profit} credits
                  </span>
                </div>
                <div className="trade-reasoning">{trade.reasoning}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SmartTradingAutomation;