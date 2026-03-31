"""add student profile composite index

Revision ID: 20260330_add_idx
Revises: fb44549e9882
Create Date: 2026-03-30

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '20260330_add_idx'
down_revision: Union[str, None] = 'add_company_verified_index'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 复合索引：加速按学校和就业状态查询
    op.create_index(
        'ix_student_profiles_university_status',
        'student_profiles',
        ['university_id', 'employment_status'],
        unique=False
    )
    # 复合索引：加速按学校和专业查询
    op.create_index(
        'ix_student_profiles_university_major',
        'student_profiles',
        ['university_id', 'major'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_student_profiles_university_status', table_name='student_profiles')
    op.drop_index('ix_student_profiles_university_major', table_name='student_profiles')
