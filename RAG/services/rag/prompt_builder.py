"""
Prompt 构建器

为不同角色构建特定的 Prompt 模板
"""

from typing import Literal

# ==================== Prompt 模板 ====================

STUDENT_QA_TEMPLATE = """你是大学生就业助手，基于以下资料回答问题：

{structured_context}

{knowledge_context}

{history}

学生问题：{question}

要求：直接回答，不要重复问题，保持简洁有条理。"""

SCHOOL_QA_TEMPLATE = """你是高校就业指导工作助手，基于以下资料回答问题：

{structured_context}

{knowledge_context}

{history}

问题：{question}

要求：直接回答，保持简洁专业。"""

COMPANY_QA_TEMPLATE = """你是企业招聘助手，基于以下资料回答问题：

{structured_context}

{knowledge_context}

{history}

问题：{question}

要求：直接回答，保持简洁实用。"""

GENERAL_QA_TEMPLATE = """基于以下资料回答问题：

{structured_context}

{knowledge_context}

{history}

问题：{question}

要求：直接回答，简洁有条理。"""


class PromptBuilder:
    """Prompt 构建器"""

    TEMPLATES = {
        "student": STUDENT_QA_TEMPLATE,
        "school": SCHOOL_QA_TEMPLATE,
        "company": COMPANY_QA_TEMPLATE,
        "general": GENERAL_QA_TEMPLATE,
    }

    def build(
        self,
        role_type: Literal["student", "school", "company"],
        question: str,
        structured_context: str,
        knowledge_context: str,
        history: str = "",
    ) -> list[dict]:
        """
        构建完整的消息列表

        Args:
            role_type: 角色类型
            question: 用户问题
            structured_context: 结构化数据上下文
            knowledge_context: 知识库上下文
            history: 历史记录

        Returns:
            消息列表，用于 LLM
        """
        template = self.TEMPLATES.get(role_type, self.TEMPLATES["general"])

        content = template.format(
            structured_context=structured_context or "暂无结构化数据",
            knowledge_context=knowledge_context or "暂无相关知识库内容",
            history=history or "（无历史记录）",
            question=question,
        )

        return [
            {"role": "user", "content": content}
        ]

    def build_with_system(self, role_type: str, system_prompt: str, question: str) -> list[dict]:
        """
        构建带有自定义 system prompt 的消息

        Args:
            role_type: 角色类型
            system_prompt: 自定义 system prompt
            question: 用户问题

        Returns:
            消息列表
        """
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ]
