from sqlalchemy import Column, String, Enum as SQLEnum, Integer, DateTime
from app.models.base import Base, TimestampMixin
import enum

class RoleType(str, enum.Enum):
    student = "student"
    school_admin = "school_admin"
    company_admin = "company_admin"
    system_admin = "system_admin"

class AccountStatus(int, enum.Enum):
    disabled = 0
    enabled = 1
    pending = 2  # 待审核

class Account(Base, TimestampMixin):
    __tablename__ = "accounts"

    account_id = Column(String(36), primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    real_name = Column(String(50))
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    role = Column(SQLEnum(RoleType), nullable=False, index=True)
    status = Column(Integer, nullable=False, default=1, index=True)
    login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
