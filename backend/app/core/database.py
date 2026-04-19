from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from app.core.config import get_settings

settings = get_settings()

if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. Please configure backend/.env file.")

# 根据DATABASE_URL判断数据库类型
is_sqlite = settings.DATABASE_URL.startswith("sqlite")


def get_engine():
    """根据数据库类型创建异步引擎"""
    if is_sqlite:
        # SQLite: 使用NullPool避免多线程问题
        return create_async_engine(
            settings.DATABASE_URL,
            echo=settings.APP_ENV == "development",
            poolclass=NullPool,
        )
    else:
        # MySQL: 使用连接池
        return create_async_engine(
            settings.DATABASE_URL,
            echo=settings.APP_ENV == "development",
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )


engine = get_engine()

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
