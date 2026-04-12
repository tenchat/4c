import enum
from sqlalchemy import Column, String, Text, Date, Integer, SmallInteger, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class AnnouncementStatus(int, enum.Enum):
    draft = 0        # 草稿
    published = 1    # 发布中
    expired = 2     # 已过期


class CompanyAnnouncement(Base, TimestampMixin):
    __tablename__ = "company_announcements"

    announcement_id = Column(String(36), primary_key=True)
    company_id = Column(String(36), ForeignKey("companies.company_id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    target_major = Column(String(200), nullable=True)
    target_degree = Column(SmallInteger, nullable=True)
    headcount = Column(Integer, nullable=True)
    deadline = Column(Date, nullable=True)
    status = Column(SmallInteger, nullable=False, default=1, index=True)
    published_at = Column(DateTime, nullable=True)

    company = relationship("Company", back_populates="announcements")