"""
响应模型
"""

from typing import Any
from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """基础响应"""

    code: int = 200
    message: str = "success"
    data: dict | None = None


class SourceItem(BaseModel):
    """来源项"""

    type: str = Field(..., description="来源类型: structured/document")
    table: str | None = Field(default=None, description="来源表名")
    doc_id: str | None = Field(default=None, description="文档ID")
    content: str = Field(..., description="内容片段")
    metadata: dict | None = Field(default=None, description="元数据")


class QAResponse(BaseModel):
    """问答响应"""

    answer: str = Field(..., description="回答内容")
    sources: list[SourceItem] = Field(default_factory=list, description="来源列表")
    session_id: str = Field(..., description="会话ID")


class UploadResponse(BaseModel):
    """上传响应"""

    doc_id: str = Field(..., description="文档ID")
    chunks: int = Field(..., description="分块数量")


class KnowledgeItem(BaseModel):
    """知识库项"""

    doc_id: str
    title: str
    category: str
    created_at: str


class MessageItem(BaseModel):
    """消息项"""

    type: str = Field(..., description="消息类型: user/assistant")
    content: str
    created_at: str
