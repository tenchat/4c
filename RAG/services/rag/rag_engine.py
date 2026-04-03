"""
RAG 引擎 - 核心编排

整合 QueryParser + StructuredQuery + VectorSearch + ContextAssembler + PromptBuilder + LLM
"""

import logging
import uuid
from functools import lru_cache
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from services.rag.structured_query import StructuredQueryService
from services.rag.vector_search import VectorSearchService
from services.rag.context_assembler import ContextAssembler
from services.rag.prompt_builder import PromptBuilder
from services.llm.factory import LLMFactory
from services.llm.base import LLMAdapter
from services.chat.db_history_service import DatabaseHistoryService

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_llm_adapter() -> LLMAdapter:
    """获取 LLM 适配器（单例）"""
    return LLMFactory.get_adapter("tongyi")


class QueryParser:
    """解析用户查询，提取实体"""

    def parse(self, question: str) -> dict:
        """
        解析查询，提取实体和意图

        Args:
            question: 用户问题

        Returns:
            {
                "intent": "employment_stats" | "job_recommend" | "policy" | "general",
                "entities": {
                    "major": "计算机" | None,
                    "province": "北京" | None,
                    "industry": "互联网" | None,
                }
            }
        """
        question_lower = question.lower()

        # 意图识别
        intent = "general"
        if any(kw in question_lower for kw in ["就业率", "就业情况", "找工作"]):
            intent = "employment"
        elif any(kw in question_lower for kw in ["职位", "工作", "招聘", "岗位"]):
            intent = "job"
        elif any(kw in question_lower for kw in ["政策", "规定", "要求"]):
            intent = "policy"

        # 实体提取（简化版，未来可升级为 LLM 解析）
        entities = {}

        # 常见专业关键词
        majors = [
            "计算机", "软件", "电子", "机械", "土木", "金融",
            "会计", "管理", "市场营销", "人工智能", "数据科学",
        ]
        for major in majors:
            if major in question:
                entities["major"] = major
                break

        # 常见城市
        cities = [
            "北京", "上海", "广州", "深圳", "杭州", "成都",
            "武汉", "西安", "南京", "苏州",
        ]
        for city in cities:
            if city in question:
                entities["province"] = city
                break

        # 常见行业
        industries = [
            "互联网", "金融", "教育", "医疗", "制造", "房地产",
            "通信", "咨询", "零售", "物流",
        ]
        for industry in industries:
            if industry in question:
                entities["industry"] = industry
                break

        return {
            "intent": intent,
            "entities": entities,
        }


