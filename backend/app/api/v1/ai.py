"""
AI 问答 API

集成 RAG 服务，提供智能问答功能
- /qa: 非流式问答
- /qa/stream: SSE 流式问答
- /knowledge/upload: 上传知识库文档
"""

import json
import logging
from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.core.config import get_settings
from app.schemas.ai import (
    EmploymentProfileRequest,
    ResumeAnalysisRequest,
    ResumeOptimizeRequest,
    DecisionRequest,
    WarningRequest,
    QARequest,
)
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)

router = APIRouter()


def get_ai_service(db: AsyncSession = Depends(get_db)) -> AIService:
    return AIService(db)


def get_rag_settings():
    return get_settings()


@router.post("/employment-profile")
async def employment_profile(
    req: EmploymentProfileRequest,
    payload: dict = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    """生成就业画像分析"""
    data = await service.generate_profile(req.model_dump())
    return {"code": 200, "message": "success", "data": data}


@router.post("/resume-analysis")
async def resume_analysis(
    req: ResumeAnalysisRequest,
    payload: dict = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    """简历分析"""
    data = await service.analyze_resume(req.resume_text, req.target_job)
    return {"code": 200, "message": "success", "data": data}


@router.post("/graduate-vs-job")
async def graduate_vs_job(
    req: DecisionRequest,
    payload: dict = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    """考研 vs 就业决策分析"""
    data = await service.graduate_vs_job(req.target_city, req.expected_salary, req.study_months)
    return {"code": 200, "message": "success", "data": data}


@router.post("/warning")
async def generate_warning(
    req: WarningRequest,
    payload: dict = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    """生成就业预警"""
    data = await service.generate_warning(req.account_ids)
    return {"code": 200, "message": "success", "data": data}


@router.post("/qa")
async def ai_qa(
    req: QARequest,
    payload: dict = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    """
    智能问答（非流式）

    调用 RAG 服务获取回答
    """
    try:
        result = await service.qa(
            question=req.question,
            user_id=payload.get("sub", req.user_id),
            role_type=req.role_type,
            session_id=req.session_id,
        )
        return {"code": 200, "message": "success", "data": result}
    except Exception as e:
        logger.error(f"AI QA error: {e}", exc_info=True)
        return {"code": 500, "message": str(e), "data": None}


@router.post("/qa/stream")
async def ai_qa_stream(
    req: QARequest,
    payload: dict = Depends(get_current_user),
):
    """
    智能问答（流式输出 - SSE）

    将 RAG 服务的 SSE 流转发给前端
    """
    settings = get_rag_settings()
    rag_url = settings.RAG_SERVICE_URL

    user_id = payload.get("sub") or req.user_id or "unknown"
    role_type = req.role_type or "student"

    async def generate():
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
                async with client.stream(
                    "POST",
                    f"{rag_url}/rag/qa/stream",
                    json={
                        "question": req.question,
                        "user_id": user_id,
                        "role_type": role_type,
                        "session_id": req.session_id,
                    },
                ) as response:
                    async for chunk in response.aiter_bytes():
                        if chunk:
                            yield chunk
        except httpx.TimeoutException:
            error_data = {"content": "RAG 服务响应超时", "done": True}
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n".encode()
        except Exception as e:
            logger.error(f"SSE stream error: {e}", exc_info=True)
            error_data = {"content": f"流式响应错误: {str(e)}", "done": True}
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n".encode()

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/knowledge/upload")
async def knowledge_upload(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form("shared"),
    payload: dict = Depends(get_current_user),
):
    """
    上传知识文档

    支持格式：.txt, .pdf, .docx, .doc
    """
    settings = get_rag_settings()
    rag_url = settings.RAG_SERVICE_URL

    # 验证文件类型
    allowed_extensions = {".txt", ".pdf", ".docx", ".doc"}
    ext = Path(file.filename).suffix.lower() if file.filename else ""

    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {ext}。支持的格式: {', '.join(allowed_extensions)}",
        )

    try:
        # 读取文件内容
        file_content = await file.read()

        # 调用 RAG 服务上传
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.post(
                f"{rag_url}/rag/knowledge/upload",
                files={"file": (file.filename or "upload", file_content)},
                data={"title": title, "category": category},
            )
            response.raise_for_status()
            result = response.json()

            if result.get("code") == 200:
                return {"code": 200, "message": "上传成功", "data": result.get("data")}
            else:
                raise HTTPException(status_code=500, detail=result.get("message", "上传失败"))

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="上传超时")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Knowledge upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/list")
async def knowledge_list(
    category: str | None = None,
    page: int = 1,
    page_size: int = 10,
    payload: dict = Depends(get_current_user),
):
    """
    获取知识库列表
    """
    settings = get_rag_settings()
    rag_url = settings.RAG_SERVICE_URL

    try:
        params = {"page": page, "page_size": page_size}
        if category:
            params["category"] = category

        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            response = await client.get(
                f"{rag_url}/rag/knowledge/list",
                params=params,
            )
            response.raise_for_status()
            result = response.json()

            if result.get("code") == 200:
                return {"code": 200, "message": "success", "data": result.get("data")}
            else:
                raise HTTPException(status_code=500, detail=result.get("message", "获取列表失败"))

    except Exception as e:
        logger.error(f"Knowledge list error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/knowledge/{doc_id}")
async def knowledge_delete(
    doc_id: str,
    payload: dict = Depends(get_current_user),
):
    """
    删除知识文档
    """
    settings = get_rag_settings()
    rag_url = settings.RAG_SERVICE_URL

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            response = await client.delete(f"{rag_url}/rag/knowledge/{doc_id}")
            response.raise_for_status()
            result = response.json()

            if result.get("code") == 200:
                return {"code": 200, "message": "删除成功", "data": None}
            else:
                raise HTTPException(status_code=500, detail=result.get("message", "删除失败"))

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="文档不存在")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Knowledge delete error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/history")
async def chat_history(
    session_id: str | None = None,
    user_id: str | None = None,
    payload: dict = Depends(get_current_user),
):
    """
    获取聊天历史
    """
    settings = get_rag_settings()
    rag_url = settings.RAG_SERVICE_URL

    try:
        params = {}
        if session_id:
            params["session_id"] = session_id
        if user_id:
            params["user_id"] = user_id

        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            response = await client.get(
                f"{rag_url}/rag/chat/history",
                params=params,
            )
            response.raise_for_status()
            result = response.json()

            if result.get("code") == 200:
                return {"code": 200, "message": "success", "data": result.get("data", [])}
            else:
                return {"code": 200, "message": "success", "data": []}

    except Exception as e:
        logger.error(f"Chat history error: {e}", exc_info=True)
        return {"code": 200, "message": "success", "data": []}


@router.post("/resume/optimize")
async def resume_optimize(
    req: ResumeOptimizeRequest,
    payload: dict = Depends(get_current_user),
    service: AIService = Depends(get_ai_service)
):
    """
    AI 简历优化

    根据学生画像和目标岗位，优化简历内容并给出修改建议
    """
    account_id = payload.get("sub")

    result = await service.optimize_resume(account_id, req.resume_text, req.target_job)

    if result.get("status") == "success":
        return {"code": 200, "message": "success", "data": result.get("data")}
    else:
        return {"code": 500, "message": result.get("message", "优化失败"), "data": None}


@router.post("/resume/export-pdf")
async def export_resume_pdf(
    req: ResumeOptimizeRequest,
    payload: dict = Depends(get_current_user),
):
    """
    导出简历为 PDF

    将 Markdown 格式的简历文本导出为 PDF 文件
    """
    from fastapi.responses import Response
    from app.services.resume_export import export_resume_to_pdf

    try:
        pdf_data = export_resume_to_pdf(req.resume_text, "optimized_resume.pdf")

        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=optimized_resume.pdf"
            }
        )
    except Exception as e:
        logger.error(f"PDF export error: {e}", exc_info=True)
        # 返回错误信息作为 JSON，而不是抛出异常（否则 axios blob 会解析失败）
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": f"PDF 导出失败: {str(e)}", "data": None}
        )


