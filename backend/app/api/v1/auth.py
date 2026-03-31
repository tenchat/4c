from fastapi import APIRouter, Depends, HTTPException, Request
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
        account = await service.register(req.username, req.password, req.real_name or "", req.role)
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
