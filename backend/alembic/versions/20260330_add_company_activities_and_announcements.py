"""add_company_activities_and_announcements

Revision ID: 20260330_add_caa
Revises: 20260330_add_job_idx
Create Date: 2026-03-30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '20260330_add_caa'
down_revision: Union[str, None] = '20260330_add_job_idx'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'company_activities',
        sa.Column('activity_id', sa.String(36), primary_key=True),
        sa.Column('company_id', sa.String(36), sa.ForeignKey('companies.company_id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.Enum('seminar', 'job_fair', name='activity_type_enum', create_type=False), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('activity_date', sa.Date, nullable=False),
        sa.Column('start_time', sa.Time, nullable=True),
        sa.Column('end_time', sa.Time, nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('status', sa.SmallInteger, nullable=False, server_default='1'),
        sa.Column('expected_num', sa.Integer, nullable=True),
        sa.Column('actual_num', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_company_activities_company_id', 'company_activities', ['company_id'])
    op.create_index('ix_company_activities_type', 'company_activities', ['type'])
    op.create_index('ix_company_activities_activity_date', 'company_activities', ['activity_date'])
    op.create_index('ix_company_activities_status', 'company_activities', ['status'])

    op.create_table(
        'company_announcements',
        sa.Column('announcement_id', sa.String(36), primary_key=True),
        sa.Column('company_id', sa.String(36), sa.ForeignKey('companies.company_id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('target_major', sa.String(200), nullable=True),
        sa.Column('target_degree', sa.SmallInteger, nullable=True),
        sa.Column('headcount', sa.Integer, nullable=True),
        sa.Column('deadline', sa.Date, nullable=True),
        sa.Column('status', sa.SmallInteger, nullable=False, server_default='1'),
        sa.Column('published_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_company_announcements_company_id', 'company_announcements', ['company_id'])
    op.create_index('ix_company_announcements_status', 'company_announcements', ['status'])


def downgrade() -> None:
    op.drop_table('company_announcements')
    op.drop_table('company_activities')