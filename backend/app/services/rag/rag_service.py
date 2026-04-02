"""
RAG 服务代理

Backend 通过此模块代理调用 RAG 服务（独立运行于 1145 端口）
遵循 Backend Patterns 的 Service Layer 模式
"""

import logging
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class RAGServiceError(Exception):
    """RAG 服务异常"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class RAGService:
    """RAG 服务代理 - 调用独立运行的 RAG 服务"""

    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.RAG_SERVICE_URL
        self.timeout = httpx.Timeout(60.0, connect=10.0)

    async def _post(self, endpoint: str, json_data: dict) -> dict:
        """
        发送 POST 请求到 RAG 服务

        Args:
            endpoint: API 端点（如 /rag/qa）
            json_data: 请求数据

        Returns:
            响应数据

        Raises:
            RAGServiceError: RAG 服务调用失败
        """
        url = f"{self.base_url}{endpoint}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=json_data)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            logger.error(f"RAG 服务超时: {url}")
            raise RAGServiceError("RAG 服务响应超时", 504)
        except httpx.ConnectError:
            logger.error(f"RAG 服务连接失败: {url}")
            raise RAGServiceError("无法连接到 RAG 服务", 503)
        except httpx.HTTPStatusError as e:
            logger.error(f"RAG 服务 HTTP 错误: {e.response.status_code}")
            raise RAGServiceError(f"RAG 服务错误: {e.response.status_code}", e.response.status_code)
        except Exception as e:
            logger.error(f"RAG 服务调用异常: {e}")
            raise RAGServiceError(f"RAG 服务调用失败: {str(e)}", 500)

    async def qa(
        self,
        question: str,
        user_id: str,
        role_type: str,
        session_id: str | None = None,
    ) -> dict:
        """
        智能问答（非流式）

        Args:
            question: 用户问题
            user_id: 用户ID
            role_type: 角色类型 (student/school/company)
            session_id: 会话ID

        Returns:
            {
                "code": 200,
                "message": "success",
                "data": {
                    "answer": "...",
                    "sources": [...],
                    "session_id": "..."
                }
            }
        """
        payload = {
            "question": question,
            "user_id": user_id,
            "role_type": role_type,
        }
        if session_id:
            payload["session_id"] = session_id

        result = await self._post("/rag/qa", payload)

        # 格式化返回数据
        if result.get("code") == 200 and result.get("data"):
            return result["data"]

        raise RAGServiceError(result.get("message", "RAG 服务返回异常"), 500)

    async def qa_stream(
        self,
        question: str,
        user_id: str,
        role_type: str,
        session_id: str | None = None,
    ) -> httpx.Response:
        """
        智能问答（流式 - SSE）

        Returns:
            httpx.Response 对象，包含 SSE 流
        """
        url = f"{self.base_url}/rag/qa/stream"
        payload = {
            "question": question,
            "user_id": user_id,
            "role_type": role_type,
        }
        if session_id:
            payload["session_id"] = session_id

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.stream("POST", url, json=payload)
                return response
        except httpx.TimeoutException:
            raise RAGServiceError("RAG 流式服务超时", 504)
        except httpx.ConnectError:
            raise RAGServiceError("无法连接到 RAG 流式服务", 503)

    async def upload_knowledge(
        self,
        file_content: bytes,
        filename: str,
        title: str,
        category: str = "shared",
    ) -> dict:
        """
        上传知识文档

        Args:
            file_content: 文件内容（字节）
            filename: 文件名
            title: 文档标题
            category: 分类 (student/school/company/shared)

        Returns:
            {
                "doc_id": "...",
                "chunks": 5
            }
        """
        url = f"{self.base_url}/rag/knowledge/upload"

        files = {"file": (filename, file_content)}
        data = {"title": title, "category": category}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, files=files, data=data)
                response.raise_for_status()
                result = response.json()

                if result.get("code") == 200 and result.get("data"):
                    return result["data"]

                raise RAGServiceError(result.get("message", "上传失败"), 500)
        except httpx.TimeoutException:
            raise RAGServiceError("上传超时", 504)
        except Exception as e:
            logger.error(f"上传知识文档失败: {e}")
            raise RAGServiceError(f"上传失败: {str(e)}", 500)

    async def list_knowledge(
        self,
        category: str | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> dict:
        """
        获取知识库列表

        Args:
            category: 分类过滤
            page: 页码
            page_size: 每页数量

        Returns:
            知识库列表数据
        """
        url = f"{self.base_url}/rag/knowledge/list"
        params = {"page": page, "page_size": page_size}
        if category:
            params["category"] = category

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                result = response.json()

                if result.get("code") == 200:
                    return result.get("data", {})

                raise RAGServiceError(result.get("message", "获取列表失败"), 500)
        except Exception as e:
            logger.error(f"获取知识库列表失败: {e}")
            raise RAGServiceError(f"获取列表失败: {str(e)}", 500)

    async def delete_knowledge(self, doc_id: str) -> bool:
        """
        删除知识文档

        Args:
            doc_id: 文档ID

        Returns:
            是否删除成功
        """
        url = f"{self.base_url}/rag/knowledge/{doc_id}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.delete(url)
                response.raise_for_status()
                result = response.json()
                return result.get("code") == 200
        except Exception as e:
            logger.error(f"删除知识文档失败: {e}")
            raise RAGServiceError(f"删除失败: {str(e)}", 500)

    async def get_chat_history(
        self,
        session_id: str | None = None,
        user_id: str | None = None,
    ) -> list[dict]:
        """
        获取会话历史

        Args:
            session_id: 会话ID
            user_id: 用户ID

        Returns:
            消息列表
        """
        url = f"{self.base_url}/rag/chat/history"
        params = {}
        if session_id:
            params["session_id"] = session_id
        if user_id:
            params["user_id"] = user_id

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                result = response.json()

                if result.get("code") == 200:
                    return result.get("data", [])

                raise RAGServiceError(result.get("message", "获取历史失败"), 500)
        except Exception as e:
            logger.error(f"获取会话历史失败: {e}")
            raise RAGServiceError(f"获取历史失败: {str(e)}", 500)

    async def health_check(self) -> bool:
        """
        检查 RAG 服务健康状态

        Returns:
            是否健康
        """
        url = f"{self.base_url}/health"

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                return response.status_code == 200
        except Exception:
            return False


# 全局单例
_rag_service: RAGService | None = None


def get_rag_service() -> RAGService:
    """获取 RAG 服务单例"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
