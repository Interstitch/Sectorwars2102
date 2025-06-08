/**
 * Foundation Sprint Test Helpers
 * Shared utilities for revolutionary trading system tests
 */

import { Page } from '@playwright/test';

export class AuthFixtures {
  private page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async loginAsPlayer(): Promise<void> {
    // Navigate to login page
    await this.page.goto('/login');
    
    // Fill in player credentials
    await this.page.fill('input[name="username"], input[type="email"]', 'test_player');
    await this.page.fill('input[name="password"], input[type="password"]', 'test_player123');
    
    // Submit login form
    await this.page.click('button[type="submit"], .login-btn');
    
    // Wait for successful login
    await this.page.waitForURL('**/dashboard', { timeout: 10000 });
  }

  async loginAsAdmin(): Promise<void> {
    // Navigate to admin login page
    await this.page.goto('/admin/login');
    
    // Fill in admin credentials
    await this.page.fill('input[name="username"], input[type="email"]', 'admin');
    await this.page.fill('input[name="password"], input[type="password"]', 'admin');
    
    // Submit login form
    await this.page.click('button[type="submit"], .login-btn');
    
    // Wait for successful login
    await this.page.waitForURL('**/admin/**', { timeout: 10000 });
  }

  async logout(): Promise<void> {
    try {
      await this.page.click('button:has-text("Logout"), .logout-btn');
      await this.page.waitForURL('**/login', { timeout: 5000 });
    } catch (e) {
      // Fallback: clear session storage and navigate to login
      await this.page.evaluate(() => {
        localStorage.clear();
        sessionStorage.clear();
      });
      await this.page.goto('/login');
    }
  }
}

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
  signature: string;
  session_id: string;
}

export class WebSocketTestHelper {
  private page: Page;
  private wsMessages: WebSocketMessage[] = [];

  constructor(page: Page) {
    this.page = page;
  }

  async setupWebSocketInterception(): Promise<void> {
    // Intercept WebSocket connections
    await this.page.addInitScript(() => {
      const originalWebSocket = window.WebSocket;
      window.WebSocket = class extends originalWebSocket {
        constructor(url: string | URL, protocols?: string | string[]) {
          super(url, protocols);
          
          // Store reference for testing
          (window as any).testWebSocket = this;
          
          // Intercept messages for validation
          this.addEventListener('message', (event) => {
            try {
              const message = JSON.parse(event.data);
              (window as any).receivedMessages = (window as any).receivedMessages || [];
              (window as any).receivedMessages.push(message);
            } catch (e) {
              console.warn('Failed to parse WebSocket message:', e);
            }
          });
        }
      };
    });
  }

  async waitForWebSocketConnection(timeout: number = 30000): Promise<void> {
    await this.page.waitForFunction(() => {
      return (window as any).testWebSocket && 
             (window as any).testWebSocket.readyState === WebSocket.OPEN;
    }, { timeout });
  }

  async sendTestMessage(message: any): Promise<void> {
    await this.page.evaluate((msg) => {
      const ws = (window as any).testWebSocket;
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(msg));
      }
    }, message);
  }

  async getReceivedMessages(): Promise<WebSocketMessage[]> {
    return await this.page.evaluate(() => {
      return (window as any).receivedMessages || [];
    });
  }

  async validateMessageSecurity(message: WebSocketMessage): Promise<boolean> {
    // OWASP A03: Input validation checks
    if (!message.type || !message.data || !message.timestamp || !message.signature) {
      return false;
    }

    // Validate message type
    const validTypes = ['market_update', 'universe_pulse', 'trading_signal', 'ai_alert'];
    if (!validTypes.includes(message.type)) {
      return false;
    }

    // Validate timestamp (not too old, not in future)
    const messageTime = new Date(message.timestamp).getTime();
    const now = Date.now();
    const fiveMinutes = 5 * 60 * 1000;
    
    return messageTime >= now - fiveMinutes && messageTime <= now + fiveMinutes;
  }
}

// Security test payloads
export const XSS_PAYLOADS = [
  '<script>alert("XSS")</script>',
  'javascript:alert("XSS")',
  '<img src=x onerror=alert("XSS")>',
  '<svg onload=alert("XSS")>',
  '"><script>alert("XSS")</script>',
  '<iframe src="javascript:alert(\'XSS\')"></iframe>'
];

