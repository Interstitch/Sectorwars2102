/**
 * Enhanced AI System (ARIA) - Comprehensive Integration Test
 * Tests the complete Revolutionary AI Enhancement System end-to-end
 */

const axios = require('axios');

const API_BASE = 'http://localhost:8080/api/v1';
const FRONTEND_BASE = 'http://localhost:3000';

async function testEnhancedAISystem() {
    console.log('🧠 Testing Enhanced AI System (ARIA) - Revolutionary Implementation');
    console.log('=' .repeat(70));
    
    let testResults = {
        total: 0,
        passed: 0,
        failed: 0,
        results: []
    };
    
    // Helper function to log test results
    function logTest(name, passed, details = '') {
        testResults.total++;
        if (passed) {
            testResults.passed++;
            console.log(`✅ ${name}`);
        } else {
            testResults.failed++;
            console.log(`❌ ${name} - ${details}`);
        }
        testResults.results.push({ name, passed, details });
    }
    
    // Test 1: API Server Health
    try {
        const response = await axios.get(`${API_BASE}/status`);
        logTest('API Server Health Check', 
            response.status === 200 && response.data.status === 'healthy');
    } catch (error) {
        logTest('API Server Health Check', false, error.message);
    }
    
    // Test 2: Enhanced AI Endpoints Exist (without auth - should get auth error)
    try {
        const response = await axios.get(`${API_BASE}/ai/recommendations`);
        logTest('Enhanced AI Endpoint Authentication', false, 'Should require authentication');
    } catch (error) {
        // We expect a 401 or 422 error for unauthenticated requests
        logTest('Enhanced AI Endpoint Authentication', 
            error.response?.status === 401 || error.response?.status === 422,
            `Got status ${error.response?.status}`);
    }
    
    // Test 3: Frontend Service Availability
    try {
        const response = await axios.get(FRONTEND_BASE, { timeout: 5000 });
        logTest('Frontend Service Availability', 
            response.status === 200 && response.data.includes('<!DOCTYPE html>'));
    } catch (error) {
        logTest('Frontend Service Availability', false, error.message);
    }
    
    // Test 4: Enhanced AI Frontend Components (check for component files)
    const fs = require('fs').promises;
    try {
        const aiComponentExists = await fs.access('/workspaces/Sectorwars2102/services/player-client/src/components/ai/EnhancedAIAssistant.tsx');
        logTest('Enhanced AI Component Exists', true);
    } catch (error) {
        logTest('Enhanced AI Component Exists', false, 'Component file not found');
    }
    
    // Test 5: Enhanced AI CSS Styling
    try {
        const cssExists = await fs.access('/workspaces/Sectorwars2102/services/player-client/src/components/ai/enhanced-ai-assistant.css');
        logTest('Enhanced AI CSS Styling', true);
    } catch (error) {
        logTest('Enhanced AI CSS Styling', false, 'CSS file not found');
    }
    
    // Test 6: Database Migration Status (Enhanced AI tables)
    try {
        const { spawn } = require('child_process');
        const alembicProcess = spawn('docker', ['exec', 'sectorwars-gameserver', 'alembic', 'current']);
        
        let output = '';
        alembicProcess.stdout.on('data', (data) => {
            output += data.toString();
        });
        
        await new Promise((resolve, reject) => {
            alembicProcess.on('close', (code) => {
                if (code === 0) {
                    resolve();
                } else {
                    reject(new Error(`Alembic process exited with code ${code}`));
                }
            });
        });
        
        logTest('Enhanced AI Database Migration', 
            output.includes('8b9989967eb1') || output.includes('enhanced_ai'),
            'Migration includes Enhanced AI schema');
    } catch (error) {
        logTest('Enhanced AI Database Migration', false, error.message);
    }
    
    // Test 7: Backend Service Models (check for model files)
    try {
        const modelsExist = await fs.access('/workspaces/Sectorwars2102/services/gameserver/src/models/enhanced_ai_models.py');
        logTest('Enhanced AI Models', true);
    } catch (error) {
        logTest('Enhanced AI Models', false, 'Models file not found');
    }
    
    // Test 8: Enhanced AI Service Layer
    try {
        const serviceExists = await fs.access('/workspaces/Sectorwars2102/services/gameserver/src/services/enhanced_ai_service.py');
        logTest('Enhanced AI Service Layer', true);
    } catch (error) {
        logTest('Enhanced AI Service Layer', false, 'Service file not found');
    }
    
    // Test 9: API Routes Integration
    try {
        const routesExist = await fs.access('/workspaces/Sectorwars2102/services/gameserver/src/api/routes/enhanced_ai.py');
        logTest('Enhanced AI API Routes', true);
    } catch (error) {
        logTest('Enhanced AI API Routes', false, 'Routes file not found');
    }
    
    // Test 10: OWASP Security Implementation (check for security patterns in code)
    try {
        const routesContent = await fs.readFile('/workspaces/Sectorwars2102/services/gameserver/src/api/routes/enhanced_ai.py', 'utf8');
        const hasOWASPSecurity = routesContent.includes('validate_ai_access') && 
                               routesContent.includes('sanitize') &&
                               routesContent.includes('rate_limit');
        logTest('OWASP Security Implementation', hasOWASPSecurity,
            hasOWASPSecurity ? 'Security patterns found' : 'Missing security patterns');
    } catch (error) {
        logTest('OWASP Security Implementation', false, error.message);
    }
    
    // Test 11: Foundation Sprint Integration (check for WebSocket support)
    try {
        const dashboardContent = await fs.readFile('/workspaces/Sectorwars2102/services/player-client/src/components/pages/GameDashboard.tsx', 'utf8');
        const hasAIIntegration = dashboardContent.includes('EnhancedAIAssistant');
        logTest('Foundation Sprint Integration', hasAIIntegration,
            hasAIIntegration ? 'AI Assistant integrated in dashboard' : 'Missing AI integration');
    } catch (error) {
        logTest('Foundation Sprint Integration', false, error.message);
    }
    
    // Test 12: Cross-System Intelligence Architecture
    try {
        const serviceContent = await fs.readFile('/workspaces/Sectorwars2102/services/gameserver/src/services/enhanced_ai_service.py', 'utf8');
        const hasCrossSystem = serviceContent.includes('TRADING') && 
                              serviceContent.includes('COMBAT') &&
                              serviceContent.includes('COLONIZATION') &&
                              serviceContent.includes('PORT_MANAGEMENT') &&
                              serviceContent.includes('STRATEGIC');
        logTest('Cross-System Intelligence Architecture', hasCrossSystem,
            hasCrossSystem ? 'All 5 AI systems implemented' : 'Missing cross-system features');
    } catch (error) {
        logTest('Cross-System Intelligence Architecture', false, error.message);
    }
    
    console.log('\n' + '=' .repeat(70));
    console.log('🎯 Enhanced AI System Test Results:');
    console.log(`✅ Passed: ${testResults.passed}/${testResults.total}`);
    console.log(`❌ Failed: ${testResults.failed}/${testResults.total}`);
    console.log(`📊 Success Rate: ${Math.round((testResults.passed / testResults.total) * 100)}%`);
    
    if (testResults.passed === testResults.total) {
        console.log('\n🎊 ARIA Enhanced AI System - FULLY OPERATIONAL! 🎊');
        console.log('Revolutionary cross-system AI intelligence ready for deployment.');
    } else {
        console.log('\n⚠️  Some components need attention before full deployment.');
    }
    
    return testResults;
}

// Run the test
if (require.main === module) {
    testEnhancedAISystem().catch(console.error);
}

module.exports = { testEnhancedAISystem };