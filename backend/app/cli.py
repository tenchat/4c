import asyncio
import sys
from sqlalchemy import text
from app.core.database import engine, Base
from app.models import *
from app.core.security import get_password_hash
from app.models.account import Account, RoleType, AccountStatus
from sqlalchemy.ext.asyncio import AsyncSession

async def init_db():
    """初始化数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("数据库表创建成功")

async def create_admin(username: str, password: str):
    """创建系统管理员"""
    async with AsyncSession(engine) as session:
        # 检查是否已存在
        result = await session.execute(
            text(f"SELECT * FROM accounts WHERE username = '{username}'")
        )
        if result.fetchone():
            print(f"管理员 {username} 已存在")
            return

        admin = Account(
            account_id="admin-001",
            username=username,
            password_hash=get_password_hash(password),
            real_name="系统管理员",
            role=RoleType.system_admin,
            status=AccountStatus.enabled.value,
        )
        session.add(admin)
        await session.commit()
        print(f"管理员创建成功: {username}")

async def seed_data():
    """创建测试数据"""
    # TODO: 实现测试数据
    print("测试数据创建功能开发中")

async def verify_company(company_id: str, action: str):
    """企业审核"""
    # TODO: 实现企业审核
    print(f"企业 {company_id} 审核状态: {action}")

async def unlock_account(username: str):
    """解锁账号"""
    # TODO: 实现账号解锁
    print(f"账号 {username} 解锁")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else None
    if cmd == "init-db":
        asyncio.run(init_db())
    elif cmd == "create-admin":
        username = sys.argv[2] if len(sys.argv) > 2 else "admin"
        password = sys.argv[3] if len(sys.argv) > 3 else "Admin123!"
        asyncio.run(create_admin(username, password))
    elif cmd == "seed-data":
        asyncio.run(seed_data())
    elif cmd == "verify-company":
        company_id = sys.argv[2] if len(sys.argv) > 2 else ""
        action = sys.argv[3] if len(sys.argv) > 3 else "approve"
        asyncio.run(verify_company(company_id, action))
    elif cmd == "unlock-account":
        username = sys.argv[2] if len(sys.argv) > 2 else ""
        asyncio.run(unlock_account(username))
    else:
        print("可用命令:")
        print("  init-db                    - 初始化数据库表")
        print("  create-admin <username> <password> - 创建系统管理员")
        print("  seed-data                  - 创建测试数据")
        print("  verify-company <company_id> <action> - 企业审核")
        print("  unlock-account <username>  - 解锁账号")
