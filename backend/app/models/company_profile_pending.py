from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class CompanyProfilePending(Base, TimestampMixin):
    """企业信息待审核表"""
    __tablename__ = "company_profile_pending"

    pending_id = Column(String(36), primary_key=True)
    company_id = Column(String(36), ForeignKey("companies.company_id", ondelete="CASCADE"), nullable=False)
    address = Column(Text)
    email = Column(String(255))
    contact = Column(String(100))
    contact_phone = Column(String(50))
    status = Column(String(20), nullable=False, default="pending")  # pending/approved/rejected
    reject_reason = Column(Text)
    submitted_at = Column(DateTime, nullable=False)
    reviewed_at = Column(DateTime)
    reviewed_by = Column(String(36))

    company = relationship("Company", back_populates="profile_pending")