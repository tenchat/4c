from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.company import Company
from app.models.company_profile_pending import CompanyProfilePending
from app.models.job import JobDescription, JobApplication
from app.models.student import StudentProfile
import uuid
from datetime import datetime, timedelta


def format_datetime_minute(dt) -> str | None:
    """格式化时间到分钟，不显示秒"""
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%d %H:%M")


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
                "published_at": format_datetime_minute(j.published_at),
                "expired_at": format_datetime_minute(j.expired_at)
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
            "published_at": format_datetime_minute(job.published_at),
            "expired_at": format_datetime_minute(job.expired_at)
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

    async def submit_profile_for_review(self, company_id: str, data: dict) -> str:
        """提交企业档案更新申请"""
        # 检查是否有待审核的申请
        pending_result = await self.db.execute(
            select(CompanyProfilePending)
            .where(
                and_(
                    CompanyProfilePending.company_id == company_id,
                    CompanyProfilePending.status == "pending"
                )
            )
        )
        existing_pending = pending_result.scalar_one_or_none()
        if existing_pending:
            raise ValueError("已有待审核的申请，请等待审核完成")

        # 创建新的待审核申请
        pending_id = str(uuid.uuid4())
        pending = CompanyProfilePending(
            pending_id=pending_id,
            company_id=company_id,
            address=data.get("address"),
            email=data.get("email"),
            contact=data.get("contact"),
            contact_phone=data.get("contact_phone"),
            status="pending",
            submitted_at=datetime.utcnow()
        )
        self.db.add(pending)
        await self.db.commit()
        return pending_id

    async def get_pending_profile(self, company_id: str) -> dict | None:
        """获取企业的待审核信息"""
        result = await self.db.execute(
            select(CompanyProfilePending)
            .where(
                and_(
                    CompanyProfilePending.company_id == company_id,
                    CompanyProfilePending.status == "pending"
                )
            )
        )
        pending = result.scalar_one_or_none()
        if not pending:
            return None
        return {
            "pending_id": pending.pending_id,
            "company_id": pending.company_id,
            "address": pending.address,
            "email": pending.email,
            "contact": pending.contact,
            "contact_phone": pending.contact_phone,
            "status": pending.status,
            "reject_reason": pending.reject_reason,
            "submitted_at": str(pending.submitted_at),
            "reviewed_at": str(pending.reviewed_at) if pending.reviewed_at else None
        }

    async def get_profile_with_pending(self, company_id: str) -> dict | None:
        """获取企业档案及待审核状态"""
        company = await self.get_profile(company_id)
        if not company:
            return None

        pending = await self.get_pending_profile(company_id)

        # 合并待审核信息到返回数据
        result = {
            "company_id": company.company_id,
            "account_id": company.account_id,
            "company_name": company.company_name,
            "industry": company.industry,
            "city": company.city,
            "size": company.size,
            "description": company.description,
            "verified": company.verified,
            "address": company.address,
            "email": company.email,
            "contact": company.contact,
            "contact_phone": company.contact_phone,
            "pending_update": pending
        }
        return result

    async def get_received_resumes(self, company_id: str, status: int = None, page: int = 1, page_size: int = 20) -> dict:
        """获取收到的简历列表"""
        from app.models.job import JobApplication, JobDescription
        from app.models.student import StudentProfile
        from app.models.account import Account

        conditions = [JobDescription.company_id == company_id]

        # 按岗位筛选
        query = (
            select(JobApplication, JobDescription, StudentProfile, Account)
            .join(JobDescription, JobApplication.job_id == JobDescription.job_id)
            .join(Account, JobApplication.account_id == Account.account_id)
            .outerjoin(StudentProfile, StudentProfile.account_id == Account.account_id)
            .where(*conditions)
            .order_by(JobApplication.created_at.desc())
        )

        # 按状态筛选
        if status is not None:
            query = query.where(JobApplication.status == status)

        # 查询总数
        count_query = select(func.count()).select_from(JobApplication).join(
            JobDescription, JobApplication.job_id == JobDescription.job_id
        ).where(JobDescription.company_id == company_id)
        if status is not None:
            count_query = count_query.where(JobApplication.status == status)

        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # 分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        rows = result.all()

        items = []
        for row in rows:
            app, job, student, account = row
            items.append({
                "application_id": app.application_id,
                "job_id": app.job_id,
                "job_title": job.title if job else "",
                "account_id": app.account_id,
                "student_name": account.real_name if account else "",
                "student_no": student.student_no if student else "",
                "college": student.college if student else "",
                "major": student.major if student else "",
                "degree": student.degree if student else 1,
                "graduation_year": student.graduation_year if student else None,
                "status": app.status,
                "applied_at": str(app.created_at)
            })

        return {
            "list": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    async def update_application_status(self, application_id: str, company_id: str, status: int) -> bool:
        """更新简历申请状态"""
        from app.models.job import JobApplication, JobDescription

        # 验证权限
        result = await self.db.execute(
            select(JobApplication).where(JobApplication.application_id == application_id)
        )
        application = result.scalar_one_or_none()
        if not application:
            return False

        # 验证是否属于该公司
        job_result = await self.db.execute(
            select(JobDescription).where(JobDescription.job_id == application.job_id)
        )
        job = job_result.scalar_one_or_none()
        if not job or job.company_id != company_id:
            raise PermissionError("无权操作")

        application.status = status
        await self.db.commit()
        return True
