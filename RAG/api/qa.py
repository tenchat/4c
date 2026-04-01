"""
问答 API 路由
"""

import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.request import QARequest
from schemas.response import BaseResponse, SourceItem
from services.rag.rag_engine import RAGEngine
from db.connection import get_db

router = APIRouter(prefix="/rag", tags=["RAG"])


async def get_rag_engine(db: AsyncSession = Depends(get_db)) -> RAGEngine:
    """获取 RAG 引擎实例"""
    return RAGEngine(db)


@router.post("/qa", response_model=BaseResponse)
async def qa(
    req: QARequest,
    engine: RAGEngine = Depends(get_rag_engine),
) -> BaseResponse:
    """
    智能问答（非流式）

    - **question**: 用户问题
    - **user_id**: 用户ID
    - **role_type**: 用户角色 (student/school/company)
    - **session_id**: 会话ID（可选）
    """
    try:
        result = await engine.ask(
            question=req.question,
            user_id=req.user_id,
            role_type=req.role_type,
            session_id=req.session_id,
        )

        # 转换 sources 格式
        sources = []
        for doc in result.get("sources", []):
            sources.append(
                SourceItem(
                    type="document",
                    content=doc.get("content", ""),
                    metadata=doc.get("metadata", {}),
                )
            )

        return BaseResponse(
            code=200,
            message="success",
            data={
                "answer": result["answer"],
                "sources": [s.model_dump() for s in sources],
                "session_id": result["session_id"],
            },
        )

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"QA 请求失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/qa/stream")
async def qa_stream(
    req: QARequest,
    engine: RAGEngine = Depends(get_rag_engine),
):
    """
    智能问答（流式输出）

    返回 SSE 格式：
    data: {"content": "字", "done": false}
    data: {"content": "符", "done": false}
    ...
    data: {"content": "", "done": true}
    """
    logger = logging.getLogger(__name__)

    async def generate():
        try:
            async for chunk in engine.ask_stream(
                question=req.question,
                user_id=req.user_id,
                role_type=req.role_type,
                session_id=req.session_id,
            ):
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        except Exception as e:
            logger.error(f"流式 QA 请求失败: {e}", exc_info=True)
            error = {"content": f"Error: {str(e)}", "done": True}
            yield f"data: {json.dumps(error, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
