"""add index on companies.verified

Revision ID: add_company_verified_index
Revises: fb44549e9882_initial
Create Date: 2026-03-30

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_company_verified_index'
down_revision = 'fb44549e9882'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 为 companies.verified 字段添加索引，加速按状态查询
    op.create_index('ix_companies_verified', 'companies', ['verified'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_companies_verified', table_name='companies')
