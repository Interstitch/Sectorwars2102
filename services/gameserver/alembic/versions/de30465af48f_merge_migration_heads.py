"""merge migration heads

Revision ID: de30465af48f
Revises: 4fc08fd7a388, n5o6p7q8r9s0
Create Date: 2025-06-02 04:02:25.158299

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'de30465af48f'
down_revision = ('4fc08fd7a388', 'n5o6p7q8r9s0')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass