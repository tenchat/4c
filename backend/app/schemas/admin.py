from pydantic import BaseModel
from typing import Optional, List

class AdminDashboardResponse(BaseModel):
    total_students: int
    total_companies: int
    total_jobs: int
    overall_employment_rate: float
    recent_warnings: List[dict]

class CollegeEmploymentUpdate(BaseModel):
    graduate_nums: Optional[int] = None
    employed_nums: Optional[int] = None
    employment_rate: Optional[float] = None
    further_study_nums: Optional[int] = None
    further_study_rate: Optional[float] = None
    overseas_nums: Optional[int] = None
    overseas_rate: Optional[float] = None
    avg_salary: Optional[int] = None

class ScarceTalentResponse(BaseModel):
    talent_id: str
    province: str
    job_type: str
    shortage_level: int
    industry: Optional[str]
    data_year: Optional[int]
