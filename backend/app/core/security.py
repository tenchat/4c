from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
import redis.asyncio as redis
from app.core.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Redis client for token blacklist (lazy initialization)
_redis_client = None


async def get_redis_client():
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=1,  # 连接超时 1 秒
                socket_timeout=1,           # 操作超时 1 秒
            )
            await _redis_client.ping()
        except (redis.ConnectionError, redis.TimeoutError, Exception):
            _redis_client = None
    return _redis_client

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    # bcrypt 72-byte limit
    password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

async def verify_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if await is_token_blacklisted(token):
            return None
        return payload
    except JWTError:
        return None


async def is_token_blacklisted(token: str) -> bool:
    client = await get_redis_client()
    if client is None:
        return False
    try:
        return await client.exists(f"blacklist:{token}") > 0
    except (redis.ConnectionError, redis.TimeoutError, Exception):
        return False


async def add_token_to_blacklist(token: str, expires_in_seconds: int) -> None:
    client = await get_redis_client()
    if client is None:
        return
    try:
        await client.setex(f"blacklist:{token}", expires_in_seconds, "1")
    except (redis.ConnectionError, redis.TimeoutError, Exception):
        pass
