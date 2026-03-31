from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str = ""  # Required: mysql+aiomysql://user:password@host:port/db
    REDIS_URL: str = "redis://localhost:6379/0"
    JWT_SECRET_KEY: str = ""  # Required: Set secure key in production
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    APP_ENV: str = "development"
    MINIMAX_API_KEY: str = ""
    MINIMAX_BASE_URL: str = "https://api.minimaxi.com/v1"
    DEEPSEEK_API_KEY: str = ""
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    DEFAULT_UNIVERSITY_ID: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
