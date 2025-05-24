"""add_missing_genesis_devices_column

Revision ID: e30ce77d055a
Revises: 504afbbd4d77
Create Date: 2025-05-24 16:57:21.821613

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e30ce77d055a'
down_revision = '504afbbd4d77'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add the missing genesis_devices column to the ships table
    op.add_column('ships', sa.Column('genesis_devices', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    # Remove the genesis_devices column
    op.drop_column('ships', 'genesis_devices')