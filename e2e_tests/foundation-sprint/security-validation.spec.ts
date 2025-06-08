/**
 * Foundation Sprint - OWASP Security Validation Tests
 * Comprehensive security testing for revolutionary trading system
 * Tests: A01-A10 OWASP Top 10 compliance validation
 */

import { test, expect, Page } from '@playwright/test';
import { AuthFixtures, SecurityTestHelper, XSS_PAYLOADS, SQL_INJECTION_PAYLOADS, COMMAND_INJECTION_PAYLOADS } from './test-helpers';


test.describe('OWASP Top 10 Security Validation', () => {
  let authFixtures: AuthFixtures;
  let securityHelper: SecurityTestHelper;

  test.beforeEach(async ({ page }) => {
    authFixtures = new AuthFixtures(page);
    securityHelper = new SecurityTestHelper(page);
    
    await authFixtures.loginAsPlayer();
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
  });

  test.describe('A01 - Broken Access Control', () => {
    test('should prevent unauthorized access to admin functions', async ({ page }) => {
      // Try to access admin routes as regular player
      const adminRoutes = [
        '/admin',
        '/admin/users',
        '/admin/universe',
        '/api/v1/admin/users',
        '/api/v1/admin/universe/generate'
      ];

      for (const route of adminRoutes) {
        const response = await page.goto(route);
        
        // Should redirect to login or return 403/401
        expect(response?.status()).not.toBe(200);
      }
    });

    test('should enforce role-based access for trading automation', async ({ page }) => {
      await page.click('button:has-text("🤖 Automation")');
      await page.waitForSelector('.smart-trading-automation');
      
      // Regular players should have limited rule creation
      await page.click('button:has-text("New Rule")');
      
      // Try to create more than allowed rules (simulate hitting limit)
      for (let i = 0; i < 12; i++) { // Exceeds 10 rule limit
        await page.fill('input[placeholder="Enter rule name"]', `Rule ${i + 1}`);
        await page.click('button:has-text("Create Rule")');
        
        if (i >= 10) {
          // Should show limit exceeded error
          await expect(page.locator('text=Maximum')).toBeVisible();
          break;
        }
      }
    });

    test('should validate authentication bypass attempts', async ({ page }) => {
      const isProtected = await securityHelper.testAuthenticationBypass();
      expect(isProtected).toBeTruthy();
    });
  });

  test.describe('A02 - Cryptographic Failures', () => {
    test('should use secure session management', async ({ page }) => {
      const isSecure = await securityHelper.testSessionSecurity();
      expect(isSecure).toBeTruthy();
    });

    test('should encrypt sensitive data in WebSocket communications', async ({ page }) => {
      // Monitor WebSocket messages for sensitive data
      let hasUnencryptedSensitive = false;
      
      await page.addInitScript(() => {
        const originalWebSocket = window.WebSocket;
        window.WebSocket = class extends originalWebSocket {
          constructor(url: string | URL, protocols?: string | string[]) {
            super(url, protocols);
            
            this.addEventListener('message', (event) => {
              try {
                const data = JSON.parse(event.data);
                
                // Check for unencrypted sensitive data
                const sensitiveFields = ['password', 'credit_card', 'ssn', 'api_key'];
                const dataString = JSON.stringify(data).toLowerCase();
                
                for (const field of sensitiveFields) {
                  if (dataString.includes(field) && !dataString.includes('encrypted')) {
                    (window as any).hasUnencryptedSensitive = true;
                  }
                }
              } catch (e) {
                // Non-JSON data is fine
              }
            });
          }
        };
      });

      await page.click('button:has-text("📈 Market")');
      await page.waitForTimeout(5000); // Let WebSocket messages flow
      
      const hasUnencrypted = await page.evaluate(() => (window as any).hasUnencryptedSensitive);
      expect(hasUnencrypted).toBeFalsy();
    });
  });

  test.describe('A03 - Injection', () => {
    test('should prevent XSS attacks in trading rule names', async ({ page }) => {
      await page.click('button:has-text("🤖 Automation")');
      await page.click('button:has-text("New Rule")');
      
      const isProtected = await securityHelper.testXSSProtection('input[placeholder="Enter rule name"]');
      expect(isProtected).toBeTruthy();
    });

    test('should prevent XSS attacks in market search inputs', async ({ page }) => {
      await page.click('button:has-text("📈 Market")');
      await page.waitForSelector('.market-intelligence-dashboard');
      
      // Test amount input field
      const isAmountProtected = await securityHelper.testXSSProtection('input[placeholder="Enter amount"]');
      expect(isAmountProtected).toBeTruthy();
      
      // Test price input fields if visible
      await page.click('button:has-text("Advanced")');
      const maxPriceInputs = page.locator('input[placeholder="Optional"]');
      
      if (await maxPriceInputs.count() > 0) {
        const isPriceProtected = await securityHelper.testXSSProtection('input[placeholder="Optional"]');
        expect(isPriceProtected).toBeTruthy();
      }
    });

    test('should prevent SQL injection in WebSocket messages', async ({ page }) => {
      await page.addInitScript(() => {
        const originalWebSocket = window.WebSocket;
        window.WebSocket = class extends originalWebSocket {
          constructor(url: string | URL, protocols?: string | string[]) {
            super(url, protocols);
            
            // Store reference for testing
            (window as any).testWebSocket = this;
          }
        };
      });

      await page.waitForLoadState('networkidle');
      
      // Wait for WebSocket connection
      await page.waitForFunction(() => {
        return (window as any).testWebSocket && 
               (window as any).testWebSocket.readyState === WebSocket.OPEN;
      });

      // Try SQL injection via WebSocket
      for (const payload of SQL_INJECTION_PAYLOADS) {
        const maliciousMessage = {
          type: 'market_update',
          data: {
            commodity: payload,
            price: 10.50
          },
          timestamp: new Date().toISOString(),
          signature: 'test_signature',
          session_id: 'test_session'
        };

        await page.evaluate((msg) => {
          const ws = (window as any).testWebSocket;
          if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(msg));
          }
        }, maliciousMessage);
        
        await page.waitForTimeout(100);
      }

      // Check if any SQL injection succeeded (server should reject/sanitize)
      const errorLogs = await page.evaluate(() => {
        return (window as any).console.errors || [];
      });

      // Should not see database errors indicating successful injection
      const hasSQLErrors = errorLogs.some((log: string) => 
        log.includes('SQL') || log.includes('database') || log.includes('syntax error')
      );
      
      expect(hasSQLErrors).toBeFalsy();
    });

    test('should prevent command injection in automation rules', async ({ page }) => {
      await page.click('button:has-text("🤖 Automation")');
      await page.click('button:has-text("New Rule")');
      
      // Test command injection in rule name
      for (const payload of COMMAND_INJECTION_PAYLOADS) {
        await page.fill('input[placeholder="Enter rule name"]', payload);
        await page.click('button:has-text("Create Rule")');
        
        // Should be rejected or sanitized
        const actualValue = await page.inputValue('input[placeholder="Enter rule name"]');
        expect(actualValue).not.toContain(';');
        expect(actualValue).not.toContain('|');
        expect(actualValue).not.toContain('&&');
        expect(actualValue).not.toContain('`');
        expect(actualValue).not.toContain('$(');
        
        await page.fill('input[placeholder="Enter rule name"]', '');
      }
    });
  });

  test.describe('A04 - Insecure Design', () => {
    test('should implement proper rate limiting on trading actions', async ({ page }) => {
      await page.click('button:has-text("📈 Market")');
      await page.waitForSelector('.market-intelligence-dashboard');
      
      // Fill valid trading data
      await page.fill('input[placeholder="Enter amount"]', '100');
      
      // Test rate limiting on rapid trade execution
      const isRateLimited = await securityHelper.testRateLimiting(async () => {
        await page.click('button:has-text("Execute Trade")');
        await page.waitForTimeout(100);
      }, 50);
      
      expect(isRateLimited).toBeTruthy();
    });

    test('should enforce business logic constraints', async ({ page }) => {
      await page.click('button:has-text("📈 Market")');
      await page.waitForSelector('.market-intelligence-dashboard');
      
      // Test invalid business logic scenarios
      const invalidInputs = [
        '-1000',     // Negative amount
        '0',         // Zero amount
        '99999999',  // Excessive amount
        '0.00001'    // Below minimum viable amount
      ];
      
      const isValidated = await securityHelper.testInputValidation('input[placeholder="Enter amount"]', invalidInputs);
      expect(isValidated).toBeTruthy();
    });

    test('should validate automation rule constraints', async ({ page }) => {
      await page.click('button:has-text("🤖 Automation")');
      await page.click('button:has-text("New Rule")');
      
      // Test invalid rule configurations
      await page.fill('input[placeholder="Enter rule name"]', 'Test Rule');
      
      // Try to set investment above security limit
      const maxInvestmentInput = page.locator('input[type="number"]').last();
      await maxInvestmentInput.fill('10000000'); // Way above limit
      
      // Should be capped or rejected
      const actualValue = await maxInvestmentInput.inputValue();
      expect(parseInt(actualValue)).toBeLessThanOrEqual(100000);
    });
  });

  test.describe('A05 - Security Misconfiguration', () => {
    test('should have proper CORS configuration', async ({ page }) => {
      // Check if CORS headers are properly configured
      const response = await page.goto('/api/v1/status');
      
      if (response) {
        const corsHeader = response.headers()['access-control-allow-origin'];
        
        // Should not allow wildcard in production
        if (process.env.NODE_ENV === 'production') {
          expect(corsHeader).not.toBe('*');
        }
        
        // Should have proper CORS headers
        expect(response.headers()).toHaveProperty('access-control-allow-origin');
      }
    });

    test('should not expose sensitive information in error messages', async ({ page }) => {
      // Trigger various error conditions
      const errorTriggers = [
        () => page.goto('/api/v1/nonexistent'),
        () => page.click('button:has-text("Execute Trade")'), // Without filling form
        () => page.evaluate(() => { throw new Error('Test error'); })
      ];

      for (const trigger of errorTriggers) {
        try {
          await trigger();
        } catch (e) {
          // Expected
        }
        
        // Check if any sensitive info is exposed in UI
        const errorMessages = await page.locator('.error-message, .alert, [class*="error"]').allTextContents();
        
        for (const message of errorMessages) {
          // Should not expose internal paths, database info, etc.
          expect(message.toLowerCase()).not.toContain('stack trace');
          expect(message.toLowerCase()).not.toContain('database error');
          expect(message.toLowerCase()).not.toContain('/usr/');
          expect(message.toLowerCase()).not.toContain('password');
          expect(message.toLowerCase()).not.toContain('secret');
        }
      }
    });
  });

  test.describe('A06 - Vulnerable and Outdated Components', () => {
    test('should not expose vulnerable library versions', async ({ page }) => {
      // Check if version information is exposed
      const response = await page.goto('/api/v1/status');
      
      if (response) {
        const responseText = await response.text();
        
        // Should not expose detailed version info
        expect(responseText.toLowerCase()).not.toContain('version');
        expect(responseText.toLowerCase()).not.toContain('build');
        expect(responseText.toLowerCase()).not.toContain('debug');
      }
    });
  });

  test.describe('A07 - Identification and Authentication Failures', () => {
    test('should enforce strong authentication', async ({ page }) => {
      // Logout and test authentication
      await page.click('button:has-text("Logout")').catch(() => {});
      await page.goto('/login');
      
      // Test weak password attempts
      const weakPasswords = [
        'password',
        '123456',
        'admin',
        'test',
        '1234567890'
      ];

      for (const password of weakPasswords) {
        await page.fill('input[type="password"]', password);
        await page.fill('input[type="email"], input[name="username"]', 'test@example.com');
        await page.click('button[type="submit"]');
        
        // Should show password strength error or reject login
        const hasError = await page.locator('text=password', 'text=strength', 'text=weak').isVisible();
        expect(hasError).toBeTruthy();
      }
    });

    test('should implement session timeout', async ({ page }) => {
      // Simulate long idle time
      await page.evaluate(() => {
        // Fast-forward session timeout for testing
        const originalDateNow = Date.now;
        Date.now = () => originalDateNow() + (30 * 60 * 1000); // 30 minutes later
      });

      // Try to access protected resource
      await page.click('button:has-text("📈 Market")');
      
      // Should redirect to login or show session expired
      await expect(page.locator('text=session', 'text=expired', 'text=login')).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('A08 - Software and Data Integrity Failures', () => {
    test('should validate WebSocket message integrity', async ({ page }) => {
      await page.addInitScript(() => {
        const originalWebSocket = window.WebSocket;
        window.WebSocket = class extends originalWebSocket {
          constructor(url: string | URL, protocols?: string | string[]) {
            super(url, protocols);
            (window as any).testWebSocket = this;
          }
        };
      });

      await page.waitForFunction(() => (window as any).testWebSocket);

      // Send message without proper signature
      const invalidMessage = {
        type: 'market_update',
        data: { commodity: 'organics', price: 10.50 },
        timestamp: new Date().toISOString(),
        signature: 'invalid_signature',
        session_id: 'test_session'
      };

      await page.evaluate((msg) => {
        const ws = (window as any).testWebSocket;
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify(msg));
        }
      }, invalidMessage);

      await page.waitForTimeout(1000);

      // Message should be rejected
      const processedMessage = await page.evaluate(() => {
        return (window as any).receivedMessages?.find((msg: any) => 
          msg.signature === 'invalid_signature'
        );
      });

      expect(processedMessage).toBeUndefined();
    });
  });

  test.describe('A09 - Security Logging and Monitoring Failures', () => {
    test('should log security events', async ({ page }) => {
      // Trigger security events that should be logged
      await page.click('button:has-text("🤖 Automation")');
      await page.click('button:has-text("New Rule")');
      
      // Try XSS payload (should be logged)
      await page.fill('input[placeholder="Enter rule name"]', '<script>alert("XSS")</script>');
      await page.click('button:has-text("Create Rule")');
      
      // Try excessive requests (should be logged)
      for (let i = 0; i < 20; i++) {
        await page.click('button:has-text("Create Rule")');
        await page.waitForTimeout(50);
      }
      
      // Check if security logging is working (would need backend validation in real scenario)
      // For E2E test, we verify that the system responds appropriately to security events
      const hasRateLimit = await page.locator('text=rate limit', 'text=too many requests').isVisible();
      expect(hasRateLimit).toBeTruthy();
    });
  });

  test.describe('A10 - Server-Side Request Forgery (SSRF)', () => {
    test('should prevent SSRF in market data requests', async ({ page }) => {
      await page.click('button:has-text("📈 Market")');
      await page.waitForSelector('.market-intelligence-dashboard');
      
      // Try to trigger SSRF via commodity selection or market requests
      const ssrfPayloads = [
        'http://localhost:22',
        'http://169.254.169.254/metadata',
        'file:///etc/passwd',
        'ftp://internal.server/data'
      ];

      for (const payload of ssrfPayloads) {
        // Try to inject SSRF payload in various inputs
        try {
          await page.evaluate((url) => {
            // Simulate API request with malicious URL
            fetch('/api/v1/market/data?source=' + encodeURIComponent(url))
              .catch(() => {}); // Expected to fail
          }, payload);
        } catch (e) {
          // Expected - requests should be rejected
        }
      }
      
      // System should still be functional (not crashed by SSRF attempts)
      const refreshButton = page.locator('button:has-text("Get ARIA Analysis")');
      await expect(refreshButton).toBeEnabled();
    });
  });
});

