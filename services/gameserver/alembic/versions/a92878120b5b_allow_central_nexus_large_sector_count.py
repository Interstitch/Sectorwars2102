"""allow_central_nexus_large_sector_count

Revision ID: a92878120b5b
Revises: 418c3401d125
Create Date: 2025-11-14 04:44:49.892569

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a92878120b5b'
down_revision = '418c3401d125'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Modify valid_sector_count constraint to allow Central Nexus (nexus tier)
    to have up to 10,000 sectors while keeping player regions limited to 1,000.
    """
    # Drop existing constraint
    op.drop_constraint('valid_sector_count', 'regions', type_='check')

    # Create new constraint with special exception for nexus tier
    op.create_check_constraint(
        'valid_sector_count',
        'regions',
        """
        (subscription_tier = 'nexus' AND total_sectors >= 100 AND total_sectors <= 10000)
        OR
        (subscription_tier != 'nexus' AND total_sectors >= 100 AND total_sectors <= 1000)
        """
    )


def downgrade() -> None:
    """
    Revert to original constraint that limits all regions to 1,000 sectors max.
    WARNING: This will prevent Central Nexus from being created if it doesn't already exist.
    """
    # Drop modified constraint
    op.drop_constraint('valid_sector_count', 'regions', type_='check')

    # Restore original constraint (100-1000 sectors for all regions)
    op.create_check_constraint(
        'valid_sector_count',
        'regions',
        'total_sectors >= 100 AND total_sectors <= 1000'
    )