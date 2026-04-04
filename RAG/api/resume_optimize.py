"""
简历优化 API 路由
"""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from schemas.response import BaseResponse
from services.rag.resume_optimize import optimize_resume

router = APIRouter(prefix="/rag", tags=["简历"])


class ResumeOptimizeRequest(BaseModel):
    user_id: str
    resume_text: str
    target_job: str


@router.post("/resume/optimize", response_model=BaseResponse)
async def optimize(
    req: ResumeOptimizeRequest,
) -> BaseResponse:
    """
    AI 简历优化

    - **user_id**: 学生账户ID
    - **resume_text**: 简历文本内容
    - **target_job**: 目标岗位
    """
    logger = logging.getLogger(__name__)

    try:
        if not req.user_id:
            raise HTTPException(status_code=400, detail="user_id 不能为空")

        if not req.resume_text:
            raise HTTPException(status_code=400, detail="resume_text 不能为空")

        if not req.target_job:
            raise HTTPException(status_code=400, detail="target_job 不能为空")

        result = await optimize_resume(req.user_id, req.resume_text, req.target_job)

        return BaseResponse(
            code=200,
            message="success",
            data=result,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"简历优化失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
