"""
向量检索服务

基于 ChromaDB 的向量存储和检索
"""

import logging
from typing import Any

from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
import config_data as config

logger = logging.getLogger(__name__)


class VectorSearchService:
    """向量检索服务"""

    def __init__(self):
        """初始化向量检索服务"""
        # 初始化 Embedding 函数
        self.embedding = DashScopeEmbeddings(
            model=config.embedding_model_name,
        )

        # 初始化 ChromaDB
        self.persist_directory = config.persist_directory
        self.collection_name = config.collection_name

        self._vector_store: Chroma | None = None

    @property
    def vector_store(self) -> Chroma:
        """懒加载向量存储"""
        if self._vector_store is None:
            self._vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embedding,
                persist_directory=self.persist_directory,
            )
        return self._vector_store

    def get_retriever(self, k: int = 5):
        """
        获取 LangChain retriever

        Args:
            k: 返回的相似文档数量

        Returns:
            LangChain Retriever
        """
        return self.vector_store.as_retriever(
            search_kwargs={"k": k}
        )

    async def search(
        self,
        query: str,
        role_type: str | None = None,
        k: int = 5,
    ) -> list[dict[str, Any]]:
        """
        向量相似度搜索

        Args:
            query: 查询文本
            role_type: 角色类型（未来扩展用）
            k: 返回数量

        Returns:
            检索结果列表，每项包含 content, metadata, score
        """
        try:
            # 执行相似度搜索
            docs = self.vector_store.similarity_search_with_score(
                query, k=k
            )

            results = []
            for doc in docs:
                results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": doc.metadata.get("score", 0.0),
                })

            logger.info(f"向量检索 '{query[:30]}...': {len(results)} 条结果")
            return results

        except Exception as e:
            logger.error(f"向量检索失败: {e}")
            return []

    async def add_documents(
        self,
        texts: list[str],
        metadatas: list[dict],
        ids: list[str] | None = None,
    ) -> list[str]:
        """
        批量添加文档到向量库

        Args:
            texts: 文档文本列表
            metadatas: 元数据列表
            ids: ID 列表（可选）

        Returns:
            生成的 ID 列表
        """
        try:
            # 生成 ID
            if ids is None:
                ids = [f"doc_{i}" for i in range(len(texts))]

            # 转换为 Document 对象
            documents = [
                Document(page_content=text, metadata=meta)
                for text, meta in zip(texts, metadatas)
            ]

            # 添加到向量库
            self.vector_store.add_documents(documents, ids=ids)

            logger.info(f"添加 {len(texts)} 个文档到向量库")
            return ids

        except Exception as e:
            logger.error(f"添加文档到向量库失败: {e}")
            raise

    async def delete_by_ids(self, ids: list[str]) -> bool:
        """
        根据 ID 删除向量

        Args:
            ids: 要删除的 ID 列表

        Returns:
            是否删除成功
        """
        try:
            self.vector_store.delete(ids=ids)
            logger.info(f"从向量库删除 {len(ids)} 个文档")
            return True

        except Exception as e:
            logger.error(f"从向量库删除文档失败: {e}")
            return False

    async def get_collection_stats(self) -> dict:
        """
        获取向量库统计信息

        Returns:
            统计信息
        """
        try:
            collection = self.vector_store._collection
            return {
                "name": self.collection_name,
                "count": collection.count(),
                "persist_directory": self.persist_directory,
            }
        except Exception as e:
            logger.error(f"获取向量库统计失败: {e}")
            return {}
