from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.student_service import StudentService
from app.services.rag.rag_service import get_rag_service

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

    return {
        "code": 200,
        "message": "success",
        "data": {
            "welcome": "欢迎来到学生中心",
            "profile_complete": profile.profile_complete if profile else 0,
            "employment_status": profile.employment_status if profile else 0,
            "recommended_jobs": [],
            "warnings": []
        }
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
            "profile_complete": profile.profile_complete,
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
    min_salary: int = 0,
    max_salary: int = 0,
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
