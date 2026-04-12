"""
岗位推荐 API 路由
"""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from schemas.response import BaseResponse
from services.rag.job_recommend import recommend_jobs

router = APIRouter(prefix="/rag", tags=["推荐"])


class RecommendRequest(BaseModel):
    user_id: str
    top_k: int = 5


@router.post("/job/recommend", response_model=BaseResponse)
async def recommend(
    req: RecommendRequest,
) -> BaseResponse:
    """
    获取岗位推荐

    - **user_id**: 学生账户ID
    - **top_k**: 推荐数量，默认5条
    """
    logger = logging.getLogger(__name__)

    try:
        if not req.user_id:
            raise HTTPException(status_code=400, detail="user_id 不能为空")

        if req.top_k < 1 or req.top_k > 20:
            top_k = 5
        else:
            top_k = req.top_k

        recommendations = await recommend_jobs(req.user_id, top_k)

        return BaseResponse(
            code=200,
            message="success",
            data={
                "recommendations": recommendations,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"岗位推荐失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
