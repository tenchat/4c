from fastapi import APIRouter, Body, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.account import Account
from app.services.school_service import SchoolService

router = APIRouter()


def get_school_service(db: AsyncSession = Depends(get_db)) -> SchoolService:
    return SchoolService(db)


async def get_university_id(db: AsyncSession, account_id: str) -> str:
    """获取当前用户关联的 university_id"""
    from app.core.config import get_settings
    settings = get_settings()
    # TODO: Account模型暂无university_id字段，暂时使用配置的默认大学ID
    # 后续应通过Account表直接关联或通过school_admin表关联
    if not settings.DEFAULT_UNIVERSITY_ID:
        raise HTTPException(status_code=403, detail="未配置学校ID")
    return settings.DEFAULT_UNIVERSITY_ID


@router.get("/dashboard")
async def dashboard(
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: SchoolService = Depends(get_school_service)
):
    from sqlalchemy import select
    university_id = await get_university_id(db, payload.get("sub"))
    data = await service.get_dashboard_data(university_id)

    return {
        "code": 200,
        "message": "success",
        "data": data
    }


@router.get("/students")
async def get_students(
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: SchoolService = Depends(get_school_service),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    employment_status: int = None,
    major: str = None,
    graduation_year: int = None
):
    from sqlalchemy import select
    university_id = await get_university_id(db, payload.get("sub"))

    filters = {
        "page": page,
        "page_size": page_size,
        "employment_status": employment_status,
        "major": major,
        "graduation_year": graduation_year
    }

    data = await service.get_students(university_id, filters)
    return {
        "code": 200,
        "message": "success",
        "data": data
    }


@router.get("/students/export")
async def export_students(
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: SchoolService = Depends(get_school_service),
    employment_status: int = None,
    major: str = None,
    graduation_year: int = None,
    profile_ids: str = None  # 逗号分隔的ID列表，用于导出选中学生
):
    """流式导出学生Excel - 分批查询避免内存溢出

    Args:
        profile_ids: 逗号分隔的学生ID列表，不传则按filters条件导出全部
    """
    import io
    from fastapi.responses import StreamingResponse
    import openpyxl

    university_id = await get_university_id(db, payload.get("sub"))

    filters = {
        "employment_status": employment_status,
        "major": major,
        "graduation_year": graduation_year
    }

    # 解析profile_ids
    parsed_profile_ids = None
    if profile_ids:
        parsed_profile_ids = [pid.strip() for pid in profile_ids.split(",") if pid.strip()]

    # 使用内存缓冲区
    output = io.BytesIO()

    # 使用 write_only 模式减少内存占用
    wb = openpyxl.Workbook(write_only=True)
    ws = wb.create_sheet("学生信息")

    # 定义表头
    headers = ["学号", "姓名", "学院", "专业", "学历", "毕业年份", "就业状态",
               "当前公司", "当前城市", "当前行业", "当前薪资", "期望城市",
               "期望行业", "期望薪资", "生源省份", "GPA", "技能特长", "实习经历", "注册状态"]

    # 写入表头
    ws.append(headers)

    # 流式分批查询并写入，每批1000条
    BATCH_SIZE = 1000
    written_count = 0

    async for batch in service.export_students_stream(university_id, filters, batch_size=BATCH_SIZE, profile_ids=parsed_profile_ids):
        for row in batch:
            ws.append(list(row.values()))
        written_count += len(batch)

    # 写入内存缓冲区
    wb.save(output)
    output.seek(0)

    # 生成文件名
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"students_export_{timestamp}.xlsx"

    # 流式发送
    async def file_iterator():
        while True:
            chunk = output.read(8192)
            if not chunk:
                break
            yield chunk

    file_size = output.getbuffer().nbytes

    return StreamingResponse(
        file_iterator(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename*=UTF-8\'\'{filename}',
            "Content-Length": str(file_size),
        },
    )


@router.get("/students/{profile_id}")
async def get_student_detail(
    profile_id: str,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: SchoolService = Depends(get_school_service)
):
    """获取学生完整档案信息"""
    detail = await service.get_student_detail(profile_id)
    if not detail:
        raise HTTPException(status_code=404, detail="学生档案不存在")
    return {"code": 200, "message": "success", "data": detail}


