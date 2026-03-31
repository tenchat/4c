"""add job description composite index

Revision ID: 20260330_add_job_idx
Revises: 20260330_add_idx
Create Date: 2026-03-30

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '20260330_add_job_idx'
down_revision: Union[str, None] = '20260330_add_idx'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 复合索引：加速按公司和状态查询岗位
    op.create_index(
        'ix_job_descriptions_company_status',
        'job_descriptions',
        ['company_id', 'status'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_job_descriptions_company_status', table_name='job_descriptions')
