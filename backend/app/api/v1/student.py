import os
import uuid
import logging
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.config import get_settings
from app.services.student_service import StudentService
from app.services.rag.rag_service import get_rag_service

logger = logging.getLogger(__name__)
router = APIRouter()


def get_student_service(db: AsyncSession = Depends(get_db)) -> StudentService:
    return StudentService(db)


def get_rag_svc():
    return get_rag_service()


@router.get("/dashboard")
async def dashboard(
    payload: dict = Depends(get_current_user),
    service: StudentService = Depends(get_student_service)
):
    account_id = payload.get("sub")
    profile = await service.get_profile(account_id)

    # 动态计算档案完整度
    def calculate_profile_complete(profile) -> int:
        if not profile:
            return 0
        filled = 0
        total = 10
        if profile.college:
            filled += 1
        if profile.major:
            filled += 1
        if profile.degree is not None:
            filled += 1
        if profile.province_origin:
            filled += 1
        if profile.gpa:
            filled += 1
        if profile.desire_city:
            filled += 1
        if profile.desire_industry:
            filled += 1
        if profile.desire_salary_min and profile.desire_salary_max:
            filled += 1
        if profile.skills and len(profile.skills) > 0:
            filled += 1
        if profile.resume_url:
            filled += 1
        return round((filled / total) * 100)

    profile_complete = calculate_profile_complete(profile)

    return {
        "code": 200,
        "message": "success",
        "data": {
            "welcome": "欢迎来到学生中心",
            "profile_complete": profile_complete,
            "employment_status": profile.employment_status if profile else 0,
            "recommended_jobs": [],
            "warnings": []
        }
    }


@router.get("/job-statistics")
async def get_job_statistics(
    payload: dict = Depends(get_current_user),
    service: StudentService = Depends(get_student_service)
):
    """获取岗位相关统计数据"""
    account_id = payload.get("sub")
    stats = await service.get_job_statistics(account_id)
    return {
        "code": 200,
        "message": "success",
        "data": stats
    }


@router.get("/databoard")
async def get_databoard(
    payload: dict = Depends(get_current_user),
    service: StudentService = Depends(get_student_service)
):
    """学生就业数据大屏 - 获取全局聚合统计数据"""
    data = await service.get_databoard_data()
    return {
        "code": 200,
        "message": "success",
        "data": data
    }


@router.get("/profile")
async def get_profile(
    payload: dict = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
    db: AsyncSession = Depends(get_db)
):
    from app.models.account import Account
    from sqlalchemy import select

    account_id = payload.get("sub")

    # 获取学生档案
    profile = await service.get_profile(account_id)

    if not profile:
        raise HTTPException(status_code=404, detail="档案不存在")

    # 获取账号信息（包含 real_name）
    result = await db.execute(
        select(Account).where(Account.account_id == account_id)
    )
    account = result.scalar_one_or_none()

    # 动态计算档案完整度
    def calc_complete(p) -> int:
        filled = 0
        total = 10
        if p.college: filled += 1
        if p.major: filled += 1
        if p.degree is not None: filled += 1
        if p.province_origin: filled += 1
        if p.gpa: filled += 1
        if p.desire_city: filled += 1
        if p.desire_industry: filled += 1
        if p.desire_salary_min and p.desire_salary_max: filled += 1
        if p.skills and len(p.skills) > 0: filled += 1
        if p.resume_url: filled += 1
        return round((filled / total) * 100)

    return {
        "code": 200,
        "message": "success",
        "data": {
            "profile_id": profile.profile_id,
            "account_id": profile.account_id,
            "university_id": profile.university_id,
            "real_name": account.real_name if account else None,
            "student_no": profile.student_no,
            "college": profile.college,
            "major": profile.major,
            "degree": profile.degree,
            "graduation_year": profile.graduation_year,
            "province_origin": profile.province_origin,
            "gpa": float(profile.gpa) if profile.gpa is not None and str(profile.gpa).replace('.', '').isdigit() else None,
            "skills": profile.skills,
            "internship": profile.internship,
            "employment_status": profile.employment_status,
            "desire_city": profile.desire_city,
            "desire_industry": profile.desire_industry,
            "desire_salary_min": profile.desire_salary_min,
            "desire_salary_max": profile.desire_salary_max,
            "cur_company": profile.cur_company,
            "cur_city": profile.cur_city,
            "cur_industry": profile.cur_industry,
            "cur_salary": profile.cur_salary,
            "resume_url": profile.resume_url,
            "profile_complete": calc_complete(profile),
        }
    }