@router.post("/students/import/preview")
async def import_students_preview(
    file: UploadFile = File(..., description="Excel/CSV 文件"),
    payload: dict = Depends(get_current_user),
    service: SchoolService = Depends(get_school_service)
):
    """Excel/CSV 导入预览：解析文件并检测注册状态"""
    if not file:
        raise HTTPException(status_code=400, detail="未上传文件")

    filename = file.filename or "unknown.csv"
    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="文件内容为空")

    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件大小不能超过 10MB")

    result = await service.import_students_preview(content, filename)
    return {"code": 200, "message": "预览成功", "data": result}


@router.post("/students/confirm-import")
async def confirm_import_students(
    payload: dict = Depends(get_current_user),
    data: dict = Body(...),
    db: AsyncSession = Depends(get_db),
    service: SchoolService = Depends(get_school_service)
):
    """确认导入：实际写入数据库"""
    if not data or "students" not in data:
        raise HTTPException(status_code=400, detail="缺少 students 字段")
    university_id = await get_university_id(db, payload.get("sub"))
    result = await service.confirm_import_students(university_id, data["students"])
    return {"code": 200, "message": "导入完成", "data": result}


@router.delete("/students/batch")
async def batch_delete_students(
    payload: dict = Depends(get_current_user),
    data: dict = Body(...),
    service: SchoolService = Depends(get_school_service)
):
    """批量删除学生"""
    if not data or "profile_ids" not in data:
        raise HTTPException(status_code=400, detail="缺少 profile_ids 字段")
    profile_ids = data["profile_ids"]
    if not isinstance(profile_ids, list) or not profile_ids:
        raise HTTPException(status_code=400, detail="profile_ids 必须为非空数组")
    result = await service.batch_delete_students(profile_ids)
    return {"code": 200, "message": "删除成功", "data": result}


@router.put("/students/batch")
async def batch_update_students(
    payload: dict = Depends(get_current_user),
    data: dict = Body(...),
    service: SchoolService = Depends(get_school_service)
):
    """批量更新学生字段"""
    if not data or "profile_ids" not in data or "updates" not in data:
        raise HTTPException(status_code=400, detail="缺少 profile_ids 或 updates 字段")
    profile_ids = data["profile_ids"]
    updates = data["updates"]
    if not isinstance(profile_ids, list) or not profile_ids:
        raise HTTPException(status_code=400, detail="profile_ids 必须为非空数组")
    result = await service.batch_update_students(profile_ids, updates)
    return {"code": 200, "message": "更新成功", "data": result}


@router.get("/warnings")
async def get_warnings(
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: SchoolService = Depends(get_school_service),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    handled: bool = None,
    level: int = None
):
    from sqlalchemy import select
    university_id = await get_university_id(db, payload.get("sub"))

    filters = {
        "page": page,
        "page_size": page_size,
        "handled": handled,
        "level": level
    }

    data = await service.get_warnings(university_id, filters)
    return {
        "code": 200,
        "message": "success",
        "data": data
    }


@router.put("/warnings/{warning_id}")
async def handle_warning(
    warning_id: str,
    data: dict,
    payload: dict = Depends(get_current_user),
    service: SchoolService = Depends(get_school_service)
):
    handled = data.get("handled", True)
    success = await service.handle_warning(warning_id, handled)

    if not success:
        raise HTTPException(status_code=404, detail="预警不存在")

    return {"code": 200, "message": "处理成功"}


@router.post("/warnings/generate")
async def generate_warnings(
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    graduation_year: int = Query(None, description="毕业年份筛选，不传则包含所有年份"),
    dry_run: bool = Query(False, description="试运行，不保存只返回结果"),
):
    """
    触发预警生成

    - **graduation_year**: 可选，按毕业年份筛选
    - **dry_run**: 试运行模式，只计算不保存
    """
    university_id = await get_university_id(db, payload.get("sub"))

    from app.services.warning_engine import WarningEngine
    engine = WarningEngine(db)

    result = engine.generate_warnings_for_university(
        university_id=university_id,
        graduation_year=graduation_year,
        dry_run=dry_run,
    )

    level_map = {1: "红色预警", 2: "黄色预警", 3: "绿色提醒", 0: "无预警"}
    summary = {
        "total_students": result["total"],
        "red_warnings": result["red"],
        "yellow_warnings": result["yellow"],
        "green_warnings": result["green"],
        "no_warning": result["no_warning"],
        "generated": result["generated"],
        "skipped": result["skipped"],
        "errors": result["errors"],
    }

    return {
        "code": 200,
        "message": "预警生成完成" if not dry_run else "试运行完成（未保存）",
        "data": {
            "summary": summary,
            "dry_run": dry_run,
        }
    }


