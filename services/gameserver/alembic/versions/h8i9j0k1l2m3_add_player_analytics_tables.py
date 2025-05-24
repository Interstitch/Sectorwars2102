"""Add player analytics tables for real-time metrics tracking

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
Create Date: 2025-05-24 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision: str = 'h8i9j0k1l2m3'
down_revision: Union[str, None] = 'g7h8i9j0k1l2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create player_sessions table
    op.create_table('player_sessions',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('player_id', UUID(as_uuid=True), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('actions_performed', sa.Integer(), nullable=False),
        sa.Column('sectors_visited', JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('credits_earned', sa.Integer(), nullable=False),
        sa.Column('credits_spent', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_player_sessions_player_id'), 'player_sessions', ['player_id'], unique=False)
    op.create_index(op.f('ix_player_sessions_start_time'), 'player_sessions', ['start_time'], unique=False)

    # Create player_analytics_snapshots table
    op.create_table('player_analytics_snapshots',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('snapshot_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('snapshot_type', sa.String(length=50), nullable=False),
        sa.Column('total_players', sa.Integer(), nullable=False),
        sa.Column('active_players', sa.Integer(), nullable=False),
        sa.Column('online_players', sa.Integer(), nullable=False),
        sa.Column('new_players_today', sa.Integer(), nullable=False),
        sa.Column('new_players_week', sa.Integer(), nullable=False),
        sa.Column('total_credits_circulation', sa.Integer(), nullable=False),
        sa.Column('average_credits_per_player', sa.Float(), nullable=False),
        sa.Column('total_ships', sa.Integer(), nullable=False),
        sa.Column('total_planets', sa.Integer(), nullable=False),
        sa.Column('total_ports', sa.Integer(), nullable=False),
        sa.Column('average_session_time', sa.Float(), nullable=False),
        sa.Column('total_actions_today', sa.Integer(), nullable=False),
        sa.Column('player_retention_rate_7d', sa.Float(), nullable=False),
        sa.Column('player_retention_rate_30d', sa.Float(), nullable=False),
        sa.Column('suspicious_activity_alerts', sa.Integer(), nullable=False),
        sa.Column('failed_login_attempts', sa.Integer(), nullable=False),
        sa.Column('player_by_status', JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('ships_by_type', JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('planets_by_type', JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('activity_by_hour', JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_player_analytics_snapshots_snapshot_time'), 'player_analytics_snapshots', ['snapshot_time'], unique=False)
    op.create_index(op.f('ix_player_analytics_snapshots_snapshot_type'), 'player_analytics_snapshots', ['snapshot_type'], unique=False)

    # Create player_activities table
    op.create_table('player_activities',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('player_id', UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', UUID(as_uuid=True), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('activity_type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('sector_id', sa.Integer(), nullable=True),
        sa.Column('target_id', sa.String(length=255), nullable=True),
        sa.Column('credits_involved', sa.Integer(), nullable=False),
        sa.Column('items_involved', JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('risk_score', sa.Integer(), nullable=False),
        sa.Column('flagged_for_review', sa.Boolean(), nullable=False),
        sa.Column('metadata', JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['player_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_player_activities_player_id'), 'player_activities', ['player_id'], unique=False)
    op.create_index(op.f('ix_player_activities_timestamp'), 'player_activities', ['timestamp'], unique=False)
    op.create_index(op.f('ix_player_activities_activity_type'), 'player_activities', ['activity_type'], unique=False)
    op.create_index(op.f('ix_player_activities_flagged_for_review'), 'player_activities', ['flagged_for_review'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('player_activities')
    op.drop_table('player_analytics_snapshots')
    op.drop_table('player_sessions')