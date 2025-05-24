"""add sector_uuid to ports

Revision ID: d4e5f6a7b8c9
Revises: cd03f6dd4946
Create Date: 2025-01-23 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd4e5f6a7b8c9'
down_revision = 'cd03f6dd4946'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add sector_uuid column to ports table
    op.add_column('ports', sa.Column('sector_uuid', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Create foreign key constraint
    op.create_foreign_key('fk_ports_sector_uuid', 'ports', 'sectors', ['sector_uuid'], ['id'], ondelete='CASCADE')
    
    # Populate sector_uuid based on existing sector_id values
    op.execute("""
        UPDATE ports 
        SET sector_uuid = sectors.id 
        FROM sectors 
        WHERE ports.sector_id = sectors.sector_id
    """)


def downgrade() -> None:
    # Drop foreign key constraint
    op.drop_constraint('fk_ports_sector_uuid', 'ports', type_='foreignkey')
    
    # Drop the column
    op.drop_column('ports', 'sector_uuid')