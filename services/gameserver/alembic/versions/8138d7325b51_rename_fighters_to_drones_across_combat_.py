"""rename fighters to drones across combat system

Comprehensive terminology change from "fighters" to "drones" across all combat-related tables.

Game Design Decision: Terminology changed from "fighters" to "drones" to better reflect
autonomous combat units. This affects combat_log table and all combat analytics.

Columns renamed:
- attacker_fighters → attacker_drones
- defender_fighters → defender_drones
- attacker_fighters_lost → attacker_drones_lost
- defender_fighters_lost → defender_drones_lost
- total_fighters_lost → total_drones_lost

Revision ID: 8138d7325b51
Revises: 75be1dd507e1
Create Date: 2025-11-16 15:41:00.287768

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8138d7325b51'
down_revision = '75be1dd507e1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Rename all fighter columns to drone columns in combat_log table"""

    # Rename columns in combat_log table
    op.alter_column('combat_log', 'attacker_fighters', new_column_name='attacker_drones')
    op.alter_column('combat_log', 'defender_fighters', new_column_name='defender_drones')
    op.alter_column('combat_log', 'attacker_fighters_lost', new_column_name='attacker_drones_lost')
    op.alter_column('combat_log', 'defender_fighters_lost', new_column_name='defender_drones_lost')
    op.alter_column('combat_log', 'total_fighters_lost', new_column_name='total_drones_lost')


def downgrade() -> None:
    """Revert drone columns back to fighter columns"""

    # Revert column names in combat_log table
    op.alter_column('combat_log', 'attacker_drones', new_column_name='attacker_fighters')
    op.alter_column('combat_log', 'defender_drones', new_column_name='defender_fighters')
    op.alter_column('combat_log', 'attacker_drones_lost', new_column_name='attacker_fighters_lost')
    op.alter_column('combat_log', 'defender_drones_lost', new_column_name='defender_fighters_lost')
    op.alter_column('combat_log', 'total_drones_lost', new_column_name='total_fighters_lost')