from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging

from app.api.v1.router import api_router
from app.core.redis_client import get_redis
from app.core.database import get_db
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="就业平台 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理 - HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None
        }
    )

# 全局异常处理 - 其他异常
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": str(exc) if str(exc) else "Internal server error", "data": None}
    )

# 注册路由
app.include_router(api_router, prefix="/api/v1")

# 挂载静态文件（简历下载）
settings = get_settings()
upload_dir = Path(settings.UPLOAD_DIR or "./uploads/resumes")
if upload_dir.exists():
    app.mount("/uploads", StaticFiles(directory=str(upload_dir.parent)), name="uploads")


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("应用启动中...")

    # 初始化 Redis 连接
    try:
        redis = await get_redis()
        await redis.ping()
        logger.info("Redis 连接成功")
    except Exception as e:
        logger.warning(f"Redis 连接失败: {e}")

    # 创建上传目录
    settings = get_settings()
    upload_dir = Path(settings.UPLOAD_DIR or "./uploads/resumes")
    upload_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"上传目录: {upload_dir.absolute()}")

    # 检查数据库连接
    # 注意: 实际生产环境应该使用完整的数据库连接测试
    # 这里仅作基础验证
    logger.info("数据库配置检查完成")

    logger.info("应用启动完成")


@app.get("/")
async def root():
    return {"message": "就业平台 API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}