class RAGEngine:
    """RAG 引擎 - 核心编排"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.query_parser = QueryParser()
        self.structured_query = StructuredQueryService(db)
        self.vector_search = VectorSearchService()
        self.context_assembler = ContextAssembler()
        self.prompt_builder = PromptBuilder()
        self.llm = _get_llm_adapter()  # 使用缓存的适配器

    def _format_history(self, messages: list[dict]) -> str:
        """
        格式化历史消息为字符串

        Args:
            messages: 消息列表 [{"type": "user", "content": "...", "created_at": "..."}]

        Returns:
            格式化的历史字符串
        """
        if not messages:
            return "（无历史记录）"

        lines = []
        for msg in messages:
            role = "用户" if msg.get("type") == "user" else "助手"
            content = msg.get("content", "")
            lines.append(f"{role}：{content}")

        return "\n".join(lines)

    async def ask(
        self,
        question: str,
        user_id: str,
        role_type: str,
        session_id: str | None = None,
    ) -> dict:
        """
        非流式问答

        Args:
            question: 用户问题
            user_id: 用户ID
            role_type: 用户角色
            session_id: 会话ID

        Returns:
            {
                "answer": "回答内容",
                "sources": [...],
                "session_id": "会话ID"
            }
        """
        # Step 1: 解析查询
        parsed = self.query_parser.parse(question)
        logger.info(f"查询解析: intent={parsed['intent']}, entities={parsed['entities']}")

        # Step 2: 查询结构化数据
        structured_data = {}
        entities = parsed.get("entities", {})

        if entities.get("major"):
            structured_data["就业数据"] = await self.structured_query.get_employment_by_major(
                entities["major"]
            )

        if entities.get("province"):
            structured_data["人才需求"] = await self.structured_query.get_talent_demand_by_province(
                entities["province"]
            )

        if entities.get("industry"):
            structured_data["职位信息"] = await self.structured_query.get_jobs_by_industry(
                entities["industry"]
            )

        # 如果是学生用户，获取学生画像
        if user_id and role_type == "student":
            profile = await self.structured_query.get_student_profile(user_id)
            if profile:
                structured_data["学生画像"] = profile

        # Step 3: 向量检索
        docs = await self.vector_search.search(
            query=question,
            role_type=role_type,
            k=5,
        )

        # Step 4: 组装上下文
        structured_context = self.context_assembler.format_structured_context(structured_data)
        knowledge_context = self.context_assembler.format_knowledge_context(docs)

        # Step 5: 获取历史
        result_session_id = session_id or str(uuid.uuid4())
        history_svc = DatabaseHistoryService()
        # 如果是新会话且有 user_id，创建会话记录
        if session_id and user_id:
            await history_svc._get_or_create_session(session_id, user_id, role_type)
        result = await history_svc.get_history(result_session_id)
        history_msgs = result["messages"]
        history = self._format_history(history_msgs)

        # Step 6: 构建 Prompt
        messages = self.prompt_builder.build(
            role_type=role_type,
            question=question,
            structured_context=structured_context,
            knowledge_context=knowledge_context,
            history=history,
        )

        logger.info(f"Prompt 构建完成，开始调用 LLM...")

        # Step 7: LLM 生成
        answer = await self.llm.chat(messages)

        # 存储历史
        await history_svc.add_message(result_session_id, "user", question, user_id)
        await history_svc.add_message(result_session_id, "assistant", answer, user_id)

        logger.info(f"问答完成，会话ID: {result_session_id}")

        return {
            "answer": answer,
            "sources": docs,
            "session_id": result_session_id,
        }

    async def ask_stream(
        self,
        question: str,
        user_id: str,
        role_type: str,
        session_id: str | None = None,
    ) -> AsyncGenerator[dict, None]:
        """
        流式问答

        Args:
            question: 用户问题
            user_id: 用户ID
            role_type: 用户角色
            session_id: 会话ID

        Yields:
            {"content": "字符", "done": false}
            ...
            {"content": "", "done": true}
        """
        # Step 0: 生成 session_id（提前，以便在首帧返回）
        result_session_id = session_id or str(uuid.uuid4())

        # Step 1-6: 同 ask
        parsed = self.query_parser.parse(question)

        structured_data = {}
        entities = parsed.get("entities", {})

        if entities.get("major"):
            structured_data["就业数据"] = await self.structured_query.get_employment_by_major(
                entities["major"]
            )

        if entities.get("province"):
            structured_data["人才需求"] = await self.structured_query.get_talent_demand_by_province(
                entities["province"]
            )

        if entities.get("industry"):
            structured_data["职位信息"] = await self.structured_query.get_jobs_by_industry(
                entities["industry"]
            )

        if user_id and role_type == "student":
            profile = await self.structured_query.get_student_profile(user_id)
            if profile:
                structured_data["学生画像"] = profile

        docs = await self.vector_search.search(
            query=question,
            role_type=role_type,
            k=5,
        )

        structured_context = self.context_assembler.format_structured_context(structured_data)
        knowledge_context = self.context_assembler.format_knowledge_context(docs)

        # 获取历史
        history_svc = DatabaseHistoryService()
        # 如果是新会话且有 user_id，创建会话记录
        if session_id and user_id:
            await history_svc._get_or_create_session(session_id, user_id, role_type)
        result = await history_svc.get_history(result_session_id)
        history_msgs = result["messages"]
        history = self._format_history(history_msgs)

        messages = self.prompt_builder.build(
            role_type=role_type,
            question=question,
            structured_context=structured_context,
            knowledge_context=knowledge_context,
            history=history,
        )

        logger.info(f"流式问答开始，会话ID: {result_session_id}")

        # Step 7: LLM 流式生成，首帧包含 session_id
        yield {"content": "", "done": False, "session_id": result_session_id}

        full_answer = ""
        async for chunk in self.llm.stream(messages):
            full_answer += chunk
            yield {"content": chunk, "done": False}

        yield {"content": "", "done": True}

        # 存储历史
        await history_svc.add_message(result_session_id, "user", question, user_id)
        await history_svc.add_message(result_session_id, "assistant", full_answer, user_id)

        logger.info(f"流式问答完成，会话ID: {result_session_id}")
