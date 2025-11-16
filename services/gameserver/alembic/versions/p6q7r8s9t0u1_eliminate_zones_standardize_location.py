"""Eliminate zones and standardize location terminology

Revision ID: p6q7r8s9t0u1
Revises: o7p8q9r0s1t2
Create Date: 2025-11-16 16:00:00.000000

CRITICAL ARCHITECTURAL CHANGE:
- Eliminate GalaxyZone concept entirely (Federation/Border/Frontier)
- Standardize on Location = Region + Sector
- Regions are now the unified concept (Central Nexus, Terran Space, Player-owned)
- Clusters belong to Regions, not Zones
- Remove district segmentation from sectors

This migration CAN wipe existing data as we're in development.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'p6q7r8s9t0u1'
down_revision = 'o7p8q9r0s1t2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Eliminate zones and standardize location architecture.

    Steps:
    1. Drop galaxy_zones table (CASCADE removes dependencies)
    2. Add region_type to regions table
    3. Update clusters to reference regions instead of zones
    4. Remove district from sectors
    5. Clean up enums
    6. Add constraints for region types
    """

    print("🔄 STEP 1: Dropping galaxy_zones table...")
    # Drop galaxy_zones table - CASCADE will handle cluster dependencies
    op.execute("DROP TABLE IF EXISTS galaxy_zones CASCADE")
    print("✅ galaxy_zones table dropped")

    print("🔄 STEP 2: Adding region_type to regions table...")
    # Add region_type column to regions
    op.add_column('regions', sa.Column('region_type', sa.String(50), nullable=False, server_default='player_owned'))
    op.create_index('idx_regions_region_type', 'regions', ['region_type'])
    print("✅ region_type column added")

    print("🔄 STEP 3: Updating clusters to reference regions...")
    # Add region_id to clusters (temporarily nullable for migration)
    op.add_column('clusters', sa.Column('region_id', postgresql.UUID(as_uuid=True), nullable=True))

    # Create foreign key to regions
    op.create_foreign_key(
        'fk_clusters_region',
        'clusters',
        'regions',
        ['region_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # Create index for performance
    op.create_index('idx_clusters_region_id', 'clusters', ['region_id'])

    # Drop old zone_id column (this will fail if there's data, which is expected in dev)
    try:
        op.drop_constraint('clusters_zone_id_fkey', 'clusters', type_='foreignkey')
    except Exception:
        pass  # May not exist if zones were already cleaned up

    try:
        op.drop_column('clusters', 'zone_id')
    except Exception:
        pass  # May not exist if already cleaned up

    # Make region_id NOT NULL now that we've dropped zone_id
    # Note: This requires all clusters to have a region_id, which they will after fresh generation
    op.alter_column('clusters', 'region_id', nullable=False)

    print("✅ Clusters now reference regions")

    print("🔄 STEP 4: Removing district from sectors...")
    # Drop district column from sectors
    try:
        op.drop_index('idx_sectors_district', table_name='sectors')
    except Exception:
        pass

    try:
        op.drop_column('sectors', 'district')
    except Exception:
        pass  # May not exist

    print("✅ District column removed from sectors")

    print("🔄 STEP 5: Cleaning up zone_type enum...")
    # Drop zone_type enum if it exists
    try:
        op.execute("DROP TYPE IF EXISTS zone_type CASCADE")
    except Exception:
        pass

    print("✅ zone_type enum dropped")

    print("🔄 STEP 6: Adding region type constraints...")
    # Add check constraint for region types and sector counts
    op.create_check_constraint(
        'check_region_type_sector_count',
        'regions',
        "(region_type != 'central_nexus' OR total_sectors = 5000) AND "
        "(region_type != 'terran_space' OR total_sectors = 300) AND "
        "(region_type != 'player_owned' OR (total_sectors >= 100 AND total_sectors <= 1000))"
    )

    print("✅ Region type constraints added")

    print("🔄 STEP 7: Removing region_distribution from galaxies...")
    # Remove region_distribution column from galaxies (was used for zone percentages)
    try:
        op.drop_column('galaxies', 'region_distribution')
    except Exception:
        pass  # May not exist

    print("✅ region_distribution removed from galaxies")

    print("✨ Migration complete: Zones eliminated, Location = Region + Sector")
    print("📍 Architecture: Region → Cluster → Sector")


def downgrade() -> None:
    """
    Rollback the zone elimination.

    WARNING: This is a one-way migration. Downgrade will recreate schema
    but will NOT restore any data.
    """

    print("⚠️  Rolling back zone elimination...")
    print("⚠️  WARNING: This will NOT restore data, only schema")

    # Recreate zone_type enum
    op.execute("CREATE TYPE zone_type AS ENUM ('FEDERATION', 'BORDER', 'FRONTIER')")

    # Recreate galaxy_zones table
    op.create_table('galaxy_zones',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_updated', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('galaxy_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('galaxies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.Enum('FEDERATION', 'BORDER', 'FRONTIER', name='zone_type'), nullable=False),
        sa.Column('sector_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('security_level', sa.Float, nullable=False, server_default='1.0'),
        sa.Column('resource_richness', sa.Float, nullable=False, server_default='1.0'),
        sa.Column('security', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('faction_control', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('resources', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('development', postgresql.JSONB, nullable=False, server_default='{}')
    )

    # Add zone_id back to clusters
    op.add_column('clusters', sa.Column('zone_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('clusters_zone_id_fkey', 'clusters', 'galaxy_zones', ['zone_id'], ['id'], ondelete='CASCADE')

    # Remove region_id from clusters
    op.drop_constraint('fk_clusters_region', 'clusters', type_='foreignkey')
    op.drop_index('idx_clusters_region_id', table_name='clusters')
    op.drop_column('clusters', 'region_id')

    # Add district back to sectors
    op.add_column('sectors', sa.Column('district', sa.String(50), nullable=True))
    op.create_index('idx_sectors_district', 'sectors', ['district'])

    # Remove region_type from regions
    op.drop_constraint('check_region_type_sector_count', 'regions', type_='check')
    op.drop_index('idx_regions_region_type', table_name='regions')
    op.drop_column('regions', 'region_type')

    # Add region_distribution back to galaxies
    op.add_column('galaxies', sa.Column('region_distribution', postgresql.JSONB, nullable=False, server_default='{"federation": 25, "border": 35, "frontier": 40}'))

    print("✅ Rollback complete: Zone schema restored (no data)")
