"""Add Central Nexus sector fields

Revision ID: n5o6p7q8r9s0
Revises: m4n5o6p7q8r9
Create Date: 2025-06-01 23:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'n5o6p7q8r9s0'
down_revision = 'm4n5o6p7q8r9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add Central Nexus specific fields to sectors table
    op.add_column('sectors', sa.Column('sector_number', sa.Integer, nullable=True))
    op.add_column('sectors', sa.Column('district', sa.String(50), nullable=True))
    op.add_column('sectors', sa.Column('security_level', sa.Integer, nullable=True, default=5))
    op.add_column('sectors', sa.Column('development_level', sa.Integer, nullable=True, default=1))
    op.add_column('sectors', sa.Column('traffic_level', sa.Integer, nullable=True, default=1))
    
    # Add indexes for Central Nexus queries
    op.create_index('idx_sectors_sector_number', 'sectors', ['sector_number'])
    op.create_index('idx_sectors_district', 'sectors', ['district'])
    op.create_index('idx_sectors_security_level', 'sectors', ['security_level'])
    op.create_index('idx_sectors_region_district', 'sectors', ['region_id', 'district'])
    
    # Update existing sectors to have sector_number = sector_id for backward compatibility
    op.execute("UPDATE sectors SET sector_number = sector_id WHERE sector_number IS NULL")
    
    # Add unique constraint on sector_number within region
    op.create_unique_constraint('uq_sectors_region_sector_number', 'sectors', ['region_id', 'sector_number'])


def downgrade() -> None:
    # Drop constraints and indexes
    op.drop_constraint('uq_sectors_region_sector_number', 'sectors')
    op.drop_index('idx_sectors_region_district')
    op.drop_index('idx_sectors_security_level')
    op.drop_index('idx_sectors_district')
    op.drop_index('idx_sectors_sector_number')
    
    # Drop columns
    op.drop_column('sectors', 'traffic_level')
    op.drop_column('sectors', 'development_level')
    op.drop_column('sectors', 'security_level')
    op.drop_column('sectors', 'district')
    op.drop_column('sectors', 'sector_number')