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
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    """
    获取会话历史

    - **session_id**: 会话ID（可选）
    - **user_id**: 用户ID（可选）
    """
    try:
        from services.chat.history_service import HistoryService

        if not session_id:
            return BaseResponse(
                code=200,
                message="success",
                data={
                    "session_id": None,
                    "messages": [],
                },
            )

        history_svc = HistoryService()
        messages = await history_svc.get_history(session_id)

        return BaseResponse(
            code=200,
            message="success",
            data={
                "session_id": session_id,
                "messages": messages,
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
