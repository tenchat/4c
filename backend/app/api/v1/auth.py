from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_user_id
from app.schemas.auth import LoginRequest, RegisterRequest, LoginResponse, RefreshRequest
from app.services.auth_service import AuthService

router = APIRouter()


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post("/register", status_code=201)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    try:
        account = await service.register(
            username=req.username,
            password=req.password,
            role=req.role,
            student_no=req.student_no,
            real_name=req.real_name,
            enterprise_name=req.enterprise_name,
            registration_code=req.registration_code,
        )
        return {"code": 201, "message": "注册成功", "data": {
            "account_id": account.account_id,
            "username": account.username,
            "role": account.role.value
        }}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    try:
        result = await service.login(req.username, req.password, req.role)
        if not result:
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        return {"code": 200, "message": "登录成功", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout")
async def logout(
    request: Request,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    # 获取原始 token
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header else None
    await service.logout(payload.get("sub"), token)
    return {"code": 200, "message": "已退出登录"}


@router.get("/me")
async def get_me(
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    result = await service.get_user_info(payload.get("sub"))
    if not result:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"code": 200, "message": "success", "data": result}


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@router.post("/change-password")
async def change_password(
    req: ChangePasswordRequest,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """修改当前用户密码"""
    service = AuthService(db)
    try:
        success = await service.change_password(payload.get("sub"), req.old_password, req.new_password)
        if not success:
            raise HTTPException(status_code=400, detail="旧密码错误")
        return {"code": 200, "message": "密码修改成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh")
async def refresh(
    req: RefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)
    result = await service.refresh_token(req.refresh_token)
    if not result:
        raise HTTPException(status_code=401, detail="Refresh token无效或已过期")
    return {"code": 200, "message": "success", "data": result}
