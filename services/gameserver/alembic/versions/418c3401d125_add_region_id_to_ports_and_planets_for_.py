"""add_region_id_to_ports_and_planets_for_business_territories

Revision ID: 418c3401d125
Revises: 03bab0cdfc79
Create Date: 2025-11-14 03:11:00.714353

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '418c3401d125'
down_revision = '03bab0cdfc79'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add region_id column to ports table for business territory association
    # This references the "regions" table (player-owned business territories),
    # NOT "galaxy_zones" (cosmological zones like Federation/Border/Frontier)
    op.add_column('ports', sa.Column('region_id', sa.UUID(), nullable=True))
    op.create_foreign_key(
        'ports_region_id_fkey',
        'ports', 'regions',
        ['region_id'], ['id'],
        ondelete='SET NULL'
    )

    # Add region_id column to planets table for business territory association
    op.add_column('planets', sa.Column('region_id', sa.UUID(), nullable=True))
    op.create_foreign_key(
        'planets_region_id_fkey',
        'planets', 'regions',
        ['region_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    # Remove foreign keys and columns
    op.drop_constraint('planets_region_id_fkey', 'planets', type_='foreignkey')
    op.drop_column('planets', 'region_id')

    op.drop_constraint('ports_region_id_fkey', 'ports', type_='foreignkey')
    op.drop_column('ports', 'region_id')