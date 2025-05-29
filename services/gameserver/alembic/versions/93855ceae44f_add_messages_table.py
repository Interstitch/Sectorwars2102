"""add_messages_table

Revision ID: 93855ceae44f
Revises: 58bd5d52ea80
Create Date: 2025-05-28 03:05:14.255776

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '93855ceae44f'
down_revision = '58bd5d52ea80'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create messages table for player communication
    op.create_table('messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sender_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recipient_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('subject', sa.String(length=255), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=False),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('deleted_by_sender', sa.Boolean(), nullable=True),
        sa.Column('deleted_by_recipient', sa.Boolean(), nullable=True),
        sa.Column('thread_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reply_to_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('message_type', sa.String(length=20), nullable=False),
        sa.Column('priority', sa.String(length=10), nullable=True),
        sa.Column('flagged', sa.Boolean(), nullable=True),
        sa.Column('flagged_reason', sa.String(length=255), nullable=True),
        sa.Column('moderated_at', sa.DateTime(), nullable=True),
        sa.Column('moderated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['moderated_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['recipient_id'], ['players.id'], ),
        sa.ForeignKeyConstraint(['reply_to_id'], ['messages.id'], ),
        sa.ForeignKeyConstraint(['sender_id'], ['players.id'], ),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for efficient querying
    op.create_index(op.f('ix_messages_sender_id'), 'messages', ['sender_id'], unique=False)
    op.create_index(op.f('ix_messages_recipient_id'), 'messages', ['recipient_id'], unique=False)
    op.create_index(op.f('ix_messages_team_id'), 'messages', ['team_id'], unique=False)
    op.create_index(op.f('ix_messages_sent_at'), 'messages', ['sent_at'], unique=False)
    op.create_index(op.f('ix_messages_thread_id'), 'messages', ['thread_id'], unique=False)
    
    # Composite indexes for common queries
    op.create_index('ix_messages_recipient_read', 'messages', ['recipient_id', 'read_at'], unique=False)
    op.create_index('ix_messages_team_sent', 'messages', ['team_id', 'sent_at'], unique=False)
    op.create_index('ix_messages_thread', 'messages', ['thread_id', 'sent_at'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_messages_thread', table_name='messages')
    op.drop_index('ix_messages_team_sent', table_name='messages')
    op.drop_index('ix_messages_recipient_read', table_name='messages')
    op.drop_index(op.f('ix_messages_thread_id'), table_name='messages')
    op.drop_index(op.f('ix_messages_sent_at'), table_name='messages')
    op.drop_index(op.f('ix_messages_team_id'), table_name='messages')
    op.drop_index(op.f('ix_messages_recipient_id'), table_name='messages')
    op.drop_index(op.f('ix_messages_sender_id'), table_name='messages')
    
    # Drop table
    op.drop_table('messages')