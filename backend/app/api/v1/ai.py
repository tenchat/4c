from fastapi import APIRouter, Depends
from app.schemas.ai import (
    EmploymentProfileRequest, EmploymentProfileResponse,
    ResumeAnalysisRequest, ResumeAnalysisResponse,
    DecisionRequest, DecisionResponse,
    WarningRequest, WarningResponse,
    QARequest, QAResponse
)
from app.core.dependencies import get_current_user
from app.services.ai_service import AIService
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_ai_service(db: AsyncSession = Depends(get_db)) -> AIService:
    return AIService(db)


@router.post("/employment-profile")
async def employment_profile(
    req: EmploymentProfileRequest,
    payload: dict = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    data = await service.generate_profile(req.model_dump())
    return {
        "code": 200,
        "message": "AI 分析功能开发中",
        "data": data
    }


@router.post("/resume-analysis")
async def resume_analysis(
    req: ResumeAnalysisRequest,
    payload: dict = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    data = await service.analyze_resume(req.resume_text, req.target_job)
    return {
        "code": 200,
        "message": "AI 简历分析功能开发中",
        "data": data
    }


@router.post("/graduate-vs-job")
async def graduate_vs_job(
    req: DecisionRequest,
    payload: dict = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    data = await service.graduate_vs_job(req.target_city, req.expected_salary, req.study_months)
    return {
        "code": 200,
        "message": "AI 决策分析功能开发中",
        "data": data
    }


@router.post("/warning")
async def generate_warning(
    req: WarningRequest,
    payload: dict = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    data = await service.generate_warning(req.account_ids)
    return {
        "code": 200,
        "message": "AI 预警功能开发中",
        "data": data
    }


@router.post("/qa")
async def ai_qa(
    req: QARequest,
    payload: dict = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    return {
        "code": 200,
        "message": "AI 问答功能开发中",
        "data": {
            "status": "not_implemented",
            "answer": "抱歉，AI 问答功能正在开发中",
            "sources": [],
            "intent": "general"
        }
    }
