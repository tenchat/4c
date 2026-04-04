from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.student import StudentProfile
from app.models.job import JobDescription, JobApplication
import uuid


class StudentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_profile(self, account_id: str) -> StudentProfile | None:
        result = await self.db.execute(
            select(StudentProfile).where(StudentProfile.account_id == account_id)
        )
        return result.scalar_one_or_none()

    async def update_profile(self, account_id: str, data: dict) -> bool:
        from app.models.account import Account

        # 获取学生档案
        result = await self.db.execute(
            select(StudentProfile).where(StudentProfile.account_id == account_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            return False

        # 更新学生档案
        for key, value in data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        # 如果有 real_name，需要更新 Account 表
        if 'real_name' in data:
            account_result = await self.db.execute(
                select(Account).where(Account.account_id == account_id)
            )
            account = account_result.scalar_one_or_none()
            if account:
                account.real_name = data['real_name']

        await self.db.commit()
        return True

    async def get_recommended_jobs(self, account_id: str, limit: int = 50) -> list:
        # 获取学生档案
        profile = await self.get_profile(account_id)
        if not profile:
            return []

        # 根据学生意向城市和行业推荐岗位
        from sqlalchemy import select
        from app.models.company import Company

        query = (
            select(JobDescription, Company.company_name)
            .outerjoin(Company, JobDescription.company_id == Company.company_id)
            .where(JobDescription.status == 1)
            .limit(limit)
        )

        result = await self.db.execute(query)
        rows = result.all()

        # 转换为包含 company_name 的结果
        jobs = []
        for row in rows:
            job = row[0]
            job.company_name = row[1] if len(row) > 1 else None
            jobs.append(job)

        return jobs

    async def get_jobs_with_filters(
        self,
        keyword: str = "",
        city: str = "",
        industry: str = "",
        min_salary: int = 0,
        max_salary: int = 0,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list, int]:
        """根据筛选条件获取岗位列表"""
        from sqlalchemy import select, func
        from app.models.company import Company

        # 构建基础查询
        query = (
            select(JobDescription, Company.company_name)
            .outerjoin(Company, JobDescription.company_id == Company.company_id)
            .where(JobDescription.status == 1)
        )

        # 关键词筛选（搜索职位名称和公司名称）
        if keyword:
            keyword_pattern = f"%{keyword}%"
            query = query.where(
                (JobDescription.title.like(keyword_pattern)) |
                (Company.company_name.like(keyword_pattern))
            )

        # 城市筛选
        if city:
            query = query.where(JobDescription.city.like(f"%{city}%"))

        # 行业筛选
        if industry:
            query = query.where(JobDescription.industry == industry)

        # 薪资范围筛选
        if min_salary > 0:
            query = query.where(JobDescription.max_salary >= min_salary)
        if max_salary > 0:
            query = query.where(JobDescription.min_salary <= max_salary)

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # 分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        # 按发布时间排序
        query = query.order_by(JobDescription.published_at.desc())

        result = await self.db.execute(query)
        rows = result.all()

        # 转换为包含 company_name 的结果
        jobs = []
        for row in rows:
            job = row[0]
            job.company_name = row[1] if len(row) > 1 else None
            jobs.append(job)

        return jobs, total

    async def apply_job(self, account_id: str, job_id: str) -> bool:
        # 检查是否重复投递
        result = await self.db.execute(
            select(JobApplication).where(
                JobApplication.job_id == job_id,
                JobApplication.account_id == account_id
            )
        )
        if result.scalar_one_or_none():
            return False

        application = JobApplication(
            application_id=str(uuid.uuid4()),
            job_id=job_id,
            account_id=account_id,
            status=0
        )
        self.db.add(application)
        await self.db.commit()
        return True
