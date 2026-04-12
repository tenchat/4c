"""
RAG 服务 FastAPI 入口

高校学生就业信息平台 - AI 对话模块
端口：1145
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("=" * 50)
    logger.info("RAG 服务启动中...")
    logger.info("端口: 1145")
    logger.info("API 文档: http://localhost:1145/docs")
    logger.info("=" * 50)

    # 检查关键目录
    chroma_dir = Path("./chroma_db")
    if not chroma_dir.exists():
        logger.warning(f"ChromaDB 目录不存在: {chroma_dir.absolute()}")
        chroma_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"已创建 ChromaDB 目录: {chroma_dir.absolute()}")

    chat_history_dir = Path("./chat_history")
    if not chat_history_dir.exists():
        chat_history_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"已创建聊天历史目录: {chat_history_dir.absolute()}")

    logger.info("RAG 服务启动完成")

    yield

    # 关闭时
    logger.info("RAG 服务关闭中...")


# 创建 FastAPI 应用
app = FastAPI(
    title="RAG 知识库服务",
    description="高校学生就业信息平台 - AI 对话与知识库检索",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ==================== CORS 配置 ====================
# 从配置读取，允许具体域名
import config_data as config

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 全局异常处理 ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP 异常处理"""
    logger.warning(f"HTTP 异常: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理"""
    # 记录完整错误信息用于调试，但不向客户端暴露
    logger.error(f"全局异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "data": None,
        },
    )


# ==================== 路由注册 ====================

def register_routes() -> None:
    """注册 API 路由"""
    from api import qa, upload, history, job_recommend, resume_optimize, resume_parse

    # 注册路由
    app.include_router(qa.router, tags=["问答"])
    app.include_router(upload.router, tags=["知识库"])
    app.include_router(history.router, tags=["会话"])
    app.include_router(job_recommend.router, tags=["推荐"])
    app.include_router(resume_optimize.router, tags=["简历"])
    app.include_router(resume_parse.router, tags=["简历"])


# ==================== 根路径和健康检查 ====================

@app.get("/", tags=["Root"])
async def root() -> dict:
    """根路径"""
    return {
        "service": "RAG 知识库服务",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health() -> dict:
    """健康检查"""
    return {
        "status": "ok",
        "service": "rag",
    }


# ==================== 启动注册 ====================

# 启动时注册路由（避免循环导入）
register_routes()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=1145,
        reload=True,
        log_level="info",
    )
