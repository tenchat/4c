from pydantic import BaseModel, Field
from typing import Optional, Literal

class LoginRequest(BaseModel):
    username: str
    password: str
    role: Literal["student", "school_admin", "company_admin", "system_admin"]

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    real_name: Optional[str] = None
    role: Literal["student", "school_admin", "company_admin"]

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
