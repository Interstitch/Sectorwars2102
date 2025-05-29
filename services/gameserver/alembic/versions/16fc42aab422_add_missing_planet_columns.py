"""add missing planet columns

Revision ID: 16fc42aab422
Revises: db03512a3a26
Create Date: 2025-05-29 03:00:51.988791

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '16fc42aab422'
down_revision = 'db03512a3a26'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing planet columns with IF NOT EXISTS to avoid errors
    op.execute('ALTER TABLE planets ADD COLUMN IF NOT EXISTS fuel_ore INTEGER DEFAULT 0')
    op.execute('ALTER TABLE planets ADD COLUMN IF NOT EXISTS organics INTEGER DEFAULT 0')
    op.execute('ALTER TABLE planets ADD COLUMN IF NOT EXISTS equipment INTEGER DEFAULT 0')
    op.execute('ALTER TABLE planets ADD COLUMN IF NOT EXISTS fighters INTEGER DEFAULT 0')
    op.execute('ALTER TABLE planets ADD COLUMN IF NOT EXISTS factory_level INTEGER DEFAULT 0')
    op.execute('ALTER TABLE planets ADD COLUMN IF NOT EXISTS farm_level INTEGER DEFAULT 0')
    op.execute('ALTER TABLE planets ADD COLUMN IF NOT EXISTS mine_level INTEGER DEFAULT 0')
    op.execute('ALTER TABLE planets ADD COLUMN IF NOT EXISTS research_level INTEGER DEFAULT 0')
    op.execute('ALTER TABLE planets ADD COLUMN IF NOT EXISTS defense_turrets INTEGER DEFAULT 0')
    op.execute('ALTER TABLE planets ADD COLUMN IF NOT EXISTS defense_shields INTEGER DEFAULT 0')
    op.execute('ALTER TABLE planets ADD COLUMN IF NOT EXISTS defense_fighters INTEGER DEFAULT 0')
    op.execute('ALTER TABLE planets ADD COLUMN IF NOT EXISTS fuel_allocation INTEGER DEFAULT 0')
    op.execute('ALTER TABLE planets ADD COLUMN IF NOT EXISTS organics_allocation INTEGER DEFAULT 0')
    op.execute('ALTER TABLE planets ADD COLUMN IF NOT EXISTS equipment_allocation INTEGER DEFAULT 0')
    op.execute('ALTER TABLE planets ADD COLUMN IF NOT EXISTS under_siege BOOLEAN DEFAULT false')
    op.execute('ALTER TABLE planets ADD COLUMN IF NOT EXISTS siege_started_at TIMESTAMP WITH TIME ZONE')
    op.execute('ALTER TABLE planets ADD COLUMN IF NOT EXISTS siege_attacker_id UUID')


def downgrade() -> None:
    # Remove the columns if needed
    op.drop_column('planets', 'siege_attacker_id')
    op.drop_column('planets', 'siege_started_at')
    op.drop_column('planets', 'under_siege')
    op.drop_column('planets', 'equipment_allocation')
    op.drop_column('planets', 'organics_allocation')
    op.drop_column('planets', 'fuel_allocation')
    op.drop_column('planets', 'defense_fighters')
    op.drop_column('planets', 'defense_shields')
    op.drop_column('planets', 'defense_turrets')
    op.drop_column('planets', 'research_level')
    op.drop_column('planets', 'mine_level')
    op.drop_column('planets', 'farm_level')
    op.drop_column('planets', 'factory_level')
    op.drop_column('planets', 'fighters')
    op.drop_column('planets', 'equipment')
    op.drop_column('planets', 'organics')
    op.drop_column('planets', 'fuel_ore')