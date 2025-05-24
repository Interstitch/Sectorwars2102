"""add missing planet columns

Revision ID: f6g7h8i9j0k1
Revises: e5f6g7h8i9j0
Create Date: 2025-01-23 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f6g7h8i9j0k1'
down_revision = 'e5f6g7h8i9j0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types for planets
    planet_type = postgresql.ENUM('TERRAN', 'DESERT', 'ICE', 'VOLCANIC', 'TOXIC', 'BARREN', 'OCEAN', 'JUNGLE', 'GAS_GIANT', 'RADIOACTIVE', name='planet_type')
    planet_status = postgresql.ENUM('UNINHABITABLE', 'HABITABLE', 'COLONIZED', 'TERRAFORMING', 'UNDER_CONSTRUCTION', 'UNDER_ATTACK', 'ABANDONED', 'QUARANTINED', 'RESTRICTED', name='planet_status')
    
    planet_type.create(op.get_bind())
    planet_status.create(op.get_bind())
    
    # Add sector_uuid column to planets table
    op.add_column('planets', sa.Column('sector_uuid', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Create foreign key constraint
    op.create_foreign_key('fk_planets_sector_uuid', 'planets', 'sectors', ['sector_uuid'], ['id'], ondelete='CASCADE')
    
    # Populate sector_uuid based on existing sector_id values
    op.execute("""
        UPDATE planets 
        SET sector_uuid = sectors.id 
        FROM sectors 
        WHERE planets.sector_id = sectors.sector_id
    """)
    
    # Add missing columns to planets table
    op.add_column('planets', sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.add_column('planets', sa.Column('type', sa.Enum('TERRAN', 'DESERT', 'ICE', 'VOLCANIC', 'TOXIC', 'BARREN', 'OCEAN', 'JUNGLE', 'GAS_GIANT', 'RADIOACTIVE', name='planet_type'), nullable=True))
    op.add_column('planets', sa.Column('status', sa.Enum('UNINHABITABLE', 'HABITABLE', 'COLONIZED', 'TERRAFORMING', 'UNDER_CONSTRUCTION', 'UNDER_ATTACK', 'ABANDONED', 'QUARANTINED', 'RESTRICTED', name='planet_status'), nullable=True))
    op.add_column('planets', sa.Column('size', sa.Integer(), nullable=True))
    op.add_column('planets', sa.Column('position', sa.Integer(), nullable=True))
    op.add_column('planets', sa.Column('gravity', sa.Float(), nullable=True))
    op.add_column('planets', sa.Column('atmosphere', sa.String(), nullable=True))
    op.add_column('planets', sa.Column('temperature', sa.Float(), nullable=True))
    op.add_column('planets', sa.Column('water_coverage', sa.Float(), nullable=True))
    op.add_column('planets', sa.Column('habitability_score', sa.Integer(), nullable=True))
    op.add_column('planets', sa.Column('radiation_level', sa.Float(), nullable=True))
    op.add_column('planets', sa.Column('resource_richness', sa.Float(), nullable=True))
    op.add_column('planets', sa.Column('resources', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('planets', sa.Column('special_resources', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('planets', sa.Column('colonized_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('planets', sa.Column('population', sa.BigInteger(), nullable=True))
    op.add_column('planets', sa.Column('max_population', sa.BigInteger(), nullable=True))
    op.add_column('planets', sa.Column('population_growth', sa.Float(), nullable=True))
    op.add_column('planets', sa.Column('economy', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('planets', sa.Column('production', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('planets', sa.Column('production_efficiency', sa.Float(), nullable=True))
    op.add_column('planets', sa.Column('defense_level', sa.Integer(), nullable=True))
    op.add_column('planets', sa.Column('shields', sa.Integer(), nullable=True))
    op.add_column('planets', sa.Column('weapon_batteries', sa.Integer(), nullable=True))
    op.add_column('planets', sa.Column('last_attacked', sa.DateTime(timezone=True), nullable=True))
    op.add_column('planets', sa.Column('last_production', sa.DateTime(timezone=True), nullable=True))
    op.add_column('planets', sa.Column('active_events', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('planets', sa.Column('description', sa.String(), nullable=True))
    op.add_column('planets', sa.Column('genesis_created', sa.Boolean(), nullable=True))
    op.add_column('planets', sa.Column('genesis_device_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Set default values for existing rows
    op.execute("""
        UPDATE planets SET
            type = 'TERRAN',
            status = 'UNINHABITABLE',
            size = 5,
            position = 3,
            gravity = 1.0,
            temperature = 0.0,
            water_coverage = 0.0,
            habitability_score = 0,
            radiation_level = 0.0,
            resource_richness = 1.0,
            resources = '{}',
            special_resources = '{}',
            population = 0,
            max_population = 0,
            population_growth = 0.0,
            economy = '{}',
            production = '{}',
            production_efficiency = 1.0,
            defense_level = 0,
            shields = 0,
            weapon_batteries = 0,
            active_events = '[]',
            genesis_created = false
        WHERE type IS NULL
    """)
    
    # Make columns not nullable after setting defaults (only for required ones)
    op.alter_column('planets', 'type', nullable=False)
    op.alter_column('planets', 'status', nullable=False)
    op.alter_column('planets', 'size', nullable=False)
    op.alter_column('planets', 'position', nullable=False)
    op.alter_column('planets', 'gravity', nullable=False)
    op.alter_column('planets', 'temperature', nullable=False)
    op.alter_column('planets', 'water_coverage', nullable=False)
    op.alter_column('planets', 'habitability_score', nullable=False)
    op.alter_column('planets', 'radiation_level', nullable=False)
    op.alter_column('planets', 'resource_richness', nullable=False)
    op.alter_column('planets', 'resources', nullable=False)
    op.alter_column('planets', 'special_resources', nullable=False)
    op.alter_column('planets', 'population', nullable=False)
    op.alter_column('planets', 'max_population', nullable=False)
    op.alter_column('planets', 'population_growth', nullable=False)
    op.alter_column('planets', 'economy', nullable=False)
    op.alter_column('planets', 'production', nullable=False)
    op.alter_column('planets', 'production_efficiency', nullable=False)
    op.alter_column('planets', 'defense_level', nullable=False)
    op.alter_column('planets', 'shields', nullable=False)
    op.alter_column('planets', 'weapon_batteries', nullable=False)
    op.alter_column('planets', 'active_events', nullable=False)
    op.alter_column('planets', 'genesis_created', nullable=False)


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint('fk_planets_sector_uuid', 'planets', type_='foreignkey')
    
    # Drop the columns
    op.drop_column('planets', 'sector_uuid')
    op.drop_column('planets', 'last_updated')
    op.drop_column('planets', 'type')
    op.drop_column('planets', 'status')
    op.drop_column('planets', 'size')
    op.drop_column('planets', 'position')
    op.drop_column('planets', 'gravity')
    op.drop_column('planets', 'atmosphere')
    op.drop_column('planets', 'temperature')
    op.drop_column('planets', 'water_coverage')
    op.drop_column('planets', 'habitability_score')
    op.drop_column('planets', 'radiation_level')
    op.drop_column('planets', 'resource_richness')
    op.drop_column('planets', 'resources')
    op.drop_column('planets', 'special_resources')
    op.drop_column('planets', 'colonized_at')
    op.drop_column('planets', 'population')
    op.drop_column('planets', 'max_population')
    op.drop_column('planets', 'population_growth')
    op.drop_column('planets', 'economy')
    op.drop_column('planets', 'production')
    op.drop_column('planets', 'production_efficiency')
    op.drop_column('planets', 'defense_level')
    op.drop_column('planets', 'shields')
    op.drop_column('planets', 'weapon_batteries')
    op.drop_column('planets', 'last_attacked')
    op.drop_column('planets', 'last_production')
    op.drop_column('planets', 'active_events')
    op.drop_column('planets', 'description')
    op.drop_column('planets', 'genesis_created')
    op.drop_column('planets', 'genesis_device_id')
    
    # Drop the enums
    postgresql.ENUM(name='planet_type').drop(op.get_bind())
    postgresql.ENUM(name='planet_status').drop(op.get_bind())