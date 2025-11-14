"""rename_galaxy_region_to_galaxy_zone_terminology

Revision ID: 5033032513e9
Revises: 6838b5cb335e
Create Date: 2025-11-14 02:23:52.293826

IMPORTANT: This migration renames GalaxyRegion → GalaxyZone to clarify terminology.
- "Zone" = Cosmological classification (Federation/Border/Frontier)
- "Territory" = Business/ownership concept (Home, Central Nexus, Player-owned)

This migration will DELETE ALL existing galaxy data to apply schema changes cleanly.
If you have production data, back it up before running this migration.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5033032513e9'
down_revision = '6838b5cb335e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Rename GalaxyRegion to GalaxyZone throughout the database schema.

    Steps:
    1. Delete all existing galaxy data (CASCADE handles related records)
    2. Rename enum type: region_type → zone_type
    3. Rename table: galaxy_regions → galaxy_zones
    4. Update foreign key references in clusters table
    """

    # STEP 1: Delete all existing galaxy data
    # This cascades to galaxy_regions, clusters, sectors, ports, planets, etc.
    print("⚠️  WARNING: Deleting all existing galaxy data...")
    op.execute("DELETE FROM galaxies CASCADE")
    print("✅ Galaxy data deleted")

    # STEP 2: Rename the enum type from region_type to zone_type
    # PostgreSQL requires creating new enum, altering column, then dropping old enum
    print("🔄 Renaming enum type: region_type → zone_type...")

    # Create new zone_type enum
    op.execute("CREATE TYPE zone_type AS ENUM ('FEDERATION', 'BORDER', 'FRONTIER')")

    # Alter the column to use new enum (table still called galaxy_regions at this point)
    op.execute("ALTER TABLE galaxy_regions ALTER COLUMN type TYPE zone_type USING type::text::zone_type")

    # Drop old enum
    op.execute("DROP TYPE region_type")

    print("✅ Enum renamed: region_type → zone_type")

    # STEP 3: Rename the table from galaxy_regions to galaxy_zones
    print("🔄 Renaming table: galaxy_regions → galaxy_zones...")
    op.rename_table('galaxy_regions', 'galaxy_zones')
    print("✅ Table renamed: galaxy_regions → galaxy_zones")

    # STEP 4: Update foreign key constraint and column name in clusters table
    print("🔄 Updating foreign key in clusters table...")

    # Drop old foreign key constraint
    op.drop_constraint('clusters_region_id_fkey', 'clusters', type_='foreignkey')

    # Rename the column
    op.alter_column('clusters', 'region_id', new_column_name='zone_id')

    # Create new foreign key constraint with updated names
    op.create_foreign_key(
        'clusters_zone_id_fkey',
        'clusters',
        'galaxy_zones',
        ['zone_id'],
        ['id'],
        ondelete='CASCADE'
    )

    print("✅ Foreign key updated: region_id → zone_id")
    print("✨ Migration complete: GalaxyRegion → GalaxyZone")


def downgrade() -> None:
    """
    Rollback the GalaxyZone rename back to GalaxyRegion.
    """

    print("⚠️  Rolling back: GalaxyZone → GalaxyRegion...")

    # Reverse STEP 4: Update foreign key back
    op.drop_constraint('clusters_zone_id_fkey', 'clusters', type_='foreignkey')
    op.alter_column('clusters', 'zone_id', new_column_name='region_id')
    op.create_foreign_key(
        'clusters_region_id_fkey',
        'clusters',
        'galaxy_regions',
        ['region_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # Reverse STEP 3: Rename table back
    op.rename_table('galaxy_zones', 'galaxy_regions')

    # Reverse STEP 2: Rename enum back
    op.execute("CREATE TYPE region_type AS ENUM ('FEDERATION', 'BORDER', 'FRONTIER')")
    op.execute("ALTER TABLE galaxy_regions ALTER COLUMN type TYPE region_type USING type::text::region_type")
    op.execute("DROP TYPE zone_type")

    print("✅ Rollback complete: Back to GalaxyRegion schema")
