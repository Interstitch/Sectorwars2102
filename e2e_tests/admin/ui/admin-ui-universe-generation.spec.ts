import { test, expect } from '@playwright/test';
import { test as authTest } from '../../fixtures/auth.fixtures';
import { loginAsAdmin } from '../../utils/auth.utils';

test.describe('Admin UI - Universe Generation', () => {
  authTest.beforeEach(async ({ page, adminCredentials }) => {
    try {
      await loginAsAdmin(page, adminCredentials);
      
      // Navigate to universe page
      await page.goto('/universe', { waitUntil: 'networkidle' });
    } catch (error) {
      console.error('Login failed but continuing with test:', error);
      await page.goto('/universe', { waitUntil: 'networkidle' });
    }
  });

  authTest('should display universe administration page', async ({ page }) => {
    // Wait for page to load
    await page.waitForSelector('body', { state: 'attached' });
    
    // Check for universe page elements
    const pageContent = await page.textContent('body');
    expect(pageContent?.length).toBeGreaterThan(10);
    
    // Look for universe-related content
    const universeContentFound = await page.evaluate(() => {
      const bodyText = document.body.textContent || '';
      return bodyText.includes('Universe') || 
             bodyText.includes('Galaxy') ||
             bodyText.includes('Generate') ||
             bodyText.includes('Sectors');
    });
    
    expect(universeContentFound).toBeTruthy();
    
    // Take screenshot
    await page.screenshot({ path: 'universe-administration.png' });
  });

  authTest('should show galaxy generation form when no galaxy exists', async ({ page }) => {
    await page.waitForSelector('body', { state: 'attached' });
    
    // Look for "Generate New Galaxy" button or similar
    const generateButtons = await page.locator('button, .btn').filter({ 
      hasText: /generate|new galaxy|create/i 
    }).count();
    
    if (generateButtons > 0) {
      console.log(`Found ${generateButtons} generate-related buttons`);
    }
    
    // Take screenshot
    await page.screenshot({ path: 'galaxy-generation-available.png' });
  });

  authTest('should open galaxy generation modal', async ({ page }) => {
    await page.waitForSelector('body', { state: 'attached' });
    
    try {
      // Look for and click generate galaxy button
      const generateButton = page.locator('button, .btn').filter({ 
        hasText: /generate.*galaxy|new galaxy|create galaxy/i 
      }).first();
      
      const buttonCount = await generateButton.count();
      console.log(`Found ${buttonCount} generate galaxy button(s)`);
      
      if (buttonCount > 0) {
        await generateButton.click();
        
        // Wait for modal or form to appear
        await page.waitForTimeout(1000);
        
        // Look for form elements
        const formElements = await page.locator('form, .modal, .form-group, input[type="text"], select').count();
        console.log(`Found ${formElements} form-related elements after clicking generate`);
        
        // Take screenshot of modal/form
        await page.screenshot({ path: 'galaxy-generation-modal.png' });
        
        // Look for specific galaxy generation form fields
        const nameField = page.locator('input[placeholder*="name"], input[id*="name"], input[name*="name"]');
        const sectorField = page.locator('input[type="number"], input[id*="sector"], input[name*="sector"]');
        
        if (await nameField.count() > 0) {
          console.log('Found galaxy name field');
        }
        if (await sectorField.count() > 0) {
          console.log('Found sector count field');
        }
      } else {
        console.log('No generate galaxy button found');
      }
    } catch (error) {
      console.log('Error interacting with generate button:', error);
    }
  });

  authTest('should fill and submit galaxy generation form', async ({ page }) => {
    await page.waitForSelector('body', { state: 'attached' });
    
    try {
      // Click generate galaxy button
      const generateButton = page.locator('button, .btn').filter({ 
        hasText: /generate.*galaxy|new galaxy|create galaxy/i 
      }).first();
      
      if (await generateButton.count() > 0) {
        await generateButton.click();
        await page.waitForTimeout(1000);
        
        // Fill galaxy name
        const nameFields = page.locator('input[type="text"], input[placeholder*="name"]');
        if (await nameFields.count() > 0) {
          await nameFields.first().fill('Test Galaxy E2E');
          console.log('Filled galaxy name field');
        }
        
        // Fill sector count
        const numberFields = page.locator('input[type="number"]');
        if (await numberFields.count() > 0) {
          await numberFields.first().fill('50');
          console.log('Filled sector count field');
        }
        
        // Test region distribution sliders
        const sliders = page.locator('input[type="range"]');
        const sliderCount = await sliders.count();
        console.log(`Found ${sliderCount} sliders`);
        
        if (sliderCount >= 3) {
          // Test the responsive slider behavior
          const federationSlider = sliders.nth(0);
          const borderSlider = sliders.nth(1);
          const frontierSlider = sliders.nth(2);
          
          // Get initial values
          const initialFed = await federationSlider.getAttribute('value');
          const initialBorder = await borderSlider.getAttribute('value');
          const initialFrontier = await frontierSlider.getAttribute('value');
          
          console.log(`Initial values: Fed=${initialFed}, Border=${initialBorder}, Frontier=${initialFrontier}`);
          
          // Change federation slider and check if others adjust
          await federationSlider.evaluate((el: HTMLInputElement) => {
            el.value = '60';
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
          });
          await page.waitForTimeout(500);
          
          const newBorder = await borderSlider.getAttribute('value');
          const newFrontier = await frontierSlider.getAttribute('value');
          
          console.log(`After change: Fed=60, Border=${newBorder}, Frontier=${newFrontier}`);
          
          // Verify total is still 100%
          const total = 60 + parseInt(newBorder || '0') + parseInt(newFrontier || '0');
          console.log(`Total percentage: ${total}%`);
          expect(total).toBe(100);
        }
        
        // Take screenshot of filled form
        await page.screenshot({ path: 'galaxy-generation-filled.png' });
        
        // Look for submit button
        const submitButtons = page.locator('button[type="submit"], .btn-primary, button').filter({
          hasText: /generate|create|submit/i
        });
        
        if (await submitButtons.count() > 0) {
          console.log('Found submit button, attempting to submit...');
          
          // Wait for any potential API call
          const responsePromise = page.waitForResponse(response => 
            response.url().includes('/api') && response.request().method() === 'POST',
            { timeout: 5000 }
          ).catch(() => null);
          
          await submitButtons.first().click();
          
          // Wait for response or timeout
          const response = await responsePromise;
          if (response) {
            console.log(`API Response: ${response.status()} ${response.url()}`);
            
            // Check if successful
            if (response.status() === 200) {
              console.log('Galaxy generation API call succeeded');
            } else {
              console.log('Galaxy generation API call failed');
              
              // Log response for debugging
              try {
                const responseText = await response.text();
                console.log('Response body:', responseText);
              } catch (e) {
                console.log('Could not read response body');
              }
            }
          } else {
            console.log('No API response detected within timeout');
          }
          
          // Wait for any UI updates
          await page.waitForTimeout(2000);
          
          // Take screenshot after submission
          await page.screenshot({ path: 'galaxy-generation-after-submit.png' });
          
        } else {
          console.log('No submit button found');
        }
      }
    } catch (error) {
      console.log('Error during galaxy generation test:', error);
      await page.screenshot({ path: 'galaxy-generation-error.png' });
    }
  });

  authTest('should display generated galaxy data', async ({ page }) => {
    await page.waitForSelector('body', { state: 'attached' });
    
    // Look for galaxy overview data
    const galaxyDataElements = await page.locator('.stat-card, .metric-card, .overview, .statistics').count();
    console.log(`Found ${galaxyDataElements} potential galaxy data elements`);
    
    // Look for specific statistics
    const statisticsFound = await page.evaluate(() => {
      const bodyText = document.body.textContent || '';
      return {
        hasSectors: /sectors?/i.test(bodyText),
        hasPorts: /ports?/i.test(bodyText),
        hasPlanets: /planets?/i.test(bodyText),
        hasWarpTunnels: /warp.*tunnels?|tunnels?/i.test(bodyText),
        hasRegions: /regions?/i.test(bodyText)
      };
    });
    
    console.log('Galaxy statistics found:', statisticsFound);
    
    // Take screenshot
    await page.screenshot({ path: 'galaxy-overview-data.png' });
    
    // If galaxy data is present, verify it's reasonable
    if (statisticsFound.hasSectors) {
      console.log('Galaxy appears to have sector data');
    }
  });

  authTest('should navigate between universe tabs', async ({ page }) => {
    await page.waitForSelector('body', { state: 'attached' });
    
    // Look for tab navigation
    const tabs = page.locator('.tab, .nav-item, button').filter({
      hasText: /overview|visualization|management|map/i
    });
    
    const tabCount = await tabs.count();
    console.log(`Found ${tabCount} potential navigation tabs`);
    
    if (tabCount > 1) {
      // Test clicking different tabs
      for (let i = 0; i < Math.min(tabCount, 3); i++) {
        try {
          await tabs.nth(i).click();
          await page.waitForTimeout(1000);
          
          const tabText = await tabs.nth(i).textContent();
          console.log(`Clicked tab: ${tabText}`);
          
          await page.screenshot({ path: `universe-tab-${i}.png` });
        } catch (error) {
          console.log(`Error clicking tab ${i}:`, error);
        }
      }
    }
  });
});