export const SQL_INJECTION_PAYLOADS = [
  "'; DROP TABLE users; --",
  "' OR '1'='1",
  "' UNION SELECT * FROM admin_credentials --",
  "'; INSERT INTO admin_credentials VALUES ('hacker', 'password'); --",
  "' OR 1=1 --",
  "admin'--",
  "admin' /*",
  "' or 1=1#"
];

export const COMMAND_INJECTION_PAYLOADS = [
  "; ls -la",
  "| cat /etc/passwd",
  "&& whoami",
  "; rm -rf /",
  "| nc -l 4444",
  "`id`",
  "$(id)",
  "${IFS}cat${IFS}/etc/passwd"
];

export class SecurityTestHelper {
  private page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async testXSSProtection(inputSelector: string, payloads: string[] = XSS_PAYLOADS): Promise<boolean> {
    let allProtected = true;

    for (const payload of payloads) {
      await this.page.fill(inputSelector, payload);
      
      // Check if input was sanitized
      const actualValue = await this.page.inputValue(inputSelector);
      
      if (actualValue.includes('<script>') || 
          actualValue.includes('javascript:') || 
          actualValue.includes('onerror=') ||
          actualValue.includes('onload=')) {
        console.error(`XSS payload not sanitized: ${payload}`);
        allProtected = false;
      }
      
      // Clear input for next test
      await this.page.fill(inputSelector, '');
    }

    return allProtected;
  }

  async testInputValidation(inputSelector: string, invalidInputs: string[]): Promise<boolean> {
    let allValidated = true;

    for (const input of invalidInputs) {
      await this.page.fill(inputSelector, input);
      
      // Try to submit form
      const submitButton = this.page.locator('button[type="submit"], .execute-trade-btn, .create-rule-btn').first();
      await submitButton.click();
      
      // Check if validation error is shown or submission is prevented
      const hasError = await this.page.locator('.error-message, .validation-error, text=validation failed').isVisible();
      const isDisabled = await submitButton.isDisabled();
      
      if (!hasError && !isDisabled) {
        console.error(`Invalid input not caught: ${input}`);
        allValidated = false;
      }
      
      // Clear any error messages
      await this.page.locator('.dismiss-btn, .close').click().catch(() => {});
      await this.page.fill(inputSelector, '');
    }

    return allValidated;
  }

  async testRateLimiting(action: () => Promise<void>, maxAttempts: number = 100): Promise<boolean> {
    let successCount = 0;
    const startTime = Date.now();

    for (let i = 0; i < maxAttempts; i++) {
      try {
        await action();
        successCount++;
      } catch (e) {
        // Rate limit hit, which is expected
        break;
      }
      
      // Small delay to avoid overwhelming the system
      await this.page.waitForTimeout(10);
    }

    const duration = Date.now() - startTime;
    
    // If all attempts succeeded in under 1 second, rate limiting may not be working
    return !(successCount === maxAttempts && duration < 1000);
  }

  async testAuthenticationBypass(): Promise<boolean> {
    // Clear authentication
    await this.page.evaluate(() => {
      localStorage.removeItem('auth_token');
      sessionStorage.clear();
      document.cookie.split(";").forEach(c => {
        document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
      });
    });

    // Try to access protected resources
    const protectedRoutes = [
      '/api/v1/trading/automation/rules',
      '/api/v1/ai/recommendations',
      '/api/v1/market/predictions'
    ];

    let allProtected = true;

    for (const route of protectedRoutes) {
      const response = await this.page.goto(route);
      
      if (response && response.status() === 200) {
        console.error(`Protected route accessible without auth: ${route}`);
        allProtected = false;
      }
    }

    return allProtected;
  }

  async testSessionSecurity(): Promise<boolean> {
    // Check if session cookies are secure
    const cookies = await this.page.context().cookies();
    
    let allSecure = true;
    for (const cookie of cookies) {
      if (cookie.name.includes('session') || cookie.name.includes('auth')) {
        if (!cookie.secure || !cookie.httpOnly) {
          console.error(`Insecure session cookie: ${cookie.name}`);
          allSecure = false;
        }
      }
    }

    return allSecure;
  }
}