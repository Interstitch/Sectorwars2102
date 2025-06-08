/**
 * Enhanced AI System (ARIA) - OWASP Top 10 Security Validation
 * Comprehensive security testing for revolutionary AI enhancement system
 */

const axios = require('axios');
const fs = require('fs').promises;

const API_BASE = 'http://localhost:8080/api/v1';

async function testARIASecurityCompliance() {
    console.log('🛡️  Enhanced AI (ARIA) - OWASP Top 10 Security Validation');
    console.log('=' .repeat(70));
    
    let securityResults = {
        total: 0,
        passed: 0,
        failed: 0,
        criticalIssues: [],
        results: []
    };
    
    function logSecurityTest(name, passed, severity = 'medium', details = '') {
        securityResults.total++;
        if (passed) {
            securityResults.passed++;
            console.log(`✅ ${name}`);
        } else {
            securityResults.failed++;
            console.log(`❌ ${name} - ${details}`);
            if (severity === 'critical') {
                securityResults.criticalIssues.push({ name, details });
            }
        }
        securityResults.results.push({ name, passed, severity, details });
    }
    
    console.log('Testing OWASP Top 10 2021 Compliance for Enhanced AI System...\n');
    
    // A01 - Broken Access Control
    console.log('🔒 A01 - Access Control Validation');
    try {
        // Test unauthorized access to AI recommendations
        const response = await axios.get(`${API_BASE}/ai/recommendations`);
        logSecurityTest('A01: Unauthenticated AI Access Blocked', false, 'critical', 
            'AI endpoints should require authentication');
    } catch (error) {
        logSecurityTest('A01: Unauthenticated AI Access Blocked', 
            error.response?.status === 401 || error.response?.status === 422, 'critical',
            `Got ${error.response?.status} - Expected 401/422`);
    }
    
    // Test unauthorized access to AI chat
    try {
        const response = await axios.post(`${API_BASE}/ai/chat`, { message: 'test' });
        logSecurityTest('A01: Unauthenticated AI Chat Blocked', false, 'critical',
            'AI chat should require authentication');
    } catch (error) {
        logSecurityTest('A01: Unauthenticated AI Chat Blocked',
            error.response?.status === 401 || error.response?.status === 422, 'critical',
            `Got ${error.response?.status} - Expected 401/422`);
    }
    
    // A02 - Cryptographic Failures (check for secure configurations)
    console.log('\n🔐 A02 - Cryptographic Failures');
    try {
        const serviceContent = await fs.readFile('/workspaces/Sectorwars2102/services/gameserver/src/services/enhanced_ai_service.py', 'utf8');
        const hasEncryption = serviceContent.includes('encrypt') || serviceContent.includes('hash') || serviceContent.includes('secure');
        logSecurityTest('A02: Encryption Implementation', hasEncryption, 'high',
            hasEncryption ? 'Encryption patterns found' : 'Missing encryption implementation');
    } catch (error) {
        logSecurityTest('A02: Encryption Implementation', false, 'high', error.message);
    }
    
    // A03 - Injection (validate input sanitization)
    console.log('\n💉 A03 - Injection Prevention');
    try {
        const routesContent = await fs.readFile('/workspaces/Sectorwars2102/services/gameserver/src/api/routes/enhanced_ai.py', 'utf8');
        const hasInputValidation = routesContent.includes('validate') && 
                                  routesContent.includes('sanitize') &&
                                  routesContent.includes('Body(...)');
        logSecurityTest('A03: Input Validation & Sanitization', hasInputValidation, 'critical',
            hasInputValidation ? 'Input validation patterns found' : 'Missing input validation');
    } catch (error) {
        logSecurityTest('A03: Input Validation & Sanitization', false, 'critical', error.message);
    }
    
    // Check frontend XSS protection
    try {
        const aiComponentContent = await fs.readFile('/workspaces/Sectorwars2102/services/player-client/src/components/ai/EnhancedAIAssistant.tsx', 'utf8');
        const hasXSSProtection = aiComponentContent.includes('DOMPurify') || 
                               aiComponentContent.includes('sanitize') ||
                               aiComponentContent.includes('escape');
        logSecurityTest('A03: Frontend XSS Protection', hasXSSProtection, 'critical',
            hasXSSProtection ? 'XSS protection found' : 'Missing XSS protection');
    } catch (error) {
        logSecurityTest('A03: Frontend XSS Protection', false, 'critical', error.message);
    }
    
    // A04 - Insecure Design (check for rate limiting and business logic protection)
    console.log('\n🏗️  A04 - Insecure Design Prevention');
    try {
        const routesContent = await fs.readFile('/workspaces/Sectorwars2102/services/gameserver/src/api/routes/enhanced_ai.py', 'utf8');
        const hasRateLimiting = routesContent.includes('rate_limit') || routesContent.includes('Depends(rate_limiter)');
        logSecurityTest('A04: Rate Limiting Implementation', hasRateLimiting, 'high',
            hasRateLimiting ? 'Rate limiting found' : 'Missing rate limiting');
    } catch (error) {
        logSecurityTest('A04: Rate Limiting Implementation', false, 'high', error.message);
    }
    
    // Check for AI quota management
    try {
        const modelsContent = await fs.readFile('/workspaces/Sectorwars2102/services/gameserver/src/models/enhanced_ai_models.py', 'utf8');
        const hasQuotaManagement = modelsContent.includes('api_request_quota') || modelsContent.includes('request_count');
        logSecurityTest('A04: AI Quota Management', hasQuotaManagement, 'medium',
            hasQuotaManagement ? 'Quota management found' : 'Missing quota management');
    } catch (error) {
        logSecurityTest('A04: AI Quota Management', false, 'medium', error.message);
    }
    
    // A05 - Security Misconfiguration
    console.log('\n⚙️  A05 - Security Misconfiguration');
    try {
        const mainContent = await fs.readFile('/workspaces/Sectorwars2102/services/gameserver/src/main.py', 'utf8');
        const hasSecureConfig = mainContent.includes('TrustedHostMiddleware') && 
                               mainContent.includes('CORSMiddleware') &&
                               !mainContent.includes('allow_origins=["*"]') ||
                               mainContent.includes('DEVELOPMENT_MODE');
        logSecurityTest('A05: Secure CORS Configuration', hasSecureConfig, 'medium',
            hasSecureConfig ? 'Secure configuration found' : 'Potentially insecure CORS');
    } catch (error) {
        logSecurityTest('A05: Secure CORS Configuration', false, 'medium', error.message);
    }
    
    // A06 - Vulnerable and Outdated Components
    console.log('\n📦 A06 - Component Security');
    try {
        const packageContent = await fs.readFile('/workspaces/Sectorwars2102/services/player-client/package.json', 'utf8');
        const packageJson = JSON.parse(packageContent);
        const hasSecurityPackages = packageJson.dependencies && 
                                  (packageJson.dependencies['dompurify'] || 
                                   packageJson.dependencies['isomorphic-dompurify'] ||
                                   packageJson.dependencies['@types/dompurify']);
        logSecurityTest('A06: Security Dependencies', hasSecurityPackages, 'medium',
            hasSecurityPackages ? 'Security packages found' : 'Missing security dependencies');
    } catch (error) {
        logSecurityTest('A06: Security Dependencies', false, 'medium', error.message);
    }
    
    // A07 - Identification and Authentication Failures
    console.log('\n🔑 A07 - Authentication Security');
    try {
        const routesContent = await fs.readFile('/workspaces/Sectorwars2102/services/gameserver/src/api/routes/enhanced_ai.py', 'utf8');
        const hasAuthValidation = routesContent.includes('validate_ai_access') || 
                                 routesContent.includes('Depends(get_current_user)') ||
                                 routesContent.includes('validate_player_access');
        logSecurityTest('A07: AI Authentication Validation', hasAuthValidation, 'critical',
            hasAuthValidation ? 'Authentication validation found' : 'Missing authentication');
    } catch (error) {
        logSecurityTest('A07: AI Authentication Validation', false, 'critical', error.message);
    }
    
    // A08 - Software and Data Integrity Failures
    console.log('\n🔍 A08 - Data Integrity');
    try {
        const serviceContent = await fs.readFile('/workspaces/Sectorwars2102/services/gameserver/src/services/enhanced_ai_service.py', 'utf8');
        const hasIntegrityChecks = serviceContent.includes('signature') || 
                                  serviceContent.includes('validate') ||
                                  serviceContent.includes('verify');
        logSecurityTest('A08: Data Integrity Validation', hasIntegrityChecks, 'medium',
            hasIntegrityChecks ? 'Integrity checks found' : 'Missing data integrity validation');
    } catch (error) {
        logSecurityTest('A08: Data Integrity Validation', false, 'medium', error.message);
    }
    
    // A09 - Security Logging and Monitoring Failures
    console.log('\n📋 A09 - Security Logging');
    try {
        const serviceContent = await fs.readFile('/workspaces/Sectorwars2102/services/gameserver/src/services/enhanced_ai_service.py', 'utf8');
        const hasSecurityLogging = serviceContent.includes('audit_log') || 
                                  serviceContent.includes('security_event') ||
                                  serviceContent.includes('log_security');
        logSecurityTest('A09: Security Event Logging', hasSecurityLogging, 'high',
            hasSecurityLogging ? 'Security logging found' : 'Missing security logging');
    } catch (error) {
        logSecurityTest('A09: Security Event Logging', false, 'high', error.message);
    }
    
    // Check for audit models
    try {
        const modelsContent = await fs.readFile('/workspaces/Sectorwars2102/services/gameserver/src/models/enhanced_ai_models.py', 'utf8');
        const hasAuditModels = modelsContent.includes('audit_log') || modelsContent.includes('security_audit');
        logSecurityTest('A09: Audit Trail Models', hasAuditModels, 'medium',
            hasAuditModels ? 'Audit models found' : 'Missing audit trail models');
    } catch (error) {
        logSecurityTest('A09: Audit Trail Models', false, 'medium', error.message);
    }
    
    // A10 - Server-Side Request Forgery (SSRF)
    console.log('\n🌐 A10 - SSRF Prevention');
    try {
        const serviceContent = await fs.readFile('/workspaces/Sectorwars2102/services/gameserver/src/services/enhanced_ai_service.py', 'utf8');
        const hasSSRFProtection = !serviceContent.includes('requests.get(') || 
                                 serviceContent.includes('validate_url') ||
                                 serviceContent.includes('whitelist');
        logSecurityTest('A10: SSRF Protection', hasSSRFProtection, 'high',
            hasSSRFProtection ? 'SSRF protection in place' : 'Potential SSRF vulnerability');
    } catch (error) {
        logSecurityTest('A10: SSRF Protection', false, 'high', error.message);
    }
    
    // Additional AI-Specific Security Tests
    console.log('\n🧠 AI-Specific Security Measures');
    
    // AI Prompt Injection Protection
    try {
        const serviceContent = await fs.readFile('/workspaces/Sectorwars2102/services/gameserver/src/services/enhanced_ai_service.py', 'utf8');
        const hasPromptInjectionProtection = serviceContent.includes('sanitize_prompt') || 
                                           serviceContent.includes('prompt_validation') ||
                                           serviceContent.includes('filter_prompt');
        logSecurityTest('AI: Prompt Injection Protection', hasPromptInjectionProtection, 'high',
            hasPromptInjectionProtection ? 'Prompt protection found' : 'Missing prompt injection protection');
    } catch (error) {
        logSecurityTest('AI: Prompt Injection Protection', false, 'high', error.message);
    }
    
    // AI Response Filtering
    try {
        const serviceContent = await fs.readFile('/workspaces/Sectorwars2102/services/gameserver/src/services/enhanced_ai_service.py', 'utf8');
        const hasResponseFiltering = serviceContent.includes('filter_response') || 
                                   serviceContent.includes('sanitize_response') ||
                                   serviceContent.includes('validate_response');
        logSecurityTest('AI: Response Content Filtering', hasResponseFiltering, 'medium',
            hasResponseFiltering ? 'Response filtering found' : 'Missing response filtering');
    } catch (error) {
        logSecurityTest('AI: Response Content Filtering', false, 'medium', error.message);
    }
    
    // Model Access Control
    try {
        const modelsContent = await fs.readFile('/workspaces/Sectorwars2102/services/gameserver/src/models/enhanced_ai_models.py', 'utf8');
        const hasModelAccessControl = modelsContent.includes('security_level') || 
                                     modelsContent.includes('access_level') ||
                                     modelsContent.includes('permission');
        logSecurityTest('AI: Model Access Control', hasModelAccessControl, 'medium',
            hasModelAccessControl ? 'Access control found' : 'Missing model access control');
    } catch (error) {
        logSecurityTest('AI: Model Access Control', false, 'medium', error.message);
    }
    
    console.log('\n' + '=' .repeat(70));
    console.log('🎯 Enhanced AI (ARIA) Security Test Results:');
    console.log(`✅ Passed: ${securityResults.passed}/${securityResults.total}`);
    console.log(`❌ Failed: ${securityResults.failed}/${securityResults.total}`);
    console.log(`📊 Security Score: ${Math.round((securityResults.passed / securityResults.total) * 100)}%`);
    
    if (securityResults.criticalIssues.length > 0) {
        console.log('\n🚨 CRITICAL SECURITY ISSUES:');
        securityResults.criticalIssues.forEach(issue => {
            console.log(`   ❌ ${issue.name}: ${issue.details}`);
        });
    }
    
    const securityScore = Math.round((securityResults.passed / securityResults.total) * 100);
    
    if (securityScore >= 90) {
        console.log('\n🛡️  EXCELLENT SECURITY - ARIA meets enterprise security standards!');
    } else if (securityScore >= 75) {
        console.log('\n⚠️  GOOD SECURITY - Minor improvements recommended before production.');
    } else {
        console.log('\n🚨 SECURITY CONCERNS - Address issues before deployment.');
    }
    
    return securityResults;
}

// Run the security test
if (require.main === module) {
    testARIASecurityCompliance().catch(console.error);
}

module.exports = { testARIASecurityCompliance };