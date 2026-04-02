"""
结构化数据查询服务

用于 RAG 检索时查询数据库中的结构化数据（就业率、薪资等），
注入到 prompt 上下文中
"""

import logging
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class StructuredQueryService:
    """查询结构化数据，用于注入 RAG prompt"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _execute(self, query: str, params: dict | None = None) -> list[dict]:
        """执行查询"""
        result = await self.db.execute(text(query), params or {})
        return [dict(row._mapping) for row in result.fetchall()]

    async def get_employment_by_major(self, major: str) -> list[dict]:
        """
        查询某专业的就业率数据

        Args:
            major: 专业名称（支持模糊匹配）

        Returns:
            就业数据列表
        """
        query = """
            SELECT
                college_name,
                graduation_year,
                degree_level,
                graduate_nums,
                employed_nums,
                contract_nums
            FROM college_employment
            WHERE college_name LIKE :major OR :major LIKE '%' || college_name || '%'
            ORDER BY graduation_year DESC
            LIMIT 5
        """
        results = await self._execute(query, {"major": f"%{major}%"})
        logger.info(f"查询专业 {major} 的就业数据: {len(results)} 条")
        return results

    async def get_talent_demand_by_province(self, province: str) -> list[dict]:
        """
        查询某省份的人才需求

        Args:
            province: 省份名称（支持模糊匹配）

        Returns:
            人才需求列表
        """
        query = """
            SELECT
                province,
                job_type,
                industry,
                shortage_level,
                data_year
            FROM scarce_talents
            WHERE province LIKE :province
            ORDER BY shortage_level DESC
            LIMIT 10
        """
        results = await self._execute(query, {"province": f"%{province}%"})
        logger.info(f"查询省份 {province} 的人才需求: {len(results)} 条")
        return results

    async def get_student_profile(self, account_id: str) -> dict | None:
        """
        获取学生画像（用于个性化建议）

        Args:
            account_id: 账户ID

        Returns:
            学生档案或 None
        """
        query = """
            SELECT
                sp.student_no,
                sp.major,
                sp.college,
                sp.degree,
                sp.employment_status,
                sp.cur_salary,
                sp.cur_industry,
                sp.cur_company,
                sp.cur_city,
                u.name
            FROM student_profiles sp
            LEFT JOIN universities u ON sp.university_id = u.university_id
            WHERE sp.account_id = :account_id
            LIMIT 1
        """
        results = await self._execute(query, {"account_id": account_id})
        return results[0] if results else None

    async def get_jobs_by_industry(
        self, industry: str, limit: int = 10
    ) -> list[dict]:
        """
        查询某行业的职位

        Args:
            industry: 行业名称
            limit: 返回数量

        Returns:
            职位列表
        """
        query = """
            SELECT
                jd.job_id,
                jd.title,
                jd.job_type,
                jd.min_salary,
                jd.max_salary,
                jd.city,
                jd.description,
                jd.keywords,
                c.company_name
            FROM job_descriptions jd
            LEFT JOIN companies c ON jd.company_id = c.company_id
            WHERE jd.industry LIKE :industry
               OR jd.description LIKE :industry
            ORDER BY jd.published_at DESC
            LIMIT :limit
        """
        results = await self._execute(query, {"industry": f"%{industry}%", "limit": limit})
        logger.info(f"查询行业 {industry} 的职位: {len(results)} 条")
        return results

    async def query_any_table(
        self,
        table: str,
        fields: list[str] | None = None,
        conditions: dict | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """
        通用动态查询 - 支持任意表/字段查询

        Args:
            table: 表名
            fields: 要查询的字段列表，None 表示全部
            conditions: 查询条件
            limit: 返回数量限制

        Returns:
            查询结果列表
        """
        # 字段白名单验证（防止 SQL 注入）
        allowed_tables = {
            "college_employment",
            "scarce_talents",
            "student_profiles",
            "job_descriptions",
            "companies",
            "universities",
        }

        if table not in allowed_tables:
            logger.warning(f"不允许查询表: {table}")
            return []

        # 构建 SELECT 子句
        if fields:
            # 简单的字段验证
            safe_fields = [f for f in fields if f.isidentifier()]
            field_str = ", ".join(safe_fields) if safe_fields else "*"
        else:
            field_str = "*"

        # 构建 WHERE 子句
        where_clauses = []
        params: dict[str, Any] = {"limit": limit}

        if conditions:
            for i, (key, value) in enumerate(conditions.items()):
                if key.isidentifier():
                    where_clauses.append(f"{key} = :cond_{i}")
                    params[f"cond_{i}"] = value

        where_str = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        query = f"SELECT {field_str} FROM {table}{where_str} LIMIT :limit"

        try:
            results = await self._execute(query, params)
            logger.info(f"动态查询 {table}: {len(results)} 条")
            return results
        except Exception as e:
            logger.error(f"动态查询失败: {e}")
            return []
