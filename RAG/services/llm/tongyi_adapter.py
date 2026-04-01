"""
通义千问适配器

基于阿里云 DashScope 的 ChatTongyi
"""

import asyncio
import logging
from typing import AsyncGenerator

from langchain_community.chat_models import ChatTongyi
import config_data as config

from services.llm.base import LLMAdapter

logger = logging.getLogger(__name__)


class TongyiAdapter(LLMAdapter):
    """通义千问适配器"""

    def __init__(self, model_name: str | None = None):
        """
        初始化适配器

        Args:
            model_name: 模型名称，默认使用配置中的模型
        """
        self.model_name = model_name or config.chat_model_name
        self.chat_model = ChatTongyi(model=self.model_name)
        logger.info(f"TongyiAdapter 初始化完成，模型: {self.model_name}")

    async def chat(self, messages: list[dict], **kwargs) -> str:
        """
        同步聊天

        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]

        Returns:
            完整回答字符串
        """
        try:
            # LangChain 的 ChatTongyi.invoke() 是 sync 的
            # 需要在线程池中运行
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.chat_model.invoke(messages),
            )
            return response.content

        except Exception as e:
            logger.error(f"Tongyi chat 失败: {e}")
            raise

    async def stream(self, messages: list[dict], **kwargs) -> AsyncGenerator[str, None]:
        """
        流式聊天

        Args:
            messages: 消息列表

        Yields:
            逐字返回的字符串
        """
        try:
            # ChatTongyi.astream() 是 async 的
            async for chunk in self.chat_model.astream(messages):
                if chunk.content:
                    yield chunk.content

        except Exception as e:
            logger.error(f"Tongyi stream 失败: {e}")
            raise
