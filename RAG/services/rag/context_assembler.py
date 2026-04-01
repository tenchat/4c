"""
上下文组装器

将结构化数据和知识库文档组装成统一的上下文字符串
"""


class ContextAssembler:
    """组装 RAG 上下文"""

    def format_structured_context(self, data: dict) -> str:
        """
        格式化结构化数据

        Args:
            data: 结构化数据字典

        Returns:
            格式化后的字符串
        """
        if not data:
            return "暂无结构化数据"

        lines = []
        for key, value in data.items():
            lines.append(f"【{key}】")
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        # 格式化字典
                        item_lines = [f"  {k}: {v}" for k, v in item.items() if v]
                        lines.extend(item_lines)
                    else:
                        lines.append(f"  - {item}")
            elif isinstance(value, dict):
                item_lines = [f"  {k}: {v}" for k, v in value.items() if v]
                lines.extend(item_lines)
            else:
                lines.append(f"  {value}")
            lines.append("")  # 空行分隔

        return "\n".join(lines).strip()

    def format_knowledge_context(self, docs: list[dict]) -> str:
        """
        格式化知识库文档

        Args:
            docs: 文档列表

        Returns:
            格式化后的字符串
        """
        if not docs:
            return "暂无相关知识库内容"

        lines = []
        for i, doc in enumerate(docs, 1):
            lines.append(f"【文档{i}】")
            lines.append(f"内容：{doc.get('content', '')}")

            metadata = doc.get("metadata", {})
            if metadata:
                source = metadata.get("source", "未知来源")
                lines.append(f"来源：{source}")

            lines.append("")  # 空行分隔

        return "\n".join(lines).strip()

    def assemble(
        self,
        structured_data: dict,
        documents: list[dict],
        role_type: str,
    ) -> str:
        """
        组装完整的上下文字符串

        Args:
            structured_data: 结构化数据
            documents: 知识库文档
            role_type: 角色类型

        Returns:
            组装后的上下文
        """
        parts = []

        # 结构化数据部分
        structured_str = self.format_structured_context(structured_data)
        if structured_str != "暂无结构化数据":
            parts.append(f"【结构化数据】\n{structured_str}")

        # 知识库部分
        knowledge_str = self.format_knowledge_context(documents)
        if knowledge_str != "暂无相关知识库内容":
            parts.append(f"【知识库内容】\n{knowledge_str}")

        return "\n\n".join(parts) if parts else "暂无相关上下文信息"
