"""add terraforming columns to planets

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('planets', sa.Column('terraforming_active', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('planets', sa.Column('terraforming_target', sa.Integer(), nullable=True))
    op.add_column('planets', sa.Column('terraforming_start_time', sa.DateTime(timezone=True), nullable=True))
    op.add_column('planets', sa.Column('terraforming_progress', sa.Float(), nullable=False, server_default='0.0'))


def downgrade() -> None:
    op.drop_column('planets', 'terraforming_progress')
    op.drop_column('planets', 'terraforming_start_time')
    op.drop_column('planets', 'terraforming_target')
    op.drop_column('planets', 'terraforming_active')
