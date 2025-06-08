/**
 * Foundation Sprint - WebSocket Real-Time System E2E Tests
 * Revolutionary Trading Interface with OWASP Security Validation
 * Tests: Market Intelligence Dashboard + Smart Trading Automation + WebSocket Foundation
 */

import { test, expect, Page } from '@playwright/test';
import { AuthFixtures, WebSocketTestHelper, WebSocketMessage } from './test-helpers';

// Test configuration for WebSocket testing
const WEBSOCKET_TIMEOUT = 30000;
const MARKET_DATA_TIMEOUT = 5000;
const SECURITY_VALIDATION_TIMEOUT = 10000;

interface MarketTestData {
  commodity: string;
  initialPrice: number;
  targetPrice: number;
  volatility: number;
}

test.describe('Foundation Sprint - WebSocket Real-Time System', () => {
  let authFixtures: AuthFixtures;
  let wsHelper: WebSocketTestHelper;

  test.beforeEach(async ({ page }) => {
    authFixtures = new AuthFixtures(page);
    wsHelper = new WebSocketTestHelper(page);
    
    // Setup WebSocket interception
    await wsHelper.setupWebSocketInterception();
    
    // Login as player
    await authFixtures.loginAsPlayer();
    
    // Navigate to game dashboard
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
  });

  test.describe('WebSocket Foundation Layer', () => {
    test('should establish secure WebSocket connection with authentication', async ({ page }) => {
      // Wait for WebSocket connection
      await wsHelper.waitForWebSocketConnection();
      
      // Verify connection status in UI
      const connectionStatus = page.locator('.connection-status .status-indicator');
      await expect(connectionStatus).toHaveClass(/connected/);
      await expect(connectionStatus).toContainText('Live');
      
      // Verify authentication succeeded
      const messages = await wsHelper.getReceivedMessages();
      const authMessage = messages.find(msg => 
        msg.type === 'ai_alert' && msg.data.action === 'auth_success'
      );
      expect(authMessage).toBeTruthy();
    });

    test('should handle WebSocket reconnection gracefully', async ({ page }) => {
      // Initial connection
      await wsHelper.waitForWebSocketConnection();
      
      // Simulate connection loss
      await page.evaluate(() => {
        const ws = (window as any).testWebSocket;
        if (ws) {
          ws.close();
        }
      });
      
      // Wait for reconnection attempt
      await page.waitForTimeout(2000);
      
      // Verify reconnection
      await wsHelper.waitForWebSocketConnection();
      
      // Check UI status
      const connectionStatus = page.locator('.connection-status .status-indicator');
      await expect(connectionStatus).toHaveClass(/connected/);
    });

    test('should validate message security and integrity', async ({ page }) => {
      await wsHelper.waitForWebSocketConnection();
      
      // Send test message with invalid structure
      const invalidMessage = {
        type: 'invalid_type',
        data: null,
        timestamp: 'invalid_timestamp'
      };
      
      await wsHelper.sendTestMessage(invalidMessage);
      await page.waitForTimeout(1000);
      
      // Verify invalid message was rejected
      const messages = await wsHelper.getReceivedMessages();
      const processedInvalidMessage = messages.find(msg => msg.type === 'invalid_type');
      expect(processedInvalidMessage).toBeUndefined();
    });

    test('should implement rate limiting protection', async ({ page }) => {
      await wsHelper.waitForWebSocketConnection();
      
      // Send rapid messages to trigger rate limiting
      const testMessage = {
        type: 'market_update',
        data: { test: true },
        timestamp: new Date().toISOString(),
        signature: 'test_signature',
        session_id: 'test_session'
      };
      
      // Send 150 messages rapidly (exceeds 100/second limit)
      for (let i = 0; i < 150; i++) {
        await wsHelper.sendTestMessage(testMessage);
      }
      
      await page.waitForTimeout(2000);
      
      // Check if rate limiting was applied (some messages should be dropped)
      const messages = await wsHelper.getReceivedMessages();
      const testMessages = messages.filter(msg => msg.data?.test === true);
      expect(testMessages.length).toBeLessThan(150);
    });
  });

  test.describe('Market Intelligence Dashboard', () => {
    test('should display real-time market data with AI predictions', async ({ page }) => {
      // Navigate to market dashboard
      await page.click('button:has-text("📈 Market")');
      await page.waitForSelector('.market-intelligence-dashboard');
      
      // Wait for WebSocket connection
      await wsHelper.waitForWebSocketConnection();
      
      // Verify commodity selector is present
      const commoditySelector = page.locator('.commodity-selector');
      await expect(commoditySelector).toBeVisible();
      
      // Select a commodity
      await page.click('.commodity-btn:has-text("Organics")');
      
      // Verify price information displays
      const currentPrice = page.locator('.current-price .price-value');
      await expect(currentPrice).toBeVisible();
      
      // Verify chart is rendered
      const marketChart = page.locator('.market-chart');
      await expect(marketChart).toBeVisible();
      
      // Request AI analysis
      await page.click('button:has-text("Get ARIA Analysis")');
      
      // Wait for AI analysis to load
      await page.waitForSelector('.aria-analysis', { timeout: 10000 });
      
      // Verify AI recommendation is displayed
      const recommendation = page.locator('.recommendation-badge');
      await expect(recommendation).toBeVisible();
      
      // Verify confidence score is shown
      const confidence = page.locator('.confidence-badge');
      await expect(confidence).toBeVisible();
      await expect(confidence).toContainText('%');
    });

    test('should execute secure trading commands with validation', async ({ page }) => {
      await page.click('button:has-text("📈 Market")');
      await page.waitForSelector('.market-intelligence-dashboard');
      
      // Fill trading form
      await page.selectOption('select', 'buy');
      await page.fill('input[placeholder="Enter amount"]', '1000');
      
      // Enable advanced controls
      await page.click('button:has-text("Advanced")');
      await page.fill('input[placeholder="Optional"]:first', '10.50'); // Max price
      
      // Execute trade
      await page.click('button:has-text("Execute Trade")');
      
      // Verify success notification
      await expect(page.locator('text=Trading command submitted successfully')).toBeVisible();
      
      // Verify form was cleared
      const amountInput = page.locator('input[placeholder="Enter amount"]');
      await expect(amountInput).toHaveValue('');
    });

    test('should prevent invalid trading inputs', async ({ page }) => {
      await page.click('button:has-text("📈 Market")');
      await page.waitForSelector('.market-intelligence-dashboard');
      
      // Try invalid amount (too large)
      await page.fill('input[placeholder="Enter amount"]', '10000000');
      await page.click('button:has-text("Execute Trade")');
      
      // Verify validation error
      await expect(page.locator('text=validation failed')).toBeVisible();
      
      // Try invalid characters in amount
      await page.fill('input[placeholder="Enter amount"]', 'invalid<script>');
      await page.click('button:has-text("Execute Trade")');
      
      // Verify input sanitization
      const amountValue = await page.inputValue('input[placeholder="Enter amount"]');
      expect(amountValue).not.toContain('<script>');
    });

    test('should update market data in real-time', async ({ page }) => {
      await page.click('button:has-text("📈 Market")');
      await page.waitForSelector('.market-intelligence-dashboard');
      await wsHelper.waitForWebSocketConnection();
      
      // Get initial price
      const initialPrice = await page.textContent('.current-price .price-value');
      
      // Simulate market update via WebSocket
      const marketUpdate = {
        type: 'market_update',
        data: {
          commodity: 'organics',
          price: 15.75,
          volume: 1000,
          predicted_price: 16.25,
          confidence: 0.85
        },
        timestamp: new Date().toISOString(),
        signature: 'test_signature',
        session_id: 'test_session'
      };
      
      await wsHelper.sendTestMessage(marketUpdate);
      
      // Wait for UI update
      await page.waitForTimeout(1000);
      
      // Verify price updated
      const updatedPrice = await page.textContent('.current-price .price-value');
      expect(updatedPrice).not.toBe(initialPrice);
      expect(updatedPrice).toContain('15.75');
      
      // Verify prediction is shown
      const predictionPrice = page.locator('.prediction-value');
      await expect(predictionPrice).toContainText('16.25');
    });
  });

  test.describe('Smart Trading Automation', () => {
    test('should create and manage trading rules securely', async ({ page }) => {
      // Navigate to automation
      await page.click('button:has-text("🤖 Automation")');
      await page.waitForSelector('.smart-trading-automation');
      
      // Create new rule
      await page.click('button:has-text("New Rule")');
      await page.waitForSelector('.rule-builder');
      
      // Select template
      await page.click('.template-card:first-child');
      
      // Fill rule details
      await page.fill('input[placeholder="Enter rule name"]', 'Test Automation Rule');
      await page.selectOption('select', 'organics');
      
      // Add buy condition
      await page.click('button:has-text("Add"):first');
      
      // Configure condition
      await page.selectOption('.condition-row select:first', 'price_below');
      await page.fill('.condition-row input[type="number"]', '10.00');
      
      // Create rule
      await page.click('button:has-text("Create Rule")');
      
      // Verify rule was created
      await page.waitForSelector('.rule-card');
      const ruleCard = page.locator('.rule-card').first();
      await expect(ruleCard).toContainText('Test Automation Rule');
    });

    test('should enforce security limits on trading rules', async ({ page }) => {
      await page.click('button:has-text("🤖 Automation")');
      await page.waitForSelector('.smart-trading-automation');
      
      await page.click('button:has-text("New Rule")');
      
      // Try to set investment above limit
      await page.fill('input[placeholder="Enter rule name"]', 'Invalid Rule');
      const maxInvestmentInput = page.locator('input[type="number"]').last();
      await maxInvestmentInput.fill('10000000'); // Above security limit
      
      // Verify input was capped at security limit
      const actualValue = await maxInvestmentInput.inputValue();
      expect(parseInt(actualValue)).toBeLessThanOrEqual(100000);
    });

    test('should toggle automation with proper state management', async ({ page }) => {
      await page.click('button:has-text("🤖 Automation")');
      await page.waitForSelector('.smart-trading-automation');
      
      // Initially automation should be inactive
      const statusBadge = page.locator('.status-badge');
      await expect(statusBadge).toHaveClass(/inactive/);
      
      // Create a rule first (automation requires rules)
      await page.click('button:has-text("New Rule")');
      await page.click('.template-card:first-child');
      await page.fill('input[placeholder="Enter rule name"]', 'Test Rule');
      await page.click('button:has-text("Create Rule")');
      
      // Activate the rule
      await page.click('.toggle-rule');
      
      // Toggle automation
      await page.click('.master-toggle');
      
      // Verify automation is active
      await expect(statusBadge).toHaveClass(/active/);
      await expect(page.locator('.master-toggle')).toHaveClass(/active/);
    });

    test('should display performance metrics and recent trades', async ({ page }) => {
      await page.click('button:has-text("🤖 Automation")');
      await page.waitForSelector('.smart-trading-automation');
      
      // Verify performance dashboard is visible
      const performanceDashboard = page.locator('.performance-dashboard');
      await expect(performanceDashboard).toBeVisible();
      
      // Check metric cards
      const metricCards = page.locator('.metric-card');
      await expect(metricCards).toHaveCount(4);
      
      // Verify metric labels
      await expect(page.locator('.metric-card .metric-label')).toContainText([
        'Today\'s Profit',
        'Trades Executed',
        'Success Rate',
        'Total Volume'
      ]);
      
      // Simulate trade execution update
      const tradeUpdate = {
        type: 'trading_signal',
        data: {
          type: 'trade_executed',
          trade: {
            type: 'buy',
            commodity: 'organics',
            amount: 100,
            profit: 50,
            timestamp: new Date().toISOString(),
            reasoning: 'AI detected favorable market conditions'
          }
        },
        timestamp: new Date().toISOString(),
        signature: 'test_signature',
        session_id: 'test_session'
      };
      
      await wsHelper.waitForWebSocketConnection();
      await wsHelper.sendTestMessage(tradeUpdate);
      
      // Wait for UI update
      await page.waitForTimeout(1000);
      
      // Verify recent trade appears
      const recentTrades = page.locator('.recent-trades');
      if (await recentTrades.isVisible()) {
        await expect(recentTrades).toContainText('organics');
        await expect(recentTrades).toContainText('+50 credits');
      }
    });
  });

  test.describe('OWASP Security Validation', () => {
    test('should prevent XSS attacks in user inputs', async ({ page }) => {
      await page.click('button:has-text("🤖 Automation")');
      await page.click('button:has-text("New Rule")');
      
      // Try XSS payload in rule name
      const xssPayload = '<script>alert("XSS")</script>';
      await page.fill('input[placeholder="Enter rule name"]', xssPayload);
      
      // Verify input was sanitized
      const sanitizedValue = await page.inputValue('input[placeholder="Enter rule name"]');
      expect(sanitizedValue).not.toContain('<script>');
      expect(sanitizedValue).not.toContain('alert');
    });

    test('should validate authentication tokens for WebSocket', async ({ page }) => {
      // Clear authentication
      await page.evaluate(() => {
        localStorage.removeItem('auth_token');
      });
      
      // Try to access trading features without auth
      await page.goto('/dashboard');
      await page.click('button:has-text("📈 Market")');
      
      // Should redirect to login or show auth error
      await expect(page.locator('text=Authentication')).toBeVisible({ timeout: 5000 });
    });

    test('should implement proper input validation for trading amounts', async ({ page }) => {
      await page.click('button:has-text("📈 Market")');
      await page.waitForSelector('.market-intelligence-dashboard');
      
      // Test various invalid inputs
      const invalidInputs = [
        '-1000',        // Negative amount
        '0',            // Zero amount
        'NaN',          // Not a number
        '1e10',         // Scientific notation (too large)
        '1000.123456'   // Too many decimal places
      ];
      
      for (const input of invalidInputs) {
        await page.fill('input[placeholder="Enter amount"]', input);
        await page.click('button:has-text("Execute Trade")');
        
        // Should show validation error or prevent submission
        const submitButton = page.locator('button:has-text("Execute Trade")');
        expect(await submitButton.isDisabled() || 
               await page.locator('text=validation failed').isVisible()).toBeTruthy();
      }
    });

    test('should protect against SQL injection in market data queries', async ({ page }) => {
      await page.click('button:has-text("📈 Market")');
      await wsHelper.waitForWebSocketConnection();
      
      // Try SQL injection payload via WebSocket
      const sqlInjectionPayload = {
        type: 'market_update',
        data: {
          commodity: "organics'; DROP TABLE markets; --",
          price: 10.50
        },
        timestamp: new Date().toISOString(),
        signature: 'test_signature',
        session_id: 'test_session'
      };
      
      await wsHelper.sendTestMessage(sqlInjectionPayload);
      await page.waitForTimeout(1000);
      
      // Message should be rejected or sanitized
      const messages = await wsHelper.getReceivedMessages();
      const maliciousMessage = messages.find(msg => 
        msg.data?.commodity?.includes('DROP TABLE')
      );
      expect(maliciousMessage).toBeUndefined();
    });
  });

  test.describe('Performance and Load Testing', () => {
    test('should handle high-frequency market updates smoothly', async ({ page }) => {
      await page.click('button:has-text("📈 Market")');
      await page.waitForSelector('.market-intelligence-dashboard');
      await wsHelper.waitForWebSocketConnection();
      
      // Send rapid market updates
      const startTime = Date.now();
      for (let i = 0; i < 50; i++) {
        const marketUpdate = {
          type: 'market_update',
          data: {
            commodity: 'organics',
            price: 10.00 + (Math.random() * 2),
            volume: Math.floor(Math.random() * 1000),
            timestamp: new Date().toISOString()
          },
          timestamp: new Date().toISOString(),
          signature: 'test_signature',
          session_id: 'test_session'
        };
        
        await wsHelper.sendTestMessage(marketUpdate);
        await page.waitForTimeout(20); // 50 updates per second
      }
      
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      // Should complete within reasonable time (< 5 seconds)
      expect(duration).toBeLessThan(5000);
      
      // UI should still be responsive
      const refreshButton = page.locator('button:has-text("Get ARIA Analysis")');
      await expect(refreshButton).toBeEnabled();
    });

    test('should maintain UI responsiveness during automation', async ({ page }) => {
      await page.click('button:has-text("🤖 Automation")');
      await page.waitForSelector('.smart-trading-automation');
      
      // Create and activate multiple rules
      for (let i = 0; i < 5; i++) {
        await page.click('button:has-text("New Rule")');
        await page.click('.template-card:first-child');
        await page.fill('input[placeholder="Enter rule name"]', `Rule ${i + 1}`);
        await page.click('button:has-text("Create Rule")');
        await page.click('.toggle-rule');
      }
      
      // Activate automation
      await page.click('.master-toggle');
      
      // Simulate rapid trading signals
      await wsHelper.waitForWebSocketConnection();
      for (let i = 0; i < 20; i++) {
        const tradingSignal = {
          type: 'trading_signal',
          data: {
            type: 'automation_update',
            status: {
              isActive: true,
              totalProfitToday: Math.random() * 1000,
              tradesExecuted: i + 1,
              rulesActive: 5
            }
          },
          timestamp: new Date().toISOString(),
          signature: 'test_signature',
          session_id: 'test_session'
        };
        
        await wsHelper.sendTestMessage(tradingSignal);
        await page.waitForTimeout(50);
      }
      
      // UI should remain responsive
      const newRuleButton = page.locator('button:has-text("New Rule")');
      await expect(newRuleButton).toBeEnabled();
      
      // Performance metrics should update
      const metricValues = page.locator('.metric-value');
      await expect(metricValues.first()).not.toHaveText('0');
    });
  });
});

