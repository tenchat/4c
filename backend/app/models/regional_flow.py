from sqlalchemy import Column, String, Integer, ForeignKey
from app.models.base import Base, TimestampMixin


class RegionalFlow(Base, TimestampMixin):
    __tablename__ = "regional_flow"

    record_id = Column(String(36), primary_key=True)
    university_id = Column(String(36), ForeignKey("universities.university_id", ondelete="CASCADE"), nullable=False)
    degree_level = Column(String(50))  # 学历层次: 本科毕业生/毕业研究生
    graduation_year = Column(Integer, nullable=False)
    east_nums = Column(Integer, default=0)  # 东部地区人数
    central_nums = Column(Integer, default=0)  # 中部地区人数
    west_chongqing_nums = Column(Integer, default=0)  # 西部地区-重庆市人数
    west_sichuan_nums = Column(Integer, default=0)  # 西部地区-四川省人数
    west_other_nums = Column(Integer, default=0)  # 西部地区-其他省区人数
    hmt_nums = Column(Integer, default=0)  # 港澳台及其他人数
    total_nums = Column(Integer, default=0)  # 统计总数
