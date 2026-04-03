from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.company import Company
from app.services.company_service import CompanyService
from app.schemas.company import JobCreate, JobStatusUpdate, ProfileUpdateRequest, ProfilePendingResponse

router = APIRouter()


def get_company_service(db: AsyncSession = Depends(get_db)) -> CompanyService:
    return CompanyService(db)


async def get_company_id(db: AsyncSession, account_id: str) -> str:
    """获取当前用户关联的 company_id"""
    result = await db.execute(
        select(Company).where(Company.account_id == account_id)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=400, detail="企业信息不存在")
    return company.company_id


@router.get("/dashboard")
async def dashboard(
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: CompanyService = Depends(get_company_service)
):
    company_id = await get_company_id(db, payload.get("sub"))
    data = await service.get_dashboard_data(company_id)

    return {
        "code": 200,
        "message": "success",
        "data": data
    }


@router.get("/jobs")
async def get_jobs(
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: CompanyService = Depends(get_company_service),
    status: int = Query(None, description="岗位状态 1招聘中 0暂停 2结束"),
    title: str = Query(None, description="岗位名称模糊搜索"),
    city: str = Query(None, description="工作城市模糊搜索"),
    industry: str = Query(None, description="行业"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    company_id = await get_company_id(db, payload.get("sub"))
    data = await service.get_jobs(
        company_id, status, page, page_size,
        title=title, city=city, industry=industry
    )

    return {
        "code": 200,
        "message": "success",
        "data": data
    }


@router.get("/jobs/{job_id}")
async def get_job(
    job_id: str,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: CompanyService = Depends(get_company_service),
):
    company_id = await get_company_id(db, payload.get("sub"))
    job = await service.get_job(job_id, company_id)
    if not job:
        raise HTTPException(status_code=404, detail="岗位不存在")
    return {"code": 200, "message": "success", "data": job}


@router.post("/jobs")
async def create_job(
    data: JobCreate,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: CompanyService = Depends(get_company_service)
):
    company_id = await get_company_id(db, payload.get("sub"))
    job_id = await service.create_job(company_id, data.model_dump())

    return {"code": 200, "message": "发布成功", "data": {"job_id": job_id}}


@router.put("/jobs/{job_id}")
async def update_job(
    job_id: str,
    data: JobCreate,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: CompanyService = Depends(get_company_service)
):
    company_id = await get_company_id(db, payload.get("sub"))

    try:
        success = await service.update_job(job_id, company_id, data.model_dump(exclude_unset=True))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    if not success:
        raise HTTPException(status_code=404, detail="岗位不存在")

    return {"code": 200, "message": "更新成功"}


@router.patch("/jobs/{job_id}/status")
async def toggle_job_status(
    job_id: str,
    data: JobStatusUpdate,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: CompanyService = Depends(get_company_service)
):
    company_id = await get_company_id(db, payload.get("sub"))

    try:
        success = await service.toggle_job_status(job_id, company_id, data.status)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    if not success:
        raise HTTPException(status_code=404, detail="岗位不存在")

    status_text = {0: "暂停", 1: "上架", 2: "结束"}.get(data.status, "操作")
    return {"code": 200, "message": f"{status_text}成功"}


@router.delete("/jobs/{job_id}")
async def delete_job(
    job_id: str,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: CompanyService = Depends(get_company_service)
):
    company_id = await get_company_id(db, payload.get("sub"))

    try:
        success = await service.delete_job(job_id, company_id)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    if not success:
        raise HTTPException(status_code=404, detail="岗位不存在")

    return {"code": 200, "message": "删除成功"}


@router.get("/profile")
async def get_profile(
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: CompanyService = Depends(get_company_service)
):
    company_id = await get_company_id(db, payload.get("sub"))
    profile = await service.get_profile_with_pending(company_id)

    if not profile:
        raise HTTPException(status_code=404, detail="企业信息不存在")

    return {
        "code": 200,
        "message": "success",
        "data": profile
    }


@router.post("/profile/submit")
async def submit_profile_for_review(
    data: ProfileUpdateRequest,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: CompanyService = Depends(get_company_service)
):
    """提交企业档案更新申请（需审核）"""
    company_id = await get_company_id(db, payload.get("sub"))

    try:
        pending_id = await service.submit_profile_for_review(company_id, data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"code": 200, "message": "提交成功，请等待学校管理员审核", "data": {"pending_id": pending_id}}


@router.get("/profile/pending")
async def get_pending_profile(
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: CompanyService = Depends(get_company_service)
):
    """获取待审核的企业信息更新"""
    company_id = await get_company_id(db, payload.get("sub"))
    pending = await service.get_pending_profile(company_id)

    return {
        "code": 200,
        "message": "success",
        "data": pending
    }


from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.company import Company
from app.services.activity_service import ActivityService
from app.services.announcement_service import AnnouncementService
from app.schemas.company_activity import (
    ActivityCreate, ActivityUpdate, ActivityOut
)
from app.schemas.company_announcement import (
    AnnouncementCreate, AnnouncementUpdate, AnnouncementOut
)


# --- Activity routes ---

@router.get("/activities")
async def list_activities(
    type: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    status: Optional[int] = Query(None),
    min_expected_num: Optional[int] = Query(None),
    max_expected_num: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_id = await get_company_id(db, payload.get("sub"))
    svc = ActivityService(db)
    data = await svc.list_activities(
        company_id,
        type=type,
        year=year,
        status=status,
        min_expected_num=min_expected_num,
        max_expected_num=max_expected_num,
        page=page,
        page_size=page_size
    )
    return {"code": 200, "message": "success", "data": data}


@router.post("/activities", status_code=201)
async def create_activity(
    data: ActivityCreate,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_id = await get_company_id(db, payload.get("sub"))
    svc = ActivityService(db)
    activity = await svc.create_activity(company_id, data)
    return {"code": 200, "message": "创建成功", "data": activity}


@router.get("/activities/{activity_id}", response_model=ActivityOut)
async def get_activity(
    activity_id: str,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_id = await get_company_id(db, payload.get("sub"))
    svc = ActivityService(db)
    activity = await svc.get_activity(activity_id, company_id)
    return {"code": 200, "message": "success", "data": activity}


@router.put("/activities/{activity_id}")
async def update_activity(
    activity_id: str,
    data: ActivityUpdate,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_id = await get_company_id(db, payload.get("sub"))
    svc = ActivityService(db)
    activity = await svc.update_activity(activity_id, company_id, data)
    return {"code": 200, "message": "更新成功", "data": activity}


@router.delete("/activities/{activity_id}")
async def delete_activity(
    activity_id: str,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_id = await get_company_id(db, payload.get("sub"))
    svc = ActivityService(db)
    await svc.delete_activity(activity_id, company_id)
    return {"code": 200, "message": "删除成功"}


@router.patch("/activities/{activity_id}/status")
async def toggle_activity_status(
    activity_id: str,
    status: int = Query(..., description="状态: 0已取消 1进行中 2已结束"),
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_id = await get_company_id(db, payload.get("sub"))
    svc = ActivityService(db)
    activity = await svc.toggle_activity_status(activity_id, company_id, status)
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    status_text = {0: "取消", 1: "开始", 2: "结束"}.get(status, "操作")
    return {"code": 200, "message": f"{status_text}成功", "data": activity}


# --- Announcement routes ---

@router.get("/announcements")
async def list_announcements(
    status: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_id = await get_company_id(db, payload.get("sub"))
    svc = AnnouncementService(db)
    data = await svc.list_announcements(company_id, status=status, year=year, page=page, page_size=page_size)
    return {"code": 200, "message": "success", "data": data}


@router.post("/announcements", status_code=201)
async def create_announcement(
    data: AnnouncementCreate,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_id = await get_company_id(db, payload.get("sub"))
    svc = AnnouncementService(db)
    announcement = await svc.create_announcement(company_id, data)
    return {"code": 200, "message": "创建成功", "data": announcement}


@router.get("/announcements/{announcement_id}", response_model=AnnouncementOut)
async def get_announcement(
    announcement_id: str,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_id = await get_company_id(db, payload.get("sub"))
    svc = AnnouncementService(db)
    announcement = await svc.get_announcement(announcement_id, company_id)
    return {"code": 200, "message": "success", "data": announcement}


@router.put("/announcements/{announcement_id}")
async def update_announcement(
    announcement_id: str,
    data: AnnouncementUpdate,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_id = await get_company_id(db, payload.get("sub"))
    svc = AnnouncementService(db)
    announcement = await svc.update_announcement(announcement_id, company_id, data)
    return {"code": 200, "message": "更新成功", "data": announcement}


@router.delete("/announcements/{announcement_id}", status_code=204)
async def delete_announcement(
    announcement_id: str,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_id = await get_company_id(db, payload.get("sub"))
    svc = AnnouncementService(db)
    await svc.delete_announcement(announcement_id, company_id)
    return {"code": 200, "message": "删除成功"}


# --- 简历管理 ---

@router.get("/resumes")
async def get_received_resumes(
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: CompanyService = Depends(get_company_service),
    status: int = Query(None, description="简历状态 0已投递 1简历筛选 2面试中 3已录用 4已拒绝"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """获取收到的简历列表"""
    company_id = await get_company_id(db, payload.get("sub"))
    data = await service.get_received_resumes(company_id, status, page, page_size)
    return {"code": 200, "message": "success", "data": data}


class ApplicationStatusUpdate(BaseModel):
    status: int

@router.patch("/resumes/{application_id}/status")
async def update_application_status(
    application_id: str,
    data: ApplicationStatusUpdate,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: CompanyService = Depends(get_company_service)
):
    """更新简历状态"""
    company_id = await get_company_id(db, payload.get("sub"))
    try:
        success = await service.update_application_status(application_id, company_id, data.status)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    if not success:
        raise HTTPException(status_code=404, detail="简历申请不存在")

    status_map = {0: "已投递", 1: "简历筛选", 2: "面试中", 3: "已录用", 4: "已拒绝"}
    return {"code": 200, "message": f"更新为{status_map.get(data.status, data.status)}"}
