"""fix_cargo_freighter_to_cargo_hauler_enum

Revision ID: fa15ada1398e
Revises: e30ce77d055a
Create Date: 2025-05-24 16:59:19.789964

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fa15ada1398e'
down_revision = 'e30ce77d055a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Update enum values from CARGO_FREIGHTER to CARGO_HAULER
    op.execute("ALTER TYPE ship_type_config RENAME VALUE 'CARGO_FREIGHTER' TO 'CARGO_HAULER'")
    op.execute("ALTER TYPE ship_choice RENAME VALUE 'CARGO_FREIGHTER' TO 'CARGO_HAULER'")
    op.execute("ALTER TYPE awarded_ship_type RENAME VALUE 'CARGO_FREIGHTER' TO 'CARGO_HAULER'")


def downgrade() -> None:
    # Revert enum values from CARGO_HAULER back to CARGO_FREIGHTER
    op.execute("ALTER TYPE ship_type_config RENAME VALUE 'CARGO_HAULER' TO 'CARGO_FREIGHTER'")
    op.execute("ALTER TYPE ship_choice RENAME VALUE 'CARGO_HAULER' TO 'CARGO_FREIGHTER'")
    op.execute("ALTER TYPE awarded_ship_type RENAME VALUE 'CARGO_HAULER' TO 'CARGO_FREIGHTER'")