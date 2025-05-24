"""add_colony_ship_and_carrier_to_choice_enums

Revision ID: 42533a92f89e
Revises: fa15ada1398e
Create Date: 2025-05-24 17:03:12.415415

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '42533a92f89e'
down_revision = 'fa15ada1398e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add COLONY_SHIP and CARRIER to ship_choice enum
    op.execute("ALTER TYPE ship_choice ADD VALUE 'COLONY_SHIP'")
    op.execute("ALTER TYPE ship_choice ADD VALUE 'CARRIER'")
    
    # Add COLONY_SHIP and CARRIER to ship_type_config enum  
    op.execute("ALTER TYPE ship_type_config ADD VALUE 'COLONY_SHIP'")
    op.execute("ALTER TYPE ship_type_config ADD VALUE 'CARRIER'")


def downgrade() -> None:
    # Note: PostgreSQL doesn't support removing enum values directly
    # This would require recreating the enum type which is complex with existing data
    # For now, we'll leave the enum values (it's safer)
    pass