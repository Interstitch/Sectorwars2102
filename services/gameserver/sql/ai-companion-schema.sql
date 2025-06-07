-- AI Companion System Database Schema
-- Personal AI Assistant for each player with learning capabilities

-- Personal AI Assistant metadata
CREATE TABLE personal_ai_assistants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL DEFAULT 'Navigator',
    personality VARCHAR(20) NOT NULL DEFAULT 'analytical' CHECK (personality IN ('analytical', 'friendly', 'tactical', 'cautious')),
    learning_style VARCHAR(20) NOT NULL DEFAULT 'observational' CHECK (learning_style IN ('observational', 'interactive', 'predictive')),
    created_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP DEFAULT NOW(),
    total_interactions INTEGER DEFAULT 0,
    learning_sessions INTEGER DEFAULT 0,
    UNIQUE(player_id)
);

-- Sector knowledge learned by AI
CREATE TABLE ai_sector_knowledge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assistant_id UUID NOT NULL REFERENCES personal_ai_assistants(id) ON DELETE CASCADE,
    sector_id UUID NOT NULL REFERENCES sectors(id) ON DELETE CASCADE,
    visits_count INTEGER DEFAULT 1,
    first_visit TIMESTAMP DEFAULT NOW(),
    last_visit TIMESTAMP DEFAULT NOW(),
    
    -- Mine detection and hazards
    known_mines JSONB DEFAULT '[]'::jsonb, -- Array of mine positions
    hazard_level VARCHAR(10) DEFAULT 'unknown' CHECK (hazard_level IN ('safe', 'low', 'medium', 'high', 'extreme', 'unknown')),
    patrol_patterns JSONB DEFAULT '{}'::jsonb, -- NPC ship movement patterns
    
    -- Resource and economic data
    resource_availability JSONB DEFAULT '{}'::jsonb, -- Planet and asteroid scan results
    traffic_patterns JSONB DEFAULT '{}'::jsonb, -- Player activity observations
    strategic_value INTEGER DEFAULT 0, -- 1-10 rating of sector importance
    
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(assistant_id, sector_id)
);

-- Trading intelligence gathered by AI
CREATE TABLE ai_trading_intelligence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assistant_id UUID NOT NULL REFERENCES personal_ai_assistants(id) ON DELETE CASCADE,
    port_id UUID NOT NULL REFERENCES ports(id) ON DELETE CASCADE,
    
    -- Price tracking
    commodity_type VARCHAR(50) NOT NULL,
    price_history JSONB DEFAULT '[]'::jsonb, -- Array of {timestamp, price, quantity_available}
    supply_patterns JSONB DEFAULT '{}'::jsonb, -- Availability cycle analysis
    last_price_check INTEGER,
    last_quantity_available INTEGER,
    
    -- Profitability analysis
    best_profit_margins JSONB DEFAULT '[]'::jsonb, -- Historical arbitrage opportunities
    trade_route_performance JSONB DEFAULT '{}'::jsonb, -- Success rates for routes from this port
    competition_analysis JSONB DEFAULT '{}'::jsonb, -- Other trader behavior observations
    
    -- Market predictions
    predicted_price_trend VARCHAR(10) DEFAULT 'stable' CHECK (predicted_price_trend IN ('rising', 'falling', 'stable', 'volatile')),
    confidence_level DECIMAL(3,2) DEFAULT 0.5, -- 0.0 to 1.0
    
    first_observed TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP DEFAULT NOW(),
    observation_count INTEGER DEFAULT 1,
    UNIQUE(assistant_id, port_id, commodity_type)
);

