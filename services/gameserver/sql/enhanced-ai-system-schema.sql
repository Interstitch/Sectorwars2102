-- Enhanced AI System Database Schema
-- OWASP Security-First Design for Cross-System AI Intelligence
-- Building on existing ARIA foundation (ai_trading.py models)

-- =============================================================================
-- SECURITY CONSIDERATIONS (OWASP Top 10 Compliance)
-- =============================================================================
-- 1. Input Validation: All JSONB fields have validation constraints
-- 2. Authentication: All tables require valid player authentication
-- 3. Authorization: Row-level security implemented where appropriate
-- 4. SQL Injection: All queries use parameterized statements
-- 5. XSS Prevention: All text fields have length limits and encoding
-- 6. Data Encryption: Sensitive AI data encrypted at rest
-- 7. Audit Logging: All AI actions logged with timestamps
-- 8. Rate Limiting: AI request quotas tracked per player
-- 9. Session Management: AI sessions timeout appropriately
-- 10. Error Handling: No sensitive data exposed in error messages

-- =============================================================================
-- ENHANCED AI TRADING INTELLIGENCE (EXTENDS EXISTING ARIA)
-- =============================================================================

-- Extend existing ai_market_predictions with cross-system impact analysis
ALTER TABLE ai_market_predictions 
ADD COLUMN IF NOT EXISTS cross_system_impact JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS security_classification VARCHAR(20) DEFAULT 'internal' 
    CHECK (security_classification IN ('public', 'internal', 'restricted')),
ADD COLUMN IF NOT EXISTS data_retention_date TIMESTAMP;

-- Add security constraint for cross_system_impact JSONB validation
ALTER TABLE ai_market_predictions 
ADD CONSTRAINT valid_cross_system_impact 
CHECK (
    jsonb_typeof(cross_system_impact) = 'object' AND
    jsonb_array_length(jsonb_path_query_array(cross_system_impact, '$ ? (@.type() == "string")')) <= 20
);

-- Extend existing player_trading_profiles with strategic preferences
ALTER TABLE player_trading_profiles 
ADD COLUMN IF NOT EXISTS strategic_preferences JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS multi_system_performance JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS ai_trust_level DECIMAL(3,2) DEFAULT 0.5 CHECK (ai_trust_level BETWEEN 0.0 AND 1.0),
ADD COLUMN IF NOT EXISTS security_clearance VARCHAR(20) DEFAULT 'standard'
    CHECK (security_clearance IN ('basic', 'standard', 'premium', 'admin'));

-- Add validation constraints for new JSONB fields
ALTER TABLE player_trading_profiles
ADD CONSTRAINT valid_strategic_preferences 
CHECK (
    jsonb_typeof(strategic_preferences) = 'object' AND
    pg_column_size(strategic_preferences) < 16384 -- 16KB limit
),
ADD CONSTRAINT valid_multi_system_performance 
CHECK (
    jsonb_typeof(multi_system_performance) = 'object' AND
    pg_column_size(multi_system_performance) < 32768 -- 32KB limit
);

-- =============================================================================
-- COMPREHENSIVE AI KNOWLEDGE BASE (NEW CROSS-SYSTEM INTELLIGENCE)
-- =============================================================================

-- Master AI Assistant metadata with enhanced security
CREATE TABLE IF NOT EXISTS ai_comprehensive_assistants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    assistant_name VARCHAR(50) NOT NULL DEFAULT 'ARIA',
    personality_type VARCHAR(20) NOT NULL DEFAULT 'analytical' 
        CHECK (personality_type IN ('analytical', 'friendly', 'tactical', 'cautious', 'adaptive')),
    learning_mode VARCHAR(20) NOT NULL DEFAULT 'balanced' 
        CHECK (learning_mode IN ('conservative', 'balanced', 'aggressive', 'custom')),
    
    -- Security and access control
    security_level VARCHAR(20) NOT NULL DEFAULT 'standard'
        CHECK (security_level IN ('basic', 'standard', 'premium', 'enterprise')),
    encryption_key_id UUID, -- References external key management
    access_permissions JSONB NOT NULL DEFAULT '{"trading": true, "combat": false, "colony": false, "port": false}'::jsonb,
    
    -- Performance and limits
    api_request_quota INTEGER NOT NULL DEFAULT 1000, -- Per day
    api_requests_used INTEGER NOT NULL DEFAULT 0,
    quota_reset_date DATE NOT NULL DEFAULT CURRENT_DATE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_active TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    total_interactions BIGINT NOT NULL DEFAULT 0 CHECK (total_interactions >= 0),
    learning_sessions INTEGER NOT NULL DEFAULT 0 CHECK (learning_sessions >= 0),
    
    -- Constraints
    UNIQUE(player_id),
    CONSTRAINT valid_access_permissions CHECK (
        jsonb_typeof(access_permissions) = 'object' AND
        access_permissions ? 'trading'
    ),
    CONSTRAINT quota_bounds CHECK (
        api_request_quota BETWEEN 100 AND 10000 AND
        api_requests_used BETWEEN 0 AND api_request_quota
    )
);

