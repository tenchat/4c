import redis.asyncio as redis
from app.core.config import get_settings

settings = get_settings()
_redis_client = None


async def get_redis():
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