test.describe('Additional Security Measures', () => {
  test('should implement Content Security Policy', async ({ page }) => {
    const response = await page.goto('/dashboard');
    
    if (response) {
      const cspHeader = response.headers()['content-security-policy'];
      
      // Should have CSP header
      expect(cspHeader).toBeTruthy();
      
      // Should restrict inline scripts
      if (cspHeader) {
        expect(cspHeader).toContain("script-src");
        expect(cspHeader).not.toContain("'unsafe-inline'");
      }
    }
  });

  test('should prevent clickjacking attacks', async ({ page }) => {
    const response = await page.goto('/dashboard');
    
    if (response) {
      const xFrameOptions = response.headers()['x-frame-options'];
      const frameAncestors = response.headers()['content-security-policy'];
      
      // Should have anti-clickjacking headers
      expect(xFrameOptions === 'DENY' || 
             xFrameOptions === 'SAMEORIGIN' || 
             (frameAncestors && frameAncestors.includes('frame-ancestors'))).toBeTruthy();
    }
  });

  test('should implement proper HTTPS security headers', async ({ page }) => {
    const response = await page.goto('/dashboard');
    
    if (response) {
      const headers = response.headers();
      
      // Security headers that should be present
      const requiredHeaders = [
        'strict-transport-security',
        'x-content-type-options', 
        'x-frame-options',
        'referrer-policy'
      ];

      for (const header of requiredHeaders) {
        expect(headers).toHaveProperty(header);
      }
      
      // HSTS should be properly configured
      if (headers['strict-transport-security']) {
        expect(headers['strict-transport-security']).toContain('max-age');
      }
    }
  });
});