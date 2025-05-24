"""add_escape_pod_to_ship_types

Revision ID: 504afbbd4d77
Revises: 467070aeef95
Create Date: 2025-05-24 16:44:50.604178

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '504afbbd4d77'
down_revision = '467070aeef95'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add ESCAPE_POD to the ship_type enum
    op.execute("ALTER TYPE ship_type ADD VALUE 'ESCAPE_POD'")


def downgrade() -> None:
    # Note: PostgreSQL doesn't support removing enum values directly
    # This would require recreating the enum type which is complex with existing data
    # For now, we'll leave the enum value (it's safer)
    pass