test.describe('Cross-Component Integration', () => {
  test('should integrate Market Dashboard with Trading Automation', async ({ page }) => {
    const authFixtures = new AuthFixtures(page);
    const wsHelper = new WebSocketTestHelper(page);
    
    await wsHelper.setupWebSocketInterception();
    await authFixtures.loginAsPlayer();
    await page.goto('/dashboard');
    
    // Start in Market Dashboard
    await page.click('button:has-text("📈 Market")');
    await page.waitForSelector('.market-intelligence-dashboard');
    
    // Get AI recommendation
    await page.click('button:has-text("Get ARIA Analysis")');
    await page.waitForSelector('.aria-analysis');
    
    // Switch to Automation
    await page.click('button:has-text("🤖 Automation")');
    await page.waitForSelector('.smart-trading-automation');
    
    // Create rule based on current market analysis
    await page.click('button:has-text("New Rule")');
    await page.fill('input[placeholder="Enter rule name"]', 'Market Intelligence Rule');
    
    // AI recommendations should be reflected in rule creation
    await page.selectOption('select', 'organics'); // Based on previous analysis
    await page.click('button:has-text("Create Rule")');
    
    // Verify integration worked
    const ruleCard = page.locator('.rule-card').first();
    await expect(ruleCard).toContainText('Market Intelligence Rule');
    await expect(ruleCard).toContainText('organics');
  });

  test('should maintain real-time sync across all components', async ({ page }) => {
    const authFixtures = new AuthFixtures(page);
    const wsHelper = new WebSocketTestHelper(page);
    
    await wsHelper.setupWebSocketInterception();
    await authFixtures.loginAsPlayer();
    await page.goto('/dashboard');
    await wsHelper.waitForWebSocketConnection();
    
    // Open both Market Dashboard and Automation in different tabs/windows
    const marketPage = page;
    await marketPage.click('button:has-text("📈 Market")');
    
    // Simulate market event that affects both components
    const marketEvent = {
      type: 'market_update',
      data: {
        commodity: 'organics',
        price: 20.00,
        volume: 5000,
        significant_change: true
      },
      timestamp: new Date().toISOString(),
      signature: 'test_signature',
      session_id: 'test_session'
    };
    
    await wsHelper.sendTestMessage(marketEvent);
    await page.waitForTimeout(1000);
    
    // Verify market dashboard updated
    await expect(page.locator('.current-price .price-value')).toContainText('20.00');
    
    // Switch to automation and verify it also updated
    await page.click('button:has-text("🤖 Automation")');
    
    // If automation has active rules for organics, it should show activity
    const lastUpdate = page.locator('.last-update');
    if (await lastUpdate.isVisible()) {
      const updateTime = await lastUpdate.textContent();
      const now = new Date();
      const timeDiff = now.getTime() - new Date(updateTime!).getTime();
      expect(timeDiff).toBeLessThan(5000); // Updated within last 5 seconds
    }
  });
});