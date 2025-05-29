"""add_audit_logs_table

Revision ID: 58bd5d52ea80
Revises: 42533a92f89e
Create Date: 2025-05-28 02:59:55.625177

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '58bd5d52ea80'
down_revision = '42533a92f89e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create audit_logs table for security and compliance tracking
    op.create_table('audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('method', sa.String(length=10), nullable=False),
        sa.Column('path', sa.String(length=255), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_type', sa.String(length=20), nullable=True),
        sa.Column('client_ip', sa.String(length=45), nullable=False),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=True),
        sa.Column('resource_type', sa.String(length=50), nullable=True),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('query_params', sa.JSON(), nullable=True),
        sa.Column('request_body', sa.JSON(), nullable=True),
        sa.Column('response_summary', sa.Text(), nullable=True),
        sa.Column('security_flags', sa.JSON(), nullable=True),
        sa.Column('violation_detected', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for efficient querying
    op.create_index(op.f('ix_audit_logs_timestamp'), 'audit_logs', ['timestamp'], unique=False)
    op.create_index(op.f('ix_audit_logs_path'), 'audit_logs', ['path'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'], unique=False)
    
    # Composite index for user activity queries
    op.create_index('ix_audit_logs_user_timestamp', 'audit_logs', ['user_id', 'timestamp'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_audit_logs_user_timestamp', table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_path'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_timestamp'), table_name='audit_logs')
    
    # Drop table
    op.drop_table('audit_logs')