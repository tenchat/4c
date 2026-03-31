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

    async def get_recommended_jobs(self, account_id: str, limit: int = 5) -> list:
        # 获取学生档案
        profile = await self.get_profile(account_id)
        if not profile:
            return []

        # 根据学生意向城市和行业推荐岗位
        query = select(JobDescription).where(JobDescription.status == 1)

        # TODO: 完善推荐逻辑（匹配城市/行业）

        result = await self.db.execute(query.limit(limit))
        return result.scalars().all()

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