-- Combat experience and tactical knowledge
CREATE TABLE ai_combat_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assistant_id UUID NOT NULL REFERENCES personal_ai_assistants(id) ON DELETE CASCADE,
    combat_id UUID, -- Reference to combat logs if available
    
    -- Battle context
    sector_id UUID REFERENCES sectors(id),
    battle_type VARCHAR(20) NOT NULL, -- 'player_vs_player', 'player_vs_npc', 'fleet_battle'
    player_role VARCHAR(20) NOT NULL, -- 'attacker', 'defender', 'support'
    outcome VARCHAR(10) NOT NULL CHECK (outcome IN ('victory', 'defeat', 'retreat', 'draw')),
    
    -- Tactical analysis
    effective_loadouts JSONB DEFAULT '[]'::jsonb, -- Weapon/ship combinations that worked
    failed_tactics JSONB DEFAULT '[]'::jsonb, -- Strategies that didn't work
    enemy_behavior JSONB DEFAULT '{}'::jsonb, -- Opponent pattern recognition
    escape_routes JSONB DEFAULT '[]'::jsonb, -- Successful retreat paths
    
    -- Performance metrics
    damage_dealt INTEGER DEFAULT 0,
    damage_received INTEGER DEFAULT 0,
    units_lost INTEGER DEFAULT 0,
    units_destroyed INTEGER DEFAULT 0,
    tactical_score DECIMAL(3,1) DEFAULT 5.0, -- 1.0 to 10.0 performance rating
    
    battle_timestamp TIMESTAMP DEFAULT NOW(),
    analysis_confidence DECIMAL(3,2) DEFAULT 0.5
);

-- Player relationship and social intelligence
CREATE TABLE ai_player_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assistant_id UUID NOT NULL REFERENCES personal_ai_assistants(id) ON DELETE CASCADE,
    target_player_id UUID NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    
    -- Relationship metrics
    interaction_count INTEGER DEFAULT 1,
    trust_level DECIMAL(3,2) DEFAULT 0.5, -- 0.0 to 1.0 (hostile to trusted ally)
    reliability_score DECIMAL(3,2) DEFAULT 0.5, -- How reliable this player is
    threat_assessment VARCHAR(10) DEFAULT 'neutral' CHECK (threat_assessment IN ('ally', 'neutral', 'competitor', 'hostile', 'dangerous')),
    
    -- Behavioral analysis
    trading_patterns JSONB DEFAULT '{}'::jsonb, -- Trading behavior observations
    combat_style JSONB DEFAULT '{}'::jsonb, -- Fighting style and preferences
    active_hours JSONB DEFAULT '[]'::jsonb, -- When this player is typically online
    communication_style JSONB DEFAULT '{}'::jsonb, -- How they communicate
    
    -- Historical interactions
    last_interaction TIMESTAMP DEFAULT NOW(),
    interaction_history JSONB DEFAULT '[]'::jsonb, -- Array of interaction summaries
    reputation_notes TEXT, -- AI's notes about this player
    
    first_met TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP DEFAULT NOW(),
    UNIQUE(assistant_id, target_player_id)
);

-- AI conversation history and context
CREATE TABLE ai_conversation_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assistant_id UUID NOT NULL REFERENCES personal_ai_assistants(id) ON DELETE CASCADE,
    
    -- Conversation metadata
    conversation_type VARCHAR(20) NOT NULL, -- 'query', 'command', 'casual', 'emergency'
    player_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    
    -- Context tracking
    game_context JSONB DEFAULT '{}'::jsonb, -- Current game state when message sent
    intent_recognized VARCHAR(50), -- What the AI thought the player wanted
    confidence_level DECIMAL(3,2) DEFAULT 0.5,
    response_time_ms INTEGER, -- How long AI took to respond
    
    -- Learning feedback
    player_satisfaction VARCHAR(10), -- 'helpful', 'neutral', 'unhelpful' if provided
    follow_up_actions JSONB DEFAULT '[]'::jsonb, -- Actions taken after this conversation
    
    timestamp TIMESTAMP DEFAULT NOW()
);

-- AI learning patterns and insights
CREATE TABLE ai_learning_patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assistant_id UUID NOT NULL REFERENCES personal_ai_assistants(id) ON DELETE CASCADE,
    
    -- Pattern metadata
    pattern_type VARCHAR(30) NOT NULL, -- 'trade_route', 'combat_tactic', 'exploration_preference', etc.
    pattern_name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Pattern data
    pattern_data JSONB NOT NULL, -- The actual pattern learned
    confidence_score DECIMAL(3,2) DEFAULT 0.5,
    success_rate DECIMAL(3,2), -- How often this pattern leads to success
    usage_count INTEGER DEFAULT 0, -- How often this pattern has been applied
    
    -- Validation
    validated BOOLEAN DEFAULT FALSE,
    validation_tests INTEGER DEFAULT 0,
    last_validation TIMESTAMP,
    
    discovered_at TIMESTAMP DEFAULT NOW(),
    last_used TIMESTAMP,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- AI query cache for performance
