from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from app.models.base import Base, TimestampMixin

class EmploymentWarning(Base, TimestampMixin):
    __tablename__ = "employment_warnings"

    warning_id = Column(String(36), primary_key=True)
    account_id = Column(String(36), ForeignKey("accounts.account_id", ondelete="CASCADE"), nullable=False)
    university_id = Column(String(36), ForeignKey("universities.university_id"))
    warning_type = Column(String(50), nullable=False)  # skill_gap/high_expectation/location_limit/experience_lack
    level = Column(Integer, nullable=False, default=2, index=True)  # 1红 2黄 3绿
    ai_suggestion = Column(Text)  # AI 生成的辅导建议
    handled = Column(Boolean, nullable=False, default=False, index=True)
    handled_at = Column(DateTime)