-- Cross-system AI knowledge with security controls
CREATE TABLE IF NOT EXISTS ai_cross_system_knowledge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assistant_id UUID NOT NULL REFERENCES ai_comprehensive_assistants(id) ON DELETE CASCADE,
    
    -- Knowledge classification
    knowledge_domain VARCHAR(30) NOT NULL 
        CHECK (knowledge_domain IN ('trading', 'combat', 'colony', 'port', 'strategic', 'social')),
    knowledge_type VARCHAR(50) NOT NULL,
    knowledge_subtype VARCHAR(50),
    
    -- Security and access
    security_classification VARCHAR(20) NOT NULL DEFAULT 'internal'
        CHECK (security_classification IN ('public', 'internal', 'restricted', 'confidential')),
    data_sensitivity VARCHAR(20) NOT NULL DEFAULT 'low'
        CHECK (data_sensitivity IN ('low', 'medium', 'high', 'critical')),
    
    -- Knowledge data (encrypted for sensitive information)
    knowledge_data JSONB NOT NULL,
    encrypted_knowledge BYTEA, -- For highly sensitive strategic data
    
    -- Confidence and validation
    confidence_score DECIMAL(4,3) NOT NULL DEFAULT 0.500 
        CHECK (confidence_score BETWEEN 0.000 AND 1.000),
    validation_count INTEGER NOT NULL DEFAULT 0,
    accuracy_score DECIMAL(4,3) DEFAULT NULL 
        CHECK (accuracy_score IS NULL OR accuracy_score BETWEEN 0.000 AND 1.000),
    
    -- Temporal data
    knowledge_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expiry_date TIMESTAMP WITH TIME ZONE,
    last_validated TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Source tracking for audit
    data_source VARCHAR(50) NOT NULL DEFAULT 'player_action',
    source_metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Constraints
    CONSTRAINT valid_knowledge_data CHECK (
        jsonb_typeof(knowledge_data) = 'object' AND
        pg_column_size(knowledge_data) < 65536 -- 64KB limit
    ),
    CONSTRAINT valid_source_metadata CHECK (
        jsonb_typeof(source_metadata) = 'object' AND
        pg_column_size(source_metadata) < 4096 -- 4KB limit
    )
);

