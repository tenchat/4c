from pydantic import BaseModel, EmailStr
from typing import Optional, List

class JobCreate(BaseModel):
    title: str
    city: Optional[str] = None
    province: Optional[str] = None
    industry: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    min_degree: Optional[int] = 1
    min_exp_years: Optional[int] = 0
    keywords: Optional[List[str]] = None
    description: Optional[str] = None


class JobStatusUpdate(BaseModel):
    status: int  # 0=暂停, 1=招聘中, 2=已结束

class JobResponse(BaseModel):
    job_id: str
    company_id: str
    title: str
    city: Optional[str]
    province: Optional[str]
    industry: Optional[str]
    min_salary: Optional[int]
    max_salary: Optional[int]
    min_degree: int
    min_exp_years: int
    keywords: Optional[List[str]]
    description: Optional[str]
    status: int
    published_at: Optional[str]
    created_at: str

class CompanyDashboardResponse(BaseModel):
    published_jobs: int
    received_resumes: int
    hired_count: int
    trend_data: List[dict]


class ProfileUpdateRequest(BaseModel):
    """企业档案更新请求（提交审核）"""
    company_name: str
    industry: Optional[str] = None
    city: Optional[str] = None
    size: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    contact: Optional[str] = None
    contact_phone: Optional[str] = None


class ProfilePendingResponse(BaseModel):
    """待审核信息响应"""
    pending_id: str
    company_id: str
    address: Optional[str]
    email: Optional[str]
    contact: Optional[str]
    contact_phone: Optional[str]
    status: str
    reject_reason: Optional[str]
    submitted_at: str
    reviewed_at: Optional[str]