CREATE TABLE ai_query_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assistant_id UUID NOT NULL REFERENCES personal_ai_assistants(id) ON DELETE CASCADE,
    
    -- Query identification
    query_hash CHAR(64) NOT NULL, -- SHA256 hash of normalized query
    query_text TEXT NOT NULL,
    query_type VARCHAR(30) NOT NULL,
    
    -- Cached response
    response_data JSONB NOT NULL,
    computation_time_ms INTEGER,
    data_freshness TIMESTAMP DEFAULT NOW(), -- When underlying data was last updated
    
    -- Cache management
    hit_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '1 hour'),
    
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(assistant_id, query_hash)
);

-- Indexes for performance
CREATE INDEX idx_ai_assistants_player_id ON personal_ai_assistants(player_id);
CREATE INDEX idx_ai_assistants_last_active ON personal_ai_assistants(last_active);

CREATE INDEX idx_sector_knowledge_assistant_sector ON ai_sector_knowledge(assistant_id, sector_id);
CREATE INDEX idx_sector_knowledge_last_visit ON ai_sector_knowledge(last_visit);
CREATE INDEX idx_sector_knowledge_hazard_level ON ai_sector_knowledge(hazard_level);

CREATE INDEX idx_trading_intel_assistant_port ON ai_trading_intelligence(assistant_id, port_id);
CREATE INDEX idx_trading_intel_commodity ON ai_trading_intelligence(commodity_type);
CREATE INDEX idx_trading_intel_last_updated ON ai_trading_intelligence(last_updated);

CREATE INDEX idx_combat_memory_assistant ON ai_combat_memory(assistant_id);
CREATE INDEX idx_combat_memory_timestamp ON ai_combat_memory(battle_timestamp);
CREATE INDEX idx_combat_memory_outcome ON ai_combat_memory(outcome);

CREATE INDEX idx_player_relationships_assistant ON ai_player_relationships(assistant_id);
CREATE INDEX idx_player_relationships_target ON ai_player_relationships(target_player_id);
CREATE INDEX idx_player_relationships_trust ON ai_player_relationships(trust_level);

CREATE INDEX idx_conversation_history_assistant ON ai_conversation_history(assistant_id);
CREATE INDEX idx_conversation_history_timestamp ON ai_conversation_history(timestamp);
CREATE INDEX idx_conversation_history_type ON ai_conversation_history(conversation_type);

CREATE INDEX idx_learning_patterns_assistant ON ai_learning_patterns(assistant_id);
CREATE INDEX idx_learning_patterns_type ON ai_learning_patterns(pattern_type);
CREATE INDEX idx_learning_patterns_confidence ON ai_learning_patterns(confidence_score);

CREATE INDEX idx_query_cache_assistant_hash ON ai_query_cache(assistant_id, query_hash);
CREATE INDEX idx_query_cache_expires ON ai_query_cache(expires_at);
CREATE INDEX idx_query_cache_last_accessed ON ai_query_cache(last_accessed);

-- Views for common queries
CREATE VIEW ai_assistant_summary AS
SELECT 
    a.id,
    a.player_id,
    a.name,
    a.personality,
    a.learning_style,
    a.total_interactions,
    a.learning_sessions,
    
    -- Knowledge statistics
    COALESCE(sk.sectors_known, 0) as sectors_known,
    COALESCE(ti.ports_tracked, 0) as ports_tracked,
    COALESCE(cm.battles_analyzed, 0) as battles_analyzed,
    COALESCE(pr.relationships_tracked, 0) as relationships_tracked,
    COALESCE(lp.patterns_learned, 0) as patterns_learned,
    
    -- Recent activity
    a.last_active,
    COALESCE(ch.recent_conversations, 0) as conversations_last_24h
    