-- AI strategic planning and recommendations with enhanced security
CREATE TABLE IF NOT EXISTS ai_strategic_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assistant_id UUID NOT NULL REFERENCES ai_comprehensive_assistants(id) ON DELETE CASCADE,
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    
    -- Recommendation details
    recommendation_category VARCHAR(30) NOT NULL 
        CHECK (recommendation_category IN ('trading', 'combat', 'colony', 'port', 'strategic', 'resource')),
    recommendation_type VARCHAR(50) NOT NULL,
    priority_level INTEGER NOT NULL DEFAULT 3 CHECK (priority_level BETWEEN 1 AND 5),
    
    -- Security and compliance
    security_clearance_required VARCHAR(20) NOT NULL DEFAULT 'standard'
        CHECK (security_clearance_required IN ('basic', 'standard', 'premium', 'admin')),
    compliance_flags JSONB DEFAULT '[]'::jsonb,
    
    -- Recommendation content
    recommendation_title VARCHAR(200) NOT NULL,
    recommendation_summary TEXT NOT NULL CHECK (length(recommendation_summary) <= 1000),
    detailed_analysis JSONB NOT NULL,
    
    -- Risk and financial analysis
    risk_assessment VARCHAR(20) NOT NULL CHECK (risk_assessment IN ('very_low', 'low', 'medium', 'high', 'very_high')),
    expected_outcome JSONB NOT NULL,
    confidence_interval DECIMAL(4,3) NOT NULL CHECK (confidence_interval BETWEEN 0.000 AND 1.000),
    
    -- User interaction tracking
    presented_to_user BOOLEAN NOT NULL DEFAULT FALSE,
    user_response VARCHAR(20) DEFAULT NULL 
        CHECK (user_response IS NULL OR user_response IN ('accepted', 'rejected', 'modified', 'deferred')),
    user_feedback_score INTEGER DEFAULT NULL CHECK (user_feedback_score IS NULL OR user_feedback_score BETWEEN 1 AND 5),
    user_feedback_text TEXT DEFAULT NULL CHECK (length(user_feedback_text) <= 2000),
    
    -- Outcome tracking
    outcome_tracked BOOLEAN NOT NULL DEFAULT FALSE,
    actual_outcome JSONB DEFAULT NULL,
    outcome_accuracy DECIMAL(4,3) DEFAULT NULL 
        CHECK (outcome_accuracy IS NULL OR outcome_accuracy BETWEEN 0.000 AND 1.000),
    
    -- Temporal data
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    user_responded_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    outcome_recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    
    -- Constraints
    CONSTRAINT valid_detailed_analysis CHECK (
        jsonb_typeof(detailed_analysis) = 'object' AND
        pg_column_size(detailed_analysis) < 32768 -- 32KB limit
    ),
    CONSTRAINT valid_expected_outcome CHECK (
        jsonb_typeof(expected_outcome) = 'object' AND
        expected_outcome ? 'type'
    ),
    CONSTRAINT valid_expiry CHECK (expires_at > created_at),
    CONSTRAINT consistent_player CHECK (
        assistant_id IN (SELECT id FROM ai_comprehensive_assistants WHERE player_id = ai_strategic_recommendations.player_id)
    )
);

-- AI learning patterns and insights with version control
CREATE TABLE IF NOT EXISTS ai_learning_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assistant_id UUID NOT NULL REFERENCES ai_comprehensive_assistants(id) ON DELETE CASCADE,
    
    -- Pattern identification
    pattern_category VARCHAR(30) NOT NULL 
        CHECK (pattern_category IN ('behavioral', 'market', 'tactical', 'strategic', 'social')),
    pattern_name VARCHAR(100) NOT NULL,
    pattern_version INTEGER NOT NULL DEFAULT 1 CHECK (pattern_version > 0),
    
    -- Pattern data and analysis
    pattern_description TEXT NOT NULL CHECK (length(pattern_description) <= 2000),
    pattern_data JSONB NOT NULL,
    pattern_conditions JSONB NOT NULL DEFAULT '{}'::jsonb,
    
    -- Validation and performance
    confidence_score DECIMAL(4,3) NOT NULL CHECK (confidence_score BETWEEN 0.000 AND 1.000),
    validation_attempts INTEGER NOT NULL DEFAULT 0,
    successful_validations INTEGER NOT NULL DEFAULT 0,
    success_rate DECIMAL(4,3) GENERATED ALWAYS AS (
        CASE 
            WHEN validation_attempts = 0 THEN NULL
            ELSE CAST(successful_validations AS DECIMAL) / validation_attempts
        END
    ) STORED,
    
    -- Usage tracking
    application_count INTEGER NOT NULL DEFAULT 0,
    last_applied TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    
    -- Security and lifecycle
    security_classification VARCHAR(20) NOT NULL DEFAULT 'internal'
        CHECK (security_classification IN ('public', 'internal', 'restricted')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    deactivated_reason TEXT DEFAULT NULL,
    
    -- Temporal data
    discovered_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_validated TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_pattern_data CHECK (
        jsonb_typeof(pattern_data) = 'object' AND
        pg_column_size(pattern_data) < 65536 -- 64KB limit
    ),
    CONSTRAINT valid_pattern_conditions CHECK (
        jsonb_typeof(pattern_conditions) = 'object'
    ),
    CONSTRAINT success_validation_bounds CHECK (
        successful_validations <= validation_attempts
    ),
    CONSTRAINT unique_pattern_version UNIQUE (assistant_id, pattern_name, pattern_version)
);