@router.post("/warnings/generate/{profile_id}")
async def generate_student_warning(
    profile_id: str,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    为单个学生生成预警
    """
    university_id = await get_university_id(db, payload.get("sub"))

    from app.services.warning_engine import WarningEngine
    engine = WarningEngine(db)

    result = await engine.generate_single_student_warning(profile_id, university_id)

    if result is None:
        return {
            "code": 200,
            "message": "该学生无需预警",
            "data": None,
        }

    return {
        "code": 200,
        "message": "预警生成成功",
        "data": result,
    }


@router.get("/databoard")
async def databoard(
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: SchoolService = Depends(get_school_service),
    year: int = Query(None, description="毕业年份筛选，如 2026")
):
    from sqlalchemy import select
    university_id = await get_university_id(db, payload.get("sub"))
    data = await service.get_databoard_data(university_id, year=year)

    return {"code": 200, "message": "success", "data": data}


@router.get("/databoard/province/{province}")
async def get_province_detail(
    province: str,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: SchoolService = Depends(get_school_service),
    tab: str = Query("students", description="Tab: students | companies"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    year: int = Query(None, description="毕业年份筛选")
):
    """省份详情弹窗数据接口"""
    from sqlalchemy import select
    university_id = await get_university_id(db, payload.get("sub"))

    if tab == "students":
        summary = await service.get_province_student_summary(province, university_id, year)
        students = await service.get_province_students_paginated(province, university_id, year, page, page_size)
        return {
            "code": 200,
            "message": "success",
            "data": {"summary": summary, "students": students},
        }
    else:
        summary = await service.get_province_company_summary(province, university_id)
        companies = await service.get_province_companies_paginated(province, university_id, page, page_size)
        return {
            "code": 200,
            "message": "success",
            "data": {"summary": summary, "companies": companies},
        }


@router.post("/databoard/regenerate")
async def regenerate_databoard_data(
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    year: int = Body(2026, description="毕业年份")
):
    """重新生成学生数据并刷新聚合表"""
    from app.services.data_generator import generate_data_from_csv
    from app.core.redis_client import get_redis

    # Find the CSV file
    import os
    from pathlib import Path

    csv_paths = [
        Path(__file__).parent.parent.parent.parent / "dataset" / "学校数据" / "4.各学院去向落实情况统计表(基数确定+就业过程数据).csv",
        Path(__file__).parent.parent.parent.parent.parent / "art-design-pro" / "dataset" / "学校数据" / "4.各学院去向落实情况统计表(基数确定+就业过程数据).csv",
    ]

    csv_path = None
    for path in csv_paths:
        if path.exists():
            csv_path = path
            break

    if not csv_path:
        return {"code": 400, "message": "找不到CSV数据文件"}

    try:
        with open(csv_path, "rb") as f:
            csv_content = f.read()

        result = await generate_data_from_csv(db, csv_content, year)

        # Invalidate Redis cache
        redis = get_redis()
        if redis:
            try:
                university_id = "UNI001"  # Default
                cache_key = f"school_databoard:{university_id}:{year}"
                redis.delete(f"school_databoard:{university_id}:all")
                redis.delete(cache_key)
            except Exception:
                pass

        if result["success"]:
            return {"code": 200, "message": "数据生成成功", "data": {"generated": result["generated"]}}
        else:
            return {"code": 400, "message": result.get("error", "数据生成失败")}
    except Exception as e:
        return {"code": 500, "message": f"数据生成失败: {str(e)}"}


@router.get("/databoard/word-cloud")
async def get_word_cloud_data(
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取词云数据（从job_descriptions表提取title和keywords）"""
    from sqlalchemy import select, func
    from app.models.job import JobDescription
    from collections import Counter
    import json

    # 查询所有招聘中的岗位
    result = await db.execute(
        select(JobDescription).where(JobDescription.status == 1)
    )
    jobs = result.scalars().all()

    word_counter = Counter()

    for job in jobs:
        # 处理title - 分割中文和英文单词
        if job.title:
            # 按中文字符和英文单词分割
            import re
            words = re.findall(r'[\u4e00-\u9fa5]+|[a-zA-Z]+', job.title)
            for word in words:
                if len(word) >= 2:  # 只统计2个字符以上的词
                    word_counter[word] += 1

        # 处理keywords - JSON数组
        if job.keywords:
            try:
                if isinstance(job.keywords, str):
                    kw_list = json.loads(job.keywords)
                else:
                    kw_list = job.keywords
                for kw in kw_list:
                    if kw and isinstance(kw, str):
                        word_counter[kw.strip()] += 1
            except (json.JSONDecodeError, TypeError):
                pass

    # 获取前50个高频词
    top_words = word_counter.most_common(50)
    word_cloud_data = [{"name": word, "value": count} for word, count in top_words]

    return {"code": 200, "message": "success", "data": word_cloud_data}


@router.get("/databoard/job-titles")
async def get_job_titles_stats(
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取热门岗位标题TOP10统计（从job_descriptions表提取）"""
    from sqlalchemy import select, func
    from app.models.job import JobDescription
    from collections import Counter
    import re

    # 查询所有招聘中的岗位
    result = await db.execute(
        select(JobDescription).where(JobDescription.status == 1)
    )
    jobs = result.scalars().all()

    # 统计岗位出现次数
    title_counter = Counter()
    for job in jobs:
        if job.title:
            # 提取岗位名称中的核心词（去掉公司名、地区等后缀）
            title = job.title.strip()
            # 移除常见的岗位后缀
            for suffix in ['有限公司', '公司', '-', '—', '_']:
                if suffix in title:
                    title = title.split(suffix)[0].strip()
            if title:
                title_counter[title] += 1

    # 获取TOP10
    top_titles = title_counter.most_common(10)
    data = [
        {"title": title, "count": count}
        for title, count in top_titles
    ]

    return {"code": 200, "message": "success", "data": data}


@router.get("/profile")
async def get_profile(
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: SchoolService = Depends(get_school_service)
):
    university_id = await get_university_id(db, payload.get("sub"))
    profile = await service.get_profile(university_id)

    if not profile:
        raise HTTPException(status_code=404, detail="学校信息不存在")

    return {
        "code": 200,
        "message": "success",
        "data": {
            "university_id": profile.university_id,
            "name": profile.name,
            "province": profile.province,
            "city": profile.city,
            "type": profile.type,
        }
    }


@router.put("/profile")
async def update_profile(
    data: dict,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: SchoolService = Depends(get_school_service)
):
    university_id = await get_university_id(db, payload.get("sub"))
    success = await service.update_profile(university_id, data)

    if not success:
        raise HTTPException(status_code=404, detail="学校信息不存在")

    return {"code": 200, "message": "更新成功"}


# ==================== 学院就业管理 ====================

@router.get("/colleges")
async def get_school_colleges(
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: SchoolService = Depends(get_school_service),
    year: int = Query(None, description="毕业年份"),
    current: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100)
):
    """获取本校学院就业数据（学校管理员端）"""
    university_id = await get_university_id(db, payload.get("sub"))
    data = await service.get_colleges(university_id, year, current, size)
    return {
        "code": 200,
        "message": "success",
        "data": data
    }


# ==================== 企业信息审核 ====================

@router.get("/jobs/pending")
async def get_pending_jobs(
    review_status: int = Query(0, description="审核状态: 0待审核 1已通过 2已拒绝"),
    current: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None, description="岗位名称关键词"),
    payload: dict = Depends(get_current_user),
    service: SchoolService = Depends(get_school_service)
):
    """获取待审核的岗位列表"""
    items, total = await service.get_pending_jobs(review_status, current, size, keyword)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "list": items,
            "total": total,
            "current": current,
            "size": size
        }
    }


@router.put("/jobs/{job_id}/review")
async def review_job(
    job_id: str,
    data: dict,
    payload: dict = Depends(get_current_user),
    service: SchoolService = Depends(get_school_service)
):
    """审核岗位"""
    action = data.get("action")
    if action not in ("approve", "reject"):
        raise HTTPException(status_code=400, detail="无效的操作")

    reviewer_id = payload.get("sub")
    reject_reason = data.get("reject_reason")

    success = await service.review_job(job_id, action, reviewer_id, reject_reason)
    if not success:
        raise HTTPException(status_code=404, detail="岗位不存在")

    return {"code": 200, "message": "操作成功"}


@router.get("/activities/pending")
async def get_pending_activities(
    review_status: int = Query(0, description="审核状态: 0待审核 1已通过 2已拒绝"),
    current: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None, description="活动标题关键词"),
    payload: dict = Depends(get_current_user),
    service: SchoolService = Depends(get_school_service)
):
    """获取待审核的活动列表"""
    items, total = await service.get_pending_activities(review_status, current, size, keyword)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "list": items,
            "total": total,
            "current": current,
            "size": size
        }
    }


@router.put("/activities/{activity_id}/review")
async def review_activity(
    activity_id: str,
    data: dict,
    payload: dict = Depends(get_current_user),
    service: SchoolService = Depends(get_school_service)
):
    """审核活动"""
    action = data.get("action")
    if action not in ("approve", "reject"):
        raise HTTPException(status_code=400, detail="无效的操作")

    reviewer_id = payload.get("sub")
    reject_reason = data.get("reject_reason")

    success = await service.review_activity(activity_id, action, reviewer_id, reject_reason)
    if not success:
        raise HTTPException(status_code=404, detail="活动不存在")

    return {"code": 200, "message": "操作成功"}


# ==================== 学校/管理员查看所有企业公告和活动 ====================

@router.get("/company/announcements")
async def get_all_company_announcements(
    keyword: str = "",
    company_name: str = "",
    major: str = "",
    degree: int | None = None,
    year: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有企业发布的公告（学校/管理员端）

    - **keyword**: 搜索关键词（标题）
    - **company_name**: 企业名称
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
    if company_name:
        conditions.append(Company.company_name.contains(company_name))
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
        select(CompanyAnnouncement, Company.company_name, Company.city)
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
        city = row[2]
        items.append({
            "announcement_id": announcement.announcement_id,
            "company_id": announcement.company_id,
            "company_name": company_name,
            "city": city,
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


@router.get("/company/announcements/{announcement_id}")
async def get_company_announcement_detail(
    announcement_id: str,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取公告详情（学校/管理员端）
    """
    from sqlalchemy import select, and_
    from app.models.company_announcement import CompanyAnnouncement
    from app.models.company import Company

    query = (
        select(CompanyAnnouncement, Company.company_name, Company.city)
        .join(Company, CompanyAnnouncement.company_id == Company.company_id)
        .where(CompanyAnnouncement.announcement_id == announcement_id)
    )
    result = await db.execute(query)
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="公告不存在")

    announcement = row[0]
    company_name = row[1]
    city = row[2]

    return {
        "code": 200,
        "message": "success",
        "data": {
            "announcement_id": announcement.announcement_id,
            "company_id": announcement.company_id,
            "company_name": company_name,
            "city": city,
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


@router.get("/company/activities")
async def get_all_company_activities(
    keyword: str = "",
    company_name: str = "",
    activity_type: str = "",
    year: int | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取所有企业发布的宣讲会/活动（学校/管理员端）

    - **keyword**: 搜索关键词（标题）
    - **company_name**: 企业名称
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
    if company_name:
        conditions.append(Company.company_name.contains(company_name))
    if activity_type:
        conditions.append(CompanyActivity.type == activity_type)
    if year:
        conditions.append(extract('year', CompanyActivity.activity_date) == year)

    # 关联公司获取公司名称
    query = (
        select(CompanyActivity, Company.company_name, Company.city)
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
        city = row[2]
        items.append({
            "activity_id": activity.activity_id,
            "company_id": activity.company_id,
            "company_name": company_name,
            "city": city,
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


@router.get("/company/activities/{activity_id}")
async def get_company_activity_detail(
    activity_id: str,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取活动详情（学校/管理员端）
    """
    from sqlalchemy import select, and_
    from app.models.company_activity import CompanyActivity
    from app.models.company import Company

    query = (
        select(CompanyActivity, Company.company_name, Company.city)
        .join(Company, CompanyActivity.company_id == Company.company_id)
        .where(CompanyActivity.activity_id == activity_id)
    )
    result = await db.execute(query)
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="活动不存在")

    activity = row[0]
    company_name = row[1]
    city = row[2]

    return {
        "code": 200,
        "message": "success",
        "data": {
            "activity_id": activity.activity_id,
            "company_id": activity.company_id,
            "company_name": company_name,
            "city": city,
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
