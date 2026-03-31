from sqlalchemy import Column, String, Text, DateTime
from app.models.base import Base
from sqlalchemy import func

class SystemConfig(Base):
    __tablename__ = "system_configs"

    config_key = Column(String(100), primary_key=True)
    config_value = Column(Text)
    description = Column(String(200))
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
