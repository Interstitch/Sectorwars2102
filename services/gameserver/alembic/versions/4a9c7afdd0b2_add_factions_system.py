"""add_factions_system

Revision ID: 4a9c7afdd0b2
Revises: 93855ceae44f
Create Date: 2025-05-28 03:22:42.936074

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4a9c7afdd0b2'
down_revision = '93855ceae44f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if factions table already exists
    connection = op.get_bind()
    result = connection.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'factions')"
    ))
    if result.fetchone()[0]:
        # Table already exists, skip
        return
    
    # Create FactionType enum if it doesn't exist
    result = connection.execute(sa.text(
        "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'factiontype')"
    ))
    if not result.fetchone()[0]:
        faction_type_enum = postgresql.ENUM(
            'Federation', 'Independents', 'Pirates', 'Merchants', 'Explorers', 'Military',
            name='factiontype'
        )
        faction_type_enum.create(connection)
    
    # Create factions table
    op.create_table('factions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('faction_type', postgresql.ENUM('Federation', 'Independents', 'Pirates', 'Merchants', 'Explorers', 'Military', name='factiontype', create_type=False), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('territory_sectors', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column('home_sector_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('base_pricing_modifier', sa.Float(), nullable=True),
        sa.Column('trade_specialties', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('aggression_level', sa.Integer(), nullable=True),
        sa.Column('diplomacy_stance', sa.String(length=50), nullable=True),
        sa.Column('color_primary', sa.String(length=7), nullable=True),
        sa.Column('color_secondary', sa.String(length=7), nullable=True),
        sa.Column('logo_url', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_factions_name'), 'factions', ['name'], unique=True)
    
    # Create faction_missions table
    op.create_table('faction_missions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('faction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('mission_type', sa.String(length=50), nullable=False),
        sa.Column('min_reputation', sa.Integer(), nullable=True),
        sa.Column('min_level', sa.Integer(), nullable=True),
        sa.Column('credit_reward', sa.Integer(), nullable=True),
        sa.Column('reputation_reward', sa.Integer(), nullable=True),
        sa.Column('item_rewards', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('target_sector_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('cargo_type', sa.String(length=50), nullable=True),
        sa.Column('cargo_quantity', sa.Integer(), nullable=True),
        sa.Column('target_faction_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_active', sa.Integer(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['faction_id'], ['factions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_faction_missions_faction_id'), 'faction_missions', ['faction_id'], unique=False)
    
    # Insert default factions - no data initially, will be added via API


def downgrade() -> None:
    # Drop tables
    op.drop_index(op.f('ix_faction_missions_faction_id'), table_name='faction_missions')
    op.drop_table('faction_missions')
    op.drop_index(op.f('ix_factions_name'), table_name='factions')
    op.drop_table('factions')
    
    # Drop enum type
    sa.Enum(name='factiontype').drop(op.get_bind())