@router.put("/profile")
async def update_profile(
    data: dict,
    payload: dict = Depends(get_current_user),
    service: StudentService = Depends(get_student_service)
):
    account_id = payload.get("sub")
    success = await service.update_profile(account_id, data)

    if not success:
        raise HTTPException(status_code=404, detail="档案不存在")

    return {"code": 200, "message": "更新成功"}


@router.get("/jobs")
async def get_jobs(
    keyword: str = "",
    city: str = "",
    industry: str = "",
    min_salary: int | None = None,
    max_salary: int | None = None,
    page: int = 1,
    page_size: int = 50,
    payload: dict = Depends(get_current_user),
    service: StudentService = Depends(get_student_service)
):
    jobs, total = await service.get_jobs_with_filters(
        keyword=keyword,
        city=city,
        industry=industry,
        min_salary=min_salary,
        max_salary=max_salary,
        page=page,
        page_size=page_size
    )

    return {
        "code": 200,
        "message": "success",
        "data": {
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
                "expired_at": str(j.expired_at) if j.expired_at else None,
                "company_name": getattr(j, 'company_name', None)
            } for j in jobs],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }


@router.post("/jobs/{job_id}/apply")
async def apply_job(
    job_id: str,
    payload: dict = Depends(get_current_user),
    service: StudentService = Depends(get_student_service)
):
    account_id = payload.get("sub")
    success = await service.apply_job(account_id, job_id)

    if not success:
        raise HTTPException(status_code=400, detail="已投递过该岗位")

    return {"code": 200, "message": "投递成功"}


@router.get("/job/recommend")
async def recommend_jobs(
    top_k: int = 6,
    payload: dict = Depends(get_current_user),
    rag_svc=Depends(get_rag_svc),
):
    """
    获取 AI 智能推荐的岗位

    - **top_k**: 推荐数量，默认6条
    """
    account_id = payload.get("sub")

    try:
        result = await rag_svc.recommend_jobs(account_id, top_k)
        return {
            "code": 200,
            "message": "success",
            "data": result,
        }
    except Exception as e:
        return {
            "code": 500,
            "message": f"推荐服务异常: {str(e)}",
            "data": {"recommendations": []},
        }


