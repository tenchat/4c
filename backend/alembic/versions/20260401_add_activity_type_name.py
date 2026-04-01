"""add_activity_type_name

Revision ID: 20260401_add_type_name
Revises: 20260330_add_caa
Create Date: 2026-04-01
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '20260401_add_type_name'
down_revision: Union[str, None] = '20260330_add_caa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add type_name column for custom activity type names
    op.add_column('company_activities', sa.Column('type_name', sa.String(50), nullable=True))


def downgrade() -> None:
    op.drop_column('company_activities', 'type_name')