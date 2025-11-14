"""rename_game_event_affected_regions_to_affected_zones

Revision ID: 03bab0cdfc79
Revises: 5033032513e9
Create Date: 2025-11-14 03:02:59.759442

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03bab0cdfc79'
down_revision = '5033032513e9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename affected_regions to affected_zones in game_events table
    # This column stores cosmological zone names/IDs (Federation/Border/Frontier)
    op.alter_column('game_events', 'affected_regions', new_column_name='affected_zones')


def downgrade() -> None:
    # Revert: rename affected_zones back to affected_regions
    op.alter_column('game_events', 'affected_zones', new_column_name='affected_regions')