from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON, Text, Index
from app.models.base import Base, TimestampMixin

class JobDescription(Base, TimestampMixin):
    __tablename__ = "job_descriptions"
    __table_args__ = (
        Index('ix_job_descriptions_company_status', 'company_id', 'status'),
    )

    job_id = Column(String(36), primary_key=True)
    company_id = Column(String(36), ForeignKey("companies.company_id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(100), nullable=False)
    city = Column(String(50))
    province = Column(String(20))
    industry = Column(String(100), index=True)
    min_salary = Column(Integer)
    max_salary = Column(Integer)
    min_degree = Column(Integer, default=1)  # 最低学历
    min_exp_years = Column(Integer, default=0)  # 最低经验年限
    keywords = Column(JSON)  # 技能关键词
    description = Column(Text)
    status = Column(Integer, default=1, index=True)  # 1招聘中 0暂停 2结束
    published_at = Column(DateTime)
    expired_at = Column(DateTime)

class JobApplication(Base, TimestampMixin):
    __tablename__ = "job_applications"

    application_id = Column(String(36), primary_key=True)
    job_id = Column(String(36), ForeignKey("job_descriptions.job_id", ondelete="CASCADE"), nullable=False)
    account_id = Column(String(36), ForeignKey("accounts.account_id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(Integer, nullable=False, default=0)  # 0已投递 1简历筛选 2面试中 3已录用 4已拒绝
