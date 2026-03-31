from sqlalchemy import Column, String, DateTime
from app.models.base import Base, TimestampMixin

class University(Base, TimestampMixin):
    __tablename__ = "universities"

    university_id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    province = Column(String(20))
    city = Column(String(50))
    type = Column(String(50))  # 综合/理工/师范等
