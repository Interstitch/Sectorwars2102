"""add_ai_logging_fields_to_dialogue_exchange

Revision ID: 6acc65ee7a72
Revises: 6b1d95a38c98
Create Date: 2025-11-20 00:35:29.073313

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6acc65ee7a72'
down_revision = '6b1d95a38c98'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add AI provider and prompt logging fields
    op.add_column('dialogue_exchanges', sa.Column('ai_provider', sa.String(length=20), nullable=True))
    op.add_column('dialogue_exchanges', sa.Column('ai_system_prompt', sa.String(), nullable=True))
    op.add_column('dialogue_exchanges', sa.Column('ai_user_prompt', sa.String(), nullable=True))
    op.add_column('dialogue_exchanges', sa.Column('ai_raw_response', sa.String(), nullable=True))

    # Add additional analysis metrics
    op.add_column('dialogue_exchanges', sa.Column('believability', sa.Float(), nullable=True))
    op.add_column('dialogue_exchanges', sa.Column('current_suspicion', sa.Float(), nullable=True))

    # Add performance and cost tracking
    op.add_column('dialogue_exchanges', sa.Column('response_time_ms', sa.Integer(), nullable=True))
    op.add_column('dialogue_exchanges', sa.Column('estimated_cost_usd', sa.Float(), nullable=True))
    op.add_column('dialogue_exchanges', sa.Column('tokens_used', sa.Integer(), nullable=True))


def downgrade() -> None:
    # Remove added columns in reverse order
    op.drop_column('dialogue_exchanges', 'tokens_used')
    op.drop_column('dialogue_exchanges', 'estimated_cost_usd')
    op.drop_column('dialogue_exchanges', 'response_time_ms')
    op.drop_column('dialogue_exchanges', 'current_suspicion')
    op.drop_column('dialogue_exchanges', 'believability')
    op.drop_column('dialogue_exchanges', 'ai_raw_response')
    op.drop_column('dialogue_exchanges', 'ai_user_prompt')
    op.drop_column('dialogue_exchanges', 'ai_system_prompt')
    op.drop_column('dialogue_exchanges', 'ai_provider')