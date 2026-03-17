"""add citadel fields to planets

Revision ID: e3f4a5b6c7d8
Revises: d2e3f4a5b6c7
Create Date: 2026-03-17 12:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3f4a5b6c7d8'
down_revision = 'd2e3f4a5b6c7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('planets', sa.Column('citadel_level', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('planets', sa.Column('citadel_upgrading', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('planets', sa.Column('citadel_upgrade_started_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('planets', sa.Column('citadel_upgrade_complete_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('planets', sa.Column('citadel_safe_credits', sa.BigInteger(), nullable=False, server_default='0'))
    op.add_column('planets', sa.Column('citadel_safe_max', sa.BigInteger(), nullable=False, server_default='0'))
    op.add_column('planets', sa.Column('citadel_drone_capacity', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('planets', sa.Column('citadel_max_population', sa.BigInteger(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('planets', 'citadel_max_population')
    op.drop_column('planets', 'citadel_drone_capacity')
    op.drop_column('planets', 'citadel_safe_max')
    op.drop_column('planets', 'citadel_safe_credits')
    op.drop_column('planets', 'citadel_upgrade_complete_at')
    op.drop_column('planets', 'citadel_upgrade_started_at')
    op.drop_column('planets', 'citadel_upgrading')
    op.drop_column('planets', 'citadel_level')
