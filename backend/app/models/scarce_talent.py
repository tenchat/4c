from sqlalchemy import Column, String, Integer
from app.models.base import Base, TimestampMixin

class ScarceTalent(Base, TimestampMixin):
    __tablename__ = "scarce_talents"

    talent_id = Column(String(36), primary_key=True)
    province = Column(String(20), nullable=False, index=True)
    job_type = Column(String(100), nullable=False)  # 岗位类型
    shortage_level = Column(Integer, nullable=False, index=True)  # 1轻微 2中等 3严重
    industry = Column(String(100))
    data_year = Column(Integer)
    source = Column(String(200))  # 数据来源
