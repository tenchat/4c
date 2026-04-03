"""
数据库会话历史服务

基于 SQLite 数据库的会话历史管理
使用 chat_sessions 和 chat_messages 表
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Literal

from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.connection import AsyncSessionLocal

logger = logging.getLogger(__name__)


class DatabaseHistoryService:
    """基于数据库的会话历史服务"""

    async def _execute(self, query, session: AsyncSession = None):
        """执行数据库操作"""
        if session:
            result = await session.execute(query)
            await session.commit()
            return result

        async with AsyncSessionLocal() as new_session:
            result = await new_session.execute(query)
            await new_session.commit()
            return result

    async def _ensure_tables(self):
        """确保表存在"""
        from sqlalchemy import text

        async with AsyncSessionLocal() as session:
            # 创建 chat_sessions 表
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    role_type TEXT DEFAULT 'student',
                    title TEXT DEFAULT '新对话',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """))

            # 创建 chat_messages 表
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    message_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    message_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    sources TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE
                )
            """))

            # 创建索引
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_messages_session
                ON chat_messages(session_id)
            """))

            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_sessions_user
                ON chat_sessions(user_id)
            """))

            await session.commit()
            logger.info("Chat history tables initialized")

    async def add_message(
        self,
        session_id: str,
        message_type: Literal["user", "assistant"],
        content: str,
        user_id: str = None,
        sources: str = None,
    ) -> dict:
        """
        添加消息到会话

        Args:
            session_id: 会话ID
            message_type: 消息类型 (user/assistant)
            content: 消息内容
            user_id: 用户ID（用于创建新会话）
            sources: 来源信息（可选）

        Returns:
            消息对象
        """
        await self._ensure_tables()

        message_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()

        # 如果会话不存在，先创建
        if user_id:
            await self._get_or_create_session(session_id, user_id)

        async with AsyncSessionLocal() as session:
            from sqlalchemy import text

            # 插入消息
            await session.execute(
                text("""
                    INSERT INTO chat_messages
                    (message_id, session_id, message_type, content, sources, created_at)
                    VALUES (:message_id, :session_id, :message_type, :content, :sources, :created_at)
                """),
                {
                    "message_id": message_id,
                    "session_id": session_id,
                    "message_type": message_type,
                    "content": content,
                    "sources": sources,
                    "created_at": created_at,
                }
            )

            # 更新会话更新时间
            await session.execute(
                text("""
                    UPDATE chat_sessions
                    SET updated_at = :updated_at
                    WHERE session_id = :session_id
                """),
                {"updated_at": created_at, "session_id": session_id}
            )

            await session.commit()

        logger.info(f"消息已添加到会话 {session_id}")

        return {
            "message_id": message_id,
            "type": message_type,
            "content": content,
            "created_at": created_at,
        }

    async def _get_or_create_session(self, session_id: str, user_id: str, role_type: str = "student"):
        """获取或创建会话"""
        await self._ensure_tables()

        from sqlalchemy import text

        async with AsyncSessionLocal() as session:
            # 检查会话是否存在
            result = await session.execute(
                text("SELECT session_id FROM chat_sessions WHERE session_id = :session_id"),
                {"session_id": session_id}
            )
            exists = result.scalar_one_or_none() is not None

            if not exists:
                now = datetime.now().isoformat()
                await session.execute(
                    text("""
                        INSERT INTO chat_sessions (session_id, user_id, role_type, title, created_at, updated_at)
                        VALUES (:session_id, :user_id, :role_type, :title, :created_at, :updated_at)
                    """),
                    {
                        "session_id": session_id,
                        "user_id": user_id,
                        "role_type": role_type,
                        "title": "新对话",
                        "created_at": now,
                        "updated_at": now,
                    }
                )
                await session.commit()
                logger.info(f"创建新会话 {session_id} for user {user_id}")

    async def get_history(
        self,
        session_id: str,
        limit: int = 50,
    ) -> list[dict]:
        """
        获取会话历史

        Args:
            session_id: 会话ID
            limit: 返回消息数量限制

        Returns:
            消息列表
        """
        await self._ensure_tables()

        from sqlalchemy import text

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                text("""
                    SELECT message_id, message_type, content, created_at
                    FROM chat_messages
                    WHERE session_id = :session_id
                    ORDER BY created_at ASC
                    LIMIT :limit
                """),
                {"session_id": session_id, "limit": limit}
            )

            rows = result.fetchall()
            return [
                {
                    "type": row[1],  # message_type
                    "content": row[2],  # content
                    "created_at": row[3],  # created_at
                }
                for row in rows
            ]

    async def get_user_sessions(self, user_id: str, limit: int = 10) -> list[dict]:
        """
        获取用户的所有会话

        Args:
            user_id: 用户ID
            limit: 返回会话数量限制

        Returns:
            会话列表
        """
        await self._ensure_tables()

        from sqlalchemy import text

        async with AsyncSessionLocal() as session:
            result = await session.execute(
                text("""
                    SELECT session_id, title, created_at, updated_at
                    FROM chat_sessions
                    WHERE user_id = :user_id
                    ORDER BY updated_at DESC
                    LIMIT :limit
                """),
                {"user_id": user_id, "limit": limit}
            )

            rows = result.fetchall()
            return [
                {
                    "session_id": row[0],
                    "title": row[1],
                    "created_at": row[2],
                    "updated_at": row[3],
                }
                for row in rows
            ]

    async def delete_history(self, session_id: str) -> bool:
        """
        删除会话历史

        Args:
            session_id: 会话ID

        Returns:
            是否成功
        """
        await self._ensure_tables()

        from sqlalchemy import text

        async with AsyncSessionLocal() as session:
            # 先删消息
            await session.execute(
                text("DELETE FROM chat_messages WHERE session_id = :session_id"),
                {"session_id": session_id}
            )
            # 再删会话
            result = await session.execute(
                text("DELETE FROM chat_sessions WHERE session_id = :session_id"),
                {"session_id": session_id}
            )
            await session.commit()

            if result.rowcount > 0:
                logger.info(f"会话已删除: {session_id}")
                return True
            return False

    async def create_session(self, user_id: str, role_type: str = "student", title: str = "新对话") -> str:
        """
        为用户创建新会话

        Args:
            user_id: 用户ID
            role_type: 用户角色
            title: 会话标题

        Returns:
            新会话ID
        """
        await self._ensure_tables()

        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        from sqlalchemy import text

        async with AsyncSessionLocal() as session:
            await session.execute(
                text("""
                    INSERT INTO chat_sessions (session_id, user_id, role_type, title, created_at, updated_at)
                    VALUES (:session_id, :user_id, :role_type, :title, :created_at, :updated_at)
                """),
                {
                    "session_id": session_id,
                    "user_id": user_id,
                    "role_type": role_type,
                    "title": title,
                    "created_at": now,
                    "updated_at": now,
                }
            )
            await session.commit()

        logger.info(f"为用户 {user_id} 创建新会话: {session_id}")
        return session_id
