from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class Company(Base, TimestampMixin):
    __tablename__ = "companies"

    company_id = Column(String(36), primary_key=True)
    account_id = Column(String(36), ForeignKey("accounts.account_id", ondelete="CASCADE"), nullable=False, unique=True)
    company_name = Column(String(100), nullable=False)
    industry = Column(String(100))
    city = Column(String(50))
    size = Column(String(20))  # 规模：50人以下/50-200人等
    description = Column(Text)
    address = Column(String(255))
    email = Column(String(100))
    contact = Column(String(50))
    contact_phone = Column(String(20))
    verified = Column(Boolean, nullable=False, default=False, index=True)  # 管理员审核，已添加索引

    activities = relationship("CompanyActivity", back_populates="company", cascade="all, delete-orphan")
    announcements = relationship("CompanyAnnouncement", back_populates="company", cascade="all, delete-orphan")
    profile_pending = relationship("CompanyProfilePending", back_populates="company", cascade="all, delete-orphan")
