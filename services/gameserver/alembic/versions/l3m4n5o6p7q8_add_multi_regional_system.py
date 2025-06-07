"""Add multi-regional system

Revision ID: l3m4n5o6p7q8
Revises: k1l2m3n4o5p6
Create Date: 2025-06-01 21:50:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'l3m4n5o6p7q8'
down_revision = 'k1l2m3n4o5p6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create regions table
    op.create_table('regions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('subscription_tier', sa.String(50), nullable=False, server_default='standard'),
        sa.Column('paypal_subscription_id', sa.String(255), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        
        # Governance Configuration
        sa.Column('governance_type', sa.String(50), nullable=False, server_default='autocracy'),
        sa.Column('voting_threshold', sa.DECIMAL(3,2), nullable=False, server_default='0.51'),
        sa.Column('election_frequency_days', sa.Integer, nullable=False, server_default='90'),
        sa.Column('constitutional_text', sa.Text, nullable=True),
        
        # Economic Configuration
        sa.Column('tax_rate', sa.DECIMAL(5,4), nullable=False, server_default='0.10'),
        sa.Column('trade_bonuses', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('economic_specialization', sa.String(50), nullable=True),
        sa.Column('starting_credits', sa.Integer, nullable=False, server_default='1000'),
        sa.Column('starting_ship', sa.String(50), nullable=False, server_default='scout'),
        
        # Cultural Identity
        sa.Column('language_pack', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('aesthetic_theme', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('traditions', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('social_hierarchy', postgresql.JSONB, nullable=False, server_default='{}'),
        
        # Infrastructure
        sa.Column('nexus_warp_gate_sector', sa.Integer, nullable=True),
        sa.Column('total_sectors', sa.Integer, nullable=False, server_default='500'),
        sa.Column('active_players_30d', sa.Integer, nullable=False, server_default='0'),
        sa.Column('total_trade_volume', sa.DECIMAL(20,2), nullable=False, server_default='0.0'),
        
        sa.CheckConstraint('voting_threshold >= 0.1 AND voting_threshold <= 0.9', name='valid_voting_threshold'),
        sa.CheckConstraint('tax_rate >= 0.05 AND tax_rate <= 0.25', name='valid_tax_rate'),
        sa.CheckConstraint('election_frequency_days >= 30 AND election_frequency_days <= 365', name='valid_election_frequency'),
        sa.CheckConstraint('starting_credits >= 100', name='valid_starting_credits'),
        sa.CheckConstraint('total_sectors >= 100 AND total_sectors <= 1000', name='valid_sector_count')
    )
    
    # Create regional memberships table
    op.create_table('regional_memberships',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('players.id'), nullable=False),
        sa.Column('region_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('regions.id'), nullable=False),
        sa.Column('membership_type', sa.String(50), nullable=False, server_default='visitor'),
        sa.Column('reputation_score', sa.Integer, nullable=False, server_default='0'),
        sa.Column('local_rank', sa.String(50), nullable=True),
        sa.Column('voting_power', sa.DECIMAL(5,4), nullable=False, server_default='1.0'),
        sa.Column('joined_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_visit', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('total_visits', sa.Integer, nullable=False, server_default='0'),
        
        sa.UniqueConstraint('player_id', 'region_id', name='unique_membership'),
        sa.CheckConstraint('voting_power >= 0.0 AND voting_power <= 5.0', name='valid_voting_power'),
        sa.CheckConstraint('reputation_score >= -1000 AND reputation_score <= 1000', name='valid_reputation')
    )
    
    # Create inter-regional travels table
    op.create_table('inter_regional_travels',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('player_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('players.id'), nullable=False),
        sa.Column('source_region_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('regions.id'), nullable=False),
        sa.Column('destination_region_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('regions.id'), nullable=False),
        sa.Column('travel_method', sa.String(50), nullable=False),
        sa.Column('travel_cost', sa.Integer, nullable=False, server_default='0'),
        sa.Column('assets_transferred', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('initiated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('completed_at', sa.TIMESTAMP, nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='in_transit'),
        
        sa.CheckConstraint('source_region_id != destination_region_id', name='different_regions'),
        sa.CheckConstraint('travel_cost >= 0', name='non_negative_cost')
    )
    
    # Create regional treaties table
    op.create_table('regional_treaties',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('region_a_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('regions.id'), nullable=False),
        sa.Column('region_b_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('regions.id'), nullable=False),
        sa.Column('treaty_type', sa.String(50), nullable=False),
        sa.Column('terms', postgresql.JSONB, nullable=False),
        sa.Column('signed_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('expires_at', sa.TIMESTAMP, nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='active'),
        
        sa.UniqueConstraint('region_a_id', 'region_b_id', 'treaty_type', name='unique_treaty'),
        sa.CheckConstraint('region_a_id != region_b_id', name='different_treaty_regions')
    )
    
    # Create regional elections table
    op.create_table('regional_elections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('region_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('regions.id'), nullable=False),
        sa.Column('position', sa.String(50), nullable=False),
        sa.Column('candidates', postgresql.JSONB, nullable=False),
        sa.Column('voting_opens_at', sa.TIMESTAMP, nullable=False),
        sa.Column('voting_closes_at', sa.TIMESTAMP, nullable=False),
        sa.Column('results', postgresql.JSONB, nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        
        sa.CheckConstraint('voting_closes_at > voting_opens_at', name='valid_election_period')
    )
    
    # Create regional votes table
    op.create_table('regional_votes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('election_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('regional_elections.id'), nullable=False),
        sa.Column('voter_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('players.id'), nullable=False),
        sa.Column('candidate_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('players.id'), nullable=False),
        sa.Column('weight', sa.DECIMAL(5,4), nullable=False, server_default='1.0'),
        sa.Column('cast_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        
        sa.UniqueConstraint('election_id', 'voter_id', name='one_vote_per_election'),
        sa.CheckConstraint('weight >= 0.0 AND weight <= 5.0', name='valid_vote_weight')
    )
    
    # Create regional policies table
    op.create_table('regional_policies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('region_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('regions.id'), nullable=False),
        sa.Column('policy_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('proposed_changes', postgresql.JSONB, nullable=False),
        sa.Column('proposed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('players.id'), nullable=False),
        sa.Column('proposed_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('voting_closes_at', sa.TIMESTAMP, nullable=False),
        sa.Column('votes_for', sa.Integer, nullable=False, server_default='0'),
        sa.Column('votes_against', sa.Integer, nullable=False, server_default='0'),
        sa.Column('status', sa.String(50), nullable=False, server_default='voting'),
        
        sa.CheckConstraint('voting_closes_at > proposed_at', name='valid_voting_period'),
        sa.CheckConstraint('votes_for >= 0', name='non_negative_votes_for'),
        sa.CheckConstraint('votes_against >= 0', name='non_negative_votes_against')
    )
    
    # Add region_id column to existing tables for regional isolation
    op.add_column('sectors', sa.Column('region_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('planets', sa.Column('region_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('ports', sa.Column('region_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('ships', sa.Column('region_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('players', sa.Column('home_region_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('players', sa.Column('current_region_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('players', sa.Column('is_galactic_citizen', sa.Boolean, nullable=False, server_default='false'))
    
    # Create foreign key constraints for regional associations
    op.create_foreign_key('fk_sectors_region', 'sectors', 'regions', ['region_id'], ['id'])
    op.create_foreign_key('fk_planets_region', 'planets', 'regions', ['region_id'], ['id'])
    op.create_foreign_key('fk_ports_region', 'ports', 'regions', ['region_id'], ['id'])
    op.create_foreign_key('fk_ships_region', 'ships', 'regions', ['region_id'], ['id'])
    op.create_foreign_key('fk_players_home_region', 'players', 'regions', ['home_region_id'], ['id'])
    op.create_foreign_key('fk_players_current_region', 'players', 'regions', ['current_region_id'], ['id'])
    
    # Create indexes for efficient regional queries
    op.create_index('idx_sectors_region_id', 'sectors', ['region_id'])
    op.create_index('idx_planets_region_id', 'planets', ['region_id'])
    op.create_index('idx_ports_region_id', 'ports', ['region_id'])
    op.create_index('idx_ships_region_id', 'ships', ['region_id'])
    op.create_index('idx_players_home_region', 'players', ['home_region_id'])
    op.create_index('idx_players_current_region', 'players', ['current_region_id'])
    op.create_index('idx_regional_memberships_player', 'regional_memberships', ['player_id'])
    op.create_index('idx_regional_memberships_region', 'regional_memberships', ['region_id'])
    op.create_index('idx_inter_regional_travels_player', 'inter_regional_travels', ['player_id'])
    op.create_index('idx_inter_regional_travels_status', 'inter_regional_travels', ['status'])
    op.create_index('idx_regional_elections_region', 'regional_elections', ['region_id'])
    op.create_index('idx_regional_policies_region', 'regional_policies', ['region_id'])
    op.create_index('idx_regional_policies_status', 'regional_policies', ['status'])
    
    # Add sectors table district column for Central Nexus
    op.add_column('sectors', sa.Column('district', sa.String(50), nullable=True))
    op.create_index('idx_sectors_district', 'sectors', ['district'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_sectors_district')
    op.drop_index('idx_regional_policies_status')
    op.drop_index('idx_regional_policies_region')
    op.drop_index('idx_regional_elections_region')
    op.drop_index('idx_inter_regional_travels_status')
    op.drop_index('idx_inter_regional_travels_player')
    op.drop_index('idx_regional_memberships_region')
    op.drop_index('idx_regional_memberships_player')
    op.drop_index('idx_players_current_region')
    op.drop_index('idx_players_home_region')
    op.drop_index('idx_ships_region_id')
    op.drop_index('idx_ports_region_id')
    op.drop_index('idx_planets_region_id')
    op.drop_index('idx_sectors_region_id')
    
    # Drop foreign key constraints
    op.drop_constraint('fk_players_current_region', 'players', type_='foreignkey')
    op.drop_constraint('fk_players_home_region', 'players', type_='foreignkey')
    op.drop_constraint('fk_ships_region', 'ships', type_='foreignkey')
    op.drop_constraint('fk_ports_region', 'ports', type_='foreignkey')
    op.drop_constraint('fk_planets_region', 'planets', type_='foreignkey')
    op.drop_constraint('fk_sectors_region', 'sectors', type_='foreignkey')
    
    # Drop columns from existing tables
    op.drop_column('sectors', 'district')
    op.drop_column('players', 'is_galactic_citizen')
    op.drop_column('players', 'current_region_id')
    op.drop_column('players', 'home_region_id')
    op.drop_column('ships', 'region_id')
    op.drop_column('ports', 'region_id')
    op.drop_column('planets', 'region_id')
    op.drop_column('sectors', 'region_id')
    
    # Drop new tables
    op.drop_table('regional_policies')
    op.drop_table('regional_votes')
    op.drop_table('regional_elections')
    op.drop_table('regional_treaties')
    op.drop_table('inter_regional_travels')
    op.drop_table('regional_memberships')
    op.drop_table('regions')