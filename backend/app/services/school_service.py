from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.student import StudentProfile
from app.models.university import University
from app.models.employment_warning import EmploymentWarning
from app.models.college_employment import CollegeEmployment
from app.models.job import JobDescription, JobApplication
from app.core.redis_client import get_redis
import json
import uuid


class SchoolService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_data(self, university_id: str) -> dict:
        """返回学校首页统计数据"""
        # 一次查询获取所有状态的学生数量
        result = await self.db.execute(
            select(
                StudentProfile.employment_status,
                func.count(StudentProfile.profile_id)
            )
            .where(StudentProfile.university_id == university_id)
            .group_by(StudentProfile.employment_status)
        )
        status_counts = {row.employment_status: row.count for row in result.all()}

        total_students = sum(status_counts.values())
        employed_nums = status_counts.get(1, 0)
        further_study_nums = status_counts.get(2, 0)
        abroad_nums = status_counts.get(3, 0)
        unemployed_nums = status_counts.get(0, 0)
        employment_rate = (employed_nums / total_students * 100) if total_students > 0 else 0.0

        # 获取预警列表
        warnings_result = await self.db.execute(
            select(EmploymentWarning)
            .where(EmploymentWarning.university_id == university_id)
            .order_by(EmploymentWarning.created_at.desc())
            .limit(5)
        )
        warnings = []
        for w in warnings_result.scalars().all():
            warnings.append({
                "warning_id": w.warning_id,
                "account_id": w.account_id,
                "warning_type": w.warning_type,
                "level": w.level,
                "handled": w.handled
            })

        # 获取学院排名
        rankings_result = await self.db.execute(
            select(CollegeEmployment)
            .where(CollegeEmployment.university_id == university_id)
            .order_by(CollegeEmployment.employment_rate.desc())
            .limit(10)
        )
        college_rankings = []
        for r in rankings_result.scalars().all():
            college_rankings.append({
                "college_name": r.college_name,
                "employment_rate": float(r.employment_rate) if r.employment_rate else 0,
                "employed_nums": r.employed_nums,
                "graduate_nums": r.graduate_nums
            })

        return {
            "total_students": total_students,
            "employed_nums": employed_nums,
            "unemployed_nums": unemployed_nums,
            "further_study_nums": further_study_nums,
            "abroad_nums": abroad_nums,
            "employment_rate": round(employment_rate, 2),
            "college_rankings": college_rankings,
            "warnings": warnings,
            "new_jobs_this_month": 0
        }

    async def get_students(self, university_id: str, filters: dict) -> dict:
        """分页查询学生列表"""
        page = filters.get("page", 1)
        page_size = filters.get("page_size", 10)
        employment_status = filters.get("employment_status")
        major = filters.get("major")
        graduation_year = filters.get("graduation_year")

        # 构建查询条件
        conditions = [StudentProfile.university_id == university_id]
        if employment_status is not None:
            conditions.append(StudentProfile.employment_status == employment_status)
        if major:
            conditions.append(StudentProfile.major.like(f"%{major}%"))
        if graduation_year:
            conditions.append(StudentProfile.graduation_year == graduation_year)

        # 查询总数
        count_result = await self.db.execute(
            select(func.count(StudentProfile.profile_id)).where(and_(*conditions))
        )
        total = count_result.scalar() or 0

        # 分页查询
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(StudentProfile)
            .where(and_(*conditions))
            .offset(offset)
            .limit(page_size)
        )
        students = result.scalars().all()

        return {
            "list": [{
                "profile_id": s.profile_id,
                "account_id": s.account_id,
                "student_no": s.student_no,
                "college": s.college,
                "major": s.major,
                "degree": s.degree,
                "graduation_year": s.graduation_year,
                "employment_status": s.employment_status,
                "cur_company": s.cur_company,
                "cur_city": s.cur_city
            } for s in students],
            "total": total,
            "page": page,
            "page_size": page_size
        }

    async def import_students_from_excel(self, file_content: bytes) -> dict:
        """Excel批量导入学生"""
        # TODO: 实现 Excel 解析和批量导入
        # 这里返回 stub 数据
        return {"success": 0, "failed": 0, "errors": ["功能开发中"]}

    async def get_warnings(self, university_id: str, filters: dict) -> dict:
        """获取预警列表"""
        page = filters.get("page", 1)
        page_size = filters.get("page_size", 10)
        handled = filters.get("handled")
        level = filters.get("level")

        conditions = [EmploymentWarning.university_id == university_id]
        if handled is not None:
            conditions.append(EmploymentWarning.handled == handled)
        if level:
            conditions.append(EmploymentWarning.level == level)

        # 查询总数
        count_result = await self.db.execute(
            select(func.count(EmploymentWarning.warning_id)).where(and_(*conditions))
        )
        total = count_result.scalar() or 0

        # 分页查询
        offset = (page - 1) * page_size
        result = await self.db.execute(
            select(EmploymentWarning)
            .where(and_(*conditions))
            .order_by(EmploymentWarning.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        warnings = result.scalars().all()

        return {
            "list": [{
                "warning_id": w.warning_id,
                "account_id": w.account_id,
                "warning_type": w.warning_type,
                "level": w.level,
                "ai_suggestion": w.ai_suggestion,
                "handled": w.handled,
                "created_at": str(w.created_at)
            } for w in warnings],
            "total": total,
            "page": page,
            "page_size": page_size
        }

    async def handle_warning(self, warning_id: str, handled: bool) -> bool:
        """处理预警"""
        from datetime import datetime

        result = await self.db.execute(
            select(EmploymentWarning).where(EmploymentWarning.warning_id == warning_id)
        )
        warning = result.scalar_one_or_none()
        if not warning:
            return False

        warning.handled = handled
        warning.handled_at = datetime.utcnow()
        await self.db.commit()
        return True

    async def get_databoard_data(self, university_id: str) -> dict:
        """数据大屏数据（带Redis缓存30分钟）"""
        redis = get_redis()
        cache_key = f"school_databoard:{university_id}"

        # 尝试从缓存获取
        if redis:
            try:
                cached = redis.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception:
                pass

        # 计算数据
        # 就业率趋势
        trends_result = await self.db.execute(
            select(CollegeEmployment)
            .where(CollegeEmployment.university_id == university_id)
            .order_by(CollegeEmployment.graduation_year)
        )
        trends = []
        for t in trends_result.scalars().all():
            trends.append({
                "year": t.graduation_year,
                "employment_rate": float(t.employment_rate) if t.employment_rate else 0,
                "graduate_nums": t.graduate_nums,
                "employed_nums": t.employed_nums
            })

        # 专业分布
        major_result = await self.db.execute(
            select(StudentProfile.major, func.count(StudentProfile.profile_id))
            .where(StudentProfile.university_id == university_id)
            .group_by(StudentProfile.major)
        )
        major_distribution = [{"major": m, "count": c} for m, c in major_result.all()]

        # 薪资分布
        salary_result = await self.db.execute(
            select(StudentProfile.cur_salary, func.count(StudentProfile.profile_id))
            .where(
                StudentProfile.university_id == university_id,
                StudentProfile.cur_salary.isnot(None)
            )
            .group_by(StudentProfile.cur_salary)
        )
        salary_distribution = [{"salary": s, "count": c} for s, c in salary_result.all()]

        data = {
            "trends": trends,
            "major_distribution": major_distribution,
            "salary_distribution": salary_distribution,
            "employment_rate": 0.0,
            "total_students": 0
        }

        # 缓存30分钟
        if redis:
            try:
                redis.setex(cache_key, 1800, json.dumps(data))
            except Exception:
                pass
        return data

    async def get_profile(self, university_id: str) -> University | None:
        """获取学校档案"""
        from app.models.university import University
        result = await self.db.execute(
            select(University).where(University.university_id == university_id)
        )
        return result.scalar_one_or_none()

    async def update_profile(self, university_id: str, data: dict) -> bool:
        """更新学校档案"""
        from app.models.university import University
        result = await self.db.execute(
            select(University).where(University.university_id == university_id)
        )
        university = result.scalar_one_or_none()
        if not university:
            return False

        # 可更新的字段
        updatable_fields = ["name", "province", "city", "type"]
        for key, value in data.items():
            if key in updatable_fields and hasattr(university, key):
                setattr(university, key, value)

        await self.db.commit()
        return True
