from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from app.models.base import Base, TimestampMixin

class RefreshToken(Base, TimestampMixin):
    __tablename__ = "refresh_tokens"

    token_id = Column(String(36), primary_key=True)
    account_id = Column(String(36), ForeignKey("accounts.account_id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), unique=True, nullable=False)
    device_info = Column(String(200))
    ip_address = Column(String(45))
    expires_at = Column(DateTime, nullable=False, index=True)
    revoked = Column(Boolean, nullable=False, default=False)
