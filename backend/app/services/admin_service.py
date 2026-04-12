from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, List
from app.models.account import Account, AccountStatus, RoleType
from app.models.student import StudentProfile
from app.models.company import Company
from app.models.company_profile_pending import CompanyProfilePending
from app.models.job import JobDescription, JobApplication
from app.models.university import University
from app.models.college_employment import CollegeEmployment
from app.models.scarce_talent import get_scarce_talent_data
from app.core.redis_client import get_redis
import json
import uuid
from datetime import datetime


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
        """学院就业率分页
        - year为空时：按学院汇总所有年份数据
        - year有值时：按学院+年份分组
        """
        conditions = [CollegeEmployment.university_id == university_id]
        if year:
            conditions.append(CollegeEmployment.graduation_year == year)
            # 按 college_name + graduation_year 分组
            query = (
                select(
                    CollegeEmployment.college_name,
                    CollegeEmployment.graduation_year,
                    func.sum(CollegeEmployment.graduate_nums).label('total_graduate_nums'),
                    func.sum(CollegeEmployment.employed_nums).label('total_employed_nums'),
                    func.sum(CollegeEmployment.further_study_nums).label('total_further_study_nums'),
                    func.sum(CollegeEmployment.overseas_nums).label('total_overseas_nums'),
                    func.round(func.avg(CollegeEmployment.employment_rate), 2).label('avg_employment_rate'),
                    func.round(func.avg(CollegeEmployment.avg_salary), 2).label('avg_salary')
                )
                .where(and_(*conditions))
                .group_by(CollegeEmployment.college_name, CollegeEmployment.graduation_year)
                .order_by(CollegeEmployment.college_name, CollegeEmployment.graduation_year.desc())
            )
        else:
            # 不选年份时：只按 college_name 分组，汇总所有年份
            query = (
                select(
                    CollegeEmployment.college_name,
                    func.sum(CollegeEmployment.graduate_nums).label('total_graduate_nums'),
                    func.sum(CollegeEmployment.employed_nums).label('total_employed_nums'),
                    func.sum(CollegeEmployment.further_study_nums).label('total_further_study_nums'),
                    func.sum(CollegeEmployment.overseas_nums).label('total_overseas_nums'),
                    func.round(func.avg(CollegeEmployment.employment_rate), 2).label('avg_employment_rate'),
                    func.round(func.avg(CollegeEmployment.avg_salary), 2).label('avg_salary')
                )
                .where(and_(*conditions))
                .group_by(CollegeEmployment.college_name)
                .order_by(CollegeEmployment.college_name)
            )

        # 查询总数
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # 分页查询
        offset = (page - 1) * page_size
        result = await self.db.execute(query.offset(offset).limit(page_size))
        rows = result.all()

        if year:
            # 按年份查看：每行包含年份
            return {
                "list": [{
                    "college_name": row.college_name,
                    "graduation_year": row.graduation_year,
                    "graduate_nums": row.total_graduate_nums or 0,
                    "employed_nums": row.total_employed_nums or 0,
                    "employment_rate": float(row.avg_employment_rate) if row.avg_employment_rate else 0,
                    "further_study_nums": row.total_further_study_nums or 0,
                    "overseas_nums": row.total_overseas_nums or 0,
                    "avg_salary": float(row.avg_salary) if row.avg_salary else 0
                } for row in rows],
                "total": total,
                "page": page,
                "page_size": page_size
            }
        else:
            # 汇总查看：不显示年份
            return {
                "list": [{
                    "college_name": row.college_name,
                    "graduate_nums": row.total_graduate_nums or 0,
                    "employed_nums": row.total_employed_nums or 0,
                    "employment_rate": float(row.avg_employment_rate) if row.avg_employment_rate else 0,
                    "further_study_nums": row.total_further_study_nums or 0,
                    "overseas_nums": row.total_overseas_nums or 0,
                    "avg_salary": float(row.avg_salary) if row.avg_salary else 0
                } for row in rows],
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
        talents = await get_scarce_talent_data(
            self.db,
            province=province if province else None,
            shortage_level=shortage_level if shortage_level else None,
            year=year if year else None,
        )

        return {
            "list": [{
                "talent_id": idx,
                "province": t.get("region_scarce") or t.get("province_city"),
                "job_type": t.get("job_title"),
                "shortage_level": t.get("level"),
                "industry": t.get("industry"),
                "data_year": t.get("year"),
                "source": t.get("shortage_type")
            } for idx, t in enumerate(talents)],
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

    async def get_pending_school_admins(self, status: int = AccountStatus.pending.value, current: int = 1, size: int = 20) -> tuple:
        """根据账号状态获取学校管理员列表（支持分页）"""
        from app.models.account import RoleType
        offset = (current - 1) * size

        # 待审核的学校管理员
        count_result = await self.db.execute(
            select(func.count()).select_from(Account)
            .where(Account.role == RoleType.school_admin, Account.status == status)
        )
        result = await self.db.execute(
            select(Account)
            .where(Account.role == RoleType.school_admin, Account.status == status)
            .offset(offset).limit(size)
        )

        total = count_result.scalar() or 0
        accounts = result.scalars().all()

        return [{
            "account_id": a.account_id,
            "username": a.username,
            "real_name": a.real_name,
            "email": a.email,
            "status": a.status,
            "created_at": str(a.created_at)
        } for a in accounts], total

    async def verify_school_admin(self, account_id: str, action: str) -> bool:
        """审核学校管理员"""
        result = await self.db.execute(
            select(Account).where(Account.account_id == account_id)
        )
        account = result.scalar_one_or_none()
        if not account:
            return False

        if account.role != RoleType.school_admin:
            return False

        if action == "approve":
            account.status = AccountStatus.enabled.value
            await self.db.commit()
            return True
        elif action == "reject":
            account.status = AccountStatus.disabled.value
            await self.db.commit()
            return True

        return False

    async def get_pending_company_admins(self, status: int = AccountStatus.pending.value, current: int = 1, size: int = 20) -> tuple:
        """根据账号状态获取企业管理员列表（支持分页）"""
        offset = (current - 1) * size

        # 待审核/已审核/已禁用的企业管理员
        count_result = await self.db.execute(
            select(func.count()).select_from(Account)
            .where(Account.role == RoleType.company_admin, Account.status == status)
        )
        result = await self.db.execute(
            select(Account)
            .where(Account.role == RoleType.company_admin, Account.status == status)
            .offset(offset).limit(size)
        )

        total = count_result.scalar() or 0
        accounts = result.scalars().all()

        return [{
            "account_id": a.account_id,
            "username": a.username,
            "real_name": a.real_name,
            "email": a.email,
            "status": a.status,
            "created_at": str(a.created_at)
        } for a in accounts], total

    async def verify_company_admin(self, account_id: str, action: str) -> bool:
        """审核企业管理员"""
        result = await self.db.execute(
            select(Account).where(Account.account_id == account_id)
        )
        account = result.scalar_one_or_none()
        if not account:
            return False

        if account.role != RoleType.company_admin:
            return False

        if action == "approve":
            account.status = AccountStatus.enabled.value
            await self.db.commit()
            return True
        elif action == "reject":
            account.status = AccountStatus.disabled.value
            await self.db.commit()
            return True

        return False

    async def get_system_configs(self) -> list:
        """获取所有系统配置"""
        from app.models.system_config import SystemConfig
        result = await self.db.execute(select(SystemConfig))
        configs = result.scalars().all()
        return [
            {
                "config_key": c.config_key,
                "config_value": c.config_value,
                "description": c.description,
                "updated_at": str(c.updated_at) if c.updated_at else None
            }
            for c in configs
        ]

    async def get_system_config(self, config_key: str) -> Optional[Dict]:
        """获取单个系统配置"""
        from app.models.system_config import SystemConfig
        result = await self.db.execute(
            select(SystemConfig).where(SystemConfig.config_key == config_key)
        )
        config = result.scalar_one_or_none()
        if not config:
            return None
        return {
            "config_key": config.config_key,
            "config_value": config.config_value,
            "description": config.description,
            "updated_at": str(config.updated_at) if config.updated_at else None
        }

    async def set_system_config(self, config_key: str, config_value: str, description: str = None) -> bool:
        """创建或更新系统配置"""
        from app.models.system_config import SystemConfig
        from datetime import datetime
        result = await self.db.execute(
            select(SystemConfig).where(SystemConfig.config_key == config_key)
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.config_value = config_value
            if description is not None:
                existing.description = description
            existing.updated_at = datetime.utcnow()
        else:
            new_config = SystemConfig(
                config_key=config_key,
                config_value=config_value,
                description=description or "",
            )
            self.db.add(new_config)
        await self.db.commit()
        return True

    async def get_pending_profile_updates(self, status: str = "pending", current: int = 1, size: int = 20) -> tuple:
        """获取待审核的企业信息更新列表"""
        try:
            offset = (current - 1) * size

            # 查询总数
            count_result = await self.db.execute(
                select(func.count()).select_from(CompanyProfilePending)
                .where(CompanyProfilePending.status == status)
            )
            total = count_result.scalar() or 0

            # 分页查询
            result = await self.db.execute(
                select(CompanyProfilePending)
                .where(CompanyProfilePending.status == status)
                .order_by(CompanyProfilePending.submitted_at.desc())
                .offset(offset)
                .limit(size)
            )
            pending_list = result.scalars().all()

            # 获取企业信息
            items = []
            for p in pending_list:
                company_result = await self.db.execute(
                    select(Company).where(Company.company_id == p.company_id)
                )
                company = company_result.scalar_one_or_none()

                items.append({
                    "pending_id": p.pending_id,
                    "company_id": p.company_id,
                    "company_name": company.company_name if company else "",
                    "industry": company.industry if company else "",
                    "city": company.city if company else "",
                    "size": company.size if company else "",
                    "description": company.description if company else "",
                    "current_address": company.address if company else "",
                    "current_email": company.email if company else "",
                    "current_contact": company.contact if company else "",
                    "current_contact_phone": company.contact_phone if company else "",
                    "address": p.address,
                    "email": p.email,
                    "contact": p.contact,
                    "contact_phone": p.contact_phone,
                    "status": p.status,
                    "reject_reason": p.reject_reason,
                    "submitted_at": str(p.submitted_at),
                    "reviewed_at": str(p.reviewed_at) if p.reviewed_at else None
                })

            return items, total
        except Exception:
            # 表不存在时返回空列表
            return [], 0

    async def review_profile_update(self, pending_id: str, action: str, reject_reason: str = None, reviewer_id: str = None) -> bool:
        """审核企业信息更新"""
        try:
            result = await self.db.execute(
                select(CompanyProfilePending).where(CompanyProfilePending.pending_id == pending_id)
            )
            pending = result.scalar_one_or_none()
            if not pending:
                return False

            if action == "approve":
                # 审核通过，更新企业信息
                company_result = await self.db.execute(
                    select(Company).where(Company.company_id == pending.company_id)
                )
                company = company_result.scalar_one_or_none()
                if company:
                    if pending.address is not None:
                        company.address = pending.address
                    if pending.email is not None:
                        company.email = pending.email
                    if pending.contact is not None:
                        company.contact = pending.contact
                    if pending.contact_phone is not None:
                        company.contact_phone = pending.contact_phone

                pending.status = "approved"
                pending.reviewed_at = datetime.utcnow()
                pending.reviewed_by = reviewer_id
                await self.db.commit()
                return True

            elif action == "reject":
                pending.status = "rejected"
                pending.reject_reason = reject_reason
                pending.reviewed_at = datetime.utcnow()
                pending.reviewed_by = reviewer_id
                await self.db.commit()
                return True

            return False
        except Exception:
            # 表不存在时返回 False
            return False
