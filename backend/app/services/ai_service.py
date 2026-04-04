"""
AI 服务

整合 RAG 服务，提供智能问答和分析功能
"""

import logging
from typing import Any

from app.services.rag import get_rag_service, RAGServiceError

logger = logging.getLogger(__name__)


class AIService:
    """AI 服务 - 代理调用 RAG 服务"""

    def __init__(self, db=None):
        self.db = db

    async def generate_profile(self, data: dict) -> dict:
        """
        生成就业画像分析

        Args:
            data: 包含 user_id, role_type 等信息

        Returns:
            画像分析结果
        """
        try:
            rag_service = get_rag_service()

            # 检查 RAG 服务是否可用
            if not await rag_service.health_check():
                return {
                    "status": "service_unavailable",
                    "message": "RAG 服务暂不可用",
                    "score": 0,
                    "professional_match": 0,
                    "skill_match": 0,
                    "location_demand": 0,
                    "salary_expectation": 0,
                    "strengths": [],
                    "weaknesses": [],
                    "suggestions": ["服务暂时不可用，请稍后再试"]
                }

            # 使用 RAG 问答获取个性化建议
            question = f"根据我的专业{data.get('major', '未知')}和期望城市{data.get('city', '未知')}，分析我的就业竞争力并给出建议"

            result = await rag_service.qa(
                question=question,
                user_id=data.get("user_id", "anonymous"),
                role_type=data.get("role_type", "student"),
            )

            return {
                "status": "success",
                "message": "分析完成",
                "answer": result.get("answer", ""),
                "sources": result.get("sources", []),
                "session_id": result.get("session_id", ""),
            }
        except RAGServiceError as e:
            logger.error(f"RAG 服务错误: {e.message}")
            return {
                "status": "error",
                "message": e.message,
                "score": 0,
                "professional_match": 0,
                "skill_match": 0,
                "location_demand": 0,
                "salary_expectation": 0,
                "strengths": [],
                "weaknesses": [],
                "suggestions": [f"服务错误: {e.message}"]
            }
        except Exception as e:
            logger.error(f"generate_profile 异常: {e}")
            return {
                "status": "error",
                "message": str(e),
                "score": 0,
                "suggestions": ["发生未知错误"]
            }

    async def analyze_resume(self, resume_text: str, target_job: str) -> dict:
        """
        简历分析

        Args:
            resume_text: 简历文本
            target_job: 目标职位

        Returns:
            ATS 分析结果
        """
        try:
            rag_service = get_rag_service()

            if not await rag_service.health_check():
                return {
                    "status": "service_unavailable",
                    "message": "RAG 服务暂不可用",
                    "ats_score": 0,
                    "matched_keywords": [],
                    "missing_keywords": [],
                    "suggestions": ["服务暂时不可用，请稍后再试"]
                }

            question = f"分析我的简历与{target_job}职位的匹配度，给出关键词匹配建议"
            result = await rag_service.qa(
                question=question,
                user_id="resume_analysis",
                role_type="student",
            )

            return {
                "status": "success",
                "message": "分析完成",
                "answer": result.get("answer", ""),
                "sources": result.get("sources", []),
                "session_id": result.get("session_id", ""),
            }
        except RAGServiceError as e:
            logger.error(f"RAG 服务错误: {e}")
            return {
                "status": "error",
                "message": e.message,
                "ats_score": 0,
                "matched_keywords": [],
                "missing_keywords": [],
                "suggestions": [f"服务错误: {e.message}"]
            }
        except Exception as e:
            logger.error(f"analyze_resume 异常: {e}")
            return {
                "status": "error",
                "message": str(e),
                "ats_score": 0,
                "suggestions": ["发生未知错误"]
            }

    async def graduate_vs_job(
        self,
        target_city: str,
        expected_salary: int,
        study_months: int
    ) -> dict:
        """
        考研 vs 就业决策分析

        Args:
            target_city: 目标城市
            expected_salary: 期望薪资
            study_months: 考研准备时间（月）

        Returns:
            决策分析结果
        """
        try:
            rag_service = get_rag_service()

            if not await rag_service.health_check():
                return {
                    "status": "service_unavailable",
                    "message": "RAG 服务暂不可用",
                    "employment_path": {},
                    "study_path": {},
                    "recommendation": "服务暂时不可用"
                }

            question = (
                f"我期望在{target_city}工作，期望薪资{expected_salary}元，"
                f"考研需要准备{study_months}个月，请分析考研和就业的利弊"
            )
            result = await rag_service.qa(
                question=question,
                user_id="decision_analysis",
                role_type="student",
            )

            return {
                "status": "success",
                "message": "分析完成",
                "answer": result.get("answer", ""),
                "sources": result.get("sources", []),
                "session_id": result.get("session_id", ""),
            }
        except RAGServiceError as e:
            logger.error(f"RAG 服务错误: {e}")
            return {
                "status": "error",
                "message": e.message,
                "recommendation": f"服务错误: {e.message}"
            }
        except Exception as e:
            logger.error(f"graduate_vs_job 异常: {e}")
            return {
                "status": "error",
                "message": str(e),
                "recommendation": "发生未知错误"
            }

    async def generate_warning(self, account_ids: list) -> dict:
        """
        生成就业预警

        Args:
            account_ids: 学生账号ID列表

        Returns:
            预警结果
        """
        try:
            rag_service = get_rag_service()

            if not await rag_service.health_check():
                return {
                    "status": "service_unavailable",
                    "message": "RAG 服务暂不可用",
                    "generated": 0,
                    "warnings": []
                }

            question = (
                f"请分析以下学生的就业风险：{', '.join(account_ids[:5])}。"
                f"给出就业预警和建议"
            )
            result = await rag_service.qa(
                question=question,
                user_id="warning_analysis",
                role_type="school",
            )

            return {
                "status": "success",
                "message": "预警生成完成",
                "answer": result.get("answer", ""),
                "sources": result.get("sources", []),
                "session_id": result.get("session_id", ""),
            }
        except RAGServiceError as e:
            logger.error(f"RAG 服务错误: {e}")
            return {
                "status": "error",
                "message": e.message,
                "generated": 0,
                "warnings": []
            }
        except Exception as e:
            logger.error(f"generate_warning 异常: {e}")
            return {
                "status": "error",
                "message": str(e),
                "generated": 0,
                "warnings": []
            }

    async def qa(
        self,
        question: str,
        user_id: str,
        role_type: str = "student",
        session_id: str | None = None
    ) -> dict:
        """
        通用问答

        Args:
            question: 问题
            user_id: 用户ID
            role_type: 角色类型
            session_id: 会话ID

        Returns:
            问答结果
        """
        try:
            rag_service = get_rag_service()
            result = await rag_service.qa(
                question=question,
                user_id=user_id,
                role_type=role_type,
                session_id=session_id,
            )
            return {
                "status": "success",
                "message": "问答完成",
                "answer": result.get("answer", ""),
                "sources": result.get("sources", []),
                "session_id": result.get("session_id", ""),
            }
        except RAGServiceError as e:
            logger.error(f"RAG 服务错误: {e}")
            return {
                "status": "error",
                "message": e.message,
                "answer": f"抱歉，RAG 服务暂时不可用：{e.message}",
                "sources": [],
                "session_id": ""
            }
        except Exception as e:
            logger.error(f"qa 异常: {e}")
            return {
                "status": "error",
                "message": str(e),
                "answer": "抱歉，发生未知错误",
                "sources": [],
                "session_id": ""
            }

    async def optimize_resume(
        self,
        account_id: str,
        resume_text: str,
        target_job: str
    ) -> dict:
        """
        AI 简历优化

        Args:
            account_id: 学生账户ID
            resume_text: 简历文本
            target_job: 目标岗位

        Returns:
            优化结果
        """
        try:
            rag_service = get_rag_service()
            result = await rag_service.optimize_resume(
                account_id=account_id,
                resume_text=resume_text,
                target_job=target_job,
            )
            return {
                "status": "success",
                "message": "简历优化完成",
                "data": result,
            }
        except RAGServiceError as e:
            logger.error(f"RAG 服务错误: {e}")
            return {
                "status": "error",
                "message": e.message,
                "data": None
            }
        except Exception as e:
            logger.error(f"optimize_resume 异常: {e}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }
