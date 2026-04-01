"""
通用仓储基类

提供基础的 CRUD 操作，支持任意表的动态查询
"""

import logging
import re
from typing import Any, Generic, TypeVar

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

T = TypeVar("T")

# 允许的表名（白名单）
ALLOWED_TABLES = {
    "knowledge_documents",
    "accounts",
    "student_profiles",
    "companies",
    "job_descriptions",
    "chat_sessions",
    "chat_messages",
}

# 允许的列名模式（简单的标识符验证）
COLUMN_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')


def _validate_identifier(identifier: str, identifier_type: str = "column") -> bool:
    """
    验证标识符（表名/列名）是否安全

    Args:
        identifier: 标识符
        identifier_type: 类型描述（用于日志）

    Returns:
        是否有效
    """
    if not identifier or not isinstance(identifier, str):
        return False
    if not COLUMN_PATTERN.match(identifier):
        logger.warning(f"无效的 {identifier_type}: {identifier}")
        return False
    if len(identifier) > 64:  # 防止超长标识符
        return False
    return True


class BaseRepository(Generic[T]):
    """通用仓储基类，支持任意表的 CRUD 和自定义查询"""

    def __init__(self, db: AsyncSession, table_name: str):
        """
        初始化仓储

        Args:
            db: 异步数据库会话
            table_name: 表名
        """
        if table_name not in ALLOWED_TABLES:
            raise ValueError(f"不允许访问表: {table_name}")
        self.db = db
        self.table_name = table_name

    async def get_by_id(self, id_value: str, id_column: str = "doc_id") -> dict | None:
        """
        根据 ID 查询

        Args:
            id_value: ID 值
            id_column: ID 列名，默认 doc_id

        Returns:
            查询结果字典或 None
        """
        if not _validate_identifier(id_column, "id_column"):
            raise ValueError(f"无效的列名: {id_column}")

        query = text(f"SELECT * FROM {self.table_name} WHERE {id_column} = :id_value")
        result = await self.db.execute(query, {"id_value": id_value})
        row = result.fetchone()
        return dict(row._mapping) if row else None

    async def get_all(
        self,
        filters: dict | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict]:
        """
        条件查询

        Args:
            filters: 过滤条件，如 {"category": "student"}
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            查询结果列表
        """
        # 验证列名
        if filters:
            for key in filters.keys():
                if not _validate_identifier(key, "filter column"):
                    raise ValueError(f"无效的过滤列名: {key}")

        query = f"SELECT * FROM {self.table_name}"
        params: dict[str, Any] = {"limit": limit, "offset": offset}

        if filters:
            where_clauses = [f"{k} = :{k}" for k in filters.keys()]
            query += " WHERE " + " AND ".join(where_clauses)
            params.update(filters)

        query += " LIMIT :limit OFFSET :offset"

        result = await self.db.execute(text(query), params)
        return [dict(row._mapping) for row in result.fetchall()]

    async def create(self, data: dict) -> dict:
        """
        新增记录

        Args:
            data: 要插入的数据

        Returns:
            插入后的数据
        """
        columns = list(data.keys())
        # 验证所有列名
        for col in columns:
            if not _validate_identifier(col, "column"):
                raise ValueError(f"无效的列名: {col}")

        values_placeholders = [f":{c}" for c in columns]

        query = text(
            f"INSERT INTO {self.table_name} ({', '.join(columns)}) "
            f"VALUES ({', '.join(values_placeholders)})"
        )

        await self.db.execute(query, data)
        await self.db.commit()

        return data

    async def update(self, id_value: str, data: dict, id_column: str = "doc_id") -> dict | None:
        """
        更新记录

        Args:
            id_value: ID 值
            data: 要更新的数据
            id_column: ID 列名

        Returns:
            更新后的数据或 None
        """
        if not _validate_identifier(id_column, "id_column"):
            raise ValueError(f"无效的列名: {id_column}")

        # 验证所有更新的列名
        for key in data.keys():
            if not _validate_identifier(key, "update column"):
                raise ValueError(f"无效的更新列名: {key}")

        set_clauses = [f"{k} = :{k}" for k in data.keys()]
        params = {**data, "id_value": id_value}

        query = text(
            f"UPDATE {self.table_name} "
            f"SET {', '.join(set_clauses)} "
            f"WHERE {id_column} = :id_value"
        )

        await self.db.execute(query, params)
        await self.db.commit()

        return await self.get_by_id(id_value, id_column)

    async def delete(self, id_value: str, id_column: str = "doc_id") -> bool:
        """
        删除记录

        Args:
            id_value: ID 值
            id_column: ID 列名

        Returns:
            是否删除成功
        """
        if not _validate_identifier(id_column, "id_column"):
            raise ValueError(f"无效的列名: {id_column}")

        query = text(f"DELETE FROM {self.table_name} WHERE {id_column} = :id_value")
        result = await self.db.execute(query, {"id_value": id_value})
        await self.db.commit()
        return result.rowcount > 0

    async def raw_query(self, sql: str, params: dict | None = None) -> list[dict]:
        """
        执行原生 SQL 查询（仅限 SELECT）

        Args:
            sql: SQL 语句（仅支持 SELECT）
            params: 查询参数

        Returns:
            查询结果列表

        Raises:
            ValueError: 非 SELECT 语句或非法 SQL
        """
        sql_stripped = sql.strip().upper()

        # 严格限制：只允许 SELECT
        if not sql_stripped.startswith("SELECT"):
            raise ValueError("raw_query 仅支持 SELECT 语句")

        # 禁止危险关键字
        dangerous_keywords = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "TRUNCATE", "EXEC", "EXECUTE"]
        for keyword in dangerous_keywords:
            if keyword in sql_stripped:
                raise ValueError(f"禁止的关键字: {keyword}")

        result = await self.db.execute(text(sql), params or {})
        return [dict(row._mapping) for row in result.fetchall()]

    async def count(self, filters: dict | None = None) -> int:
        """
        统计数量

        Args:
            filters: 过滤条件

        Returns:
            记录数量
        """
        query = f"SELECT COUNT(*) as cnt FROM {self.table_name}"
        params: dict[str, Any] = {}

        if filters:
            for key in filters.keys():
                if not _validate_identifier(key, "filter column"):
                    raise ValueError(f"无效的过滤列名: {key}")
            where_clauses = [f"{k} = :{k}" for k in filters.keys()]
            query += " WHERE " + " AND ".join(where_clauses)
            params.update(filters)

        result = await self.db.execute(text(query), params)
        row = result.fetchone()
        return row["cnt"] if row else 0
