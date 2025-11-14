"""allow_central_nexus_zero_tax_rate

Revision ID: f31c4c163705
Revises: 73274e435be4
Create Date: 2025-11-14 04:51:11.188942

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f31c4c163705'
down_revision = '73274e435be4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Modify valid_tax_rate constraint to allow Central Nexus (nexus tier)
    to have 0% tax rate since it's a platform-owned galactic hub.
    Player regions still require 5-25% tax rate.
    """
    # Drop existing constraint
    op.drop_constraint('valid_tax_rate', 'regions', type_='check')

    # Create new constraint with exception for nexus tier
    op.create_check_constraint(
        'valid_tax_rate',
        'regions',
        """
        (subscription_tier = 'nexus' AND tax_rate = 0.0)
        OR
        (subscription_tier != 'nexus' AND tax_rate >= 0.05 AND tax_rate <= 0.25)
        """
    )


def downgrade() -> None:
    """
    Revert to original constraint requiring all regions to have 5-25% tax rate.
    WARNING: This will prevent Central Nexus from being created if it doesn't already exist.
    """
    # Drop modified constraint
    op.drop_constraint('valid_tax_rate', 'regions', type_='check')

    # Restore original constraint (all regions 5-25% tax)
    op.create_check_constraint(
        'valid_tax_rate',
        'regions',
        'tax_rate >= 0.05 AND tax_rate <= 0.25'
    )