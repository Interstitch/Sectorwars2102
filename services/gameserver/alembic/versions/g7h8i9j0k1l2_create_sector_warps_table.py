"""create sector_warps table

Revision ID: g7h8i9j0k1l2
Revises: f6g7h8i9j0k1
Create Date: 2025-01-23 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'g7h8i9j0k1l2'
down_revision = 'f6g7h8i9j0k1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create sector_warps association table
    op.create_table('sector_warps',
        sa.Column('source_sector_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('destination_sector_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_bidirectional', sa.Boolean(), nullable=False, default=True),
        sa.Column('turn_cost', sa.Integer(), nullable=False, default=1),
        sa.Column('warp_stability', sa.Float(), nullable=False, default=1.0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['source_sector_id'], ['sectors.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['destination_sector_id'], ['sectors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('source_sector_id', 'destination_sector_id')
    )


def downgrade() -> None:
    op.drop_table('sector_warps')