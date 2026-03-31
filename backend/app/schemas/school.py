from pydantic import BaseModel
from typing import Optional, List

class SchoolDashboardResponse(BaseModel):
    total_students: int
    employed_nums: int
    unemployed_nums: int
    further_study_nums: int
    abroad_nums: int
    employment_rate: float
    college_rankings: List[dict]
    warnings: List[dict]
    new_jobs_this_month: int

class WarningResponse(BaseModel):
    warning_id: str
    account_id: str
    warning_type: str
    level: int
    ai_suggestion: Optional[str]
    handled: bool
    created_at: str