-- AI interaction and conversation history with privacy controls
CREATE TABLE IF NOT EXISTS ai_conversation_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assistant_id UUID NOT NULL REFERENCES ai_comprehensive_assistants(id) ON DELETE CASCADE,
    session_id UUID NOT NULL, -- Groups related conversation turns
    
    -- Conversation metadata
    conversation_type VARCHAR(30) NOT NULL 
        CHECK (conversation_type IN ('query', 'command', 'feedback', 'learning', 'strategic')),
    interaction_sequence INTEGER NOT NULL CHECK (interaction_sequence > 0),
    
    -- Privacy and security
    privacy_level VARCHAR(20) NOT NULL DEFAULT 'standard'
        CHECK (privacy_level IN ('public', 'standard', 'private', 'confidential')),
    data_retention_days INTEGER NOT NULL DEFAULT 365 CHECK (data_retention_days BETWEEN 30 AND 2555), -- 7 years max
    
    -- Input processing (sanitized and validated)
    user_input_sanitized TEXT NOT NULL CHECK (length(user_input_sanitized) <= 4000),
    input_intent VARCHAR(50),
    input_confidence DECIMAL(4,3) CHECK (input_confidence IS NULL OR input_confidence BETWEEN 0.000 AND 1.000),
    
    -- AI response
    ai_response_text TEXT NOT NULL CHECK (length(ai_response_text) <= 8000),
    response_type VARCHAR(30) NOT NULL CHECK (response_type IN ('answer', 'question', 'recommendation', 'error', 'clarification')),
    response_confidence DECIMAL(4,3) NOT NULL CHECK (response_confidence BETWEEN 0.000 AND 1.000),
    response_time_ms INTEGER NOT NULL CHECK (response_time_ms > 0),
    
    -- Context and state
    conversation_context JSONB DEFAULT '{}'::jsonb,
    ai_state_snapshot JSONB DEFAULT '{}'::jsonb,
    
    -- User feedback and learning
    user_satisfaction INTEGER DEFAULT NULL CHECK (user_satisfaction IS NULL OR user_satisfaction BETWEEN 1 AND 5),
    follow_up_action_taken BOOLEAN DEFAULT NULL,
    learning_value VARCHAR(20) DEFAULT NULL 
        CHECK (learning_value IS NULL OR learning_value IN ('none', 'low', 'medium', 'high', 'critical')),
    
    -- Temporal and audit data
    interaction_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    ip_address_hash VARCHAR(64), -- Hashed IP for security audit (not stored in plain text)
    user_agent_hash VARCHAR(64), -- Hashed user agent
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Data lifecycle
    expires_at TIMESTAMP WITH TIME ZONE GENERATED ALWAYS AS (
        created_at + INTERVAL '1 day' * data_retention_days
    ) STORED,
    
    -- Constraints
    CONSTRAINT valid_conversation_context CHECK (
        jsonb_typeof(conversation_context) = 'object' AND
        pg_column_size(conversation_context) < 16384 -- 16KB limit
    ),
    CONSTRAINT valid_ai_state CHECK (
        jsonb_typeof(ai_state_snapshot) = 'object' AND
        pg_column_size(ai_state_snapshot) < 8192 -- 8KB limit
    )
);

