import enum
from sqlalchemy import Column, String, Text, Date, Time, Integer, SmallInteger, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class ActivityType(str, enum.Enum):
    seminar = "seminar"
    job_fair = "job_fair"
    other = "other"


class ActivityStatus(int, enum.Enum):
    ongoing = 1       # 进行中/待举办
    ended = 2         # 已结束
    cancelled = 0     # 已取消


class CompanyActivity(Base, TimestampMixin):
    __tablename__ = "company_activities"

    activity_id = Column(String(36), primary_key=True)
    company_id = Column(String(36), ForeignKey("companies.company_id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(SQLEnum(ActivityType, name="activity_type_enum", create_type=False), nullable=False, index=True)
    type_name = Column(String(50), nullable=True, comment="当type为other时，自定义活动类型名称")
    title = Column(String(200), nullable=False)
    location = Column(String(200), nullable=True)
    activity_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(SmallInteger, nullable=False, default=1, index=True)
    expected_num = Column(Integer, nullable=True)
    actual_num = Column(Integer, nullable=True)

    company = relationship("Company", back_populates="activities")