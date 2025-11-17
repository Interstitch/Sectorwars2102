"""change planet population columns to bigint

Revision ID: dbbfad27a7ef
Revises: e86cb8130b5b
Create Date: 2025-11-17 03:43:36.504656

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dbbfad27a7ef'
down_revision = 'e86cb8130b5b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Change population and max_population columns from INTEGER to BIGINT
    op.alter_column('planets', 'population',
                    existing_type=sa.Integer(),
                    type_=sa.BigInteger(),
                    existing_nullable=False)
    op.alter_column('planets', 'max_population',
                    existing_type=sa.Integer(),
                    type_=sa.BigInteger(),
                    existing_nullable=False)


def downgrade() -> None:
    # Revert back to INTEGER (this will fail if values exceed INTEGER max)
    op.alter_column('planets', 'max_population',
                    existing_type=sa.BigInteger(),
                    type_=sa.Integer(),
                    existing_nullable=False)
    op.alter_column('planets', 'population',
                    existing_type=sa.BigInteger(),
                    type_=sa.Integer(),
                    existing_nullable=False)