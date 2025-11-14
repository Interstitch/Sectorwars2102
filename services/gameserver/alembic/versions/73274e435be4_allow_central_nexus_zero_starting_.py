"""allow_central_nexus_zero_starting_credits

Revision ID: 73274e435be4
Revises: a92878120b5b
Create Date: 2025-11-14 04:48:18.354125

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73274e435be4'
down_revision = 'a92878120b5b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Modify valid_starting_credits constraint to allow Central Nexus (nexus tier)
    to have 0 starting credits since it's not a player spawn region.
    Player regions still require >= 100 credits.
    """
    # Drop existing constraint
    op.drop_constraint('valid_starting_credits', 'regions', type_='check')

    # Create new constraint with exception for nexus tier
    op.create_check_constraint(
        'valid_starting_credits',
        'regions',
        """
        (subscription_tier = 'nexus' AND starting_credits = 0)
        OR
        (subscription_tier != 'nexus' AND starting_credits >= 100)
        """
    )


def downgrade() -> None:
    """
    Revert to original constraint requiring all regions to have >= 100 starting credits.
    WARNING: This will prevent Central Nexus from being created if it doesn't already exist.
    """
    # Drop modified constraint
    op.drop_constraint('valid_starting_credits', 'regions', type_='check')

    # Restore original constraint (all regions >= 100 credits)
    op.create_check_constraint(
        'valid_starting_credits',
        'regions',
        'starting_credits >= 100'
    )