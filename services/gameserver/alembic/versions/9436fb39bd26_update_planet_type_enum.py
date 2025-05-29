"""update planet type enum

Revision ID: 9436fb39bd26
Revises: 16fc42aab422
Create Date: 2025-05-29 03:02:45.988791

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9436fb39bd26'
down_revision = '16fc42aab422'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing enum values to planet_type
    op.execute("ALTER TYPE planet_type ADD VALUE 'OCEANIC'")
    op.execute("ALTER TYPE planet_type ADD VALUE 'TROPICAL'")
    op.execute("ALTER TYPE planet_type ADD VALUE 'ARCTIC'")
    op.execute("ALTER TYPE planet_type ADD VALUE 'MOUNTAINOUS'")
    op.execute("ALTER TYPE planet_type ADD VALUE 'ARTIFICIAL'")


def downgrade() -> None:
    # Note: PostgreSQL doesn't support removing enum values directly
    # This would require recreating the enum type
    pass