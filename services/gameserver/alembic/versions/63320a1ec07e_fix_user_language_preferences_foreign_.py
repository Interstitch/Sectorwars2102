"""fix_user_language_preferences_foreign_key_type

Revision ID: 63320a1ec07e
Revises: de30465af48f
Create Date: 2025-06-02 04:11:08.555569

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '63320a1ec07e'
down_revision = 'de30465af48f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if user_language_preferences table exists
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'user_language_preferences'
        );
    """))
    table_exists = result.scalar()
    
    if table_exists:
        # Drop the foreign key constraint first
        try:
            op.drop_constraint('user_language_preferences_user_id_fkey', 'user_language_preferences', type_='foreignkey')
        except Exception:
            pass  # Constraint might not exist yet
        
        # Alter the column type from INTEGER to UUID
        op.alter_column('user_language_preferences', 'user_id',
                       existing_type=sa.INTEGER(),
                       type_=postgresql.UUID(as_uuid=True),
                       postgresql_using='user_id::text::uuid')
        
        # Recreate the foreign key constraint
        op.create_foreign_key('user_language_preferences_user_id_fkey', 
                            'user_language_preferences', 'users', 
                            ['user_id'], ['id'])
    else:
        # Create the table with correct types if it doesn't exist
        op.create_table('user_language_preferences',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('language_id', sa.Integer(), nullable=False),
            sa.Column('detected_language', sa.String(length=10), nullable=True),
            sa.Column('manual_override', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['language_id'], ['languages.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id')
        )
        op.create_index(op.f('ix_user_language_preferences_language_id'), 'user_language_preferences', ['language_id'], unique=False)
        op.create_index(op.f('ix_user_language_preferences_user_id'), 'user_language_preferences', ['user_id'], unique=False)


def downgrade() -> None:
    # Check if user_language_preferences table exists
    conn = op.get_bind()
    result = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'user_language_preferences'
        );
    """))
    table_exists = result.scalar()
    
    if table_exists:
        # Drop the foreign key constraint first
        try:
            op.drop_constraint('user_language_preferences_user_id_fkey', 'user_language_preferences', type_='foreignkey')
        except Exception:
            pass
        
        # Alter the column type back from UUID to INTEGER
        # Note: This is destructive and will lose data if UUIDs can't be converted to integers
        op.alter_column('user_language_preferences', 'user_id',
                       existing_type=postgresql.UUID(as_uuid=True),
                       type_=sa.INTEGER(),
                       postgresql_using='user_id::text::int')
        
        # Recreate the foreign key constraint with INTEGER type
        op.create_foreign_key('user_language_preferences_user_id_fkey', 
                            'user_language_preferences', 'users', 
                            ['user_id'], ['id'])