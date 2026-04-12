from pydantic import BaseModel, Field
from typing import Optional, Literal

class LoginRequest(BaseModel):
    username: str
    password: str
    role: Literal["student", "school_admin", "company_admin", "system_admin"]

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    role: Literal["student", "school_admin", "company_admin"]
    student_no: Optional[str] = None       # 学生必填
    real_name: Optional[str] = None        # 学生姓名
    enterprise_name: Optional[str] = None  # 企业名称
    registration_code: Optional[str] = None # 学校管理员注册码

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserInfo(BaseModel):
    account_id: str
    username: str
    real_name: Optional[str]
    role: str
    status: int

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserInfo

class RefreshRequest(BaseModel):
    refresh_token: str
