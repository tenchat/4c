"""
会话历史 API
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.request import HistoryRequest
from schemas.response import BaseResponse, MessageItem
from db.connection import get_db

router = APIRouter(prefix="/rag/chat", tags=["Chat"])

logger = logging.getLogger(__name__)


@router.get("/history", response_model=BaseResponse)
async def get_history(
    session_id: str | None = Query(None),
    user_id: str | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    """
    获取会话历史

    - **session_id**: 会话ID（可选）
    - **user_id**: 用户ID（可选）
    - **offset**: 跳过的消息数量（分页用）
    - **limit**: 返回消息数量限制
    """
    try:
        from services.chat.db_history_service import DatabaseHistoryService

        if not session_id:
            return BaseResponse(
                code=200,
                message="success",
                data={
                    "session_id": None,
                    "messages": [],
                    "has_more": False,
                },
            )

        history_svc = DatabaseHistoryService()
        result = await history_svc.get_history(session_id, limit=limit, offset=offset)

        return BaseResponse(
            code=200,
            message="success",
            data={
                "session_id": session_id,
                "messages": result["messages"],
                "has_more": result["has_more"],
            },
        )

    except Exception as e:
        logger.error(f"获取会话历史失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history", response_model=BaseResponse)
async def delete_history(
    session_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    """
    清空会话历史

    - **session_id**: 要删除的会话ID
    """
    try:
        from services.chat.history_service import HistoryService

        history_svc = HistoryService()
        success = await history_svc.delete_history(session_id)

        if not success:
            raise HTTPException(status_code=404, detail="会话不存在")

        return BaseResponse(
            code=200,
            message="删除成功",
            data={"session_id": session_id},
        )

    except Exception as e:
        logger.error(f"删除会话历史失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
