"""update_reputation_for_factions

Revision ID: ecc8d2f023f2
Revises: 4a9c7afdd0b2
Create Date: 2025-05-28 03:24:14.642282

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ecc8d2f023f2'
down_revision = '4a9c7afdd0b2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # First, let's check if the reputation table has any data
    connection = op.get_bind()
    result = connection.execute(sa.text("SELECT COUNT(*) FROM reputations"))
    count = result.fetchone()[0]
    
    if count > 0:
        # If there's existing data, we need to preserve it
        # Create a temporary column for the new faction_id
        op.add_column('reputations', sa.Column('faction_id_new', postgresql.UUID(as_uuid=True), nullable=True))
        
        # Get faction IDs for migration
        result = connection.execute(sa.text("SELECT id, faction_type FROM factions"))
        faction_map = {row[1]: str(row[0]) for row in result}
        
        # Migrate existing data - map old string faction_id to new UUID
        # This is a simplified mapping - adjust based on your actual data
        for old_faction, new_faction_id in faction_map.items():
            op.execute(f"""
                UPDATE reputations 
                SET faction_id_new = '{new_faction_id}'::uuid 
                WHERE faction_id = '{old_faction}'
            """)
        
        # Drop the old column and rename the new one
        op.drop_column('reputations', 'faction_id')
        op.alter_column('reputations', 'faction_id_new', new_column_name='faction_id', nullable=False)
    else:
        # No data, we can just drop and recreate the column
        op.drop_column('reputations', 'faction_id')
        op.add_column('reputations', sa.Column('faction_id', postgresql.UUID(as_uuid=True), nullable=False))
    
    # Add foreign key constraint
    op.create_foreign_key('reputations_faction_id_fkey', 'reputations', 'factions', ['faction_id'], ['id'], ondelete='CASCADE')
    
    # Add unique constraint for player-faction combination
    op.create_unique_constraint('uq_player_faction_reputation', 'reputations', ['player_id', 'faction_id'])


def downgrade() -> None:
    # Drop constraints
    op.drop_constraint('uq_player_faction_reputation', 'reputations', type_='unique')
    op.drop_constraint('reputations_faction_id_fkey', 'reputations', type_='foreignkey')
    
    # Revert faction_id column back to string
    op.drop_column('reputations', 'faction_id')
    op.add_column('reputations', sa.Column('faction_id', sa.String(length=50), nullable=False))