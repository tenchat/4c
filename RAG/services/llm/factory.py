"""
LLM 工厂类

统一创建 LLM 适配器，支持后续扩展 DeepSeek、MiniMax 等
"""

import logging
from typing import TypeVar

from services.llm.base import LLMAdapter
from services.llm.tongyi_adapter import TongyiAdapter

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=LLMAdapter)


class LLMFactory:
    """LLM 适配器工厂"""

    _adapters: dict[str, type[LLMAdapter]] = {
        "tongyi": TongyiAdapter,
        # 后续扩展
        # "deepseek": DeepSeekAdapter,
        # "minimax": MiniMaxAdapter,
    }

    @classmethod
    def get_adapter(cls, provider: str = "tongyi", **kwargs) -> LLMAdapter:
        """
        获取指定 provider 的适配器

        Args:
            provider: 提供商名称 (tongyi/deepseek/minimax)
            **kwargs: 传递给适配器的参数

        Returns:
            LLM 适配器实例

        Raises:
            ValueError: 不支持的 provider
        """
        provider_lower = provider.lower()

        adapter_class = cls._adapters.get(provider_lower)
        if not adapter_class:
            available = ", ".join(cls._adapters.keys())
            raise ValueError(
                f"不支持的 LLM provider: {provider}. 可用: {available}"
            )

        logger.info(f"创建 LLM 适配器: {provider_lower}")
        return adapter_class(**kwargs)

    @classmethod
    def register_adapter(cls, name: str, adapter_class: type[T]) -> None:
        """
        注册新的适配器（后续扩展用）

        Args:
            name: 适配器名称
            adapter_class: 适配器类
        """
        cls._adapters[name.lower()] = adapter_class
        logger.info(f"注册新 LLM 适配器: {name}")

    @classmethod
    def list_adapters(cls) -> list[str]:
        """列出所有可用的适配器"""
        return list(cls._adapters.keys())
