from pydantic import BaseModel
from typing import Optional, List

class StudentProfileResponse(BaseModel):
    profile_id: str
    account_id: str
    university_id: Optional[str]
    student_no: Optional[str]
    college: Optional[str]
    major: Optional[str]
    degree: int
    graduation_year: Optional[int]
    province_origin: Optional[str]
    gpa: Optional[float]
    skills: Optional[List[str]]
    internship: Optional[str]
    employment_status: int
    desire_city: Optional[str]
    desire_industry: Optional[str]
    desire_salary_min: Optional[int]
    desire_salary_max: Optional[int]
    cur_company: Optional[str]
    cur_city: Optional[str]
    cur_industry: Optional[str]
    cur_salary: Optional[int]
    resume_url: Optional[str]
    profile_complete: int

class StudentProfileUpdate(BaseModel):
    college: Optional[str] = None
    major: Optional[str] = None
    degree: Optional[int] = None
    graduation_year: Optional[int] = None
    province_origin: Optional[str] = None
    gpa: Optional[float] = None
    skills: Optional[List[str]] = None
    internship: Optional[str] = None
    employment_status: Optional[int] = None
    desire_city: Optional[str] = None
    desire_industry: Optional[str] = None
    desire_salary_min: Optional[int] = None
    desire_salary_max: Optional[int] = None
    cur_company: Optional[str] = None
    cur_city: Optional[str] = None
    cur_industry: Optional[str] = None
    cur_salary: Optional[int] = None
    resume_url: Optional[str] = None

class JobApplicationResponse(BaseModel):
    application_id: str
    job_id: str
    account_id: str
    status: int
    applied_at: str
