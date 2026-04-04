"""
简历文档解析 API 路由
"""

import logging
import os
import uuid
import tempfile

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel

from schemas.response import BaseResponse
from services.document.resume_parser import resume_parser

router = APIRouter(prefix="/rag", tags=["简历"])


class ResumeParseRequest(BaseModel):
    """简历解析请求（用于描述）"""
    pass


@router.post("/resume/parse")
async def parse_resume(
    file: UploadFile = File(...),
) -> BaseResponse:
    """
    解析简历文档

    支持 PDF、Word (.docx, .doc)、纯文本格式
    上传文件后返回解析后的文本内容
    """
    logger = logging.getLogger(__name__)

    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名为空")

        # 检查文件类型
        ext = os.path.splitext(file.filename)[1].lower()
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
        temp_filename = f"resume_{uuid.uuid4().hex}{ext}"
        temp_path = os.path.join(temp_dir, temp_filename)

        with open(temp_path, "wb") as f:
            f.write(content)

        try:
            # 解析文档
            text = resume_parser.parse(temp_path)
            logger.info(f"简历解析成功: {file.filename}, {len(text)} 字符")
            return BaseResponse(
                code=200,
                message="success",
                data={
                    "filename": file.filename,
                    "text": text,
                    "char_count": len(text)
                }
            )
        finally:
            # 删除临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"简历解析失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"简历解析失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")
