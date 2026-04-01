from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.company import Company
from app.models.job import JobDescription, JobApplication
from app.models.student import StudentProfile
import uuid
from datetime import datetime, timedelta


class CompanyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_data(self, company_id: str) -> dict:
        """企业招聘统计 - 优化为单次查询"""
        # 一次查询获取岗位统计和申请统计
        result = await self.db.execute(
            select(
                func.count(JobDescription.job_id).filter(JobDescription.status == 1).label('published'),
                func.count(JobApplication.application_id).label('received'),
                func.count(JobApplication.application_id).filter(JobApplication.status == 3).label('hired')
            )
            .outerjoin(JobApplication, JobApplication.job_id == JobDescription.job_id)
            .where(JobDescription.company_id == company_id)
        )
        row = result.one()

        return {
            "published_jobs": row.published or 0,
            "received_resumes": row.received or 0,
            "hired_count": row.hired or 0,
            "trend_data": []
        }

    async def get_jobs(
        self,
        company_id: str,
        status: int,
        page: int,
        page_size: int,
        title: str = None,
        city: str = None,
        industry: str = None,
        min_salary: int = None,
        max_salary: int = None
    ) -> dict:
        """岗位列表"""
        conditions = [JobDescription.company_id == company_id]
        if status is not None:
            conditions.append(JobDescription.status == status)
        if title:
            conditions.append(JobDescription.title.like(f"%{title}%"))
        if city:
            conditions.append(JobDescription.city.like(f"%{city}%"))
        if industry:
            conditions.append(JobDescription.industry == industry)

        # 查询总数
        count_result = await self.db.execute(
            select(func.count(JobDescription.job_id)).where(and_(*conditions))
        )
        total = count_result.scalar() or 0

        # 分页查询
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(JobDescription)
            .where(and_(*conditions))
            .order_by(JobDescription.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        jobs = result.scalars().all()

        return {
            "list": [{
                "job_id": j.job_id,
                "title": j.title,
                "city": j.city,
                "province": j.province,
                "industry": j.industry,
                "min_salary": j.min_salary,
                "max_salary": j.max_salary,
                "min_degree": j.min_degree,
                "min_exp_years": j.min_exp_years,
                "keywords": j.keywords,
                "description": j.description,
                "status": j.status,
                "published_at": str(j.published_at) if j.published_at else None,
                "expired_at": str(j.expired_at) if j.expired_at else None
            } for j in jobs],
            "total": total,
            "page": page,
            "page_size": page_size
        }

    async def get_job(self, job_id: str, company_id: str) -> dict | None:
        """获取单个岗位"""
        result = await self.db.execute(
            select(JobDescription).where(
                and_(JobDescription.job_id == job_id, JobDescription.company_id == company_id)
            )
        )
        job = result.scalar_one_or_none()
        if not job:
            return None
        return {
            "job_id": job.job_id,
            "title": job.title,
            "city": job.city,
            "province": job.province,
            "industry": job.industry,
            "min_salary": job.min_salary,
            "max_salary": job.max_salary,
            "min_degree": job.min_degree,
            "min_exp_years": job.min_exp_years,
            "keywords": job.keywords,
            "description": job.description,
            "status": job.status,
            "published_at": str(job.published_at) if job.published_at else None,
            "expired_at": str(job.expired_at) if job.expired_at else None
        }

    async def create_job(self, company_id: str, data: dict) -> str:
        """发布岗位"""
        published_at = datetime.utcnow()
        # Default expired_at is 30 days after publishing
        expired_at = datetime.utcnow() + timedelta(days=30)
        job = JobDescription(
            job_id=str(uuid.uuid4()),
            company_id=company_id,
            title=data.get("title"),
            city=data.get("city"),
            province=data.get("province"),
            industry=data.get("industry"),
            min_salary=data.get("min_salary"),
            max_salary=data.get("max_salary"),
            min_degree=data.get("min_degree", 1),
            min_exp_years=data.get("min_exp_years", 0),
            keywords=data.get("keywords"),
            description=data.get("description"),
            status=1,
            published_at=published_at,
            expired_at=expired_at
        )
        self.db.add(job)
        await self.db.commit()
        return job.job_id

    async def update_job(self, job_id: str, company_id: str, data: dict) -> bool:
        """更新岗位（检查权限）"""
        result = await self.db.execute(
            select(JobDescription).where(JobDescription.job_id == job_id)
        )
        job = result.scalar_one_or_none()
        if not job:
            return False

        if job.company_id != company_id:
            raise PermissionError("无权限修改")

        for key, value in data.items():
            if hasattr(job, key) and key not in ("job_id", "company_id"):
                setattr(job, key, value)

        await self.db.commit()
        return True

    async def toggle_job_status(self, job_id: str, company_id: str, status: int) -> bool:
        """切换岗位上下架状态"""
        result = await self.db.execute(
            select(JobDescription).where(JobDescription.job_id == job_id)
        )
        job = result.scalar_one_or_none()
        if not job:
            return False

        if job.company_id != company_id:
            raise PermissionError("无权限修改")

        job.status = status
        await self.db.commit()
        return True

    async def delete_job(self, job_id: str, company_id: str) -> bool:
        """删除岗位（硬删除）"""
        result = await self.db.execute(
            select(JobDescription).where(JobDescription.job_id == job_id)
        )
        job = result.scalar_one_or_none()
        if not job:
            return False

        if job.company_id != company_id:
            raise PermissionError("无权限删除")

        # 硬删除岗位（JobApplication 会通过 CASCADE 自动删除）
        await self.db.delete(job)
        await self.db.commit()
        return True

    async def get_profile(self, company_id: str) -> Company | None:
        """获取企业档案"""
        result = await self.db.execute(
            select(Company).where(Company.company_id == company_id)
        )
        return result.scalar_one_or_none()

    async def update_profile(self, company_id: str, data: dict) -> bool:
        """更新企业档案"""
        result = await self.db.execute(
            select(Company).where(Company.company_id == company_id)
        )
        company = result.scalar_one_or_none()
        if not company:
            return False

        # 可更新的字段
        updatable_fields = ["company_name", "industry", "city", "size", "description"]
        for key, value in data.items():
            if key in updatable_fields and hasattr(company, key):
                setattr(company, key, value)

        await self.db.commit()
        return True