FROM personal_ai_assistants a
LEFT JOIN (
    SELECT assistant_id, COUNT(*) as sectors_known 
    FROM ai_sector_knowledge 
    GROUP BY assistant_id
) sk ON a.id = sk.assistant_id
LEFT JOIN (
    SELECT assistant_id, COUNT(*) as ports_tracked 
    FROM ai_trading_intelligence 
    GROUP BY assistant_id
) ti ON a.id = ti.assistant_id
LEFT JOIN (
    SELECT assistant_id, COUNT(*) as battles_analyzed 
    FROM ai_combat_memory 
    GROUP BY assistant_id
) cm ON a.id = cm.assistant_id
LEFT JOIN (
    SELECT assistant_id, COUNT(*) as relationships_tracked 
    FROM ai_player_relationships 
    GROUP BY assistant_id
) pr ON a.id = pr.assistant_id
LEFT JOIN (
    SELECT assistant_id, COUNT(*) as patterns_learned 
    FROM ai_learning_patterns 
    WHERE validated = TRUE
    GROUP BY assistant_id
) lp ON a.id = lp.assistant_id
LEFT JOIN (
    SELECT assistant_id, COUNT(*) as recent_conversations 
    FROM ai_conversation_history 
    WHERE timestamp > NOW() - INTERVAL '24 hours'
    GROUP BY assistant_id
) ch ON a.id = ch.assistant_id;

-- Functions for AI operations

-- Function to initialize a new AI assistant for a player
CREATE OR REPLACE FUNCTION create_ai_assistant(
    p_player_id UUID,
    p_name VARCHAR(50) DEFAULT 'Navigator',
    p_personality VARCHAR(20) DEFAULT 'analytical'
) RETURNS UUID AS $$
DECLARE
    assistant_id UUID;
BEGIN
    INSERT INTO personal_ai_assistants (player_id, name, personality)
    VALUES (p_player_id, p_name, p_personality)
    RETURNING id INTO assistant_id;
    
    RETURN assistant_id;
END;
$$ LANGUAGE plpgsql;

-- Function to record AI learning from player action
CREATE OR REPLACE FUNCTION record_ai_learning(
    p_assistant_id UUID,
    p_action_type VARCHAR(30),
    p_action_data JSONB
) RETURNS VOID AS $$
BEGIN
    -- Update interaction count
    UPDATE personal_ai_assistants 
    SET total_interactions = total_interactions + 1,
        last_active = NOW()
    WHERE id = p_assistant_id;
    
    -- Process different types of learning
    CASE p_action_type
        WHEN 'sector_entry' THEN
            INSERT INTO ai_sector_knowledge (assistant_id, sector_id)
            VALUES (p_assistant_id, (p_action_data->>'sector_id')::UUID)
            ON CONFLICT (assistant_id, sector_id) DO UPDATE SET
                visits_count = ai_sector_knowledge.visits_count + 1,
                last_visit = NOW();
                
        WHEN 'port_docking' THEN
            INSERT INTO ai_trading_intelligence (assistant_id, port_id, commodity_type, last_price_check)
            VALUES (
                p_assistant_id,
                (p_action_data->>'port_id')::UUID,
                p_action_data->>'commodity_type',
                (p_action_data->>'price')::INTEGER
            )
            ON CONFLICT (assistant_id, port_id, commodity_type) DO UPDATE SET
                last_price_check = (p_action_data->>'price')::INTEGER,
                last_updated = NOW(),
                observation_count = ai_trading_intelligence.observation_count + 1;
                
        WHEN 'combat_result' THEN
            INSERT INTO ai_combat_memory (
                assistant_id, sector_id, battle_type, player_role, outcome,
                damage_dealt, damage_received, units_lost, units_destroyed
            ) VALUES (
                p_assistant_id,
                (p_action_data->>'sector_id')::UUID,
                p_action_data->>'battle_type',
                p_action_data->>'player_role',
                p_action_data->>'outcome',
                (p_action_data->>'damage_dealt')::INTEGER,
                (p_action_data->>'damage_received')::INTEGER,
                (p_action_data->>'units_lost')::INTEGER,
                (p_action_data->>'units_destroyed')::INTEGER
            );
    END CASE;
