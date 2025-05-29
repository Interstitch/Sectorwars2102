"""add_fleet_battle_system

Revision ID: 28492992f0a8
Revises: 1baaead3ff00
Create Date: 2025-05-28 04:09:38.918065

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '28492992f0a8'
down_revision = '1baaead3ff00'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create fleets table
    op.create_table('fleets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('commander_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('formation', sa.String(length=50), nullable=True),
        sa.Column('sector_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('total_ships', sa.Integer(), nullable=False),
        sa.Column('total_firepower', sa.Integer(), nullable=False),
        sa.Column('total_shields', sa.Integer(), nullable=False),
        sa.Column('total_hull', sa.Integer(), nullable=False),
        sa.Column('average_speed', sa.Float(), nullable=False),
        sa.Column('morale', sa.Integer(), nullable=False),
        sa.Column('supply_level', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('disbanded_at', sa.DateTime(), nullable=True),
        sa.Column('last_battle', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['commander_id'], ['players.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['sector_id'], ['sectors.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fleets_sector_id'), 'fleets', ['sector_id'], unique=False)
    op.create_index(op.f('ix_fleets_team_id'), 'fleets', ['team_id'], unique=False)
    
    # Create fleet_members table
    op.create_table('fleet_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('fleet_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ship_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('position', sa.Integer(), nullable=True),
        sa.Column('joined_at', sa.DateTime(), nullable=True),
        sa.Column('ready_status', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['fleet_id'], ['fleets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ship_id'], ['ships.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fleet_members_fleet_id'), 'fleet_members', ['fleet_id'], unique=False)
    op.create_index(op.f('ix_fleet_members_player_id'), 'fleet_members', ['player_id'], unique=False)
    op.create_index(op.f('ix_fleet_members_ship_id'), 'fleet_members', ['ship_id'], unique=False)
    
    # Create fleet_battles table
    op.create_table('fleet_battles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('attacker_fleet_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('defender_fleet_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('sector_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('phase', sa.String(length=50), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('attacker_ships_initial', sa.Integer(), nullable=True),
        sa.Column('defender_ships_initial', sa.Integer(), nullable=True),
        sa.Column('winner', sa.String(length=20), nullable=True),
        sa.Column('attacker_ships_destroyed', sa.Integer(), nullable=True),
        sa.Column('defender_ships_destroyed', sa.Integer(), nullable=True),
        sa.Column('attacker_ships_retreated', sa.Integer(), nullable=True),
        sa.Column('defender_ships_retreated', sa.Integer(), nullable=True),
        sa.Column('total_damage_dealt', sa.Integer(), nullable=True),
        sa.Column('attacker_damage_dealt', sa.Integer(), nullable=True),
        sa.Column('defender_damage_dealt', sa.Integer(), nullable=True),
        sa.Column('battle_log', sa.JSON(), nullable=True),
        sa.Column('credits_looted', sa.Integer(), nullable=True),
        sa.Column('resources_looted', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['attacker_fleet_id'], ['fleets.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['defender_fleet_id'], ['fleets.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['sector_id'], ['sectors.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create fleet_battle_casualties table
    op.create_table('fleet_battle_casualties',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('battle_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ship_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('fleet_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ship_name', sa.String(length=100), nullable=True),
        sa.Column('ship_type', sa.String(length=50), nullable=True),
        sa.Column('was_attacker', sa.Boolean(), nullable=True),
        sa.Column('destroyed', sa.Boolean(), nullable=True),
        sa.Column('retreated', sa.Boolean(), nullable=True),
        sa.Column('damage_taken', sa.Integer(), nullable=True),
        sa.Column('damage_dealt', sa.Integer(), nullable=True),
        sa.Column('kills', sa.Integer(), nullable=True),
        sa.Column('casualty_time', sa.DateTime(), nullable=True),
        sa.Column('battle_phase', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['battle_id'], ['fleet_battles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['fleet_id'], ['fleets.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['ship_id'], ['ships.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fleet_battle_casualties_battle_id'), 'fleet_battle_casualties', ['battle_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_fleet_battle_casualties_battle_id'), table_name='fleet_battle_casualties')
    op.drop_table('fleet_battle_casualties')
    op.drop_table('fleet_battles')
    op.drop_index(op.f('ix_fleet_members_ship_id'), table_name='fleet_members')
    op.drop_index(op.f('ix_fleet_members_player_id'), table_name='fleet_members')
    op.drop_index(op.f('ix_fleet_members_fleet_id'), table_name='fleet_members')
    op.drop_table('fleet_members')
    op.drop_index(op.f('ix_fleets_team_id'), table_name='fleets')
    op.drop_index(op.f('ix_fleets_sector_id'), table_name='fleets')
    op.drop_table('fleets')