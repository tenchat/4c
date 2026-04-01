"""
知识库仓储
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from db.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class KnowledgeRepository(BaseRepository):
    """知识库文档仓储"""

    def __init__(self, db: AsyncSession):
        super().__init__(db, "knowledge_documents")

    async def get_by_type(self, doc_type: str) -> list[dict]:
        """
        按文档类型查询

        Args:
            doc_type: 文档类型

        Returns:
            文档列表
        """
        return await self.get_all(filters={"doc_type": doc_type})

    async def search_by_title(self, keyword: str) -> list[dict]:
        """
        按标题搜索

        Args:
            keyword: 关键词

        Returns:
            匹配的文档列表
        """
        query = """
            SELECT * FROM knowledge_documents
            WHERE title LIKE :keyword
            ORDER BY created_at DESC
        """
        return await self.raw_query(query, {"keyword": f"%{keyword}%"})

    async def get_with_pagination(
        self,
        doc_type: str | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[dict], int]:
        """
        分页查询

        Args:
            doc_type: 文档类型过滤
            page: 页码（从 1 开始）
            page_size: 每页数量

        Returns:
            (文档列表, 总数)
        """
        offset = (page - 1) * page_size

        if doc_type:
            filters = {"doc_type": doc_type}
            total = await self.count(filters)
            items = await self.get_all(filters=filters, limit=page_size, offset=offset)
        else:
            total = await self.count()
            items = await self.get_all(limit=page_size, offset=offset)

        return items, total

    async def find_by_ids(self, doc_ids: list[str]) -> list[dict]:
        """
        批量查询

        Args:
            doc_ids: 文档 ID 列表

        Returns:
            匹配的文档列表
        """
        if not doc_ids:
            return []

        placeholders = ", ".join([f":id_{i}" for i in range(len(doc_ids))])
        params = {f"id_{i}": doc_id for i, doc_id in enumerate(doc_ids)}

        query = f"SELECT * FROM knowledge_documents WHERE doc_id IN ({placeholders})"
        return await self.raw_query(query, params)
