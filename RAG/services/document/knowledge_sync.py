"""
知识库同步服务

将上传文档同时写入 SQLite（metadata）和 ChromaDB（vectors）
"""

import logging
import uuid
from datetime import datetime
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config_data as config
from db.repositories.knowledge_repo import KnowledgeRepository
from services.rag.vector_search import VectorSearchService
from services.document.parser import DocumentParser

logger = logging.getLogger(__name__)


class KnowledgeSyncService:
    """知识库同步服务 - SQLite + ChromaDB 双写"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.parser = DocumentParser()
        self.knowledge_repo = KnowledgeRepository(db)
        self.vector_search = VectorSearchService()

        # 初始化文本分割器
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=config.separators,
        )

    async def add_document(
        self,
        file_path: str,
        title: str,
        category: str = "shared",
        operator: str = "system",
    ) -> dict:
        """
        添加文档到知识库

        流程：
        1. 解析文档 → 文本
        2. 文本分块
        3. 同步写入 SQLite (metadata)
        4. 同步写入 ChromaDB (vectors)
        5. 更新 SQLite 的 vector_ids

        Args:
            file_path: 文件路径
            title: 文档标题
            category: 分类
            operator: 操作人

        Returns:
            {"doc_id": "xxx", "chunks": 5, "message": "success"}
        """
        logger.info(f"开始添加文档: {title}, 分类: {category}")

        # Step 1: 解析文档
        content = self.parser.parse(file_path)

        if not content or len(content.strip()) < 10:
            raise ValueError("文档内容过少或为空")

        # Step 2: 文本分块
        if len(content) > config.max_split_char_num:
            chunks = self.splitter.split_text(content)
        else:
            chunks = [content]

        logger.info(f"文档分块完成: {len(chunks)} 个块")

        # Step 3: 生成 doc_id
        doc_id = str(uuid.uuid4())

        # Step 4: 写入 SQLite (metadata)
        # 只存储前 max_split_char_num 字符作为预览
        preview_limit = config.max_split_char_num
        doc_data = {
            "doc_id": doc_id,
            "title": title,
            "content": content[:preview_limit] if len(content) > preview_limit else content,
            "doc_type": Path(file_path).suffix,
            "category": category,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        await self.knowledge_repo.create(doc_data)
        logger.info(f"文档元数据已写入 SQLite: {doc_id}")

        # Step 5: 写入 ChromaDB (vectors)
        metadatas = [
            {
                "source": title,
                "doc_id": doc_id,
                "chunk_index": i,
                "operator": operator,
                "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            for i in range(len(chunks))
        ]

        # 生成固定的 ID 列表
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]

        await self.vector_search.add_documents(chunks, metadatas, ids)
        logger.info(f"文档向量已写入 ChromaDB: {len(ids)} 个")

        # Step 6: 更新 SQLite 的 vector_ids
        vector_ids = ",".join(ids)
        await self.knowledge_repo.update(doc_id, {"vector_ids": vector_ids})

        logger.info(f"文档添加完成: {doc_id}, {len(chunks)} 个块")

        return {
            "doc_id": doc_id,
            "chunks": len(chunks),
            "message": "success",
        }

    async def delete_document(self, doc_id: str) -> bool:
        """
        删除文档（SQLite + ChromaDB 同步删除）

        Args:
            doc_id: 文档ID

        Returns:
            是否成功
        """
        logger.info(f"开始删除文档: {doc_id}")

        # Step 1: 获取 vector_ids
        doc = await self.knowledge_repo.get_by_id(doc_id)
        if not doc:
            logger.warning(f"文档不存在: {doc_id}")
            return False

        # Step 2: 删除 ChromaDB vectors
        if doc.get("vector_ids"):
            ids = doc["vector_ids"].split(",")
            await self.vector_search.delete_by_ids(ids)
            logger.info(f"已从 ChromaDB 删除向量: {len(ids)} 个")

        # Step 3: 删除 SQLite record
        await self.knowledge_repo.delete(doc_id)

        logger.info(f"文档删除完成: {doc_id}")

        return True
