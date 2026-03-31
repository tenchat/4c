from sqlalchemy import Column, String, Boolean, Integer, DateTime
from app.models.base import Base, TimestampMixin

class KnowledgeDocument(Base, TimestampMixin):
    __tablename__ = "knowledge_documents"

    doc_id = Column(String(36), primary_key=True)
    title = Column(String(200), nullable=False)
    doc_type = Column(String(50), nullable=False)  # college_report/job_market/policy/scarce_talent
    collection = Column(String(50), nullable=False, index=True)  # ChromaDB collection 名
    source = Column(String(300))
    chunk_count = Column(Integer, default=0)
    indexed = Column(Boolean, default=False, index=True)
