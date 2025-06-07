"""Add PayPal subscription tracking

Revision ID: m4n5o6p7q8r9
Revises: l3m4n5o6p7q8
Create Date: 2025-06-01 22:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'm4n5o6p7q8r9'
down_revision = 'l3m4n5o6p7q8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add PayPal subscription tracking to users table
    op.add_column('users', sa.Column('paypal_subscription_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('subscription_tier', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('subscription_status', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('subscription_started_at', sa.TIMESTAMP, nullable=True))
    op.add_column('users', sa.Column('subscription_expires_at', sa.TIMESTAMP, nullable=True))
    
    # Add index for PayPal subscription ID lookups
    op.create_index('idx_users_paypal_subscription', 'users', ['paypal_subscription_id'])
    op.create_index('idx_users_subscription_tier', 'users', ['subscription_tier'])
    op.create_index('idx_users_subscription_status', 'users', ['subscription_status'])
    
    # Add PayPal subscription tracking to regions table (already has paypal_subscription_id)
    op.add_column('regions', sa.Column('subscription_status', sa.String(50), nullable=True))
    op.add_column('regions', sa.Column('subscription_started_at', sa.TIMESTAMP, nullable=True))
    op.add_column('regions', sa.Column('subscription_expires_at', sa.TIMESTAMP, nullable=True))
    op.add_column('regions', sa.Column('last_payment_at', sa.TIMESTAMP, nullable=True))
    op.add_column('regions', sa.Column('next_billing_at', sa.TIMESTAMP, nullable=True))
    
    # Add indexes for regional subscription tracking
    op.create_index('idx_regions_subscription_status', 'regions', ['subscription_status'])
    op.create_index('idx_regions_paypal_subscription', 'regions', ['paypal_subscription_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_regions_paypal_subscription')
    op.drop_index('idx_regions_subscription_status')
    op.drop_index('idx_users_subscription_status')
    op.drop_index('idx_users_subscription_tier')
    op.drop_index('idx_users_paypal_subscription')
    
    # Drop columns from regions
    op.drop_column('regions', 'next_billing_at')
    op.drop_column('regions', 'last_payment_at')
    op.drop_column('regions', 'subscription_expires_at')
    op.drop_column('regions', 'subscription_started_at')
    op.drop_column('regions', 'subscription_status')
    
    # Drop columns from users
    op.drop_column('users', 'subscription_expires_at')
    op.drop_column('users', 'subscription_started_at')
    op.drop_column('users', 'subscription_status')
    op.drop_column('users', 'subscription_tier')
    op.drop_column('users', 'paypal_subscription_id')