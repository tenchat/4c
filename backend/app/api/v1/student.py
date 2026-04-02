from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.services.student_service import StudentService

router = APIRouter()


def get_student_service(db: AsyncSession = Depends(get_db)) -> StudentService:
    return StudentService(db)


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
    payload: dict = Depends(get_current_user),
    service: StudentService = Depends(get_student_service)
):
    account_id = payload.get("sub")
    jobs = await service.get_recommended_jobs(account_id, limit=10)

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
                "status": j.status
            } for j in jobs],
            "total": len(jobs),
            "page": 1,
            "page_size": 10
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
