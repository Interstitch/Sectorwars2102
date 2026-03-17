"""add attack_turn_cost and equipment_slots to ships

Revision ID: d2e3f4a5b6c7
Revises: c1d2e3f4a5b6
Create Date: 2026-03-17 12:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = 'd2e3f4a5b6c7'
down_revision = 'c1d2e3f4a5b6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add attack_turn_cost to ships table
    op.add_column('ships', sa.Column('attack_turn_cost', sa.Integer(), nullable=True))

    # Add equipment_slots JSONB to ships table
    op.add_column('ships', sa.Column('equipment_slots', JSONB(), nullable=False, server_default='{}'))

    # Add attack_turn_cost to ship_specifications table
    op.add_column('ship_specifications', sa.Column('attack_turn_cost', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('ship_specifications', 'attack_turn_cost')
    op.drop_column('ships', 'equipment_slots')
    op.drop_column('ships', 'attack_turn_cost')
