"""
LLM 适配器基类
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator


class LLMAdapter(ABC):
    """LLM 适配器抽象基类"""

    @abstractmethod
    async def chat(self, messages: list[dict], **kwargs) -> str:
        """
        同步聊天

        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            **kwargs: 其他参数

        Returns:
            完整回答字符串
        """
        pass

    @abstractmethod
    async def stream(self, messages: list[dict], **kwargs) -> AsyncGenerator[str, None]:
        """
        流式聊天

        Args:
            messages: 消息列表
            **kwargs: 其他参数

        Yields:
            逐字返回的字符串
        """
        pass
