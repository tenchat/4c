"""
知识库文档模型
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy 声明基类"""

    pass


class KnowledgeDocument(Base):
    """知识库文档表"""

    __tablename__ = "knowledge_documents"

    doc_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    doc_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    category: Mapped[str] = mapped_column(
        String(20), nullable=False, default="shared"
    )
    vector_ids: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "content": self.content,
            "doc_type": self.doc_type,
            "category": self.category,
            "vector_ids": self.vector_ids,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
