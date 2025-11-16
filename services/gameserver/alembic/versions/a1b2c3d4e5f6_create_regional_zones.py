"""Create regional zones architecture

Revision ID: a1b2c3d4e5f6
Revises: 0c90fa7cdc03
Create Date: 2025-11-16 18:00:00.000000

REGIONAL ZONES ARCHITECTURE:
- Create zones table (zones belong to Regions, not Galaxy)
- Zones define security/policing regions within a parent Region
- Zones are independent of Clusters (orthogonal dimensions)
- Sectors have BOTH zone_id AND cluster_id

Zone Types by Region:
- Central Nexus (region_type=central_nexus): One zone "The Expanse" (5000 sectors)
- Terran Space (region_type=terran_space): Three zones Fed/Border/Frontier (300 sectors in thirds)
- Player Regions (region_type=player_owned): Three zones Fed/Border/Frontier (100-1000 sectors in thirds)

Hierarchy: Sector < Cluster < Zone < Region < Galaxy
           Sector < Zone < Region < Galaxy
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '0c90fa7cdc03'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create regional zones architecture:
    1. Create zones table with constraints
    2. Add sector.zone_id column
    3. Populate zones for each region based on region_type
    4. Assign sectors to zones based on sector_number ranges
    5. Clean up deprecated galaxy_zones table if exists
    """

    # ============================================================================
    # STEP 1: Create zones table
    # ============================================================================
    op.create_table(
        'zones',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('region_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('regions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('zone_type', sa.String(50), nullable=False),
        sa.Column('start_sector', sa.Integer(), nullable=False),
        sa.Column('end_sector', sa.Integer(), nullable=False),
        sa.Column('policing_level', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('danger_rating', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),

        # Check constraints
        sa.CheckConstraint('start_sector >= 1', name='check_start_sector_positive'),
        sa.CheckConstraint('end_sector >= start_sector', name='check_end_after_start'),
        sa.CheckConstraint('policing_level >= 0 AND policing_level <= 10', name='check_policing_range'),
        sa.CheckConstraint('danger_rating >= 0 AND danger_rating <= 10', name='check_danger_range'),
    )

    # Create index on region_id for query performance
    op.create_index('ix_zones_region_id', 'zones', ['region_id'])

    # ============================================================================
    # STEP 2: Add zone_id to sectors table
    # ============================================================================
    op.add_column('sectors', sa.Column('zone_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_sectors_zone_id', 'sectors', 'zones', ['zone_id'], ['id'], ondelete='SET NULL')
    op.create_index('ix_sectors_zone_id', 'sectors', ['zone_id'])

    # ============================================================================
    # STEP 3: Add region_type to regions (if not exists)
    # ============================================================================
    # Check if column exists first (idempotent)
    connection = op.get_bind()
    result = connection.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='regions' AND column_name='region_type'"
    ))
    if not result.fetchone():
        op.add_column('regions', sa.Column('region_type', sa.String(50), nullable=False, server_default='player_owned'))

        # Add check constraint for region type sector counts
        op.create_check_constraint(
            'valid_region_type_sector_count',
            'regions',
            "(region_type != 'central_nexus' OR total_sectors = 5000) AND "
            "(region_type != 'terran_space' OR total_sectors = 300) AND "
            "(region_type != 'player_owned' OR (total_sectors >= 100 AND total_sectors <= 1000))"
        )

    # ============================================================================
    # STEP 4: Populate zones for each region
    # ============================================================================

    # CENTRAL NEXUS: Create "The Expanse" (one massive zone)
    op.execute("""
        INSERT INTO zones (region_id, name, zone_type, start_sector, end_sector, policing_level, danger_rating)
        SELECT
            id,
            'The Expanse',
            'EXPANSE',
            1,
            5000,
            3,  -- Light policing (sparse region)
            6   -- Moderate danger
        FROM regions
        WHERE region_type = 'central_nexus'
    """)

    # TERRAN SPACE: Create Federation/Border/Frontier zones (300 sectors in thirds)
    op.execute("""
        INSERT INTO zones (region_id, name, zone_type, start_sector, end_sector, policing_level, danger_rating)
        SELECT
            id,
            'Federation Space',
            'FEDERATION',
            1,
            100,  -- First 33% (sectors 1-100)
            9,    -- Heavily policed
            1     -- Very safe
        FROM regions
        WHERE region_type = 'terran_space'
    """)

    op.execute("""
        INSERT INTO zones (region_id, name, zone_type, start_sector, end_sector, policing_level, danger_rating)
        SELECT
            id,
            'Border Regions',
            'BORDER',
            101,  -- Middle 33% (sectors 101-200)
            200,
            5,    -- Moderate policing
            4     -- Some danger
        FROM regions
        WHERE region_type = 'terran_space'
    """)

    op.execute("""
        INSERT INTO zones (region_id, name, zone_type, start_sector, end_sector, policing_level, danger_rating)
        SELECT
            id,
            'Frontier Space',
            'FRONTIER',
            201,  -- Last 34% (sectors 201-300)
            300,
            2,    -- Light policing
            8     -- High danger
        FROM regions
        WHERE region_type = 'terran_space'
    """)

    # PLAYER-OWNED REGIONS: Create Federation/Border/Frontier zones (dynamic thirds)
    # Federation Space: First 33%
    op.execute("""
        INSERT INTO zones (region_id, name, zone_type, start_sector, end_sector, policing_level, danger_rating)
        SELECT
            id,
            'Federation Space',
            'FEDERATION',
            1,
            CAST(total_sectors * 0.33 AS INTEGER),  -- First third
            9,    -- Heavily policed
            1     -- Very safe
        FROM regions
        WHERE region_type = 'player_owned'
    """)

    # Border Regions: Middle 33%
    op.execute("""
        INSERT INTO zones (region_id, name, zone_type, start_sector, end_sector, policing_level, danger_rating)
        SELECT
            id,
            'Border Regions',
            'BORDER',
            CAST(total_sectors * 0.33 AS INTEGER) + 1,  -- Start of middle third
            CAST(total_sectors * 0.67 AS INTEGER),      -- End of middle third
            5,    -- Moderate policing
            4     -- Some danger
        FROM regions
        WHERE region_type = 'player_owned'
    """)

    # Frontier Space: Last 34%
    op.execute("""
        INSERT INTO zones (region_id, name, zone_type, start_sector, end_sector, policing_level, danger_rating)
        SELECT
            id,
            'Frontier Space',
            'FRONTIER',
            CAST(total_sectors * 0.67 AS INTEGER) + 1,  -- Start of last third
            total_sectors,                              -- All remaining sectors
            2,    -- Light policing
            8     -- High danger
        FROM regions
        WHERE region_type = 'player_owned'
    """)

    # ============================================================================
    # STEP 5: Assign sectors to zones based on sector_number
    # ============================================================================
    op.execute("""
        UPDATE sectors
        SET zone_id = zones.id
        FROM zones
        WHERE sectors.region_id = zones.region_id
          AND sectors.sector_number >= zones.start_sector
          AND sectors.sector_number <= zones.end_sector
    """)

    # ============================================================================
    # STEP 6: Remove deprecated galaxy_zones table if exists
    # ============================================================================
    # This is for cleanup if migrating from old architecture
    connection = op.get_bind()
    result = connection.execute(sa.text(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_name='galaxy_zones'"
    ))
    if result.fetchone():
        op.drop_table('galaxy_zones')
        # Drop associated enum if exists
        try:
            op.execute("DROP TYPE IF EXISTS zone_type CASCADE")
        except:
            pass  # Enum might not exist

    # ============================================================================
    # STEP 7: Remove district column from sectors if exists
    # ============================================================================
    connection = op.get_bind()
    result = connection.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='sectors' AND column_name='district'"
    ))
    if result.fetchone():
        op.drop_column('sectors', 'district')

    # ============================================================================
    # STEP 8: Update cluster.zone_id to cluster.region_id if needed
    # ============================================================================
    # Check if clusters still have zone_id instead of region_id
    connection = op.get_bind()
    result = connection.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='clusters' AND column_name='zone_id'"
    ))
    if result.fetchone():
        # Rename zone_id to region_id (clusters belong to regions, not zones)
        op.alter_column('clusters', 'zone_id', new_column_name='region_id')

        # Update foreign key to point to regions
        op.drop_constraint('clusters_zone_id_fkey', 'clusters', type_='foreignkey')
        op.create_foreign_key('fk_clusters_region_id', 'clusters', 'regions', ['region_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """
    Rollback regional zones architecture:
    1. Remove sector.zone_id column
    2. Drop zones table (CASCADE will handle relationships)
    3. Optionally restore previous state (not implemented - one-way migration)
    """

    # Remove sector.zone_id
    op.drop_constraint('fk_sectors_zone_id', 'sectors', type_='foreignkey')
    op.drop_index('ix_sectors_zone_id', 'sectors')
    op.drop_column('sectors', 'zone_id')

    # Drop zones table (CASCADE will remove references)
    op.drop_index('ix_zones_region_id', 'zones')
    op.drop_table('zones')

    # Note: We do NOT restore galaxy_zones table or revert cluster changes
    # This is a one-way migration by design
    # If full rollback is needed, restore from database backup
