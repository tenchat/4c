"""
会话历史服务

基于文件的会话历史管理
后续可迁移到数据库
"""

import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Literal

logger = logging.getLogger(__name__)

# 会话历史存储目录
HISTORY_DIR = Path(__file__).parent.parent / "chat_history"
HISTORY_DIR.mkdir(parents=True, exist_ok=True)


class HistoryService:
    """会话历史服务"""

    def __init__(self):
        self.history_dir = HISTORY_DIR

    def _get_session_file(self, session_id: str) -> Path:
        """获取会话文件路径"""
        return self.history_dir / f"{session_id}.json"

    def _read_file_sync(self, file_path: Path) -> list:
        """同步读取文件"""
        if not file_path.exists():
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []

    def _write_file_sync(self, file_path: Path, messages: list) -> None:
        """同步写入文件"""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)

    async def add_message(
        self,
        session_id: str,
        message_type: Literal["user", "assistant"],
        content: str,
    ) -> dict:
        """
        添加消息到会话

        Args:
            session_id: 会话ID
            message_type: 消息类型 (user/assistant)
            content: 消息内容

        Returns:
            消息对象
        """
        file_path = self._get_session_file(session_id)

        # 在线程池中执行同步文件 I/O
        messages = await asyncio.to_thread(self._read_file_sync, file_path)

        # 创建新消息
        message = {
            "type": message_type,
            "content": content,
            "created_at": datetime.now().isoformat(),
        }

        messages.append(message)

        # 在线程池中执行同步文件 I/O
        await asyncio.to_thread(self._write_file_sync, file_path, messages)

        logger.info(f"消息已添加到会话 {session_id}")

        return message

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
        file_path = self._get_session_file(session_id)

        # 在线程池中执行同步文件 I/O
        messages = await asyncio.to_thread(self._read_file_sync, file_path)

        # 返回最新的 limit 条消息
        return messages[-limit:] if messages else []

    async def delete_history(self, session_id: str) -> bool:
        """
        删除会话历史

        Args:
            session_id: 会话ID

        Returns:
            是否成功
        """
        file_path = self._get_session_file(session_id)

        if not file_path.exists():
            return False

        try:
            await asyncio.to_thread(file_path.unlink)
            logger.info(f"会话已删除: {session_id}")
            return True

        except Exception as e:
            logger.error(f"删除会话失败: {e}")
            return False

    async def list_sessions(self, user_id: str | None = None) -> list[dict]:
        """
        列出所有会话

        Args:
            user_id: 用户ID（预留，用于后续多用户支持）

        Returns:
            会话列表
        """
        sessions = []

        for file_path in self.history_dir.glob("*.json"):
            try:
                messages = await asyncio.to_thread(self._read_file_sync, file_path)

                if messages:
                    sessions.append({
                        "session_id": file_path.stem,
                        "last_message": messages[-1]["content"][:50],
                        "message_count": len(messages),
                        "updated_at": messages[-1].get("created_at"),
                    })

            except (json.JSONDecodeError, KeyError, IOError):
                continue

        # 按更新时间排序
        sessions.sort(
            key=lambda x: x.get("updated_at", ""),
            reverse=True
        )

        return sessions
