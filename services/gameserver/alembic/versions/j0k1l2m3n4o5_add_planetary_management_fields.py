"""add planetary management fields

Revision ID: j0k1l2m3n4o5
Revises: i9j0k1l2m3n4
Create Date: 2025-05-28 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'j0k1l2m3n4o5'
down_revision = 'i9j0k1l2m3n4'
branch_labels = None
depends_on = None


def upgrade():
    # Add colonization and allocation fields
    op.add_column('planets', sa.Column('colonists', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('planets', sa.Column('max_colonists', sa.Integer(), nullable=False, server_default='10000'))
    op.add_column('planets', sa.Column('fuel_allocation', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('planets', sa.Column('organics_allocation', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('planets', sa.Column('equipment_allocation', sa.Integer(), nullable=False, server_default='0'))
    
    # Add resource storage
    op.add_column('planets', sa.Column('fuel_ore', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('planets', sa.Column('organics', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('planets', sa.Column('equipment', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('planets', sa.Column('fighters', sa.Integer(), nullable=False, server_default='0'))
    
    # Add building levels
    op.add_column('planets', sa.Column('factory_level', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('planets', sa.Column('farm_level', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('planets', sa.Column('mine_level', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('planets', sa.Column('research_level', sa.Integer(), nullable=False, server_default='0'))
    
    # Add defense fields
    op.add_column('planets', sa.Column('defense_turrets', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('planets', sa.Column('defense_shields', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('planets', sa.Column('defense_fighters', sa.Integer(), nullable=False, server_default='0'))
    
    # Add planet type and specialization
    op.add_column('planets', sa.Column('planet_type', sa.String(50), nullable=True))
    op.add_column('planets', sa.Column('specialization', sa.String(50), nullable=True))
    
    # Add siege fields
    op.add_column('planets', sa.Column('under_siege', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('planets', sa.Column('siege_started_at', sa.DateTime(), nullable=True))
    op.add_column('planets', sa.Column('siege_attacker_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Add genesis devices to players table if it doesn't exist
    # Check if column exists first
    from alembic import context
    conn = context.get_bind()
    
    # Check if column already exists
    result = conn.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='players' AND column_name='genesis_devices'
    """)
    
    if not result.fetchone():
        op.add_column('players', sa.Column('genesis_devices', sa.Integer(), nullable=False, server_default='0'))


def downgrade():
    # Remove columns in reverse order
    op.drop_column('players', 'genesis_devices')
    
    op.drop_column('planets', 'siege_attacker_id')
    op.drop_column('planets', 'siege_started_at')
    op.drop_column('planets', 'under_siege')
    
    op.drop_column('planets', 'specialization')
    op.drop_column('planets', 'planet_type')
    
    op.drop_column('planets', 'defense_fighters')
    op.drop_column('planets', 'defense_shields')
    op.drop_column('planets', 'defense_turrets')
    
    op.drop_column('planets', 'research_level')
    op.drop_column('planets', 'mine_level')
    op.drop_column('planets', 'farm_level')
    op.drop_column('planets', 'factory_level')
    
    op.drop_column('planets', 'fighters')
    op.drop_column('planets', 'equipment')
    op.drop_column('planets', 'organics')
    op.drop_column('planets', 'fuel_ore')
    
    op.drop_column('planets', 'equipment_allocation')
    op.drop_column('planets', 'organics_allocation')
    op.drop_column('planets', 'fuel_allocation')
    op.drop_column('planets', 'max_colonists')
    op.drop_column('planets', 'colonists')