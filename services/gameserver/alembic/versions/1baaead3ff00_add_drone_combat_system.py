"""add_drone_combat_system

Revision ID: 1baaead3ff00
Revises: ecc8d2f023f2
Create Date: 2025-05-28 03:48:07.087211

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1baaead3ff00'
down_revision = 'ecc8d2f023f2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create drones table with string columns instead of enums
    op.create_table('drones',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('drone_type', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('health', sa.Integer(), nullable=False),
        sa.Column('max_health', sa.Integer(), nullable=False),
        sa.Column('attack_power', sa.Integer(), nullable=False),
        sa.Column('defense_power', sa.Integer(), nullable=False),
        sa.Column('speed', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('sector_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('deployed_at', sa.DateTime(), nullable=True),
        sa.Column('last_action', sa.DateTime(), nullable=True),
        sa.Column('kills', sa.Integer(), nullable=False),
        sa.Column('damage_dealt', sa.Integer(), nullable=False),
        sa.Column('damage_taken', sa.Integer(), nullable=False),
        sa.Column('battles_fought', sa.Integer(), nullable=False),
        sa.Column('abilities', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('destroyed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sector_id'], ['sectors.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_drones_player_id'), 'drones', ['player_id'], unique=False)
    op.create_index(op.f('ix_drones_sector_id'), 'drones', ['sector_id'], unique=False)
    op.create_index(op.f('ix_drones_team_id'), 'drones', ['team_id'], unique=False)
    
    # Create drone_deployments table
    op.create_table('drone_deployments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('drone_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sector_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('deployed_at', sa.DateTime(), nullable=False),
        sa.Column('recalled_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('deployment_type', sa.String(length=50), nullable=True),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('enemies_destroyed', sa.Integer(), nullable=True),
        sa.Column('resources_collected', sa.Integer(), nullable=True),
        sa.Column('damage_prevented', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['drone_id'], ['drones.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sector_id'], ['sectors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_drone_deployments_drone_id'), 'drone_deployments', ['drone_id'], unique=False)
    op.create_index(op.f('ix_drone_deployments_player_id'), 'drone_deployments', ['player_id'], unique=False)
    op.create_index(op.f('ix_drone_deployments_sector_id'), 'drone_deployments', ['sector_id'], unique=False)
    
    # Create drone_combats table
    op.create_table('drone_combats',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('attacker_drone_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('defender_drone_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('sector_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('rounds', sa.Integer(), nullable=True),
        sa.Column('winner_drone_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('attacker_damage_dealt', sa.Integer(), nullable=True),
        sa.Column('defender_damage_dealt', sa.Integer(), nullable=True),
        sa.Column('combat_log', sa.String(length=2000), nullable=True),
        sa.ForeignKeyConstraint(['attacker_drone_id'], ['drones.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['defender_drone_id'], ['drones.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['sector_id'], ['sectors.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop tables
    op.drop_table('drone_combats')
    op.drop_index(op.f('ix_drone_deployments_sector_id'), table_name='drone_deployments')
    op.drop_index(op.f('ix_drone_deployments_player_id'), table_name='drone_deployments')
    op.drop_index(op.f('ix_drone_deployments_drone_id'), table_name='drone_deployments')
    op.drop_table('drone_deployments')
    op.drop_index(op.f('ix_drones_team_id'), table_name='drones')
    op.drop_index(op.f('ix_drones_sector_id'), table_name='drones')
    op.drop_index(op.f('ix_drones_player_id'), table_name='drones')
    op.drop_table('drones')