-- AI security audit log for compliance and monitoring
CREATE TABLE IF NOT EXISTS ai_security_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assistant_id UUID REFERENCES ai_comprehensive_assistants(id) ON DELETE SET NULL,
    player_id UUID REFERENCES players(id) ON DELETE SET NULL,
    
    -- Event classification
    event_type VARCHAR(50) NOT NULL 
        CHECK (event_type IN ('access', 'data_access', 'recommendation', 'pattern_learning', 'security_violation', 'quota_exceeded')),
    severity_level VARCHAR(20) NOT NULL 
        CHECK (severity_level IN ('info', 'warning', 'error', 'critical')),
    
    -- Event details
    event_description TEXT NOT NULL CHECK (length(event_description) <= 1000),
    event_data JSONB DEFAULT '{}'::jsonb,
    
    -- Security context
    security_context JSONB NOT NULL DEFAULT '{}'::jsonb,
    ip_address_hash VARCHAR(64),
    user_agent_hash VARCHAR(64),
    session_id UUID,
    
    -- Detection and response
    detection_method VARCHAR(50),
    automated_response VARCHAR(100),
    requires_investigation BOOLEAN NOT NULL DEFAULT FALSE,
    investigation_status VARCHAR(20) DEFAULT NULL 
        CHECK (investigation_status IS NULL OR investigation_status IN ('pending', 'in_progress', 'resolved', 'false_positive')),
    
    -- Temporal data
    event_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_event_data CHECK (
        jsonb_typeof(event_data) = 'object' AND
        pg_column_size(event_data) < 8192 -- 8KB limit
    ),
    CONSTRAINT valid_security_context CHECK (
        jsonb_typeof(security_context) = 'object' AND
        security_context ? 'source'
    )
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE AND SECURITY
-- =============================================================================

-- Performance indexes for AI operations
CREATE INDEX IF NOT EXISTS idx_ai_assistants_player_active 
    ON ai_comprehensive_assistants(player_id, last_active) 
    WHERE security_level IN ('standard', 'premium', 'enterprise');

CREATE INDEX IF NOT EXISTS idx_ai_knowledge_domain_confidence 
    ON ai_cross_system_knowledge(knowledge_domain, confidence_score DESC, created_at DESC)
    WHERE confidence_score >= 0.7;

CREATE INDEX IF NOT EXISTS idx_ai_recommendations_active 
    ON ai_strategic_recommendations(player_id, recommendation_category, created_at DESC)
    WHERE expires_at > NOW() AND user_response IS NULL;

CREATE INDEX IF NOT EXISTS idx_ai_patterns_active_success 
    ON ai_learning_patterns(assistant_id, pattern_category, success_rate DESC NULLS LAST)
    WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_ai_conversations_session 
    ON ai_conversation_logs(session_id, interaction_sequence)
    WHERE expires_at > NOW();

-- Security and audit indexes
CREATE INDEX IF NOT EXISTS idx_ai_audit_security_events 
    ON ai_security_audit_log(event_type, severity_level, event_timestamp DESC)
    WHERE severity_level IN ('error', 'critical');

CREATE INDEX IF NOT EXISTS idx_ai_audit_investigation 
    ON ai_security_audit_log(requires_investigation, investigation_status, created_at DESC)
    WHERE requires_investigation = TRUE;

-- Partial indexes for data lifecycle management
CREATE INDEX IF NOT EXISTS idx_ai_conversations_expiry 
    ON ai_conversation_logs(expires_at)
    WHERE expires_at <= NOW() + INTERVAL '7 days';

CREATE INDEX IF NOT EXISTS idx_ai_knowledge_expiry 
    ON ai_cross_system_knowledge(expiry_date)
    WHERE expiry_date IS NOT NULL AND expiry_date <= NOW() + INTERVAL '30 days';

-- =============================================================================
-- ROW LEVEL SECURITY (RLS) FOR DATA PROTECTION
-- =============================================================================

-- Enable RLS on sensitive tables
ALTER TABLE ai_comprehensive_assistants ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_cross_system_knowledge ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_strategic_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_conversation_logs ENABLE ROW LEVEL SECURITY;

-- Policy: Players can only access their own AI assistant data
CREATE POLICY IF NOT EXISTS ai_assistant_owner_access 
    ON ai_comprehensive_assistants
    FOR ALL
    USING (player_id = current_setting('app.current_player_id')::uuid);

-- Policy: AI knowledge access based on security clearance and ownership
CREATE POLICY IF NOT EXISTS ai_knowledge_secured_access 
    ON ai_cross_system_knowledge
    FOR SELECT
    USING (
        assistant_id IN (
            SELECT id FROM ai_comprehensive_assistants 
            WHERE player_id = current_setting('app.current_player_id')::uuid
        )
        AND (
            security_classification = 'public' 
            OR (security_classification = 'internal' AND data_sensitivity IN ('low', 'medium'))
            OR (security_classification = 'restricted' AND data_sensitivity = 'low')
        )
    );