@router.post("/resume/parse-file")
async def parse_resume_file(
    file: UploadFile = File(...),
    payload: dict = Depends(get_current_user),
):
    """
    解析简历文档（文件上传方式）

    上传 PDF、Word 文件，返回解析后的文本内容
    """
    import tempfile
    import os
    from fastapi import UploadFile, File, HTTPException

    settings = get_rag_settings()
    rag_url = settings.RAG_SERVICE_URL

    try:
        # 检查文件类型
        ext = os.path.splitext(file.filename or "")[1].lower()
        allowed_exts = {".pdf", ".docx", ".doc", ".txt"}
        if ext not in allowed_exts:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的格式: {ext}。支持的格式: {', '.join(allowed_exts)}"
            )

        # 读取文件内容
        content = await file.read()

        # 检查文件大小 (10MB)
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="文件超过 10MB 限制")

        # 保存到临时文件
        temp_dir = tempfile.gettempdir()
        temp_filename = f"resume_upload_{os.getpid()}{ext}"
        temp_path = os.path.join(temp_dir, temp_filename)

        with open(temp_path, "wb") as f:
            f.write(content)

        try:
            # 调用 RAG 服务解析
            async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
                with open(temp_path, "rb") as f:
                    files = {"file": (file.filename or "resume", f)}
                    response = await client.post(
                        f"{rag_url}/rag/resume/parse",
                        files=files
                    )
                response.raise_for_status()
                result = response.json()

                if result.get("code") == 200:
                    return {"code": 200, "message": "success", "data": result.get("data")}
                else:
                    raise HTTPException(status_code=500, detail=result.get("message", "解析失败"))
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"简历解析失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")
