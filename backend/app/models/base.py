from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime


def get_local_time():
    """获取本地时间（兼容Windows和Linux）"""
    return datetime.now(timezone(timedelta(hours=8))).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at = Column(DateTime, default=get_local_time, nullable=False)
    updated_at = Column(DateTime, default=get_local_time, onupdate=get_local_time, nullable=False)
