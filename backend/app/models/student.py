from sqlalchemy import Column, String, Integer, DateTime, DECIMAL, ForeignKey, JSON, Index
from app.models.base import Base, TimestampMixin

class StudentProfile(Base, TimestampMixin):
    __tablename__ = "student_profiles"
    __table_args__ = (
        Index('ix_student_profiles_university_status', 'university_id', 'employment_status'),
        Index('ix_student_profiles_university_major', 'university_id', 'major'),
    )

    profile_id = Column(String(36), primary_key=True)
    account_id = Column(String(36), ForeignKey("accounts.account_id", ondelete="CASCADE"), nullable=False, unique=True)
    university_id = Column(String(36), ForeignKey("universities.university_id"), index=True)
    student_no = Column(String(30))
    college = Column(String(100))  # 所在学院
    major = Column(String(100))
    degree = Column(Integer, default=1)  # 1本科 2硕士 3博士
    graduation_year = Column(Integer)
    province_origin = Column(String(20))  # 生源省份
    gpa = Column(String(10))  # 存储为字符串，API层做类型转换
    skills = Column(JSON)  # ["Python","Java"]
    internship = Column(String(1000))
    employment_status = Column(Integer, default=0, index=True)  # 0待就业 1已就业 2升学 3出国
    desire_city = Column(String(50))
    desire_industry = Column(String(100))
    desire_salary_min = Column(Integer)
    desire_salary_max = Column(Integer)
    cur_company = Column(String(100))
    cur_city = Column(String(50))
    cur_industry = Column(String(100))
    cur_salary = Column(Integer)
    resume_url = Column(String(255))
    profile_complete = Column(Integer, default=0)  # 档案完整度 0-100
