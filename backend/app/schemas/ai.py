from pydantic import BaseModel
from typing import Optional, List

# TODO: AI - 接口完整定义，逻辑暂不实现

class EmploymentProfileRequest(BaseModel):
    major: str
    gpa: Optional[float] = None
    skills: List[str] = []
    target_city: Optional[str] = None
    internship: Optional[str] = None

class EmploymentProfileResponse(BaseModel):
    status: str = "not_implemented"
    message: str = "AI 分析功能开发中"
    score: Optional[int] = None
    professional_match: Optional[float] = None
    skill_match: Optional[float] = None
    location_demand: Optional[float] = None
    salary_expectation: Optional[int] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None

class ResumeAnalysisRequest(BaseModel):
    resume_text: str
    target_job: str

class ResumeAnalysisResponse(BaseModel):
    status: str = "not_implemented"
    message: str = "AI 简历分析功能开发中"
    ats_score: Optional[int] = None
    matched_keywords: Optional[List[str]] = None
    missing_keywords: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None

class DecisionRequest(BaseModel):
    target_city: str
    expected_salary: int
    study_months: int

class DecisionResponse(BaseModel):
    status: str = "not_implemented"
    message: str = "AI 决策分析功能开发中"
    employment_path: Optional[dict] = None
    study_path: Optional[dict] = None
    recommendation: Optional[str] = None

class WarningRequest(BaseModel):
    account_ids: List[str]

class WarningResponse(BaseModel):
    status: str = "not_implemented"
    message: str = "AI 预警功能开发中"
    generated: Optional[int] = None
    warnings: Optional[List[dict]] = None

class QARequest(BaseModel):
    question: str
    user_id: Optional[str] = None
    role_type: str = "student"
    session_id: Optional[str] = None

class QAResponse(BaseModel):
    status: str = "not_implemented"
    message: str = "AI 问答功能开发中"
    answer: Optional[str] = None
    sources: Optional[List[str]] = None
    intent: Optional[str] = None

class ResumeOptimizeRequest(BaseModel):
    resume_text: str
    target_job: str

class SuggestionItem(BaseModel):
    section: str
    original: str
    suggested: str
    reason: str

class MatchAnalysis(BaseModel):
    score: int
    strengths: List[str]
    weaknesses: List[str]

class ResumeOptimizeResponse(BaseModel):
    status: str = "not_implemented"
    message: str = "AI 简历优化功能开发中"
    optimized_resume: Optional[str] = None
    suggestions: Optional[List[SuggestionItem]] = None
    match_analysis: Optional[MatchAnalysis] = None
