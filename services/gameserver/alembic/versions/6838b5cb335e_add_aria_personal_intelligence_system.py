"""add_aria_personal_intelligence_system

Revision ID: 6838b5cb335e
Revises: 8b9989967eb1
Create Date: 2025-06-08 03:39:11.032085

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '6838b5cb335e'
down_revision = '8b9989967eb1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create aria_personal_memories table
    op.create_table('aria_personal_memories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('players.id', ondelete='CASCADE'), nullable=False),
        sa.Column('memory_type', sa.String(50), nullable=False),
        sa.Column('importance_score', sa.Float(), nullable=False, default=0.5),
        sa.Column('confidence_level', sa.Float(), nullable=False, default=0.5),
        sa.Column('memory_content', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('memory_hash', sa.String(64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('last_accessed', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('access_count', sa.Integer(), nullable=False, default=0),
        sa.Column('decay_rate', sa.Float(), nullable=False, default=0.01),
        sa.Column('current_strength', sa.Float(), nullable=False, default=1.0),
        sa.UniqueConstraint('player_id', 'memory_hash', name='uq_player_memory_hash'),
    )
    op.create_index('idx_aria_memory_player_type', 'aria_personal_memories', ['player_id', 'memory_type'])
    op.create_index('idx_aria_memory_importance', 'aria_personal_memories', ['importance_score'])
    
    # Create aria_market_intelligence table
    op.create_table('aria_market_intelligence',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('players.id', ondelete='CASCADE'), nullable=False),
        sa.Column('port_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ports.id', ondelete='CASCADE'), nullable=True),
        sa.Column('sector_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sectors.id', ondelete='CASCADE'), nullable=False),
        sa.Column('commodity', sa.String(50), nullable=False),
        sa.Column('price_observations', postgresql.JSONB(astext_type=sa.Text()), nullable=False, default=[]),
        sa.Column('average_price', sa.Float(), nullable=True),
        sa.Column('price_volatility', sa.Float(), nullable=False, default=0.0),
        sa.Column('identified_patterns', postgresql.JSONB(astext_type=sa.Text()), nullable=False, default=[]),
        sa.Column('pattern_confidence', postgresql.JSONB(astext_type=sa.Text()), nullable=False, default={}),
        sa.Column('price_trend', sa.String(20), nullable=True),
        sa.Column('next_prediction', sa.Float(), nullable=True),
        sa.Column('prediction_confidence', sa.Float(), nullable=False, default=0.0),
        sa.Column('prediction_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('trades_executed', sa.Integer(), nullable=False, default=0),
        sa.Column('successful_trades', sa.Integer(), nullable=False, default=0),
        sa.Column('total_profit', sa.Float(), nullable=False, default=0.0),
        sa.Column('data_points', sa.Integer(), nullable=False, default=0),
        sa.Column('last_visit', sa.DateTime(timezone=True), nullable=True),
        sa.Column('intelligence_quality', sa.Float(), nullable=False, default=0.0),
        sa.UniqueConstraint('player_id', 'port_id', 'commodity', name='uq_player_port_commodity'),
    )
    op.create_index('idx_aria_intel_player_location', 'aria_market_intelligence', ['player_id', 'sector_id', 'commodity'])
    op.create_index('idx_aria_intel_quality', 'aria_market_intelligence', ['intelligence_quality'])
    
    # Create aria_exploration_maps table
    op.create_table('aria_exploration_maps',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('players.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sector_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sectors.id', ondelete='CASCADE'), nullable=False),
        sa.Column('first_visit', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('last_visit', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('visit_count', sa.Integer(), nullable=False, default=1),
        sa.Column('ports_discovered', postgresql.JSONB(astext_type=sa.Text()), nullable=False, default=[]),
        sa.Column('warp_tunnels_mapped', postgresql.JSONB(astext_type=sa.Text()), nullable=False, default=[]),
        sa.Column('hazards_identified', postgresql.JSONB(astext_type=sa.Text()), nullable=False, default=[]),
        sa.Column('market_volatility', sa.Float(), nullable=False, default=0.0),
        sa.Column('safety_rating', sa.Float(), nullable=False, default=0.5),
        sa.Column('trade_opportunity_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('strategic_notes', sa.Text(), nullable=True),
        sa.Column('last_analysis', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('player_id', 'sector_id', name='uq_player_sector_exploration'),
    )
    op.create_index('idx_aria_exploration_player_sector', 'aria_exploration_maps', ['player_id', 'sector_id'])
    
    # Create aria_trading_patterns table
    op.create_table('aria_trading_patterns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('players.id', ondelete='CASCADE'), nullable=False),
        sa.Column('pattern_id', sa.String(100), nullable=False),
        sa.Column('pattern_type', sa.String(50), nullable=False),
        sa.Column('pattern_dna', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('generation', sa.Integer(), nullable=False, default=1),
        sa.Column('parent_pattern', sa.String(100), nullable=True),
        sa.Column('mutations', postgresql.JSONB(astext_type=sa.Text()), nullable=False, default=[]),
        sa.Column('times_used', sa.Integer(), nullable=False, default=0),
        sa.Column('success_rate', sa.Float(), nullable=False, default=0.0),
        sa.Column('average_profit', sa.Float(), nullable=False, default=0.0),
        sa.Column('best_profit', sa.Float(), nullable=False, default=0.0),
        sa.Column('worst_loss', sa.Float(), nullable=False, default=0.0),
        sa.Column('fitness_score', sa.Float(), nullable=False, default=0.5),
        sa.Column('survival_probability', sa.Float(), nullable=False, default=0.5),
        sa.Column('discovered_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('last_used', sa.DateTime(timezone=True), nullable=True),
        sa.Column('evolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('player_id', 'pattern_id', name='uq_player_pattern'),
    )
    op.create_index('idx_aria_pattern_player_fitness', 'aria_trading_patterns', ['player_id', 'fitness_score'])
    
    # Create aria_quantum_cache table
    op.create_table('aria_quantum_cache',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('players.id', ondelete='CASCADE'), nullable=False),
        sa.Column('cache_key', sa.String(255), nullable=False),
        sa.Column('commodity', sa.String(50), nullable=False),
        sa.Column('port_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('ports.id', ondelete='CASCADE'), nullable=True),
        sa.Column('sector_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sectors.id', ondelete='CASCADE'), nullable=False),
        sa.Column('quantum_states', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('ghost_results', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('expected_value', sa.Float(), nullable=False),
        sa.Column('confidence_interval', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('hit_count', sa.Integer(), nullable=False, default=0),
    )
    op.create_index('idx_quantum_cache_player_key', 'aria_quantum_cache', ['player_id', 'cache_key'])
    op.create_index('idx_quantum_cache_expiry', 'aria_quantum_cache', ['expires_at'])
    
    # Create aria_security_logs table
    op.create_table('aria_security_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('players.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('event_severity', sa.String(20), nullable=False),
        sa.Column('event_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(255), nullable=True),
        sa.Column('session_id', sa.String(100), nullable=True),
        sa.Column('anomaly_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('manipulation_indicators', postgresql.JSONB(astext_type=sa.Text()), nullable=False, default=[]),
        sa.Column('security_flags', postgresql.JSONB(astext_type=sa.Text()), nullable=False, default=[]),
        sa.Column('action_taken', sa.String(100), nullable=True),
        sa.Column('notification_sent', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    op.create_index('idx_aria_security_player_time', 'aria_security_logs', ['player_id', 'created_at'])
    op.create_index('idx_aria_security_severity', 'aria_security_logs', ['event_severity'])
    op.create_index('idx_aria_security_anomaly', 'aria_security_logs', ['anomaly_score'])


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_index('idx_aria_security_anomaly', table_name='aria_security_logs')
    op.drop_index('idx_aria_security_severity', table_name='aria_security_logs')
    op.drop_index('idx_aria_security_player_time', table_name='aria_security_logs')
    op.drop_table('aria_security_logs')
    
    op.drop_index('idx_quantum_cache_expiry', table_name='aria_quantum_cache')
    op.drop_index('idx_quantum_cache_player_key', table_name='aria_quantum_cache')
    op.drop_table('aria_quantum_cache')
    
    op.drop_index('idx_aria_pattern_player_fitness', table_name='aria_trading_patterns')
    op.drop_table('aria_trading_patterns')
    
    op.drop_index('idx_aria_exploration_player_sector', table_name='aria_exploration_maps')
    op.drop_table('aria_exploration_maps')
    
    op.drop_index('idx_aria_intel_quality', table_name='aria_market_intelligence')
    op.drop_index('idx_aria_intel_player_location', table_name='aria_market_intelligence')
    op.drop_table('aria_market_intelligence')
    
    op.drop_index('idx_aria_memory_importance', table_name='aria_personal_memories')
    op.drop_index('idx_aria_memory_player_type', table_name='aria_personal_memories')
    op.drop_table('aria_personal_memories')