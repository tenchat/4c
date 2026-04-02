"""
数据库连接管理

使用 SQLite 数据库，通过 SQLAlchemy async 进行操作
"""

import logging
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import event
from sqlalchemy.pool import NullPool

logger = logging.getLogger(__name__)

# 数据库路径
# 优先使用 backend 目录下的 SQLite 数据库文件
BACKEND_DB_PATH = Path(__file__).parent.parent.parent / "backend" / "employment.db"
LOCAL_DB_PATH = Path(__file__).parent.parent / "data" / "rag_sqlite.db"

# 选择存在的数据库文件
if BACKEND_DB_PATH.exists():
    DATABASE_URL = f"sqlite+aiosqlite:///{BACKEND_DB_PATH}"
elif LOCAL_DB_PATH.exists():
    DATABASE_URL = f"sqlite+aiosqlite:///{LOCAL_DB_PATH}"
else:
    # 如果都不存在，使用本地路径（后续初始化时创建）
    DATABASE_URL = f"sqlite+aiosqlite:///{LOCAL_DB_PATH}"
    LOCAL_DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_engine():
    """创建数据库引擎"""
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,  # 生产环境设为 False
        poolclass=NullPool,  # SQLite 使用 NullPool 避免多线程问题
    )

    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """为 SQLite 连接启用外键约束"""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


# 创建引擎和会话工厂
engine = get_engine()
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的依赖注入函数

    用法：
        async def route(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """初始化数据库连接"""
    try:
        async with engine.begin() as conn:
            logger.info(f"数据库连接成功: {DATABASE_URL}")
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise
