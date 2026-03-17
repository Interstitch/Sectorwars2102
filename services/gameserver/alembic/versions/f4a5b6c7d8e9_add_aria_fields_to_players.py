"""add ARIA consciousness fields to players

Revision ID: f4a5b6c7d8e9
Revises: e3f4a5b6c7d8
Create Date: 2026-03-17 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f4a5b6c7d8e9'
down_revision = 'e3f4a5b6c7d8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('players', sa.Column('aria_bonus_multiplier', sa.Float(), nullable=False, server_default='1.0'))
    op.add_column('players', sa.Column('aria_consciousness_level', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('players', sa.Column('aria_relationship_score', sa.Integer(), nullable=False, server_default='25'))
    op.add_column('players', sa.Column('aria_total_interactions', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('players', 'aria_total_interactions')
    op.drop_column('players', 'aria_relationship_score')
    op.drop_column('players', 'aria_consciousness_level')
    op.drop_column('players', 'aria_bonus_multiplier')
