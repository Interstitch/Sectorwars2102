"""add_guard_personality_to_first_login_sessions

Revision ID: ec92f8afd44a
Revises: c5e32c313020
Create Date: 2025-11-17 23:50:13.437232

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec92f8afd44a'
down_revision = 'c5e32c313020'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add guard personality fields to first_login_sessions table
    op.add_column('first_login_sessions', sa.Column('guard_name', sa.String(), nullable=True))
    op.add_column('first_login_sessions', sa.Column('guard_title', sa.String(), nullable=True))
    op.add_column('first_login_sessions', sa.Column('guard_trait', sa.String(), nullable=True))
    op.add_column('first_login_sessions', sa.Column('guard_base_suspicion', sa.Float(), nullable=True))
    op.add_column('first_login_sessions', sa.Column('guard_description', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove guard personality fields
    op.drop_column('first_login_sessions', 'guard_description')
    op.drop_column('first_login_sessions', 'guard_base_suspicion')
    op.drop_column('first_login_sessions', 'guard_trait')
    op.drop_column('first_login_sessions', 'guard_title')
    op.drop_column('first_login_sessions', 'guard_name')