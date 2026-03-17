"""add planet morale and siege_turns columns

Revision ID: a1b2c3d4e5f6
Revises: 5f5a988bdbb1
Create Date: 2026-03-16 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '5f5a988bdbb1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add morale column to planets (0-100 scale, default 100)
    op.add_column('planets', sa.Column('morale', sa.Integer(), nullable=False, server_default='100'))
    # Add siege_turns counter to track consecutive turns with enemies present
    op.add_column('planets', sa.Column('siege_turns', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('planets', 'siege_turns')
    op.drop_column('planets', 'morale')
