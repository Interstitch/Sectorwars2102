import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, MessageCircle, TrendingUp, Navigation, AlertTriangle, Settings, Star } from 'lucide-react';
import aiTradingService from '../../services/aiTradingService';
import { TradingRecommendation as TradingRecommendationType } from './types';
import './ai-assistant.css';

// Use the proper type from types.ts
type TradingRecommendation = TradingRecommendationType;

interface AIAssistantProps {
  isOpen: boolean;
  onClose: () => void;
  playerId: string;
}

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'recommendation' | 'system';
  content: string;
  timestamp: Date;
  data?: any;
}

const AIAssistant: React.FC<AIAssistantProps> = ({ isOpen, onClose, playerId }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [recommendations, setRecommendations] = useState<TradingRecommendation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      initializeAssistant();
    }
  }, [isOpen]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const initializeAssistant = async () => {
    setIsLoading(true);
    try {
      // Welcome message
      const welcomeMessage: ChatMessage = {
        id: Date.now().toString(),
        type: 'assistant',
        content: "Hello! I'm ARIA, your AI trading companion. I'm here to help you make smarter trading decisions with personalized recommendations and market analysis.",
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);

      // Load initial recommendations
      await loadRecommendations();
    } catch (error) {
      console.error('Error initializing AI assistant:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadRecommendations = async () => {
    try {
      const data = await aiTradingService.getRecommendations(5, false);
      setRecommendations(data);
      
      if (data.length > 0) {
        const recommendationMessage: ChatMessage = {
          id: Date.now().toString() + '_rec',
          type: 'recommendation',
          content: `I've found ${data.length} trading opportunities for you. Here are my top recommendations:`,
          timestamp: new Date(),
          data: data
        };
        setMessages(prev => [...prev, recommendationMessage]);
      }
    } catch (error) {
      console.error('Error loading recommendations:', error);
      // Add error message to chat
      const errorMessage: ChatMessage = {
        id: Date.now().toString() + '_error',
        type: 'system',
        content: 'Unable to load trading recommendations. AI services may be temporarily unavailable.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    // Simulate AI response (in real implementation, this would call the AI service)
    setTimeout(() => {
      const aiResponse = generateAIResponse(inputMessage);
      const assistantMessage: ChatMessage = {
        id: Date.now().toString() + '_ai',
        type: 'assistant',
        content: aiResponse,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMessage]);
      setIsTyping(false);
    }, 1500);
  };

  const generateAIResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();
    
    if (input.includes('market') || input.includes('price')) {
      return "Based on current market analysis, I'm seeing increased volatility in tech commodities. The sectors near Alpha Centauri are showing promising buy opportunities with 15-20% profit potential.";
    } else if (input.includes('route') || input.includes('travel')) {
      return "I've calculated an optimal 3-sector route that could yield approximately 2,500 credits profit. Would you like me to show you the detailed path and commodity recommendations?";
    } else if (input.includes('risk') || input.includes('safe')) {
      return "Your current risk tolerance is set to moderate. Based on recent piracy reports, I recommend avoiding the outer rim sectors for the next 6 hours. The core sectors remain relatively safe.";
    } else if (input.includes('help') || input.includes('what')) {
      return "I can help you with:\n• Market analysis and price predictions\n• Optimal trading route planning\n• Risk assessment and warnings\n• Commodity recommendations\n• Performance tracking\n\nJust ask me about any trading topic!";
    } else {
      return "I understand you're asking about trading strategies. Let me analyze the current market conditions and get back to you with personalized recommendations based on your trading history.";
    }
  };

  const handleRecommendationAction = async (recommendation: TradingRecommendation, action: 'accept' | 'decline') => {
    try {
      await aiTradingService.submitRecommendationFeedback(recommendation.id, {
        accepted: action === 'accept',
        feedback_score: action === 'accept' ? 5 : 3
      });

      const systemMessage: ChatMessage = {
        id: Date.now().toString(),
        type: 'system',
        content: `${action === 'accept' ? 'Accepted' : 'Declined'} recommendation: ${recommendation.reasoning}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, systemMessage]);
      
      // Remove the recommendation from the list
      setRecommendations(prev => prev.filter(r => r.id !== recommendation.id));
    } catch (error) {
      console.error('Error handling recommendation feedback:', error);
      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        type: 'system',
        content: 'Failed to submit feedback. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low': return '#10B981';
      case 'medium': return '#F59E0B';
      case 'high': return '#EF4444';
      default: return '#6B7280';
    }
  };

  const getRecommendationIcon = (type: string) => {
    switch (type) {
      case 'buy': return <TrendingUp className="w-4 h-4" />;
      case 'sell': return <TrendingUp className="w-4 h-4 rotate-180" />;
      case 'route': return <Navigation className="w-4 h-4" />;
      case 'avoid': return <AlertTriangle className="w-4 h-4" />;
      default: return <Star className="w-4 h-4" />;
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, x: 300 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 300 }}
          transition={{ duration: 0.3 }}
          className="ai-assistant-panel"
        >
          <div className="ai-assistant-header">
            <div className="ai-assistant-title">
              <MessageCircle className="w-5 h-5" />
              <span>ARIA - AI Trading Assistant</span>
              <div className="ai-status-indicator" />
            </div>
            <button 
              onClick={onClose}
              className="ai-assistant-close"
              aria-label="Close AI Assistant"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="ai-assistant-content">
            <div className="ai-messages-container">
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`ai-message ai-message-${message.type}`}
                >
                  {message.type === 'recommendation' && message.data ? (
                    <div className="ai-recommendations-group">
                      <div className="ai-message-content">{message.content}</div>
                      <div className="ai-recommendations-list">
                        {message.data.slice(0, 3).map((rec: TradingRecommendation) => (
                          <div key={rec.id} className="ai-recommendation-card">
                            <div className="ai-recommendation-header">
                              <div className="ai-recommendation-type">
                                {getRecommendationIcon(rec.type)}
                                <span>{rec.type.toUpperCase()}</span>
                              </div>
                              <div 
                                className="ai-recommendation-risk"
                                style={{ color: getRiskLevelColor(rec.risk_level) }}
                              >
                                {rec.risk_level.toUpperCase()}
                              </div>
                            </div>
                            
                            <div className="ai-recommendation-content">
                              <p>{rec.reasoning}</p>
                              {rec.expected_profit && (
                                <div className="ai-recommendation-profit">
                                  Expected Profit: <span className="profit-amount">+{rec.expected_profit.toLocaleString()} credits</span>
                                </div>
                              )}
                              <div className="ai-recommendation-confidence">
                                Confidence: <span className="confidence-score">{Math.round(rec.confidence * 100)}%</span>
                              </div>
                            </div>

                            <div className="ai-recommendation-actions">
                              <button 
                                onClick={() => handleRecommendationAction(rec, 'accept')}
                                className="ai-action-button ai-accept-button"
                              >
                                Accept
                              </button>
                              <button 
                                onClick={() => handleRecommendationAction(rec, 'decline')}
                                className="ai-action-button ai-decline-button"
                              >
                                Decline
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="ai-message-content">
                      {message.content}
                    </div>
                  )}
                  <div className="ai-message-timestamp">
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </motion.div>
              ))}
              
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="ai-message ai-message-assistant"
                >
                  <div className="ai-typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </motion.div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            <div className="ai-input-container">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Ask me about trading opportunities, market analysis, or routes..."
                className="ai-input-field"
                disabled={isTyping}
              />
              <button 
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isTyping}
                className="ai-send-button"
                aria-label="Send message"
              >
                <MessageCircle className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="ai-assistant-footer">
            <button className="ai-settings-button">
              <Settings className="w-4 h-4" />
              <span>AI Settings</span>
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default AIAssistant;