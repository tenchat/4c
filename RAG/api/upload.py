"""
知识库上传 API
"""

import logging
import os
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.response import BaseResponse, UploadResponse
from services.document.knowledge_sync import KnowledgeSyncService
from db.connection import get_db

router = APIRouter(prefix="/rag/knowledge", tags=["Knowledge"])

logger = logging.getLogger(__name__)


def _sanitize_filename(filename: str | None) -> str:
    """
    清理文件名，防止路径遍历

    Args:
        filename: 原始文件名

    Returns:
        清理后的安全文件名
    """
    if not filename:
        return "uploaded_file"

    # 移除路径组件，只保留文件名
    safe_name = os.path.basename(filename)

    # 移除非安全字符（保留字母、数字、中文、点和短横线）
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in (".", "-", "_", " "))

    # 移除多余的点和空格
    safe_name = safe_name.strip(". ")

    # 如果为空或无效，生成随机名称
    if not safe_name:
        safe_name = f"upload_{uuid.uuid4().hex[:8]}"

    return safe_name[:255]  # 限制最大长度


@router.post("/upload", response_model=BaseResponse)
async def upload_knowledge(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form("shared"),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    """
    上传知识文档

    支持格式：.txt, .pdf, .docx
    - **file**: 要上传的文件
    - **title**: 文档标题
    - **category**: 分类 (student/school/company/shared)
    """
    # 1. 验证文件类型
    allowed_extensions = {".txt", ".pdf", ".docx", ".doc"}
    safe_filename = _sanitize_filename(file.filename)
    ext = Path(safe_filename).suffix.lower()

    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {ext}。支持的格式: {', '.join(allowed_extensions)}",
        )

    # 2. 保存到临时文件
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        logger.info(f"文件已保存到临时目录: {tmp_path}")

        # 3. 同步到知识库
        sync_service = KnowledgeSyncService(db)
        result = await sync_service.add_document(
            file_path=tmp_path,
            title=title,
            category=category,
        )

        return BaseResponse(
            code=200,
            message="上传成功",
            data=UploadResponse(
                doc_id=result["doc_id"],
                chunks=result["chunks"],
            ).model_dump(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传文件失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="服务器内部错误")

    finally:
        # 4. 清理临时文件
        if tmp_path and Path(tmp_path).exists():
            os.unlink(tmp_path)
            logger.info(f"临时文件已清理: {tmp_path}")


@router.get("/list", response_model=BaseResponse)
async def list_knowledge(
    category: str | None = None,
    page: int = 1,
    page_size: int = 10,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    """获取知识库列表"""
    from db.repositories.knowledge_repo import KnowledgeRepository

    try:
        repo = KnowledgeRepository(db)

        if category:
            items = await repo.get_by_type(category)
        else:
            items = await repo.get_all(limit=page_size, offset=(page - 1) * page_size)

        return BaseResponse(
            code=200,
            message="success",
            data={
                "items": items,
                "total": len(items),
                "page": page,
                "page_size": page_size,
            },
        )

    except Exception as e:
        logger.error(f"获取知识库列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{doc_id}", response_model=BaseResponse)
async def delete_knowledge(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse:
    """删除知识文档"""
    from services.document.knowledge_sync import KnowledgeSyncService

    try:
        sync_service = KnowledgeSyncService(db)
        success = await sync_service.delete_document(doc_id)

        if not success:
            raise HTTPException(status_code=404, detail="文档不存在")

        return BaseResponse(
            code=200,
            message="删除成功",
            data={"doc_id": doc_id},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除文档失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