@router.post("/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    payload: dict = Depends(get_current_user),
):
    """
    上传并解析简历

    支持 PDF、Word (.docx, .doc)、纯文本格式
    返回文件存储路径和解析后的文本内容
    """
    account_id = payload.get("sub")
    settings = get_settings()

    # 验证文件类型
    ext = os.path.splitext(file.filename or "")[1].lower()
    allowed_exts = {".pdf", ".docx", ".doc", ".txt"}
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的格式: {ext}。支持的格式: {', '.join(allowed_exts)}"
        )

    # 读取文件内容
    content = await file.read()

    # 检查文件大小 (10MB)
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件超过 10MB 限制")

    # 确保上传目录存在
    upload_dir = Path(settings.UPLOAD_DIR or "./uploads/resumes")
    upload_dir.mkdir(parents=True, exist_ok=True)

    # 生成唯一文件名
    file_id = uuid.uuid4().hex
    safe_filename = f"resume_{account_id[:8]}_{file_id}{ext}"
    file_path = upload_dir / safe_filename

    try:
        # 保存文件
        with open(file_path, "wb") as f:
            f.write(content)
        logger.info(f"简历保存成功: {file_path}")

        # 解析文本
        from app.services.document.resume_parser import resume_parser
        try:
            text = resume_parser.parse(str(file_path))
            logger.info(f"简历解析成功: {file_path}, {len(text)} 字符")
        except Exception as e:
            logger.warning(f"简历解析失败: {e}")
            text = ""

        # 返回相对路径（可供后续访问）
        relative_path = f"/uploads/resumes/{safe_filename}"

        return {
            "code": 200,
            "message": "上传成功",
            "data": {
                "file_path": relative_path,
                "file_name": file.filename,
                "text": text,
                "char_count": len(text)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"简历上传失败: {e}", exc_info=True)
        # 清理已创建的文件
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/resume/text")
async def get_resume_text(
    file_path: str,
    payload: dict = Depends(get_current_user),
):
    """
    获取指定简历文件的解析文本

    用于页面加载时恢复已保存的简历内容
    """
    import urllib.parse

    settings = get_settings()
    # file_path 是相对路径如 "/uploads/resumes/xxx.pdf"
    # 转换为实际文件路径
    relative_path = file_path.lstrip("/")
    full_path = Path(relative_path)

    if not full_path.exists():
        # 尝试相对于 uploads 目录
        upload_dir = Path(settings.UPLOAD_DIR or "./uploads/resumes")
        full_path = upload_dir / Path(relative_path).name

    if not full_path.exists():
        raise HTTPException(status_code=404, detail="简历文件不存在")

    try:
        from app.services.document.resume_parser import resume_parser
        text = resume_parser.parse(str(full_path))
        return {
            "code": 200,
            "message": "success",
            "data": {
                "file_path": file_path,
                "text": text,
                "char_count": len(text)
            }
        }
    except Exception as e:
        logger.warning(f"简历解析失败: {e}")
        return {
            "code": 200,
            "message": "success",
            "data": {
                "file_path": file_path,
                "text": "",
                "char_count": 0
            }
        }


@router.get("/resume/download")
async def download_resume(
    file_path: str,
    payload: dict = Depends(get_current_user),
):
    """
    下载简历文件

    返回文件流，浏览器触发下载而非直接打开
    """
    settings = get_settings()

    try:
        # file_path 可能是 "/uploads/resumes/xxx.pdf"
        relative_path = file_path.lstrip("/")
        upload_dir = Path(settings.UPLOAD_DIR or "./uploads/resumes")

        # 尝试直接路径
        full_path = Path(relative_path)
        if not full_path.exists():
            full_path = upload_dir / Path(relative_path).name

        if not full_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")

        from fastapi.responses import StreamingResponse

        def file_iterator():
            with open(full_path, "rb") as f:
                while chunk := f.read(8192):
                    yield chunk

        filename = full_path.name
        from starlette.formparsers import MultiPartException

        return StreamingResponse(
            file_iterator(),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename*=UTF-8\'\'{filename}',
                "Content-Length": str(full_path.stat().st_size),
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载简历失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


@router.delete("/resume")
async def delete_resume(
    file_path: str,
    payload: dict = Depends(get_current_user),
):
    """
    删除指定路径的简历文件

    用于学生删除简历时清理本地存储
    """
    settings = get_settings()

    try:
        # file_path 可能是相对路径如 "/uploads/resumes/xxx.pdf"
        relative_path = file_path.lstrip("/")
        upload_dir = Path(settings.UPLOAD_DIR or "./uploads/resumes")

        # 尝试直接路径
        full_path = Path(relative_path)
        if not full_path.exists():
            # 尝试 uploads 目录下
            full_path = upload_dir / Path(relative_path).name

        if full_path.exists():
            full_path.unlink()
            logger.info(f"简历文件已删除: {full_path}")
            return {"code": 200, "message": "删除成功"}

        raise HTTPException(status_code=404, detail="文件不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除简历失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


# ==================== AI 分析记录 ====================

@router.get("/ai-history")
async def get_ai_history(
    analysis_type: str = "employment_profile",
    page: int = 1,
    page_size: int = 10,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取学生的 AI 分析历史记录

    用于跨设备同步历史记录
    """
    from sqlalchemy import select, desc
    from app.models.ai_record import AIAnalysisRecord

    account_id = payload.get("sub")

    try:
        # 查询该用户的分析记录
        stmt = (
            select(AIAnalysisRecord)
            .where(
                AIAnalysisRecord.account_id == account_id,
                AIAnalysisRecord.analysis_type == analysis_type,
                AIAnalysisRecord.status == 1
            )
            .order_by(desc(AIAnalysisRecord.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(stmt)
        records = result.scalars().all()

        # 转换为前端需要的格式（与前端 dateStr 格式一致）
        items = []
        for r in records:
            # 使用与前端一致的时间格式: "4/9 15:49"
            if r.created_at:
                # 确保使用本地时区
                local_dt = r.created_at.replace(tzinfo=None) if r.created_at.tzinfo else r.created_at
                date_str = f"{local_dt.month}/{local_dt.day} {local_dt.hour}:{local_dt.minute:02d}"
            else:
                date_str = ""
            items.append({
                "record_id": r.record_id,
                "date": date_str,
                "score": r.output_data.get("overallScore", 0) if r.output_data else 0,
                "input_data": r.input_data,
                "result_data": r.output_data
            })

        return {"code": 200, "message": "success", "data": items}

    except Exception as e:
        logger.error(f"获取AI历史记录失败: {e}", exc_info=True)
        return {"code": 200, "message": "success", "data": []}


@router.post("/ai-history")
async def save_ai_history(
    data: dict,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    保存 AI 分析记录

    将分析结果保存到数据库，用于跨设备同步
    """
    from sqlalchemy import select, desc
    from app.models.ai_record import AIAnalysisRecord

    account_id = payload.get("sub")
    record_id = str(uuid.uuid4())
    analysis_type = data.get("analysis_type", "employment_profile")
    input_data = data.get("input_data", {})
    result_data = data.get("result_data", {})

    try:
        # 创建新记录
        record = AIAnalysisRecord(
            record_id=record_id,
            account_id=account_id,
            analysis_type=analysis_type,
            input_data=input_data,
            output_data=result_data,
            status=1
        )
        db.add(record)
        await db.commit()

        return {
            "code": 200,
            "message": "保存成功",
            "data": {"record_id": record_id}
        }

    except Exception as e:
        logger.error(f"保存AI历史记录失败: {e}", exc_info=True)
        await db.rollback()
        return {"code": 500, "message": f"保存失败: {str(e)}", "data": None}


@router.delete("/ai-history/{record_id}")
async def delete_ai_history(
    record_id: str,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除指定的 AI 分析记录
    """
    from sqlalchemy import delete
    from app.models.ai_record import AIAnalysisRecord

    account_id = payload.get("sub")

    try:
        stmt = delete(AIAnalysisRecord).where(
            AIAnalysisRecord.record_id == record_id,
            AIAnalysisRecord.account_id == account_id
        )
        result = await db.execute(stmt)
        await db.commit()

        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="记录不存在")

        return {"code": 200, "message": "删除成功"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除AI历史记录失败: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


# ==================== 学生端公告和活动 ====================

@router.get("/announcements")
async def get_student_announcements(
    keyword: str = "",
    major: str = "",
    degree: int | None = None,
    year: int | None = None,
    page: int = 1,
    page_size: int = 20,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有已发布的招聘公告（学生端）

    - **keyword**: 搜索关键词（标题）
    - **major**: 专业要求
    - **degree**: 学历要求
    - **year**: 发布年份
    - **page**: 页码
    - **page_size**: 每页数量
    """
    from sqlalchemy import select, func, and_, or_
    from app.models.company_announcement import CompanyAnnouncement
    from app.models.company import Company

    # 只查询已发布的公告 (status = 1)
    conditions = [CompanyAnnouncement.status == 1]

    if keyword:
        conditions.append(CompanyAnnouncement.title.contains(keyword))
    if major:
        conditions.append(CompanyAnnouncement.target_major.contains(major))
    if degree is not None:
        conditions.append(CompanyAnnouncement.target_degree <= degree)
    if year:
        from sqlalchemy import extract
        conditions.append(
            and_(
                CompanyAnnouncement.published_at.isnot(None),
                extract('year', CompanyAnnouncement.published_at) == year
            )
        )

    # 关联公司获取公司名称
    query = (
        select(CompanyAnnouncement, Company.company_name)
        .join(Company, CompanyAnnouncement.company_id == Company.company_id)
        .where(and_(*conditions))
        .order_by(CompanyAnnouncement.published_at.desc())
    )

    # 计算总数
    count_query = (
        select(func.count())
        .select_from(CompanyAnnouncement)
        .join(Company, CompanyAnnouncement.company_id == Company.company_id)
        .where(and_(*conditions))
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    rows = result.all()

    items = []
    for row in rows:
        announcement = row[0]
        company_name = row[1]
        items.append({
            "announcement_id": announcement.announcement_id,
            "company_id": announcement.company_id,
            "company_name": company_name,
            "title": announcement.title,
            "content": announcement.content,
            "target_major": announcement.target_major,
            "target_degree": announcement.target_degree,
            "headcount": announcement.headcount,
            "deadline": str(announcement.deadline) if announcement.deadline else None,
            "status": announcement.status,
            "published_at": str(announcement.published_at) if announcement.published_at else None,
        })

    return {
        "code": 200,
        "message": "success",
        "data": {
            "list": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }


@router.get("/announcements/{announcement_id}")
async def get_student_announcement_detail(
    announcement_id: str,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取公告详情（学生端）
    """
    from sqlalchemy import select, and_
    from app.models.company_announcement import CompanyAnnouncement
    from app.models.company import Company

    query = (
        select(CompanyAnnouncement, Company.company_name)
        .join(Company, CompanyAnnouncement.company_id == Company.company_id)
        .where(
            and_(
                CompanyAnnouncement.announcement_id == announcement_id,
                CompanyAnnouncement.status == 1
            )
        )
    )
    result = await db.execute(query)
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="公告不存在或已下架")

    announcement = row[0]
    company_name = row[1]

    return {
        "code": 200,
        "message": "success",
        "data": {
            "announcement_id": announcement.announcement_id,
            "company_id": announcement.company_id,
            "company_name": company_name,
            "title": announcement.title,
            "content": announcement.content,
            "target_major": announcement.target_major,
            "target_degree": announcement.target_degree,
            "headcount": announcement.headcount,
            "deadline": str(announcement.deadline) if announcement.deadline else None,
            "status": announcement.status,
            "published_at": str(announcement.published_at) if announcement.published_at else None,
        }
    }


@router.get("/activities")
async def get_student_activities(
    keyword: str = "",
    activity_type: str = "",
    year: int | None = None,
    page: int = 1,
    page_size: int = 20,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有已发布的宣讲会/活动（学生端）

    - **keyword**: 搜索关键词（标题）
    - **activity_type**: 活动类型 (seminar/job_fair/other)
    - **year**: 活动年份
    - **page**: 页码
    - **page_size**: 每页数量
    """
    from sqlalchemy import select, func, and_, extract
    from app.models.company_activity import CompanyActivity
    from app.models.company import Company

    # 只查询已发布的活动 (status = 1)
    conditions = [CompanyActivity.status == 1]

    if keyword:
        conditions.append(CompanyActivity.title.contains(keyword))
    if activity_type:
        conditions.append(CompanyActivity.type == activity_type)
    if year:
        conditions.append(extract('year', CompanyActivity.activity_date) == year)

    # 关联公司获取公司名称
    query = (
        select(CompanyActivity, Company.company_name)
        .join(Company, CompanyActivity.company_id == Company.company_id)
        .where(and_(*conditions))
        .order_by(CompanyActivity.activity_date.desc())
    )

    # 计算总数
    count_query = (
        select(func.count())
        .select_from(CompanyActivity)
        .join(Company, CompanyActivity.company_id == Company.company_id)
        .where(and_(*conditions))
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # 分页
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    rows = result.all()

    items = []
    for row in rows:
        activity = row[0]
        company_name = row[1]
        items.append({
            "activity_id": activity.activity_id,
            "company_id": activity.company_id,
            "company_name": company_name,
            "type": activity.type,
            "type_name": activity.type_name,
            "title": activity.title,
            "location": activity.location,
            "activity_date": str(activity.activity_date) if activity.activity_date else None,
            "start_time": str(activity.start_time) if activity.start_time else None,
            "end_time": str(activity.end_time) if activity.end_time else None,
            "description": activity.description,
            "expected_num": activity.expected_num,
            "actual_num": activity.actual_num,
            "status": activity.status,
        })

    return {
        "code": 200,
        "message": "success",
        "data": {
            "list": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    }


@router.get("/activities/{activity_id}")
async def get_student_activity_detail(
    activity_id: str,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取活动详情（学生端）
    """
    from sqlalchemy import select, and_
    from app.models.company_activity import CompanyActivity
    from app.models.company import Company

    query = (
        select(CompanyActivity, Company.company_name)
        .join(Company, CompanyActivity.company_id == Company.company_id)
        .where(
            and_(
                CompanyActivity.activity_id == activity_id,
                CompanyActivity.status == 1
            )
        )
    )
    result = await db.execute(query)
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="活动不存在或已取消")

    activity = row[0]
    company_name = row[1]

    return {
        "code": 200,
        "message": "success",
        "data": {
            "activity_id": activity.activity_id,
            "company_id": activity.company_id,
            "company_name": company_name,
            "type": activity.type,
            "type_name": activity.type_name,
            "title": activity.title,
            "location": activity.location,
            "activity_date": str(activity.activity_date) if activity.activity_date else None,
            "start_time": str(activity.start_time) if activity.start_time else None,
            "end_time": str(activity.end_time) if activity.end_time else None,
            "description": activity.description,
            "expected_num": activity.expected_num,
            "actual_num": activity.actual_num,
            "status": activity.status,
        }
    }
