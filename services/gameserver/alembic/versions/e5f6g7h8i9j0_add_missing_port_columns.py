"""add missing port columns

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6a7b8c9
Create Date: 2025-01-23 12:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e5f6g7h8i9j0'
down_revision = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    port_type = postgresql.ENUM('TRADING', 'MILITARY', 'INDUSTRIAL', 'MINING', 'SCIENTIFIC', 'SHIPYARD', 'OUTPOST', 'BLACK_MARKET', 'DIPLOMATIC', 'CORPORATE', name='port_type')
    port_status = postgresql.ENUM('OPERATIONAL', 'DAMAGED', 'UNDER_CONSTRUCTION', 'UNDER_ATTACK', 'LOCKDOWN', 'ABANDONED', 'RESTRICTED', name='port_status')
    
    port_type.create(op.get_bind())
    port_status.create(op.get_bind())
    
    # Add missing columns to ports table
    op.add_column('ports', sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.add_column('ports', sa.Column('type', sa.Enum('TRADING', 'MILITARY', 'INDUSTRIAL', 'MINING', 'SCIENTIFIC', 'SHIPYARD', 'OUTPOST', 'BLACK_MARKET', 'DIPLOMATIC', 'CORPORATE', name='port_type'), nullable=True))
    op.add_column('ports', sa.Column('status', sa.Enum('OPERATIONAL', 'DAMAGED', 'UNDER_CONSTRUCTION', 'UNDER_ATTACK', 'LOCKDOWN', 'ABANDONED', 'RESTRICTED', name='port_status'), nullable=True))
    op.add_column('ports', sa.Column('size', sa.Integer(), nullable=True))
    op.add_column('ports', sa.Column('faction_affiliation', sa.String(), nullable=True))
    op.add_column('ports', sa.Column('trade_volume', sa.Integer(), nullable=True))
    op.add_column('ports', sa.Column('price_modifiers', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('ports', sa.Column('import_restrictions', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('ports', sa.Column('export_restrictions', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('ports', sa.Column('services', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('ports', sa.Column('service_prices', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('ports', sa.Column('tax_rate', sa.Float(), nullable=True))
    op.add_column('ports', sa.Column('defense_level', sa.Integer(), nullable=True))
    op.add_column('ports', sa.Column('shields', sa.Integer(), nullable=True))
    op.add_column('ports', sa.Column('defense_weapons', sa.Integer(), nullable=True))
    op.add_column('ports', sa.Column('security_rating', sa.Float(), nullable=True))
    op.add_column('ports', sa.Column('last_attacked', sa.DateTime(timezone=True), nullable=True))
    op.add_column('ports', sa.Column('active_events', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('ports', sa.Column('description', sa.String(), nullable=True))
    op.add_column('ports', sa.Column('special_features', postgresql.ARRAY(sa.String()), nullable=True))
    
    # Set default values for existing rows
    op.execute("""
        UPDATE ports SET
            type = 'TRADING',
            status = 'OPERATIONAL',
            size = 5,
            trade_volume = 100,
            price_modifiers = '{}',
            import_restrictions = '{}',
            export_restrictions = '{}',
            services = '{}',
            service_prices = '{}',
            tax_rate = 0.05,
            defense_level = 0,
            shields = 0,
            defense_weapons = 0,
            security_rating = 0.5,
            active_events = '[]',
            special_features = '{}'
        WHERE type IS NULL
    """)
    
    # Make columns not nullable after setting defaults
    op.alter_column('ports', 'type', nullable=False)
    op.alter_column('ports', 'status', nullable=False)
    op.alter_column('ports', 'size', nullable=False)
    op.alter_column('ports', 'trade_volume', nullable=False)
    op.alter_column('ports', 'price_modifiers', nullable=False)
    op.alter_column('ports', 'import_restrictions', nullable=False)
    op.alter_column('ports', 'export_restrictions', nullable=False)
    op.alter_column('ports', 'services', nullable=False)
    op.alter_column('ports', 'service_prices', nullable=False)
    op.alter_column('ports', 'tax_rate', nullable=False)
    op.alter_column('ports', 'defense_level', nullable=False)
    op.alter_column('ports', 'shields', nullable=False)
    op.alter_column('ports', 'defense_weapons', nullable=False)
    op.alter_column('ports', 'security_rating', nullable=False)
    op.alter_column('ports', 'active_events', nullable=False)
    op.alter_column('ports', 'special_features', nullable=False)


def downgrade() -> None:
    # Drop the columns
    op.drop_column('ports', 'last_updated')
    op.drop_column('ports', 'type')
    op.drop_column('ports', 'status')
    op.drop_column('ports', 'size')
    op.drop_column('ports', 'faction_affiliation')
    op.drop_column('ports', 'trade_volume')
    op.drop_column('ports', 'price_modifiers')
    op.drop_column('ports', 'import_restrictions')
    op.drop_column('ports', 'export_restrictions')
    op.drop_column('ports', 'services')
    op.drop_column('ports', 'service_prices')
    op.drop_column('ports', 'tax_rate')
    op.drop_column('ports', 'defense_level')
    op.drop_column('ports', 'shields')
    op.drop_column('ports', 'defense_weapons')
    op.drop_column('ports', 'security_rating')
    op.drop_column('ports', 'last_attacked')
    op.drop_column('ports', 'active_events')
    op.drop_column('ports', 'description')
    op.drop_column('ports', 'special_features')
    
    # Drop the enums
    postgresql.ENUM(name='port_type').drop(op.get_bind())
    postgresql.ENUM(name='port_status').drop(op.get_bind())