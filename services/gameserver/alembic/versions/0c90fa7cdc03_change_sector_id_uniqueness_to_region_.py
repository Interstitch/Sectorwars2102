"""change sector_id uniqueness to region_id+sector_id composite

Revision ID: 0c90fa7cdc03
Revises: f31c4c163705
Create Date: 2025-11-15 01:55:39.326174

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c90fa7cdc03'
down_revision = 'f31c4c163705'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the existing unique constraint on sector_id alone
    op.drop_constraint('sectors_sector_id_key', 'sectors', type_='unique')

    # Add composite unique constraint on (region_id, sector_id)
    # This allows each region to have its own sector numbering (1-N)
    op.create_unique_constraint(
        'uq_sectors_region_sector',
        'sectors',
        ['region_id', 'sector_id']
    )


def downgrade() -> None:
    # Reverse the changes
    op.drop_constraint('uq_sectors_region_sector', 'sectors', type_='unique')
    op.create_unique_constraint('sectors_sector_id_key', 'sectors', ['sector_id'])