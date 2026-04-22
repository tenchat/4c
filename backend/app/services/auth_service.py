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

    async def register(
        self,
        username: str,
        password: str,
        role: str,
        student_no: str = None,
        real_name: str = None,
        enterprise_name: str = None,
        registration_code: str = None,
    ) -> Account:
        from app.models.student import StudentProfile
        from app.models.company import Company
        from app.core.security import get_password_hash

        # 1. 校验用户名唯一性
        result = await self.db.execute(select(Account).where(Account.username == username))
        if result.scalar_one_or_none():
            raise Exception("用户名已存在")

        settings = get_settings()

        # 2. 根据 role 分支处理
        if role == "student":
            # 学生注册：关联已导入档案或创建新档案
            if not student_no:
                raise Exception("学生注册必须填写学号")

            university_id = settings.DEFAULT_UNIVERSITY_ID or ""

            # 查询是否存在匹配的 student_profiles（可能有多条同名学号）
            profile_result = await self.db.execute(
                select(StudentProfile).where(StudentProfile.student_no == student_no)
            )
            existing_profiles = profile_result.scalars().all()

            if len(existing_profiles) > 1:
                raise Exception("存在多条同名学号记录，请联系管理员处理")

            account = Account(
                account_id=str(uuid.uuid4()),
                username=username,
                password_hash=get_password_hash(password),
                real_name=real_name or student_no,
                role=RoleType.student,
                status=AccountStatus.enabled.value,
            )
            self.db.add(account)
            await self.db.flush()

            if len(existing_profiles) == 1:
                existing_profile = existing_profiles[0]
                if existing_profile.account_id:
                    # 档案已绑定其他账户
                    raise Exception("该学号已注册，如有问题请联系管理员")
                # 绑定到已有档案
                existing_profile.account_id = account.account_id
            else:
                # 无匹配档案，创建新档案
                new_profile = StudentProfile(
                    profile_id=str(uuid.uuid4()),
                    account_id=account.account_id,
                    university_id=university_id,
                    student_no=student_no,
                    college="",
                    major="",
                    degree=1,
                )
                self.db.add(new_profile)

        elif role == "school_admin":
            # 学校管理员：校验注册码（优先从 system_configs 读取，否则用 .env 兜底）
            if not registration_code:
                raise Exception("学校管理员注册必须填写注册码")
            # 尝试从数据库配置读取
            from app.models.system_config import SystemConfig
            db_config_result = await self.db.execute(
                select(SystemConfig).where(SystemConfig.config_key == "SCHOOL_ADMIN_REGISTRATION_CODE")
            )
            db_config = db_config_result.scalar_one_or_none()
            valid_code = db_config.config_value if db_config and db_config.config_value else settings.SCHOOL_ADMIN_REGISTRATION_CODE
            if registration_code != valid_code:
                raise Exception("注册码错误，请联系管理员获取正确注册码")

            account = Account(
                account_id=str(uuid.uuid4()),
                username=username,
                password_hash=get_password_hash(password),
                real_name=real_name or username,
                role=RoleType.school_admin,
                status=AccountStatus.pending.value,
            )
            self.db.add(account)

        elif role == "company_admin":
            # 企业：创建 Account + Company
            if not enterprise_name:
                raise Exception("企业注册必须填写企业名称")

            account = Account(
                account_id=str(uuid.uuid4()),
                username=username,
                password_hash=get_password_hash(password),
                real_name=real_name or enterprise_name,
                role=RoleType.company_admin,
                status=AccountStatus.pending.value,
            )
            self.db.add(account)
            await self.db.flush()

            company = Company(
                company_id=str(uuid.uuid4()),
                account_id=account.account_id,
                company_name=enterprise_name,
            )
            self.db.add(company)

        else:
            raise Exception("不支持的角色类型")

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

    async def change_password(self, account_id: str, old_password: str, new_password: str) -> bool:
        """修改用户密码"""
        result = await self.db.execute(
            select(Account).where(Account.account_id == account_id)
        )
        account = result.scalar_one_or_none()
        if not account:
            return False

        # 验证旧密码
        if not verify_password(old_password, account.password_hash):
            return False

        # 更新新密码
        account.password_hash = get_password_hash(new_password)
        await self.db.commit()
        return True
