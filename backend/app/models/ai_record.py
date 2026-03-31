from sqlalchemy import Column, String, Integer, JSON
from app.models.base import Base, TimestampMixin

class AIAnalysisRecord(Base, TimestampMixin):
    __tablename__ = "ai_analysis_records"

    record_id = Column(String(36), primary_key=True)
    account_id = Column(String(36), nullable=False, index=True)
    analysis_type = Column(String(50), nullable=False)  # employment_profile/resume/decision/skill_path/warning/qa
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON)
    tokens_used = Column(Integer)
    duration_ms = Column(Integer)
    status = Column(Integer, default=1)  # 1成功 0失败
