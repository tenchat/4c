"""
Prompt 构建器

为不同角色构建特定的 Prompt 模板
"""

from typing import Literal

# ==================== Prompt 模板 ====================

STUDENT_QA_TEMPLATE = """你是大学生就业助手。请根据以下参考资料回答学生的问题。

{structured_context}

{knowledge_context}

{history}

学生问题：{question}

回答要求：
1. 基于提供的参考资料回答，不要编造信息
2. 如果有具体数据（如就业率、薪资），请引用
3. 结合学生个人情况给出个性化建议
4. 回答要专业、友好、有帮助
5. 如果信息不足，请明确告知学生
"""

SCHOOL_QA_TEMPLATE = """你是高校就业指导工作助手。请根据以下参考资料回答问题。

{structured_context}

{knowledge_context}

{history}

问题：{question}

回答要求：
1. 回答要专业、规范
2. 涉及数据统计时说明统计口径
3. 预警相关问题请结合平台数据
4. 回答要有条理，便于学校工作人员使用
"""

COMPANY_QA_TEMPLATE = """你是企业招聘助手。请根据以下参考资料回答问题。

{structured_context}

{knowledge_context}

{history}

问题：{question}

回答要求：
1. 提供专业的招聘建议
2. 涉及劳动法相关内容要准确
3. 帮助企业更好地发布职位和筛选人才
4. 回答要简洁、实用
"""

GENERAL_QA_TEMPLATE = """请根据以下参考资料回答问题。

{structured_context}

{knowledge_context}

{history}

问题：{question}

回答要求：
1. 基于提供的参考资料回答
2. 回答要准确、专业
3. 如有数据请引用来源
"""


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
