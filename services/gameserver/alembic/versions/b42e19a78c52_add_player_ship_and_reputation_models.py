"""add_player_ship_and_reputation_models

Revision ID: b42e19a78c52
Revises: a69c2f372d7e
Create Date: 2026-06-20 14:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'b42e19a78c52'
down_revision = 'a69c2f372d7e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    
    # Check if enum types already exist and try to drop them if needed
    def enum_exists(enum_name):
        result = connection.execute(text(
            "SELECT 1 FROM pg_type WHERE typname = :enum_name"
        ).bindparams(enum_name=enum_name))
        return result.scalar() is not None
    
    def safe_drop_enum(enum_name):
        try:
            connection.execute(text(f"DROP TYPE IF EXISTS {enum_name} CASCADE"))
            return True
        except Exception as e:
            print(f"Warning: Could not drop enum {enum_name}: {e}")
            return False
    
    # Handle each enum type
    enum_types = {
        "ship_type": ['LIGHT_FREIGHTER', 'CARGO_HAULER', 'FAST_COURIER', 'SCOUT_SHIP', 
                     'COLONY_SHIP', 'DEFENDER', 'CARRIER', 'WARP_JUMPER'],
        "failure_type": ['NONE', 'MINOR', 'MAJOR', 'CATASTROPHIC'],
        "upgrade_type": ['ENGINE', 'CARGO_HOLD', 'SHIELD', 'HULL', 'SENSOR', 
                       'DRONE_BAY', 'GENESIS_CONTAINMENT', 'MAINTENANCE_SYSTEM'],
        "insurance_type": ['NONE', 'BASIC', 'STANDARD', 'PREMIUM'],
        "reputation_level": ['PUBLIC_ENEMY', 'CRIMINAL', 'OUTLAW', 'PIRATE', 'SMUGGLER', 
                           'UNTRUSTWORTHY', 'SUSPICIOUS', 'QUESTIONABLE', 'NEUTRAL',
                           'RECOGNIZED', 'ACKNOWLEDGED', 'TRUSTED', 'RESPECTED', 
                           'VALUED', 'HONORED', 'REVERED', 'EXALTED']
    }
    
    for enum_name, values in enum_types.items():
        if enum_exists(enum_name):
            # If the enum exists but has migration issues, try to drop it
            print(f"Enum {enum_name} already exists, attempting to drop it")
            if safe_drop_enum(enum_name):
                print(f"Successfully dropped enum {enum_name}, will recreate")
                # Create the enum using execute directly since we just dropped it
                values_str = "', '".join(values)
                connection.execute(text(f"CREATE TYPE {enum_name} AS ENUM ('{values_str}')"))
        else:
            # Create using SQLAlchemy's method
            enum = sa.Enum(*values, name=enum_name)
            enum.create(connection, checkfirst=True)
    
    # Teams table
    op.create_table('teams',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(80), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('leader_id', UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.Column('reputation_calculation_method', sa.String(20), nullable=False, server_default='AVERAGE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Planets table (simplified for reference)
    op.create_table('planets',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('sector_id', sa.Integer(), nullable=False),
        sa.Column('owner_id', UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Ports table (simplified for reference)
    op.create_table('ports',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('sector_id', sa.Integer(), nullable=False),
        sa.Column('owner_id', UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Players table
    op.create_table('players',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('nickname', sa.String(50), nullable=True),
        sa.Column('credits', sa.Integer(), nullable=False, server_default='10000'),
        sa.Column('turns', sa.Integer(), nullable=False, server_default='1000'),
        sa.Column('reputation', JSONB, nullable=False, server_default='{}'),
        sa.Column('current_ship_id', UUID(as_uuid=True), nullable=True),
        sa.Column('home_sector_id', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('current_sector_id', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_ported', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_landed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('team_id', UUID(as_uuid=True), nullable=True),
        sa.Column('attack_drones', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('defense_drones', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('mines', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('insurance', JSONB, nullable=True),
        sa.Column('last_game_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('turn_reset_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('settings', JSONB, nullable=False, server_default='{}'),
        sa.Column('first_login', JSONB, nullable=False, server_default='{"completed": false}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Ships table
    op.create_table('ships',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('type', sa.Enum('LIGHT_FREIGHTER', 'CARGO_HAULER', 'FAST_COURIER', 'SCOUT_SHIP', 
                                 'COLONY_SHIP', 'DEFENDER', 'CARRIER', 'WARP_JUMPER',
                                 name='ship_type'), nullable=False),
        sa.Column('owner_id', UUID(as_uuid=True), nullable=False),
        sa.Column('sector_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.Column('base_speed', sa.Float(), nullable=False),
        sa.Column('current_speed', sa.Float(), nullable=False),
        sa.Column('turn_cost', sa.Integer(), nullable=False),
        sa.Column('warp_capable', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('maintenance', JSONB, nullable=False),
        sa.Column('cargo', JSONB, nullable=False),
        sa.Column('has_cloaking', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('genesis_devices', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_genesis_devices', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('mines', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_mines', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('has_automated_maintenance', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('combat', JSONB, nullable=False),
        sa.Column('upgrades', JSONB, nullable=False, server_default='[]'),
        sa.Column('insurance', JSONB, nullable=True),
        sa.Column('is_destroyed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_flagship', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('purchase_value', sa.Integer(), nullable=False),
        sa.Column('current_value', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['players.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Update players table to reference flagship ship
    op.create_foreign_key(
        'fk_player_current_ship', 
        'players', 'ships',
        ['current_ship_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Reputation table
    op.create_table('reputations',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('player_id', UUID(as_uuid=True), nullable=False),
        sa.Column('faction_id', sa.String(50), nullable=False),
        sa.Column('current_value', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('current_level', sa.Enum('PUBLIC_ENEMY', 'CRIMINAL', 'OUTLAW', 'PIRATE', 'SMUGGLER', 
                                 'UNTRUSTWORTHY', 'SUSPICIOUS', 'QUESTIONABLE', 'NEUTRAL',
                                 'RECOGNIZED', 'ACKNOWLEDGED', 'TRUSTED', 'RESPECTED', 
                                 'VALUED', 'HONORED', 'REVERED', 'EXALTED',
                                 name='reputation_level'), nullable=False, server_default='NEUTRAL'),
        sa.Column('title', sa.String(50), nullable=False, server_default='Neutral'),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('decay_paused', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('history', JSONB, nullable=False, server_default='[]'),
        sa.Column('trade_modifier', sa.Float(), nullable=False, server_default='0'),
        sa.Column('mission_availability', JSONB, nullable=False, server_default='[]'),
        sa.Column('port_access_level', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('combat_response', sa.String(50), nullable=False, server_default='neutral'),
        sa.Column('is_locked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('lock_reason', sa.String(255), nullable=True),
        sa.Column('lock_expires', sa.DateTime(timezone=True), nullable=True),
        sa.Column('special_status', sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('player_id', 'faction_id', name='uq_player_faction_reputation')
    )
    
    # Team reputation table
    op.create_table('team_reputations',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', UUID(as_uuid=True), nullable=False),
        sa.Column('calculation_method', sa.String(20), nullable=False, server_default='AVERAGE'),
        sa.Column('faction_reputation', JSONB, nullable=False, server_default='{}'),
        sa.Column('history', JSONB, nullable=False, server_default='[]'),
        sa.Column('last_recalculated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('next_recalculation', sa.DateTime(timezone=True), nullable=False),
        sa.Column('pending_notifications', JSONB, nullable=False, server_default='[]'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id')
    )
    
    # Player-owned planets relation
    op.create_table('player_planets',
        sa.Column('player_id', UUID(as_uuid=True), nullable=False),
        sa.Column('planet_id', UUID(as_uuid=True), nullable=False),
        sa.Column('acquired_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['planet_id'], ['planets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('player_id', 'planet_id')
    )
    
    # Player-owned ports relation
    op.create_table('player_ports',
        sa.Column('player_id', UUID(as_uuid=True), nullable=False),
        sa.Column('port_id', UUID(as_uuid=True), nullable=False),
        sa.Column('acquired_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['port_id'], ['ports.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('player_id', 'port_id')
    )
    
    # Ship specifications table
    op.create_table('ship_specifications',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.Enum('LIGHT_FREIGHTER', 'CARGO_HAULER', 'FAST_COURIER', 'SCOUT_SHIP', 
                                 'COLONY_SHIP', 'DEFENDER', 'CARRIER', 'WARP_JUMPER',
                                 name='ship_type'), nullable=False),
        sa.Column('base_cost', sa.Integer(), nullable=False),
        sa.Column('speed', sa.Float(), nullable=False),
        sa.Column('turn_cost', sa.Integer(), nullable=False),
        sa.Column('max_cargo', sa.Integer(), nullable=False),
        sa.Column('max_colonists', sa.Integer(), nullable=False),
        sa.Column('max_drones', sa.Integer(), nullable=False),
        sa.Column('max_shields', sa.Integer(), nullable=False),
        sa.Column('shield_recharge_rate', sa.Float(), nullable=False),
        sa.Column('hull_points', sa.Integer(), nullable=False),
        sa.Column('evasion', sa.Integer(), nullable=False),
        sa.Column('radar_range', sa.Integer(), nullable=False),
        sa.Column('max_weapons', sa.Integer(), nullable=False),
        sa.Column('max_upgrades', sa.Integer(), nullable=False),
        sa.Column('is_warp_capable', sa.Boolean(), nullable=False),
        sa.Column('is_military', sa.Boolean(), nullable=False),
        sa.Column('is_civilian', sa.Boolean(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('maintenance_cost', sa.Integer(), nullable=False),
        sa.Column('insurance_multiplier', sa.Float(), nullable=False),
        sa.Column('resale_value_multiplier', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_players_team_id'), 'players', ['team_id'], unique=False)
    op.create_index(op.f('ix_players_user_id'), 'players', ['user_id'], unique=True)
    op.create_index(op.f('ix_ships_owner_id'), 'ships', ['owner_id'], unique=False)
    op.create_index(op.f('ix_ships_sector_id'), 'ships', ['sector_id'], unique=False)
    op.create_index(op.f('ix_reputations_player_id'), 'reputations', ['player_id'], unique=False)
    op.create_index(op.f('ix_team_reputations_team_id'), 'team_reputations', ['team_id'], unique=True)
    op.create_index(op.f('ix_planets_sector_id'), 'planets', ['sector_id'], unique=False)
    op.create_index(op.f('ix_ports_sector_id'), 'ports', ['sector_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order of dependencies
    op.drop_table('player_ports')
    op.drop_table('player_planets')
    op.drop_table('ship_specifications')
    op.drop_table('team_reputations')
    op.drop_table('reputations')
    op.drop_table('ships')
    op.drop_table('players')
    op.drop_table('ports')
    op.drop_table('planets')
    op.drop_table('teams')
    
    # Drop the ENUM types
    op.execute('DROP TYPE IF EXISTS ship_type')
    op.execute('DROP TYPE IF EXISTS failure_type')
    op.execute('DROP TYPE IF EXISTS upgrade_type')
    op.execute('DROP TYPE IF EXISTS insurance_type')
    op.execute('DROP TYPE IF EXISTS reputation_level') 