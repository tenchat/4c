from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.account import Account, RoleType, AccountStatus
from app.models.refresh_token import RefreshToken
from app.models.university import University
from app.models.student import StudentProfile
from app.models.company import Company
from app.core.security import (
    get_password_hash, verify_password,
    create_access_token, create_refresh_token, add_token_to_blacklist, verify_token, is_token_blacklisted
)
from app.core.config import get_settings
import uuid

settings = get_settings()

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, username: str, password: str, real_name: str, role: str) -> Account:
        # 检查用户名是否已存在
        result = await self.db.execute(select(Account).where(Account.username == username))
        if result.scalar_one_or_none():
            raise Exception("用户名已存在")

        account = Account(
            account_id=str(uuid.uuid4()),
            username=username,
            password_hash=get_password_hash(password),
            real_name=real_name,
            role=RoleType(role),
            status=AccountStatus.enabled.value if role != "company_admin" else AccountStatus.pending.value,
        )
        self.db.add(account)
        await self.db.flush()

        # 创建关联的档案
        if role == "student":
            student_profile = StudentProfile(
                profile_id=str(uuid.uuid4()),
                account_id=account.account_id,
            )
            self.db.add(student_profile)
        elif role == "company_admin":
            company = Company(
                company_id=str(uuid.uuid4()),
                account_id=account.account_id,
                company_name=real_name or username,
            )
            self.db.add(company)

        await self.db.commit()
        await self.db.refresh(account)
        return account

    async def login(self, username: str, password: str, role: str) -> dict | None:
        result = await self.db.execute(
            select(Account).where(Account.username == username)
        )
        account = result.scalar_one_or_none()

        if not account:
            return None

        # 验证角色匹配 - 防止用户选择错误角色登录
        if account.role.value != role:
            raise Exception(f"账号类型不匹配，请选择正确的账号类型登录")

        # 检查账号状态
        if account.status == AccountStatus.disabled.value:
            raise Exception("账号已禁用")
        if account.status == AccountStatus.pending.value:
            raise Exception("账号待审核")
        if account.locked_until and account.locked_until > datetime.utcnow():
            raise Exception("账号已锁定，请15分钟后再试")

        # 验证密码
        if not verify_password(password, account.password_hash):
            account.login_attempts += 1
            if account.login_attempts >= 5:
                account.locked_until = datetime.utcnow() + timedelta(minutes=15)
            await self.db.commit()
            raise Exception("密码错误")

        # 登录成功，重置失败计数
        account.login_attempts = 0
        account.last_login = datetime.utcnow()
        await self.db.commit()

        # 生成 token
        token_data = {"sub": account.account_id, "role": account.role.value}
        access_token = create_access_token(token_data)
        refresh_token_str = create_refresh_token(token_data)

        # 存储 refresh token
        rt = RefreshToken(
            token_id=str(uuid.uuid4()),
            account_id=account.account_id,
            token_hash=str(hash(refresh_token_str)),
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        self.db.add(rt)
        await self.db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token_str,
            "user": {
                "userId": hash(account.account_id) % 1000000,
                "userName": account.username,
                "roles": [account.role.value],
                "buttons": [],
                "email": account.email or "",
                "realName": account.real_name,
                "status": account.status,
            }
        }

    async def refresh_token(self, refresh_token: str) -> dict | None:
        """验证 refresh token 并生成新的 access_token + refresh_token (Token Rotation)"""
        from jose import jwt, JWTError

        # 1. 验证 token 格式和签名
        try:
            payload = jwt.decode(
                refresh_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
        except JWTError:
            return None

        # 2. 检查 token 类型
        if payload.get("type") != "refresh":
            return None

        # 3. 检查是否在黑名单
        if await is_token_blacklisted(refresh_token):
            return None

        # 4. 检查 refresh token 是否存在于数据库且未撤销
        token_hash = str(hash(refresh_token))
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked == False
            )
        )
        stored_token = result.scalar_one_or_none()
        if not stored_token:
            return None

        # 5. 检查是否过期
        if stored_token.expires_at < datetime.utcnow():
            return None

        account_id = payload.get("sub")

        # 6. 撤销旧 refresh token (Token Rotation)
        stored_token.revoked = True

        # 7. 生成新 token
        token_data = {"sub": account_id, "role": payload.get("role")}
        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)

        # 8. 存储新 refresh token
        new_rt = RefreshToken(
            token_id=str(uuid.uuid4()),
            account_id=account_id,
            token_hash=str(hash(new_refresh_token)),
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        self.db.add(new_rt)
        await self.db.commit()

        # 9. 将旧 token 加入黑名单
        await add_token_to_blacklist(refresh_token, settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token
        }

    async def logout(self, account_id: str, token: str = None) -> None:
        """撤销用户的 refresh token"""
        if token:
            # 将当前 access token 加入黑名单
            await add_token_to_blacklist(token, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)

        # 撤销该账户的所有 refresh tokens
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.account_id == account_id,
                RefreshToken.revoked == False
            )
        )
        tokens = result.scalars().all()
        for t in tokens:
            t.revoked = True
            # 将每个 refresh token 加入黑名单
            await add_token_to_blacklist(str(t.token_hash), settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400)

        await self.db.commit()

    async def get_user_info(self, account_id: str) -> dict | None:
        result = await self.db.execute(
            select(Account).where(Account.account_id == account_id)
        )
        account = result.scalar_one_or_none()
        if not account:
            return None

        return {
            "userId": hash(account.account_id) % 1000000,  # 转换为数字 ID
            "userName": account.username,
            "roles": [account.role.value],  # 包装为数组
            "buttons": [],  # 按钮权限暂为空
            "email": account.email or "",
            "realName": account.real_name,
            "status": account.status,
        }
