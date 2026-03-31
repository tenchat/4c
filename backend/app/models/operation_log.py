from sqlalchemy import Column, String, Integer, BigInteger, DateTime
from app.models.base import Base, TimestampMixin

class OperationLog(Base, TimestampMixin):
    __tablename__ = "operation_logs"

    log_id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_id = Column(String(36), index=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100))
    ip_address = Column(String(45))
    user_agent = Column(String(300))
    result = Column(Integer, default=1)  # 1成功 0失败
