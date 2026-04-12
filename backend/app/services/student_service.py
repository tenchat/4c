from sqlalchemy import select, func, case, and_, or_
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
        min_salary: int | None = None,
        max_salary: int | None = None,
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
        if min_salary is not None and max_salary is not None:
            if min_salary == 0 and max_salary == 0:
                # 面议：只显示 min_salary=0 且 max_salary=0 的职位
                query = query.where(JobDescription.min_salary == 0, JobDescription.max_salary == 0)
            elif min_salary == 0 and max_salary > 0:
                # 5k以下：排除面议职位
                query = query.where(
                    JobDescription.min_salary <= max_salary,
                    JobDescription.min_salary > 0
                )
            elif min_salary > 0 and max_salary > 0:
                # 指定范围：排除面议职位
                query = query.where(
                    JobDescription.max_salary >= min_salary,
                    JobDescription.min_salary <= max_salary,
                    ~((JobDescription.min_salary == 0) & (JobDescription.max_salary == 0))
                )
        elif min_salary is not None and min_salary > 0:
            # 只有 min_salary（20k以上）：薪资上限无限制
            query = query.where(
                JobDescription.max_salary >= min_salary,
                ~((JobDescription.min_salary == 0) & (JobDescription.max_salary == 0))
            )
        elif max_salary is not None and max_salary > 0:
            # 只有 max_salary（5k以下）
            query = query.where(
                JobDescription.min_salary <= max_salary,
                ~((JobDescription.min_salary == 0) & (JobDescription.max_salary == 0))
            )
        # 如果 min_salary 和 max_salary 都是 None，不筛选薪资，显示全部

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

    async def get_job_statistics(self, account_id: str) -> dict:
        """获取学生岗位相关统计"""
        from sqlalchemy import func
        from app.models.job import JobDescription
        from datetime import datetime, timedelta

        # 已投递数量
        applied_result = await self.db.execute(
            select(func.count()).select_from(JobApplication).where(
                JobApplication.account_id == account_id
            )
        )
        applied_count = applied_result.scalar() or 0

        # 在招职位总数
        total_result = await self.db.execute(
            select(func.count()).select_from(JobDescription).where(
                JobDescription.status == 1
            )
        )
        total_jobs = total_result.scalar() or 0

        # 新增职位数量（7天内）
        seven_days_ago = datetime.now() - timedelta(days=7)
        new_result = await self.db.execute(
            select(func.count()).select_from(JobDescription).where(
                JobDescription.status == 1,
                JobDescription.published_at >= seven_days_ago
            )
        )
        new_jobs = new_result.scalar() or 0

        # 最高薪资
        max_salary_result = await self.db.execute(
            select(func.max(JobDescription.max_salary)).where(
                JobDescription.status == 1,
                JobDescription.max_salary > 0
            )
        )
        max_salary = max_salary_result.scalar() or 0

        return {
            "applied_count": applied_count,
            "total_jobs": total_jobs,
            "new_jobs": new_jobs,
            "max_salary": max_salary
        }

    async def get_databoard_data(self) -> dict:
        """
        学生就业数据大屏数据（全局聚合，不限学校）

        返回13项关键指标：
        1. 毕业生流向分布 - employment_status分布
        2. 行业热门度TOP10 - cur_industry/desire_industry分布
        3. 城市就业热度TOP10 - cur_city/desire_city分布
        4. 期望薪资分布 - desire_salary分段统计
        5. 行业薪资对比 - 归一化行业平均薪资（雷达图）
        6. 紧缺岗位推荐 - scarce_talent按紧缺程度
        7. 专业就业率 - college_employment聚合
        8. 实习价值分析 - 有无实习的就业率对比
        9. 就业满意度分布 - 暂无数据
        10. 学历与就业方向 - degree + employment_status堆叠
        11. 性别与行业选择 - 暂无gender字段
        12. 紧缺岗位学历要求 - scarce_talent.education分布
        13. 城市薪资水平 - scarce_talent.region_scarce薪资
        """
        from sqlalchemy import func, case, and_, or_
        from app.models.college_employment import CollegeEmployment
        from app.services.scarce_talent_analyzer import ScarceTalentAnalyzer
        from app.utils.industry_normalizer import normalize_industry
        from collections import Counter

        # 1. 毕业生流向分布
        direction_result = await self.db.execute(
            select(
                StudentProfile.employment_status,
                func.count(StudentProfile.profile_id).label("count"),
            ).where(StudentProfile.employment_status.isnot(None))
            .group_by(StudentProfile.employment_status)
        )
        STATUS_MAP = {0: "待就业", 1: "已就业", 2: "升学", 3: "出国"}
        direction_distribution = [
            {"name": STATUS_MAP.get(row.employment_status, "未知"), "value": row.count}
            for row in direction_result.all()
        ]

        # 2. 行业热门度TOP10（结合cur_industry和desire_industry）
        industry_counter = Counter()
        for field in [StudentProfile.cur_industry, StudentProfile.desire_industry]:
            result = await self.db.execute(
                select(field).where(and_(field.isnot(None), field != ""))
            )
            for row in result.scalars().all():
                if row:
                    industry_counter[row] += 1
        industry_hot = [
            {"name": industry, "value": count}
            for industry, count in industry_counter.most_common(20)
        ]

        # 3. 城市就业热度TOP10（结合cur_city和desire_city）
        city_counter = Counter()
        for field in [StudentProfile.cur_city, StudentProfile.desire_city]:
            result = await self.db.execute(
                select(field).where(and_(field.isnot(None), field != ""))
            )
            for row in result.scalars().all():
                if row:
                    city_counter[row] += 1
        city_hot = [
            {"name": city, "value": count}
            for city, count in city_counter.most_common(10)
        ]

        # 4. 期望薪资分布
        salary_result = await self.db.execute(
            select(StudentProfile.desire_salary_min, StudentProfile.desire_salary_max)
            .where(
                StudentProfile.desire_salary_min.isnot(None),
                StudentProfile.desire_salary_max.isnot(None),
            )
        )
        BUCKETS = [
            (0, 3000, "0-3k"), (3000, 5000, "3k-5k"), (5000, 8000, "5k-8k"),
            (8000, 10000, "8k-10k"), (10000, 15000, "10k-15k"),
            (15000, 20000, "15k-20k"), (20000, 30000, "20k-30k"), (30000, float("inf"), "30k+"),
        ]
        salary_counts = {label: 0 for _, _, label in BUCKETS}
        for row in salary_result.all():
            min_sal = row.desire_salary_min or 0
            max_sal = row.desire_salary_max or 0
            if min_sal <= 0 and max_sal <= 0:
                continue
            avg_sal = (min_sal + max_sal) / 2
            for low, high, label in BUCKETS:
                if low <= avg_sal < high:
                    salary_counts[label] += 1
                    break
            else:
                if avg_sal >= 30000:
                    salary_counts["30k+"] += 1
        salary_distribution = [
            {"range": label, "count": count}
            for label, count in salary_counts.items() if count > 0
        ]

        # 5. 行业薪资对比（从scarce_talent表获取）
        scarce_data: list[dict] = []
        industry_salary_radar: list[dict] = []
        try:
            analyzer = ScarceTalentAnalyzer(self.db)
            scarce_data = await analyzer.get_raw_data()
            industry_salary: dict[str, list[int]] = {}
            for item in scarce_data:
                industry = item.get("industry", "")
                salary = item.get("salary")
                if industry and salary:
                    normalized = normalize_industry(industry)
                    if normalized not in industry_salary:
                        industry_salary[normalized] = []
                    industry_salary[normalized].append(int(salary))
            industry_salary_avg = [
                {"industry": ind, "salary": int(sum(salaries) / len(salaries))}
                for ind, salaries in industry_salary.items() if salaries
            ]
            industry_salary_avg.sort(key=lambda x: x["salary"], reverse=True)
            industry_salary_radar = industry_salary_avg[:8]
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"获取稀缺人才数据失败: {e}")
            scarce_data = []

        # 6. 紧缺岗位推荐（从scarce_talent）
        scarce_talent_list = sorted(
            scarce_data,
            key=lambda x: x.get("level") or 0,
            reverse=True
        )[:10]
        scarce_jobs = [
            {
                "job_title": item.get("job_title", ""),
                "industry": item.get("industry", ""),
                "region": item.get("region_scarce", ""),
                "level": item.get("level", 0),
                "education": item.get("education", ""),
                "salary": item.get("salary", 0),
            }
            for item in scarce_talent_list
        ]

        # 7. 专业就业率（从college_employment）
        major_result = await self.db.execute(
            select(
                CollegeEmployment.college_name,
                func.sum(CollegeEmployment.graduate_nums).label("total"),
                func.sum(CollegeEmployment.employed_nums).label("employed"),
            ).group_by(CollegeEmployment.college_name)
        )
        major_employment = []
        for row in major_result.all():
            total = row.total or 0
            employed = row.employed or 0
            rate = round(employed / total * 100, 2) if total > 0 else 0
            major_employment.append({
                "college": row.college_name,
                "total": total,
                "employed": employed,
                "rate": rate,
            })
        major_employment.sort(key=lambda x: x["rate"], reverse=True)

        # 8. 实习价值分析
        has_intern_result = await self.db.execute(
            select(
                func.count(StudentProfile.profile_id).label("total"),
                func.sum(case((StudentProfile.employment_status == 1, 1), else_=0)).label("employed"),
            ).where(
                StudentProfile.internship.isnot(None),
                StudentProfile.internship != ""
            )
        )
        no_intern_result = await self.db.execute(
            select(
                func.count(StudentProfile.profile_id).label("total"),
                func.sum(case((StudentProfile.employment_status == 1, 1), else_=0)).label("employed"),
            ).where(
                or_(StudentProfile.internship.is_(None), StudentProfile.internship == "")
            )
        )
        def calc_rate(result):
            row = result.one()
            total = row.total or 0
            employed = row.employed or 0
            rate = round(employed / total * 100, 2) if total > 0 else 0
            return {"total": total, "employed": employed, "rate": rate}
        internship_value = [
            {"name": "有实习经历", **calc_rate(has_intern_result)},
            {"name": "无实习经历", **calc_rate(no_intern_result)},
        ]

        # 9. 就业满意度分布（暂无数据）
        satisfaction_distribution = []

        # 10. 学历与就业方向
        DEGREE_MAP = {1: "本科", 2: "硕士", 3: "博士"}
        degree_dir_result = await self.db.execute(
            select(
                StudentProfile.degree,
                StudentProfile.employment_status,
                func.count(StudentProfile.profile_id).label("count"),
            ).where(StudentProfile.degree.isnot(None))
            .group_by(StudentProfile.degree, StudentProfile.employment_status)
        )
        degree_dir_data: dict[int, dict[int, int]] = {}
        for row in degree_dir_result.all():
            deg = row.degree
            status = row.employment_status
            count = row.count
            if deg not in degree_dir_data:
                degree_dir_data[deg] = {}
            degree_dir_data[deg][status] = count
        degree_direction = []
        for deg, status_map in degree_dir_data.items():
            degree_direction.append({
                "degree": DEGREE_MAP.get(deg, "未知"),
                "待就业": status_map.get(0, 0),
                "已就业": status_map.get(1, 0),
                "升学": status_map.get(2, 0),
                "出国": status_map.get(3, 0),
            })

        # 11. 性别与行业选择（暂无gender字段）
        gender_industry = []

        # 12. 紧缺岗位学历要求
        education_counter = Counter(
            item.get("education", "") for item in scarce_data if item.get("education")
        )
        education_distribution = [
            {"name": edu, "value": count}
            for edu, count in education_counter.most_common()
        ]

        # 13. 城市薪资水平
        region_salary: dict[str, list[int]] = {}
        for item in scarce_data:
            region = item.get("region_scarce", "")
            salary = item.get("salary")
            if region and salary:
                if region not in region_salary:
                    region_salary[region] = []
                region_salary[region].append(int(salary))
        region_salary_avg = [
            {"region": reg, "salary": int(sum(sals) / len(sals))}
            for reg, sals in region_salary.items() if sals
        ]
        region_salary_avg.sort(key=lambda x: x["salary"], reverse=True)
        city_salary_level = region_salary_avg[:10]

        return {
            # 1. 毕业生流向分布
            "direction_distribution": direction_distribution,
            # 2. 行业热门度TOP10
            "industry_hot": industry_hot,
            # 3. 城市就业热度TOP10
            "city_hot": city_hot,
            # 4. 期望薪资分布
            "salary_distribution": salary_distribution,
            # 5. 行业薪资对比
            "industry_salary_radar": industry_salary_radar,
            # 6. 紧缺岗位推荐
            "scarce_jobs": scarce_jobs,
            # 7. 专业就业率
            "major_employment": major_employment,
            # 8. 实习价值分析
            "internship_value": internship_value,
            # 9. 就业满意度分布
            "satisfaction_distribution": satisfaction_distribution,
            # 10. 学历与就业方向
            "degree_direction": degree_direction,
            # 11. 性别与行业选择
            "gender_industry": gender_industry,
            # 12. 紧缺岗位学历要求
            "education_distribution": education_distribution,
            # 13. 城市薪资水平
            "city_salary_level": city_salary_level,
        }