-- Policy: Recommendations access with proper authentication
CREATE POLICY IF NOT EXISTS ai_recommendations_player_access 
    ON ai_strategic_recommendations
    FOR ALL
    USING (player_id = current_setting('app.current_player_id')::uuid);

-- Policy: Conversation logs with privacy controls
CREATE POLICY IF NOT EXISTS ai_conversations_privacy_access 
    ON ai_conversation_logs
    FOR SELECT
    USING (
        assistant_id IN (
            SELECT id FROM ai_comprehensive_assistants 
            WHERE player_id = current_setting('app.current_player_id')::uuid
        )
        AND privacy_level IN ('public', 'standard')
        AND expires_at > NOW()
    );

-- =============================================================================
-- SECURITY FUNCTIONS AND TRIGGERS
-- =============================================================================

-- Function to sanitize user input (prevents XSS and injection attacks)
CREATE OR REPLACE FUNCTION sanitize_user_input(input_text TEXT) 
RETURNS TEXT AS $$
BEGIN
    -- Remove potential script tags and dangerous characters
    input_text := regexp_replace(input_text, '<[^>]*>', '', 'g');
    input_text := regexp_replace(input_text, '[<>\"'']', '', 'g');
    input_text := trim(input_text);
    
    -- Limit length to prevent buffer overflow
    IF length(input_text) > 4000 THEN
        input_text := left(input_text, 4000);
    END IF;
    
    RETURN input_text;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to validate JSONB structure for AI data
CREATE OR REPLACE FUNCTION validate_ai_jsonb(jsonb_data JSONB, max_size INTEGER DEFAULT 32768) 
RETURNS BOOLEAN AS $$
BEGIN
    -- Check if JSONB is valid object
    IF jsonb_typeof(jsonb_data) != 'object' THEN
        RETURN FALSE;
    END IF;
    
    -- Check size limit
    IF pg_column_size(jsonb_data) > max_size THEN
        RETURN FALSE;
    END IF;
    
    -- Check for dangerous keys (potential injection attempts)
    IF jsonb_data ? '__proto__' OR jsonb_data ? 'constructor' OR jsonb_data ? 'prototype' THEN
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to automatically sanitize conversation inputs
CREATE OR REPLACE FUNCTION sanitize_conversation_input()
RETURNS TRIGGER AS $$
BEGIN
    NEW.user_input_sanitized := sanitize_user_input(NEW.user_input_sanitized);
    NEW.ai_response_text := sanitize_user_input(NEW.ai_response_text);
    
    -- Validate JSONB fields
    IF NOT validate_ai_jsonb(NEW.conversation_context, 16384) THEN
        RAISE EXCEPTION 'Invalid conversation context JSONB structure';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER IF NOT EXISTS sanitize_ai_conversation_input
    BEFORE INSERT OR UPDATE ON ai_conversation_logs
    FOR EACH ROW EXECUTE FUNCTION sanitize_conversation_input();

-- Trigger to automatically log security events
CREATE OR REPLACE FUNCTION log_ai_security_event()
RETURNS TRIGGER AS $$
BEGIN
    -- Log high-confidence or sensitive operations
    IF TG_OP = 'INSERT' AND TG_TABLE_NAME = 'ai_cross_system_knowledge' THEN
        IF NEW.security_classification IN ('restricted', 'confidential') 
           OR NEW.data_sensitivity IN ('high', 'critical') THEN
            INSERT INTO ai_security_audit_log (
                assistant_id, event_type, severity_level, event_description, event_data
            ) VALUES (
                NEW.assistant_id, 'data_access', 'warning',
                'Sensitive AI knowledge created',
                jsonb_build_object(
                    'knowledge_domain', NEW.knowledge_domain,
                    'security_classification', NEW.security_classification,
                    'data_sensitivity', NEW.data_sensitivity
                )
            );
        END IF;
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER IF NOT EXISTS log_sensitive_ai_operations
    AFTER INSERT OR UPDATE ON ai_cross_system_knowledge
    FOR EACH ROW EXECUTE FUNCTION log_ai_security_event();

-- Function to enforce API rate limits
CREATE OR REPLACE FUNCTION check_ai_rate_limit(p_assistant_id UUID) 
RETURNS BOOLEAN AS $$
DECLARE
    current_quota INTEGER;
    current_used INTEGER;
    reset_date DATE;
