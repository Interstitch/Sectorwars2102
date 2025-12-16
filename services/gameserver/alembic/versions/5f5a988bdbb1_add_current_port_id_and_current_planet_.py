"""add current_port_id and current_planet_id to players

Revision ID: 5f5a988bdbb1
Revises: 2e78250f47bc
Create Date: 2025-12-07 00:11:21.249737

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '5f5a988bdbb1'
down_revision = '2e78250f47bc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add current_port_id column to track which station player is docked at
    op.add_column('players', sa.Column('current_port_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_players_current_port_id_stations',
        'players', 'stations',
        ['current_port_id'], ['id'],
        ondelete='SET NULL'
    )

    # Add current_planet_id column to track which planet player is landed on
    op.add_column('players', sa.Column('current_planet_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        'fk_players_current_planet_id_planets',
        'players', 'planets',
        ['current_planet_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint('fk_players_current_planet_id_planets', 'players', type_='foreignkey')
    op.drop_column('players', 'current_planet_id')

    op.drop_constraint('fk_players_current_port_id_stations', 'players', type_='foreignkey')
    op.drop_column('players', 'current_port_id')