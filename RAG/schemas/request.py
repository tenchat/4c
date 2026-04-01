"""
请求模型
"""

from pydantic import BaseModel, Field


class QARequest(BaseModel):
    """问答请求"""

    question: str = Field(..., description="用户问题", min_length=1)
    user_id: str = Field(..., description="用户ID")
    role_type: str = Field(
        default="student",
        description="用户角色",
        pattern="^(student|school|company)$",
    )
    session_id: str | None = Field(default=None, description="会话ID")


class UploadRequest(BaseModel):
    """上传请求"""

    title: str = Field(..., description="文档标题", min_length=1)
    category: str = Field(
        default="shared",
        description="分类",
        pattern="^(student|school|company|shared)$",
    )


class HistoryRequest(BaseModel):
    """会话历史请求"""

    session_id: str | None = None
    user_id: str | None = None
