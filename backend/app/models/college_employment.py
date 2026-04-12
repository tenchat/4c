from sqlalchemy import Column, String, Integer, DECIMAL, ForeignKey
from app.models.base import Base, TimestampMixin

class CollegeEmployment(Base, TimestampMixin):
    __tablename__ = "college_employment"

    record_id = Column(String(36), primary_key=True)
    university_id = Column(String(36), ForeignKey("universities.university_id", ondelete="CASCADE"), nullable=False)
    college_name = Column(String(100), nullable=False)
    graduation_year = Column(Integer, nullable=False)
    degree_level = Column(String(50))  # 学历层次：本科生/硕士生/博士生
    graduation_type = Column(String(20))  # 毕业/结业
    graduate_nums = Column(Integer, default=0)
    employed_nums = Column(Integer, default=0)
    contract_nums = Column(Integer, default=0)  # 签约人数
    total_graduate_school_nums = Column(Integer, default=0)  # 总升学人数
    domestic_graduate_school_nums = Column(Integer, default=0)  # 境内升学人数
    overseas_graduate_school_nums = Column(Integer, default=0)  # 境外升学人数
    employment_rate = Column(DECIMAL(5, 2))
    further_study_nums = Column(Integer, default=0)
    further_study_rate = Column(DECIMAL(5, 2))
    overseas_nums = Column(Integer, default=0)
    overseas_rate = Column(DECIMAL(5, 2))
    avg_salary = Column(Integer)
