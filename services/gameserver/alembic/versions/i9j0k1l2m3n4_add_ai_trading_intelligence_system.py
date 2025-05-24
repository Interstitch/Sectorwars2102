"""Add AI trading intelligence system tables

Revision ID: i9j0k1l2m3n4
Revises: h8i9j0k1l2m3
Create Date: 2025-05-24 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision: str = 'i9j0k1l2m3n4'
down_revision: Union[str, None] = 'h8i9j0k1l2m3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ai_market_predictions table
    op.create_table('ai_market_predictions',
        sa.Column('id', UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('commodity_id', UUID(as_uuid=True), nullable=False),
        sa.Column('sector_id', UUID(as_uuid=True), nullable=False),
        sa.Column('predicted_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('confidence_interval', sa.Numeric(3, 2), nullable=False),
        sa.Column('prediction_horizon', sa.Integer(), nullable=False),  # hours ahead
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('training_data_points', sa.Integer(), nullable=False),
        sa.Column('prediction_factors', JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('actual_price', sa.Numeric(10, 2), nullable=True),  # For accuracy tracking
        sa.Column('accuracy_score', sa.Numeric(3, 2), nullable=True),
        sa.ForeignKeyConstraint(['sector_id'], ['sectors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ai_market_predictions_commodity_sector', 'ai_market_predictions', ['commodity_id', 'sector_id'], unique=False)
    op.create_index('ix_ai_market_predictions_expires_at', 'ai_market_predictions', ['expires_at'], unique=False)
    op.create_index('ix_ai_market_predictions_created_at', 'ai_market_predictions', ['created_at'], unique=False)

    # Create player_trading_profiles table
    op.create_table('player_trading_profiles',
        sa.Column('id', UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('player_id', UUID(as_uuid=True), nullable=False),
        sa.Column('risk_tolerance', sa.Numeric(3, 2), nullable=False, server_default=sa.text('0.5')),
        sa.Column('preferred_commodities', JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('avoided_sectors', JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('trading_patterns', JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('performance_metrics', JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ai_assistance_level', sa.String(length=20), nullable=False, server_default=sa.text("'medium'")),  # 'minimal', 'medium', 'full'
        sa.Column('notification_preferences', JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('learning_data', JSONB(astext_type=sa.Text()), nullable=True),  # ML model training data
        sa.Column('last_active_sector', UUID(as_uuid=True), nullable=True),
        sa.Column('average_profit_per_trade', sa.Numeric(10, 2), nullable=False, server_default=sa.text('0')),
        sa.Column('total_trades_analyzed', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['last_active_sector'], ['sectors.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('player_id')
    )
    op.create_index('ix_player_trading_profiles_player_id', 'player_trading_profiles', ['player_id'], unique=True)
    op.create_index('ix_player_trading_profiles_updated_at', 'player_trading_profiles', ['updated_at'], unique=False)

    # Create ai_recommendations table
    op.create_table('ai_recommendations',
        sa.Column('id', UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('player_id', UUID(as_uuid=True), nullable=False),
        sa.Column('recommendation_type', sa.String(length=50), nullable=False),  # 'buy', 'sell', 'route', 'avoid'
        sa.Column('recommendation_data', JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('confidence_score', sa.Numeric(3, 2), nullable=False),
        sa.Column('expected_profit', sa.Numeric(10, 2), nullable=True),
        sa.Column('risk_assessment', sa.String(length=20), nullable=False),  # 'low', 'medium', 'high'
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('priority_level', sa.Integer(), nullable=False, server_default=sa.text('3')),  # 1-5 scale
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('accepted', sa.Boolean(), nullable=True),  # NULL = pending, True/False = user decision
        sa.Column('acceptance_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('outcome_profit', sa.Numeric(10, 2), nullable=True),
        sa.Column('outcome_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('feedback_score', sa.Integer(), nullable=True),  # 1-5 user feedback rating
        sa.Column('feedback_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ai_recommendations_player_id', 'ai_recommendations', ['player_id'], unique=False)
    op.create_index('ix_ai_recommendations_type_priority', 'ai_recommendations', ['recommendation_type', 'priority_level'], unique=False)
    op.create_index('ix_ai_recommendations_expires_at', 'ai_recommendations', ['expires_at'], unique=False)
    op.create_index('ix_ai_recommendations_accepted', 'ai_recommendations', ['accepted'], unique=False)

    # Create ai_model_performance table for tracking AI system effectiveness
    op.create_table('ai_model_performance',
        sa.Column('id', UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('performance_date', sa.Date(), nullable=False),
        sa.Column('total_predictions', sa.Integer(), nullable=False),
        sa.Column('correct_predictions', sa.Integer(), nullable=False),
        sa.Column('accuracy_percentage', sa.Numeric(5, 2), nullable=False),
        sa.Column('average_confidence', sa.Numeric(3, 2), nullable=False),
        sa.Column('user_acceptance_rate', sa.Numeric(3, 2), nullable=False),
        sa.Column('average_user_satisfaction', sa.Numeric(3, 2), nullable=True),
        sa.Column('profit_improvement_rate', sa.Numeric(5, 2), nullable=True),
        sa.Column('performance_metrics', JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ai_model_performance_date_model', 'ai_model_performance', ['performance_date', 'model_name'], unique=True)
    op.create_index('ix_ai_model_performance_accuracy', 'ai_model_performance', ['accuracy_percentage'], unique=False)

    # Create ai_training_data table for storing market pattern data
    op.create_table('ai_training_data',
        sa.Column('id', UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('data_type', sa.String(length=50), nullable=False),  # 'market_price', 'trade_volume', 'player_behavior'
        sa.Column('sector_id', UUID(as_uuid=True), nullable=True),
        sa.Column('commodity_id', UUID(as_uuid=True), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('data_value', sa.Numeric(12, 4), nullable=False),
        sa.Column('contextual_data', JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('quality_score', sa.Numeric(3, 2), nullable=False, server_default=sa.text('1.0')),  # Data quality for training
        sa.Column('used_in_training', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['sector_id'], ['sectors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ai_training_data_type_timestamp', 'ai_training_data', ['data_type', 'timestamp'], unique=False)
    op.create_index('ix_ai_training_data_sector_commodity', 'ai_training_data', ['sector_id', 'commodity_id'], unique=False)
    op.create_index('ix_ai_training_data_quality_training', 'ai_training_data', ['quality_score', 'used_in_training'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order of creation
    op.drop_table('ai_training_data')
    op.drop_table('ai_model_performance')
    op.drop_table('ai_recommendations')
    op.drop_table('player_trading_profiles')
    op.drop_table('ai_market_predictions')