END;
$$ LANGUAGE plpgsql;

-- Function to get AI insights for natural language queries
CREATE OR REPLACE FUNCTION get_ai_insights(
    p_assistant_id UUID,
    p_query_type VARCHAR(30),
    p_context JSONB DEFAULT '{}'::jsonb
) RETURNS JSONB AS $$
DECLARE
    result JSONB := '{}';
BEGIN
    CASE p_query_type
        WHEN 'best_trade_route' THEN
            -- Analyze trading intelligence for best current opportunities
            result := (
                SELECT jsonb_build_object(
                    'recommendations', jsonb_agg(
                        jsonb_build_object(
                            'port_id', port_id,
                            'commodity', commodity_type,
                            'last_price', last_price_check,
                            'confidence', confidence_level
                        )
                    )
                )
                FROM ai_trading_intelligence
                WHERE assistant_id = p_assistant_id
                  AND confidence_level > 0.7
                ORDER BY confidence_level DESC
                LIMIT 5
            );
            
        WHEN 'sector_safety' THEN
            -- Assess sector danger levels
            result := (
                SELECT jsonb_build_object(
                    'safety_assessment', jsonb_agg(
                        jsonb_build_object(
                            'sector_id', sector_id,
                            'hazard_level', hazard_level,
                            'visits', visits_count,
                            'last_visit', last_visit
                        )
                    )
                )
                FROM ai_sector_knowledge
                WHERE assistant_id = p_assistant_id
                ORDER BY hazard_level DESC, visits_count DESC
                LIMIT 10
            );
            
        WHEN 'player_relationships' THEN
            -- Provide social intelligence
            result := (
                SELECT jsonb_build_object(
                    'relationships', jsonb_agg(
                        jsonb_build_object(
                            'player_id', target_player_id,
                            'trust_level', trust_level,
                            'threat_assessment', threat_assessment,
                            'interactions', interaction_count
                        )
                    )
                )
                FROM ai_player_relationships
                WHERE assistant_id = p_assistant_id
                ORDER BY trust_level DESC, interaction_count DESC
                LIMIT 20
            );
    END CASE;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Clean up old AI data (run periodically)
CREATE OR REPLACE FUNCTION cleanup_ai_data() RETURNS VOID AS $$
BEGIN
    -- Remove old conversation history (keep last 1000 per assistant)
    DELETE FROM ai_conversation_history
    WHERE id NOT IN (
        SELECT id FROM (
            SELECT id, ROW_NUMBER() OVER (
                PARTITION BY assistant_id ORDER BY timestamp DESC
            ) as rn
            FROM ai_conversation_history
        ) ranked
        WHERE rn <= 1000
    );
    
    -- Remove expired query cache
    DELETE FROM ai_query_cache WHERE expires_at < NOW();
    
    -- Clean up old cache entries (keep most recent 100 per assistant)
    DELETE FROM ai_query_cache
    WHERE id NOT IN (
        SELECT id FROM (
            SELECT id, ROW_NUMBER() OVER (
                PARTITION BY assistant_id ORDER BY last_accessed DESC
            ) as rn
            FROM ai_query_cache
        ) ranked
        WHERE rn <= 100
    );
END;
$$ LANGUAGE plpgsql;

COMMENT ON TABLE personal_ai_assistants IS 'Core AI assistant metadata for each player';
COMMENT ON TABLE ai_sector_knowledge IS 'AI learning about sectors, hazards, and strategic value';
COMMENT ON TABLE ai_trading_intelligence IS 'AI market knowledge and trading pattern analysis';
COMMENT ON TABLE ai_combat_memory IS 'AI tactical learning from combat experiences';
COMMENT ON TABLE ai_player_relationships IS 'AI social intelligence about other players';
COMMENT ON TABLE ai_conversation_history IS 'Natural language conversation logs with context';
COMMENT ON TABLE ai_learning_patterns IS 'Discovered behavioral patterns and strategies';
COMMENT ON TABLE ai_query_cache IS 'Performance cache for complex AI queries';