from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.admin_service import AdminService
from app.services.stats_service import StatsService
from app.core.redis_client import get_redis
from app.schemas.company import JobCreate
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


def get_admin_service(db: AsyncSession = Depends(get_db)) -> AdminService:
    return AdminService(db)


@router.get("/dashboard")
async def dashboard(
    payload: dict = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service)
):
    data = await service.get_dashboard_data()
    return {
        "code": 200,
        "message": "success",
        "data": data
    }


@router.get("/statistics")
async def statistics(
    payload: dict = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service),
    dimension: str = Query(..., description="统计维度: province/industry/degree"),
    year: int = Query(None, description="统计年份")
):
    data = await service.get_statistics(dimension, year)
    return {"code": 200, "message": "success", "data": data}


@router.get("/colleges")
async def get_colleges(
    payload: dict = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service),
    university_id: str = Query(..., description="学校ID"),
    year: int = Query(None, description="毕业年份"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    data = await service.get_colleges(university_id, year, page, page_size)
    return {
        "code": 200,
        "message": "success",
        "data": data
    }


@router.put("/colleges/{record_id}")
async def update_college(
    record_id: str,
    data: dict,
    payload: dict = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service)
):
    success = await service.update_college(record_id, data)
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在")
    return {"code": 200, "message": "更新成功"}


@router.post("/colleges/import")
async def import_colleges(
    payload: dict = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service)
):
    return {"code": 200, "message": "导入功能开发中", "data": {"success": 0, "failed": 0}}


@router.get("/scarce-talents")
async def get_scarce_talents(
    payload: dict = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service),
    province: str = Query(None, description="省份"),
    shortage_level: int = Query(None, description="紧缺程度 1轻微 2中等 3严重"),
    year: int = Query(None, description="数据年份")
):
    data = await service.get_scarce_talents(province, shortage_level, year)
    return {"code": 200, "message": "success", "data": data}


@router.get("/databoard")
async def databoard(
    payload: dict = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service)
):
    data = await service.get_databoard_data()
    return {"code": 200, "message": "success", "data": data}


@router.get("/companies/pending")
async def get_pending_companies(
    status: int = 0,
    current: int = 1,
    size: int = 20,
    payload: dict = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service)
):
    """status: 0=待审核, 1=已审核"""
    import time
    t0 = time.perf_counter()
    t_auth = time.perf_counter()
    companies, total = await service.get_companies_by_status(status, current, size)
    t_db = time.perf_counter()
    logger.info(f"[TIMING] auth={t_auth-t0:.3f}s db={t_db-t_auth:.3f}s total={t_db-t0:.3f}s")
    return {
        "code": 200,
        "message": "success",
        "data": {
            "list": companies,
            "total": total,
            "current": current,
            "size": size
        }
    }


@router.put("/companies/{company_id}/verify")
async def verify_company(
    company_id: str,
    data: dict,
    payload: dict = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service)
):
    action = data.get("action")
    if action not in ("approve", "reject"):
        raise HTTPException(status_code=400, detail="无效的操作")

    success = await service.verify_company(company_id, action)
    if not success:
        raise HTTPException(status_code=404, detail="企业不存在")

    return {"code": 200, "message": "操作成功"}


@router.get("/company-profile-updates/pending")
async def get_pending_profile_updates(
    status: str = "pending",
    current: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    payload: dict = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service)
):
    """获取待审核的企业信息更新列表"""
    items, total = await service.get_pending_profile_updates(status, current, size)
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


@router.put("/company-profile-updates/{pending_id}/review")
async def review_profile_update(
    pending_id: str,
    data: dict,
    payload: dict = Depends(get_current_user),
    service: AdminService = Depends(get_admin_service)
):
    """审核企业信息更新"""
    action = data.get("action")
    if action not in ("approve", "reject"):
        raise HTTPException(status_code=400, detail="无效的操作")

    reviewer_id = payload.get("sub")
    reject_reason = data.get("reject_reason")

    success = await service.review_profile_update(pending_id, action, reject_reason, reviewer_id)
    if not success:
        raise HTTPException(status_code=404, detail="待审核记录不存在")

    return {"code": 200, "message": "操作成功"}


@router.get("/enterprise-stats")
async def get_enterprise_stats(
    year: Optional[int] = Query(None),
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取企业相关聚合统计数据（管理端）"""
    svc = StatsService()
    redis = await get_redis()
    if redis is None:
        # Create a dummy redis-like object for when Redis is unavailable
        class DummyRedis:
            async def get(self, key):
                return None
            async def setex(self, key, ttl, value):
                pass
        redis = DummyRedis()
    return await svc.get_enterprise_stats(db, redis, year)
