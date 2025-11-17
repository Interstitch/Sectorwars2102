"""add personal reputation and military rank to players

Revision ID: fe22441146b1
Revises: dbbfad27a7ef
Create Date: 2025-11-17 04:04:31.563809

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe22441146b1'
down_revision = 'dbbfad27a7ef'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add personal reputation system fields
    op.add_column('players', sa.Column('personal_reputation', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('players', sa.Column('reputation_tier', sa.String(length=50), nullable=False, server_default='Neutral'))
    op.add_column('players', sa.Column('name_color', sa.String(length=20), nullable=False, server_default='#FFFFFF'))

    # Add military ranking system fields
    op.add_column('players', sa.Column('military_rank', sa.String(length=50), nullable=False, server_default='Recruit'))
    op.add_column('players', sa.Column('rank_points', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    # Remove fields in reverse order
    op.drop_column('players', 'rank_points')
    op.drop_column('players', 'military_rank')
    op.drop_column('players', 'name_color')
    op.drop_column('players', 'reputation_tier')
    op.drop_column('players', 'personal_reputation')