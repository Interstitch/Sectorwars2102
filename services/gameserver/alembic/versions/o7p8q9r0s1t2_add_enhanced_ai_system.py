"""add enhanced ai system

Revision ID: o7p8q9r0s1t2
Revises: n5o6p7q8r9s0
Create Date: 2025-06-07 23:40:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'o7p8q9r0s1t2'
down_revision = '63320a1ec07e'
branch_labels = None
depends_on = None


def upgrade():
    # Extend existing ai_market_predictions
    op.add_column('ai_market_predictions', sa.Column('cross_system_impact', postgresql.JSONB(astext_type=sa.Text()), nullable=True, default={}))
    op.add_column('ai_market_predictions', sa.Column('security_classification', sa.String(20), nullable=True, default='internal'))
    op.add_column('ai_market_predictions', sa.Column('data_retention_date', sa.DateTime(timezone=True), nullable=True))
    
    # Extend existing player_trading_profiles
    op.add_column('player_trading_profiles', sa.Column('strategic_preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=True, default={}))
    op.add_column('player_trading_profiles', sa.Column('multi_system_performance', postgresql.JSONB(astext_type=sa.Text()), nullable=True, default={}))
    op.add_column('player_trading_profiles', sa.Column('ai_trust_level', sa.Numeric(3, 2), nullable=True, default=0.5))
    op.add_column('player_trading_profiles', sa.Column('security_clearance', sa.String(20), nullable=True, default='standard'))

    # Create ai_comprehensive_assistants table
    op.create_table('ai_comprehensive_assistants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('players.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('assistant_name', sa.String(50), nullable=False, default='ARIA'),
        sa.Column('personality_type', sa.String(20), nullable=False, default='analytical'),
        sa.Column('learning_mode', sa.String(20), nullable=False, default='balanced'),
        sa.Column('security_level', sa.String(20), nullable=False, default='standard'),
        sa.Column('encryption_key_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('access_permissions', postgresql.JSONB(astext_type=sa.Text()), nullable=False, default={"trading": True, "combat": False, "colony": False, "port": False}),
        sa.Column('api_request_quota', sa.Integer(), nullable=False, default=1000),
        sa.Column('api_requests_used', sa.Integer(), nullable=False, default=0),
        sa.Column('quota_reset_date', sa.Date(), nullable=False, server_default=sa.text('CURRENT_DATE')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('last_active', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('total_interactions', sa.BigInteger(), nullable=False, default=0),
        sa.Column('learning_sessions', sa.Integer(), nullable=False, default=0),
        sa.CheckConstraint("personality_type IN ('analytical', 'friendly', 'tactical', 'cautious', 'adaptive')", name='valid_personality_type'),
        sa.CheckConstraint("learning_mode IN ('conservative', 'balanced', 'aggressive', 'custom')", name='valid_learning_mode'),
        sa.CheckConstraint("security_level IN ('basic', 'standard', 'premium', 'enterprise')", name='valid_security_level'),
        sa.CheckConstraint("api_request_quota BETWEEN 100 AND 10000 AND api_requests_used BETWEEN 0 AND api_request_quota", name='quota_bounds'),
        sa.CheckConstraint("total_interactions >= 0 AND learning_sessions >= 0", name='positive_counters'),
    )

    # Create ai_cross_system_knowledge table
    op.create_table('ai_cross_system_knowledge',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('assistant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_comprehensive_assistants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('knowledge_domain', sa.String(30), nullable=False),
        sa.Column('knowledge_type', sa.String(50), nullable=False),
        sa.Column('knowledge_subtype', sa.String(50), nullable=True),
        sa.Column('security_classification', sa.String(20), nullable=False, default='internal'),
        sa.Column('data_sensitivity', sa.String(20), nullable=False, default='low'),
        sa.Column('knowledge_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('encrypted_knowledge', postgresql.BYTEA(), nullable=True),
        sa.Column('confidence_score', sa.Numeric(4, 3), nullable=False, default=0.500),
        sa.Column('validation_count', sa.Integer(), nullable=False, default=0),
        sa.Column('accuracy_score', sa.Numeric(4, 3), nullable=True),
        sa.Column('knowledge_timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('expiry_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_validated', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('data_source', sa.String(50), nullable=False, default='player_action'),
        sa.Column('source_metadata', postgresql.JSONB(astext_type=sa.Text()), default={}),
        sa.CheckConstraint("knowledge_domain IN ('trading', 'combat', 'colony', 'port', 'strategic', 'social')", name='valid_knowledge_domain'),
        sa.CheckConstraint("security_classification IN ('public', 'internal', 'restricted', 'confidential')", name='valid_security_classification'),
        sa.CheckConstraint("data_sensitivity IN ('low', 'medium', 'high', 'critical')", name='valid_data_sensitivity'),
        sa.CheckConstraint("confidence_score BETWEEN 0.000 AND 1.000", name='valid_confidence_score'),
        sa.CheckConstraint("accuracy_score IS NULL OR accuracy_score BETWEEN 0.000 AND 1.000", name='valid_accuracy_score'),
        sa.CheckConstraint("validation_count >= 0", name='positive_validation_count'),
    )

    # Create ai_strategic_recommendations table
    op.create_table('ai_strategic_recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('assistant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_comprehensive_assistants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('players.id', ondelete='CASCADE'), nullable=False),
        sa.Column('recommendation_category', sa.String(30), nullable=False),
        sa.Column('recommendation_type', sa.String(50), nullable=False),
        sa.Column('priority_level', sa.Integer(), nullable=False, default=3),
        sa.Column('security_clearance_required', sa.String(20), nullable=False, default='standard'),
        sa.Column('compliance_flags', postgresql.JSONB(astext_type=sa.Text()), default=[]),
        sa.Column('recommendation_title', sa.String(200), nullable=False),
        sa.Column('recommendation_summary', sa.Text(), nullable=False),
        sa.Column('detailed_analysis', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('risk_assessment', sa.String(20), nullable=False),
        sa.Column('expected_outcome', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('confidence_interval', sa.Numeric(4, 3), nullable=False),
        sa.Column('presented_to_user', sa.Boolean(), nullable=False, default=False),
        sa.Column('user_response', sa.String(20), nullable=True),
        sa.Column('user_feedback_score', sa.Integer(), nullable=True),
        sa.Column('user_feedback_text', sa.Text(), nullable=True),
        sa.Column('outcome_tracked', sa.Boolean(), nullable=False, default=False),
        sa.Column('actual_outcome', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('outcome_accuracy', sa.Numeric(4, 3), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('user_responded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('outcome_recorded_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("recommendation_category IN ('trading', 'combat', 'colony', 'port', 'strategic', 'resource')", name='valid_recommendation_category'),
        sa.CheckConstraint("priority_level BETWEEN 1 AND 5", name='valid_priority_level'),
        sa.CheckConstraint("security_clearance_required IN ('basic', 'standard', 'premium', 'enterprise')", name='valid_security_clearance'),
        sa.CheckConstraint("risk_assessment IN ('very_low', 'low', 'medium', 'high', 'very_high')", name='valid_risk_assessment'),
        sa.CheckConstraint("confidence_interval BETWEEN 0.000 AND 1.000", name='valid_confidence_interval'),
        sa.CheckConstraint("user_response IS NULL OR user_response IN ('accepted', 'rejected', 'modified', 'deferred')", name='valid_user_response'),
        sa.CheckConstraint("user_feedback_score IS NULL OR user_feedback_score BETWEEN 1 AND 5", name='valid_feedback_score'),
        sa.CheckConstraint("outcome_accuracy IS NULL OR outcome_accuracy BETWEEN 0.000 AND 1.000", name='valid_outcome_accuracy'),
        sa.CheckConstraint("expires_at > created_at", name='valid_expiry'),
    )

    # Create ai_learning_patterns table
    op.create_table('ai_learning_patterns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('assistant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_comprehensive_assistants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('pattern_category', sa.String(30), nullable=False),
        sa.Column('pattern_name', sa.String(100), nullable=False),
        sa.Column('pattern_version', sa.Integer(), nullable=False, default=1),
        sa.Column('pattern_description', sa.Text(), nullable=False),
        sa.Column('pattern_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('pattern_conditions', postgresql.JSONB(astext_type=sa.Text()), nullable=False, default={}),
        sa.Column('confidence_score', sa.Numeric(4, 3), nullable=False),
        sa.Column('validation_attempts', sa.Integer(), nullable=False, default=0),
        sa.Column('successful_validations', sa.Integer(), nullable=False, default=0),
        sa.Column('application_count', sa.Integer(), nullable=False, default=0),
        sa.Column('last_applied', sa.DateTime(timezone=True), nullable=True),
        sa.Column('security_classification', sa.String(20), nullable=False, default='internal'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('deactivated_reason', sa.Text(), nullable=True),
        sa.Column('discovered_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('last_validated', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint("pattern_category IN ('behavioral', 'market', 'tactical', 'strategic', 'social')", name='valid_pattern_category'),
        sa.CheckConstraint("pattern_version > 0", name='positive_pattern_version'),
        sa.CheckConstraint("confidence_score BETWEEN 0.000 AND 1.000", name='valid_confidence_score'),
        sa.CheckConstraint("validation_attempts >= 0", name='positive_validation_attempts'),
        sa.CheckConstraint("successful_validations <= validation_attempts", name='success_validation_bounds'),
        sa.CheckConstraint("application_count >= 0", name='positive_application_count'),
        sa.CheckConstraint("security_classification IN ('public', 'internal', 'restricted')", name='valid_security_classification'),
        sa.UniqueConstraint('assistant_id', 'pattern_name', 'pattern_version', name='unique_pattern_version'),
    )

    # Create ai_conversation_logs table
    op.create_table('ai_conversation_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('assistant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_comprehensive_assistants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_type', sa.String(30), nullable=False),
        sa.Column('interaction_sequence', sa.Integer(), nullable=False),
        sa.Column('privacy_level', sa.String(20), nullable=False, default='standard'),
        sa.Column('data_retention_days', sa.Integer(), nullable=False, default=365),
        sa.Column('user_input_sanitized', sa.Text(), nullable=False),
        sa.Column('input_intent', sa.String(50), nullable=True),
        sa.Column('input_confidence', sa.Numeric(4, 3), nullable=True),
        sa.Column('ai_response_text', sa.Text(), nullable=False),
        sa.Column('response_type', sa.String(30), nullable=False),
        sa.Column('response_confidence', sa.Numeric(4, 3), nullable=False),
        sa.Column('response_time_ms', sa.Integer(), nullable=False),
        sa.Column('conversation_context', postgresql.JSONB(astext_type=sa.Text()), default={}),
        sa.Column('ai_state_snapshot', postgresql.JSONB(astext_type=sa.Text()), default={}),
        sa.Column('user_satisfaction', sa.Integer(), nullable=True),
        sa.Column('follow_up_action_taken', sa.Boolean(), nullable=True),
        sa.Column('learning_value', sa.String(20), nullable=True),
        sa.Column('interaction_timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('ip_address_hash', sa.String(64), nullable=True),
        sa.Column('user_agent_hash', sa.String(64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint("conversation_type IN ('query', 'command', 'feedback', 'learning', 'strategic')", name='valid_conversation_type'),
        sa.CheckConstraint("interaction_sequence > 0", name='positive_interaction_sequence'),
        sa.CheckConstraint("privacy_level IN ('public', 'standard', 'private', 'confidential')", name='valid_privacy_level'),
        sa.CheckConstraint("data_retention_days BETWEEN 30 AND 2555", name='valid_retention_days'),
        sa.CheckConstraint("response_type IN ('answer', 'question', 'recommendation', 'error', 'clarification')", name='valid_response_type'),
        sa.CheckConstraint("input_confidence IS NULL OR input_confidence BETWEEN 0.000 AND 1.000", name='valid_input_confidence'),
        sa.CheckConstraint("response_confidence BETWEEN 0.000 AND 1.000", name='valid_response_confidence'),
        sa.CheckConstraint("response_time_ms > 0", name='positive_response_time'),
        sa.CheckConstraint("user_satisfaction IS NULL OR user_satisfaction BETWEEN 1 AND 5", name='valid_user_satisfaction'),
        sa.CheckConstraint("learning_value IS NULL OR learning_value IN ('none', 'low', 'medium', 'high', 'critical')", name='valid_learning_value'),
    )

    # Create ai_security_audit_log table
    op.create_table('ai_security_audit_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('assistant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ai_comprehensive_assistants.id', ondelete='SET NULL'), nullable=True),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('players.id', ondelete='SET NULL'), nullable=True),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('severity_level', sa.String(20), nullable=False),
        sa.Column('event_description', sa.Text(), nullable=False),
        sa.Column('event_data', postgresql.JSONB(astext_type=sa.Text()), default={}),
        sa.Column('security_context', postgresql.JSONB(astext_type=sa.Text()), nullable=False, default={}),
        sa.Column('ip_address_hash', sa.String(64), nullable=True),
        sa.Column('user_agent_hash', sa.String(64), nullable=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('detection_method', sa.String(50), nullable=True),
        sa.Column('automated_response', sa.String(100), nullable=True),
        sa.Column('requires_investigation', sa.Boolean(), nullable=False, default=False),
        sa.Column('investigation_status', sa.String(20), nullable=True),
        sa.Column('event_timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint("event_type IN ('access', 'data_access', 'recommendation', 'pattern_learning', 'security_violation', 'quota_exceeded')", name='valid_event_type'),
        sa.CheckConstraint("severity_level IN ('info', 'warning', 'error', 'critical')", name='valid_severity_level'),
        sa.CheckConstraint("investigation_status IS NULL OR investigation_status IN ('pending', 'in_progress', 'resolved', 'false_positive')", name='valid_investigation_status'),
    )

    # Create indexes
    op.create_index('idx_ai_assistants_player_active', 'ai_comprehensive_assistants', ['player_id', 'last_active'])
    op.create_index('idx_ai_knowledge_domain_confidence', 'ai_cross_system_knowledge', ['knowledge_domain', sa.text('confidence_score DESC'), sa.text('created_at DESC')])
    op.create_index('idx_ai_recommendations_active', 'ai_strategic_recommendations', ['player_id', 'recommendation_category', sa.text('created_at DESC')])
    op.create_index('idx_ai_patterns_active_success', 'ai_learning_patterns', ['assistant_id', 'pattern_category'])
    op.create_index('idx_ai_conversations_session', 'ai_conversation_logs', ['session_id', 'interaction_sequence'])
    op.create_index('idx_ai_audit_security_events', 'ai_security_audit_log', ['event_type', 'severity_level', sa.text('event_timestamp DESC')])
    op.create_index('idx_ai_audit_investigation', 'ai_security_audit_log', ['requires_investigation', 'investigation_status', sa.text('created_at DESC')])


def downgrade():
    # Drop tables in reverse order
    op.drop_table('ai_security_audit_log')
    op.drop_table('ai_conversation_logs')
    op.drop_table('ai_learning_patterns')
    op.drop_table('ai_strategic_recommendations')
    op.drop_table('ai_cross_system_knowledge')
    op.drop_table('ai_comprehensive_assistants')
    
    # Remove columns from existing tables
    op.drop_column('player_trading_profiles', 'security_clearance')
    op.drop_column('player_trading_profiles', 'ai_trust_level')
    op.drop_column('player_trading_profiles', 'multi_system_performance')
    op.drop_column('player_trading_profiles', 'strategic_preferences')
    
    op.drop_column('ai_market_predictions', 'data_retention_date')
    op.drop_column('ai_market_predictions', 'security_classification')
    op.drop_column('ai_market_predictions', 'cross_system_impact')