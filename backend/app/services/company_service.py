from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.models.company import Company
from app.models.company_profile_pending import CompanyProfilePending
from app.models.job import JobDescription, JobApplication
from app.models.student import StudentProfile
import uuid
import asyncio
import logging
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

        # 获取公司名称用于索引
        company_name = ""
        try:
            company_result = await self.db.execute(
                select(Company.company_name).where(Company.company_id == company_id)
            )
            company_row = company_result.scalar_one_or_none()
            if company_row:
                company_name = company_row
        except Exception as e:
            logging.warning(f"获取公司名称失败: {e}")

        # 索引新岗位到向量库
        job_data_with_company = {**data, 'company_name': company_name}
        try:
            self._index_job_to_vector_sync(job.job_id, job_data_with_company)
            logging.info(f"岗位已索引到向量库: {job.job_id}")
        except Exception as e:
            logging.error(f"岗位索引失败: {job.job_id}, error: {e}")

        return job.job_id

    def _index_job_to_vector_sync(self, job_id: str, job_data: dict):
        """同步索引岗位到向量库"""
        import sys
        import os

        # 计算项目根目录和 RAG 目录
        current_file = os.path.abspath(__file__)
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))  # backend/
        project_root = os.path.dirname(backend_dir)  # 项目根目录 (backend的父目录)
        rag_path = os.path.join(project_root, 'RAG')
        persist_dir = os.path.join(rag_path, 'chroma_db')

        if rag_path not in sys.path:
            sys.path.insert(0, rag_path)

        from langchain_community.embeddings import DashScopeEmbeddings
        from langchain_chroma import Chroma
        from langchain_core.documents import Document

        # 直接从环境变量获取 embedding model
        settings = get_settings()
        embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-v4")
        collection_name = os.getenv("CHROMA_COLLECTION_NAME", "rag")
        dashscope_api_key = settings.DASHSCOPE_API_KEY

        # 构建索引文本
        degree_text = {1: '本科', 2: '硕士', 3: '博士', 4: '大专'}.get(job_data.get('min_degree', 1) or 1, '本科')

        # 处理 keywords：可能是列表或字符串
        keywords_raw = job_data.get('keywords')
        if isinstance(keywords_raw, list):
            keywords = ', '.join(str(k) for k in keywords_raw)
        elif isinstance(keywords_raw, str):
            keywords = keywords_raw
        else:
            keywords = ''

        text = f"""岗位: {job_data.get('title', '未知职位')}
公司: {job_data.get('company_name', '未知公司')}
城市: {job_data.get('city', '未知')} | 省份: {job_data.get('province', '未知')}
行业: {job_data.get('industry', '未知')}
薪资范围: {job_data.get('min_salary') or 0}~{job_data.get('max_salary') or 0}元/月
学历要求: {degree_text}
经验要求: {job_data.get('min_exp_years', 0)}年
技能关键词: {keywords}
职位描述: {job_data.get('description', '暂无描述')}"""

        metadata = {
            'job_id': job_id,
            'title': job_data.get('title'),
            'company_name': job_data.get('company_name'),
            'city': job_data.get('city'),
            'province': job_data.get('province'),
            'industry': job_data.get('industry'),
            'min_salary': job_data.get('min_salary') or 0,
            'max_salary': job_data.get('max_salary') or 0,
        }

        embedding = DashScopeEmbeddings(model=embedding_model, dashscope_api_key=dashscope_api_key)
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embedding,
            persist_directory=persist_dir,
        )

        doc = Document(page_content=text, metadata=metadata)
        doc_id = f"job_{job_id}"
        # Upsert: 先删后加，避免重复文档
        vector_store.delete(ids=[doc_id])
        vector_store.add_documents([doc], ids=[doc_id])
        # 显式持久化
        # Chroma auto-persists on add/delete

    def _delete_job_from_vector(self, job_id: str):
        """从向量库删除岗位"""
        import sys
        import os

        current_file = os.path.abspath(__file__)
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        project_root = os.path.dirname(backend_dir)
        rag_path = os.path.join(project_root, 'RAG')
        persist_dir = os.path.join(rag_path, 'chroma_db')

        if rag_path not in sys.path:
            sys.path.insert(0, rag_path)

        from langchain_community.embeddings import DashScopeEmbeddings
        from langchain_chroma import Chroma

        settings = get_settings()
        embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-v4")
        collection_name = os.getenv("CHROMA_COLLECTION_NAME", "rag")
        dashscope_api_key = settings.DASHSCOPE_API_KEY

        embedding = DashScopeEmbeddings(model=embedding_model, dashscope_api_key=dashscope_api_key)
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embedding,
            persist_directory=persist_dir,
        )

        doc_id = f"job_{job_id}"
        vector_store.delete(ids=[doc_id])
        # Chroma auto-persists on add/delete

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

        # 同步更新向量库
        try:
            company_name = ""
            try:
                company_result = await self.db.execute(
                    select(Company.company_name).where(Company.company_id == company_id)
                )
                company_name = company_result.scalar_one_or_none() or ""
            except Exception:
                pass
            job_data = {**data, 'company_name': company_name}
            self._index_job_to_vector_sync(job_id, job_data)
            logging.info(f"岗位已更新向量库: {job_id}")
        except Exception as e:
            logging.error(f"更新向量库失败: {job_id}, error: {e}")

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

        # 从向量库删除
        try:
            self._delete_job_from_vector(job_id)
            logging.info(f"岗位已从向量库删除: {job_id}")
        except Exception as e:
            logging.error(f"从向量库删除失败: {job_id}, error: {e}")

        return True

    async def get_profile(self, company_id: str) -> Company | None:
        """获取企业档案"""
        result = await self.db.execute(
            select(Company).where(Company.company_id == company_id)
        )
        return result.scalar_one_or_none()

    async def update_profile(self, company_id: str, data: dict) -> bool:
        """更新企业档案（直接更新，无需审核）"""
        result = await self.db.execute(
            select(Company).where(Company.company_id == company_id)
        )
        company = result.scalar_one_or_none()
        if not company:
            return False

        # 可更新的字段
        updatable_fields = ["company_name", "industry", "city", "size", "description", "address", "email", "contact", "contact_phone"]
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
        try:
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
        except Exception:
            # 表不存在时返回 None，不影响主要功能
            return None

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
            "address": getattr(company, 'address', None),
            "email": getattr(company, 'email', None),
            "contact": getattr(company, 'contact', None),
            "contact_phone": getattr(company, 'contact_phone', None),
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

    # ========== 企业数据大屏 ==========

    async def get_enterprise_databoard_data(self, year: int | None = None) -> dict:
        """企业数据大屏 - 平台级紧缺人才分析（支持年份筛选）"""
        from app.services.scarce_talent_analyzer import ScarceTalentAnalyzer
        from collections import Counter

        # 1. 企业统计（平台级）
        total_companies_result = await self.db.execute(select(func.count(Company.company_id)))
        total_companies = total_companies_result.scalar() or 0

        verified_companies_result = await self.db.execute(
            select(func.count(Company.company_id)).where(Company.verified == True)
        )
        verified_companies = verified_companies_result.scalar() or 0

        # 2. 岗位统计（平台级，在招 = status != 2）
        active_jobs_result = await self.db.execute(
            select(func.count(JobDescription.job_id)).where(JobDescription.status != 2)
        )
        active_jobs = active_jobs_result.scalar() or 0

        # 3. 紧缺人才分析（复用 analyzer）
        analyzer = ScarceTalentAnalyzer(self.db)
        scarce_summary = await analyzer.get_scarce_talent_summary()
        raw_data = await analyzer.get_raw_data()
        industry_wordcloud = await analyzer.get_industry_wordcloud()

        # 4. 各地区紧缺岗位数量（地图热力图）- 从 student_profiles 表查询，包含本硕博分层数据
        from app.models.student import StudentProfile
        conditions = []
        if year:
            conditions.append(StudentProfile.graduation_year == year)

        province_query = select(
            StudentProfile.province_origin,
            StudentProfile.degree,
            func.count(StudentProfile.profile_id).label("count"),
        ).where(and_(*conditions, StudentProfile.province_origin.isnot(None), StudentProfile.province_origin != "")).group_by(StudentProfile.province_origin, StudentProfile.degree)

        province_result = await self.db.execute(province_query)

        # Organize data by province with degree breakdown
        province_data: dict = {}
        for row in province_result.all():
            province = row.province_origin
            if province not in province_data:
                province_data[province] = {"bachelor": 0, "master": 0, "doctoral": 0}
            # degree: 1=本科, 2=硕士, 3=博士
            if row.degree == 1:
                province_data[province]["bachelor"] += row.count
            elif row.degree == 2:
                province_data[province]["master"] += row.count
            elif row.degree == 3:
                province_data[province]["doctoral"] += row.count

        # Convert to list format
        map_data = []
        for province, counts in province_data.items():
            total = counts["bachelor"] + counts["master"] + counts["doctoral"]
            map_data.append({
                "province": province,
                "bachelor": counts["bachelor"],
                "master": counts["master"],
                "doctoral": counts["doctoral"],
                "total": total,
            })

        # region_map_data for backward compatibility
        region_map_data = [{"name": d["province"], "value": d["total"]} for d in map_data]

        # 5. 紧缺行业排名（水平柱状图）- 从 student_profiles cur_industry 查询
        industry_query = select(
            StudentProfile.cur_industry,
            func.count(StudentProfile.profile_id).label("count"),
        ).where(
            StudentProfile.cur_industry.isnot(None),
            StudentProfile.cur_industry != ""
        )
        if year:
            industry_query = industry_query.where(StudentProfile.graduation_year == year)
        industry_query = industry_query.group_by(StudentProfile.cur_industry).order_by(func.count(StudentProfile.profile_id).desc())

        industry_result = await self.db.execute(industry_query)
        industry_ranking_data = [
            {"name": row.cur_industry, "value": row.count}
            for row in industry_result.all()
        ]

        # 6. 薪资分布直方图 - 从 job_descriptions 表查询岗位薪资范围
        salary_buckets = [
            (0, 5000, "5k以下"),
            (5000, 8000, "5k-8k"),
            (8000, 10000, "8k-10k"),
            (10000, 15000, "10k-15k"),
            (15000, 20000, "15k-20k"),
            (20000, 30000, "20k-30k"),
            (30000, float("inf"), "30k以上"),
        ]
        salary_counts = {label: 0 for _, _, label in salary_buckets}

        salary_result = await self.db.execute(
            select(JobDescription.min_salary, JobDescription.max_salary)
            .where(JobDescription.status != 2, JobDescription.min_salary.isnot(None))
        )
        for row in salary_result.all():
            avg_sal = ((row.min_salary or 0) + (row.max_salary or 0)) / 2
            for low, high, label in salary_buckets:
                if low <= avg_sal < high:
                    salary_counts[label] += 1
                    break

        salary_distribution = [
            {"name": label, "value": count}
            for label, count in salary_counts.items()
            if count > 0
        ]

        # 7. 新兴产业人才需求（环形图）- 从 student_profiles cur_industry 查询
        emerging_demand = [
            {"name": row.cur_industry, "value": row.count}
            for row in industry_result.all()
        ]

        # 8. 学历层次对比 - 从 student_profiles degree 和 employment_status 统计
        DEGREE_MAP = {1: "本科", 2: "硕士", 3: "博士"}
        degree_query = select(
            StudentProfile.degree,
            StudentProfile.employment_status,
            func.count(StudentProfile.profile_id).label("count"),
        ).where(StudentProfile.degree.isnot(None))
        if year:
            degree_query = degree_query.where(StudentProfile.graduation_year == year)
        degree_query = degree_query.group_by(StudentProfile.degree, StudentProfile.employment_status)

        degree_result = await self.db.execute(degree_query)

        # 学历层次对比
        degree_counts = {}
        for row in degree_result.all():
            if row.degree not in degree_counts:
                degree_counts[row.degree] = {"graduate_nums": 0, "employed_nums": 0, "further_study_nums": 0}
            degree_counts[row.degree]["graduate_nums"] += row.count
            if row.employment_status == 1:  # 已就业
                degree_counts[row.degree]["employed_nums"] += row.count
            elif row.employment_status == 2:  # 升学
                degree_counts[row.degree]["further_study_nums"] += row.count

        degree_comparison = {
            "doctoral": {
                "graduate_nums": degree_counts.get(3, {}).get("graduate_nums", 0),
                "employed_nums": degree_counts.get(3, {}).get("employed_nums", 0),
                "further_study_nums": degree_counts.get(3, {}).get("further_study_nums", 0),
            },
            "master": {
                "graduate_nums": degree_counts.get(2, {}).get("graduate_nums", 0),
                "employed_nums": degree_counts.get(2, {}).get("employed_nums", 0),
                "further_study_nums": degree_counts.get(2, {}).get("further_study_nums", 0),
            },
            "bachelor": {
                "graduate_nums": degree_counts.get(1, {}).get("graduate_nums", 0),
                "employed_nums": degree_counts.get(1, {}).get("employed_nums", 0),
                "further_study_nums": degree_counts.get(1, {}).get("further_study_nums", 0),
            },
        }

        # 9. 岗位类型分布（词云）- 按 job_title 统计
        job_title_counter: Counter = Counter()
        for item in raw_data:
            title = item.get("job_title", "")
            if title:
                job_title_counter[title] += 1
        job_type_wordcloud = [
            {"name": title, "value": count}
            for title, count in job_title_counter.most_common(50)
        ]

        # 行业词云
        industry_wordcloud_data = [
            {"name": item.get("word", ""), "value": item.get("value", 0)}
            for item in industry_wordcloud
        ]

        # 10. 各地区人才缺口排名（柱状图，与 region_map_data 相同来源）
        region_talent_gap = region_map_data.copy()

        # 11. 行业分布（雷达图）- 从 student_profiles cur_industry 归一化统计
        industry_all_query = select(StudentProfile.cur_industry).where(
            StudentProfile.cur_industry.isnot(None),
            StudentProfile.cur_industry != ""
        )
        if year:
            industry_all_query = industry_all_query.where(StudentProfile.graduation_year == year)

        industry_all_result = await self.db.execute(industry_all_query)
        from app.utils.industry_normalizer import normalize_industry
        normalized_industries = [normalize_industry(ind) for ind in industry_all_result.scalars().all()]
        industry_counter = Counter(normalized_industries)
        industry_radar = [
            {"industry": name, "count": count}
            for name, count in industry_counter.most_common(15)
        ]

        # 12. 毕业生总数
        total_graduates_query = select(func.count(StudentProfile.profile_id))
        if year:
            total_graduates_query = total_graduates_query.where(StudentProfile.graduation_year == year)
        total_graduates_result = await self.db.execute(total_graduates_query)
        total_graduates = total_graduates_result.scalar() or 0

        # 13. 区域流向分布
        regional_flow = {"distribution": region_map_data.copy()}

        # 14. 专业分布TOP20 - 从 student_profiles major 统计
        major_query = select(
            StudentProfile.major,
            func.count(StudentProfile.profile_id).label("count"),
        ).where(
            StudentProfile.major.isnot(None),
            StudentProfile.major != ""
        )
        if year:
            major_query = major_query.where(StudentProfile.graduation_year == year)
        major_query = major_query.group_by(StudentProfile.major).order_by(func.count(StudentProfile.profile_id).desc()).limit(20)

        major_result = await self.db.execute(major_query)
        major_distribution = [
            {"major": row.major, "count": row.count}
            for row in major_result.all()
        ]

        # 15. 城市偏好分布 - 从 student_profiles cur_city 统计
        city_query = select(
            StudentProfile.cur_city,
            func.count(StudentProfile.profile_id).label("count"),
        ).where(
            StudentProfile.cur_city.isnot(None),
            StudentProfile.cur_city != ""
        )
        if year:
            city_query = city_query.where(StudentProfile.graduation_year == year)
        city_query = city_query.group_by(StudentProfile.cur_city).order_by(func.count(StudentProfile.profile_id).desc())

        city_result = await self.db.execute(city_query)
        city_preference = [
            {"city": row.cur_city, "count": row.count}
            for row in city_result.all()
        ]

        # 16. 紧缺人才分析
        scarce_talent = {
            "summary": scarce_summary if scarce_summary else {}
        }

        return {
            # 数字卡片
            "summary": {
                "total_companies": total_companies,
                "verified_companies": verified_companies,
                "active_jobs": active_jobs,
                "total_graduates": total_graduates,
            },
            # 地图数据
            "map_data": map_data,
            # 各地区紧缺岗位数量
            "region_map_data": region_map_data,
            # 紧缺行业排名
            "industry_ranking": industry_ranking_data,
            # 薪资分布直方图
            "salary_distribution": salary_distribution,
            # 行业分布（雷达图）
            "industry_radar": industry_radar,
            # 岗位类型分布（词云）
            "job_type_wordcloud": job_type_wordcloud,
            # 行业词云
            "industry_wordcloud": industry_wordcloud_data,
            # 各地区人才缺口排名
            "region_talent_gap": region_talent_gap,
            # 学历层次对比
            "degree_comparison": degree_comparison,
            # 区域流向分布
            "regional_flow": regional_flow,
            # 专业分布TOP20
            "major_distribution": major_distribution,
            # 城市偏好分布
            "city_preference": city_preference,
            # 紧缺人才分析
            "scarce_talent": scarce_talent,
        }
