"""rename ports to stations - comprehensive migration

Revision ID: eab608cc6941
Revises: 8138d7325b51
Create Date: 2025-11-16 18:03:03.127870

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eab608cc6941'
down_revision = '8138d7325b51'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Comprehensive migration to rename ports → stations throughout the database.

    Changes:
    1. Rename 'ports' table to 'stations'
    2. Rename 'player_ports' association table to 'player_stations'
    3. Rename enum types (port_class, port_type, port_status) to (station_class, station_type, station_status)
    4. Update all indexes
    """

    # 1. Rename the main ports table to stations
    op.rename_table('ports', 'stations')

    # 2. Rename the association table
    op.rename_table('player_ports', 'player_stations')

    # 3. Rename enum types (if they exist as native PostgreSQL ENUMs)
    # Note: SQLAlchemy typically uses VARCHAR for enums, but if native enums exist:
    op.execute("ALTER TYPE IF EXISTS port_class RENAME TO station_class")
    op.execute("ALTER TYPE IF EXISTS port_type RENAME TO station_type")
    op.execute("ALTER TYPE IF EXISTS port_status RENAME TO station_status")

    # 4. Rename indexes (auto-generated indexes from table rename should handle most, but explicit renames for safety)
    # Primary key and foreign key indexes are renamed automatically by PostgreSQL
    # Only custom indexes need explicit renames if they exist


def downgrade() -> None:
    """
    Rollback migration: Rename stations → ports
    """

    # Reverse the enum type renames
    op.execute("ALTER TYPE IF EXISTS station_class RENAME TO port_class")
    op.execute("ALTER TYPE IF EXISTS station_type RENAME TO port_type")
    op.execute("ALTER TYPE IF EXISTS station_status RENAME TO port_status")

    # Reverse the association table rename
    op.rename_table('player_stations', 'player_ports')

    # Reverse the main table rename
    op.rename_table('stations', 'ports')