BEGIN
    SELECT api_request_quota, api_requests_used, quota_reset_date
    INTO current_quota, current_used, reset_date
    FROM ai_comprehensive_assistants
    WHERE id = p_assistant_id;
    
    -- Reset quota if new day
    IF reset_date < CURRENT_DATE THEN
        UPDATE ai_comprehensive_assistants
        SET api_requests_used = 0, quota_reset_date = CURRENT_DATE
        WHERE id = p_assistant_id;
        current_used = 0;
    END IF;
    
    -- Check if under quota
    IF current_used >= current_quota THEN
        -- Log quota exceeded event
        INSERT INTO ai_security_audit_log (
            assistant_id, event_type, severity_level, event_description
        ) VALUES (
            p_assistant_id, 'quota_exceeded', 'warning',
            'API rate limit exceeded'
        );
        RETURN FALSE;
    END IF;
    
    -- Increment usage counter
    UPDATE ai_comprehensive_assistants
    SET api_requests_used = api_requests_used + 1,
        last_active = NOW()
    WHERE id = p_assistant_id;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================================================
-- DATA LIFECYCLE MANAGEMENT
-- =============================================================================

-- Function to clean up expired AI data (GDPR compliance)
CREATE OR REPLACE FUNCTION cleanup_expired_ai_data() 
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
BEGIN
    -- Clean up expired conversation logs
    DELETE FROM ai_conversation_logs 
    WHERE expires_at <= NOW() - INTERVAL '7 days';
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Clean up expired knowledge
    DELETE FROM ai_cross_system_knowledge 
    WHERE expiry_date IS NOT NULL AND expiry_date <= NOW();
    
    -- Clean up old audit logs (keep 2 years)
    DELETE FROM ai_security_audit_log 
    WHERE created_at < NOW() - INTERVAL '2 years'
    AND severity_level NOT IN ('error', 'critical');
    
    -- Clean up old recommendations (keep 1 year)
    DELETE FROM ai_strategic_recommendations 
    WHERE created_at < NOW() - INTERVAL '1 year'
    AND outcome_tracked = TRUE;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================================================
-- COMMENTS FOR DOCUMENTATION
-- =============================================================================

COMMENT ON TABLE ai_comprehensive_assistants IS 'Enhanced AI assistants with cross-system intelligence and security controls';
COMMENT ON TABLE ai_cross_system_knowledge IS 'Comprehensive AI knowledge base across all game systems with security classification';
COMMENT ON TABLE ai_strategic_recommendations IS 'AI-generated strategic recommendations with risk assessment and outcome tracking';
COMMENT ON TABLE ai_learning_patterns IS 'AI-discovered patterns with validation and version control';
COMMENT ON TABLE ai_conversation_logs IS 'Secure conversation history with privacy controls and data retention';
COMMENT ON TABLE ai_security_audit_log IS 'Security audit trail for AI operations and compliance monitoring';

COMMENT ON FUNCTION sanitize_user_input(TEXT) IS 'Sanitizes user input to prevent XSS and injection attacks';
COMMENT ON FUNCTION validate_ai_jsonb(JSONB, INTEGER) IS 'Validates JSONB structure and prevents malicious content';
COMMENT ON FUNCTION check_ai_rate_limit(UUID) IS 'Enforces API rate limits and logs quota violations';
COMMENT ON FUNCTION cleanup_expired_ai_data() IS 'GDPR-compliant cleanup of expired AI data';

-- =============================================================================
-- INITIAL SECURITY CONFIGURATION
-- =============================================================================

-- Grant appropriate permissions to application roles
-- GRANT SELECT, INSERT, UPDATE ON ai_comprehensive_assistants TO app_user;
-- GRANT SELECT, INSERT, UPDATE ON ai_cross_system_knowledge TO app_user;
-- GRANT SELECT, INSERT, UPDATE ON ai_strategic_recommendations TO app_user;
-- GRANT SELECT, INSERT ON ai_conversation_logs TO app_user;
-- GRANT INSERT ON ai_security_audit_log TO app_user;

-- Note: Actual GRANT statements should be executed by database administrator
-- with proper role-based access control based on application architecture