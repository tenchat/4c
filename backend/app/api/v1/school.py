from fastapi import APIRouter, Depends, HTTPException, Query
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


@router.post("/students/import")
async def import_students(
    payload: dict = Depends(get_current_user),
    service: SchoolService = Depends(get_school_service)
):
    # TODO: 实现 Excel 导入
    return {"code": 200, "message": "导入功能开发中", "data": {"success": 0, "failed": 0}}


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


@router.get("/databoard")
async def databoard(
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: SchoolService = Depends(get_school_service)
):
    from sqlalchemy import select
    university_id = await get_university_id(db, payload.get("sub"))
    data = await service.get_databoard_data(university_id)

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
