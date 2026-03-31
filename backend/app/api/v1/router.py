from fastapi import APIRouter
from app.api.v1 import auth, student, school, admin, company, ai

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(student.router, prefix="/student", tags=["学生"])
api_router.include_router(school.router, prefix="/school", tags=["学校"])
api_router.include_router(admin.router, prefix="/admin", tags=["管理员"])
api_router.include_router(company.router, prefix="/company", tags=["企业"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])
