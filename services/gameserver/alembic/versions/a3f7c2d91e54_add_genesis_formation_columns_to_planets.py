"""add genesis formation columns to planets

Revision ID: a3f7c2d91e54
Revises: 5f5a988bdbb1
Create Date: 2026-03-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3f7c2d91e54'
down_revision = '5f5a988bdbb1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add genesis tier column (basic / enhanced / advanced)
    op.add_column('planets', sa.Column('genesis_tier', sa.String(20), nullable=True))

    # Add formation status column (forming / complete)
    op.add_column('planets', sa.Column('formation_status', sa.String(20), nullable=True))

    # Add formation timing columns
    op.add_column('planets', sa.Column(
        'formation_started_at',
        sa.DateTime(timezone=True),
        nullable=True
    ))
    op.add_column('planets', sa.Column(
        'formation_complete_at',
        sa.DateTime(timezone=True),
        nullable=True
    ))


def downgrade() -> None:
    op.drop_column('planets', 'formation_complete_at')
    op.drop_column('planets', 'formation_started_at')
    op.drop_column('planets', 'formation_status')
    op.drop_column('planets', 'genesis_tier')
