from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.account import Account, AccountStatus
from app.models.student import StudentProfile
from app.models.company import Company
from app.models.job import JobDescription, JobApplication
from app.models.university import University
from app.models.college_employment import CollegeEmployment
from app.models.scarce_talent import ScarceTalent
from app.core.redis_client import get_redis
import json
import uuid


class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_data(self) -> dict:
        """全平台数据汇总"""
        # 统计学生总数
        total_students = await self.db.execute(select(func.count(Account.account_id)))
        students_count = (await self.db.execute(
            select(func.count(StudentProfile.profile_id))
        )).scalar() or 0

        # 统计企业总数
        companies_count = (await self.db.execute(
            select(func.count(Company.company_id))
        )).scalar() or 0

        # 统计岗位总数
        jobs_count = (await self.db.execute(
            select(func.count(JobDescription.job_id))
        )).scalar() or 0

        # 统计已就业学生
        employed_count = (await self.db.execute(
            select(func.count(StudentProfile.profile_id))
            .where(StudentProfile.employment_status == 1)
        )).scalar() or 0

        employment_rate = (employed_count / students_count * 100) if students_count > 0 else 0.0

        return {
            "total_students": students_count,
            "total_companies": companies_count,
            "total_jobs": jobs_count,
            "overall_employment_rate": round(employment_rate, 2),
            "recent_warnings": []
        }

    async def get_statistics(self, dimension: str, year: int) -> dict:
        """多维度统计"""
        if dimension == "province":
            # 按省份统计
            result = await self.db.execute(
                select(
                    University.province,
                    func.count(StudentProfile.profile_id),
                    func.sum(func.if_(StudentProfile.employment_status == 1, 1, 0))
                )
                .join(StudentProfile, StudentProfile.university_id == University.university_id)
                .group_by(University.province)
            )
            return {
                "dimension": "province",
                "year": year,
                "data": [{"province": p, "total": t, "employed": e} for p, t, e in result.all()]
            }

        elif dimension == "industry":
            # 按行业统计
            result = await self.db.execute(
                select(
                    StudentProfile.cur_industry,
                    func.count(StudentProfile.profile_id)
                )
                .where(StudentProfile.cur_industry.isnot(None))
                .group_by(StudentProfile.cur_industry)
            )
            return {
                "dimension": "industry",
                "year": year,
                "data": [{"industry": i, "count": c} for i, c in result.all()]
            }

        elif dimension == "degree":
            # 按学历统计
            result = await self.db.execute(
                select(
                    StudentProfile.degree,
                    func.count(StudentProfile.profile_id)
                )
                .group_by(StudentProfile.degree)
            )
            return {
                "dimension": "degree",
                "year": year,
                "data": [{"degree": d, "count": c} for d, c in result.all()]
            }

        return {"dimension": dimension, "year": year, "data": []}

    async def get_colleges(self, university_id: str, year: int, page: int, page_size: int) -> dict:
        """学院就业率分页"""
        conditions = [CollegeEmployment.university_id == university_id]
        if year:
            conditions.append(CollegeEmployment.graduation_year == year)

        # 查询总数
        count_result = await self.db.execute(
            select(func.count(CollegeEmployment.record_id)).where(and_(*conditions))
        )
        total = count_result.scalar() or 0

        # 分页查询
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(CollegeEmployment)
            .where(and_(*conditions))
            .order_by(CollegeEmployment.employment_rate.desc())
            .offset(offset)
            .limit(page_size)
        )
        colleges = result.scalars().all()

        return {
            "list": [{
                "record_id": c.record_id,
                "college_name": c.college_name,
                "graduation_year": c.graduation_year,
                "graduate_nums": c.graduate_nums,
                "employed_nums": c.employed_nums,
                "employment_rate": float(c.employment_rate) if c.employment_rate else 0,
                "further_study_nums": c.further_study_nums,
                "overseas_nums": c.overseas_nums,
                "avg_salary": c.avg_salary
            } for c in colleges],
            "total": total,
            "page": page,
            "page_size": page_size
        }

    async def update_college(self, record_id: str, data: dict) -> bool:
        """更新学院数据"""
        result = await self.db.execute(
            select(CollegeEmployment).where(CollegeEmployment.record_id == record_id)
        )
        college = result.scalar_one_or_none()
        if not college:
            return False

        for key, value in data.items():
            if hasattr(college, key):
                setattr(college, key, value)

        await self.db.commit()
        return True

    async def get_scarce_talents(self, province: str, shortage_level: int, year: int) -> dict:
        """稀缺人才数据"""
        conditions = []
        if province:
            conditions.append(ScarceTalent.province == province)
        if shortage_level:
            conditions.append(ScarceTalent.shortage_level == shortage_level)
        if year:
            conditions.append(ScarceTalent.data_year == year)

        result = await self.db.execute(
            select(ScarceTalent).where(and_(*conditions))
        )
        talents = result.scalars().all()

        return {
            "list": [{
                "talent_id": t.talent_id,
                "province": t.province,
                "job_type": t.job_type,
                "shortage_level": t.shortage_level,
                "industry": t.industry,
                "data_year": t.data_year,
                "source": t.source
            } for t in talents],
            "total": len(talents)
        }

    async def get_databoard_data(self) -> dict:
        """管理端大屏数据"""
        redis = get_redis()
        cache_key = "admin_databoard"

        # 尝试从缓存获取
        if redis:
            try:
                cached = redis.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception:
                pass

        # 统计各高校就业率 - 一次查询替代 N+1 问题
        universities_result = await self.db.execute(
            select(University)
        )
        universities = {u.university_id: u for u in universities_result.scalars().all()}

        # 批量获取所有高校的学生统计数据
        stats_result = await self.db.execute(
            select(
                StudentProfile.university_id,
                func.count(StudentProfile.profile_id).label('total'),
                func.sum(func.if_(StudentProfile.employment_status == 1, 1, 0)).label('employed')
            )
            .group_by(StudentProfile.university_id)
        )
        stats_map = {row.university_id: {'total': row.total or 0, 'employed': row.employed or 0}
                      for row in stats_result.all()}

        university_stats = []
        for uid, u in universities.items():
            stats = stats_map.get(uid, {'total': 0, 'employed': 0})
            total = stats['total']
            employed = stats['employed']
            rate = (employed / total * 100) if total > 0 else 0
            university_stats.append({
                "university_id": uid,
                "name": u.name,
                "province": u.province,
                "total_students": total,
                "employed": employed,
                "employment_rate": round(rate, 2)
            })

        # 行业分布
        industry_result = await self.db.execute(
            select(Company.industry, func.count(Company.company_id))
            .where(Company.industry.isnot(None))
            .group_by(Company.industry)
        )
        industry_distribution = [{"industry": i, "count": c} for i, c in industry_result.all()]

        data = {
            "university_stats": university_stats,
            "industry_distribution": industry_distribution,
            "total_students": sum(s["total_students"] for s in university_stats),
            "total_companies": sum(i["count"] for i in industry_distribution)
        }

        # 缓存30分钟
        if redis:
            try:
                redis.setex(cache_key, 1800, json.dumps(data))
            except Exception:
                pass
        return data

    async def get_pending_companies(self) -> list:
        """待审核企业"""
        result = await self.db.execute(
            select(Company).where(Company.verified == False)
        )
        companies = result.scalars().all()

        return [{
            "company_id": c.company_id,
            "company_name": c.company_name,
            "industry": c.industry,
            "city": c.city,
            "size": c.size,
            "description": c.description,
            "created_at": str(c.created_at)
        } for c in companies]

    async def get_companies_by_status(self, status: int, current: int = 1, size: int = 20) -> tuple:
        """根据审核状态获取企业列表（支持分页）"""
        offset = (current - 1) * size

        if status == 0:
            # 待审核
            count_result = await self.db.execute(
                select(func.count()).select_from(Company).where(Company.verified == False)
            )
            result = await self.db.execute(
                select(Company).where(Company.verified == False).offset(offset).limit(size)
            )
        else:
            # 已审核
            count_result = await self.db.execute(
                select(func.count()).select_from(Company).where(Company.verified == True)
            )
            result = await self.db.execute(
                select(Company).where(Company.verified == True).offset(offset).limit(size)
            )

        total = count_result.scalar() or 0
        companies = result.scalars().all()

        return [{
            "company_id": c.company_id,
            "company_name": c.company_name,
            "industry": c.industry,
            "city": c.city,
            "size": c.size,
            "description": c.description,
            "verified": c.verified,
            "created_at": str(c.created_at)
        } for c in companies], total

    async def verify_company(self, company_id: str, action: str) -> bool:
        """审核企业"""
        result = await self.db.execute(
            select(Company).where(Company.company_id == company_id)
        )
        company = result.scalar_one_or_none()
        if not company:
            return False

        # 获取关联的账号
        account_result = await self.db.execute(
            select(Account).where(Account.account_id == company.account_id)
        )
        account = account_result.scalar_one_or_none()

        if action == "approve":
            company.verified = True
            # 审核通过后，将账号状态设为 enabled
            if account:
                account.status = AccountStatus.enabled.value
            await self.db.commit()
            return True
        elif action == "reject":
            # 审核拒绝后，将账号状态设为 disabled，且 verified=False 移出已审核列表
            company.verified = False
            if account:
                account.status = AccountStatus.disabled.value
            await self.db.commit()
            return True

        return False
