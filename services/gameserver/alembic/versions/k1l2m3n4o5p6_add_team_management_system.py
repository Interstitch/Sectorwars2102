"""Add team management system

Revision ID: k1l2m3n4o5p6
Revises: j0k1l2m3n4o5
Create Date: 2025-05-28 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'k1l2m3n4o5p6'
down_revision = 'j0k1l2m3n4o5'
branch_labels = None
depends_on = None


def upgrade():
    # Create team_members table
    op.create_table(
        'team_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('permissions', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('can_invite', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('can_kick', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('can_manage_treasury', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('can_manage_missions', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('can_manage_alliances', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('last_active', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('contribution_credits', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for team_members
    op.create_index(op.f('ix_team_members_player_id'), 'team_members', ['player_id'], unique=False)
    op.create_index(op.f('ix_team_members_team_id'), 'team_members', ['team_id'], unique=False)
    op.create_index(op.f('ix_team_members_role'), 'team_members', ['role'], unique=False)
    
    # Add unique constraint for player-team combination
    op.create_unique_constraint('uq_team_members_team_player', 'team_members', ['team_id', 'player_id'])
    
    # Add new columns to teams table
    op.add_column('teams', sa.Column('recruitment_status', sa.String(20), nullable=False, server_default='OPEN'))
    
    # Treasury columns
    op.add_column('teams', sa.Column('treasury_credits', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('teams', sa.Column('treasury_fuel', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('teams', sa.Column('treasury_organics', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('teams', sa.Column('treasury_equipment', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('teams', sa.Column('treasury_technology', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('teams', sa.Column('treasury_luxury_items', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('teams', sa.Column('treasury_precious_metals', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('teams', sa.Column('treasury_raw_materials', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('teams', sa.Column('treasury_plasma', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('teams', sa.Column('treasury_bio_samples', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('teams', sa.Column('treasury_dark_matter', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('teams', sa.Column('treasury_quantum_crystals', sa.Integer(), nullable=False, server_default='0'))
    
    # Additional team management columns
    op.add_column('teams', sa.Column('invitation_codes', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'))
    
    # Update messages table to ensure team_id column exists with proper constraints
    # First check if column exists
    connection = op.get_bind()
    result = connection.execute(
        "SELECT column_name FROM information_schema.columns WHERE table_name='messages' AND column_name='team_id'"
    )
    if not result.fetchone():
        op.add_column('messages', sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=True))
        op.create_foreign_key('fk_messages_team_id', 'messages', 'teams', ['team_id'], ['id'])
        op.create_index(op.f('ix_messages_team_id'), 'messages', ['team_id'], unique=False)


def downgrade():
    # Remove indexes from messages
    op.drop_index(op.f('ix_messages_team_id'), table_name='messages')
    op.drop_constraint('fk_messages_team_id', 'messages', type_='foreignkey')
    op.drop_column('messages', 'team_id')
    
    # Remove team management columns
    op.drop_column('teams', 'invitation_codes')
    
    # Remove treasury columns
    op.drop_column('teams', 'treasury_quantum_crystals')
    op.drop_column('teams', 'treasury_dark_matter')
    op.drop_column('teams', 'treasury_bio_samples')
    op.drop_column('teams', 'treasury_plasma')
    op.drop_column('teams', 'treasury_raw_materials')
    op.drop_column('teams', 'treasury_precious_metals')
    op.drop_column('teams', 'treasury_luxury_items')
    op.drop_column('teams', 'treasury_technology')
    op.drop_column('teams', 'treasury_equipment')
    op.drop_column('teams', 'treasury_organics')
    op.drop_column('teams', 'treasury_fuel')
    op.drop_column('teams', 'treasury_credits')
    op.drop_column('teams', 'recruitment_status')
    
    # Drop team_members table
    op.drop_constraint('uq_team_members_team_player', 'team_members', type_='unique')
    op.drop_index(op.f('ix_team_members_role'), table_name='team_members')
    op.drop_index(op.f('ix_team_members_team_id'), table_name='team_members')
    op.drop_index(op.f('ix_team_members_player_id'), table_name='team_members')
    op.drop_table('team_members')