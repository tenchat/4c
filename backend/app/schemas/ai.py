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


class InterviewPrepRequest(BaseModel):
    """面试准备请求"""
    job_title: str  # 目标岗位
    industry: Optional[str] = None  # 目标行业
    city: Optional[str] = None  # 目标城市
    major: Optional[str] = None  # 专业
    skills: List[str] = []  # 技能列表
    internship: Optional[str] = None  # 实习经历
    degree: Optional[int] = 1  # 学历: 1本科 2硕士 3博士
    salary_min: Optional[int] = None  # 期望最低薪资
    salary_max: Optional[int] = None  # 期望最高薪资
    interview_type: str = "technical"  # technical/hr/stress/group
    interview_round: str = "first"  # first/second/final
    company_type: str = "medium"  # large/medium/small/foreign/state
    action: str = "generate_questions"  # generate_questions/self_intro/questions_to_ask/salary_negotiation/follow_up_email/dressing_advice


class InterviewQuestion(BaseModel):
    """面试问题"""
    question: str
    answer_example: str
    key_points: List[str]
    notes: str


class InterviewPrepResponse(BaseModel):
    """面试准备响应"""
    status: str = "success"
    message: str = "success"
    questions: Optional[List[InterviewQuestion]] = None
    self_intro: Optional[str] = None
    questions_to_ask: Optional[List[str]] = None
    salary_tips: Optional[str] = None
    follow_up_email: Optional[str] = None
    dressing_tips: Optional[str] = None


class InterviewPracticeReviewRequest(BaseModel):
    """模拟练习点评请求"""
    question: str
    user_answer: str
    job_title: str


class InterviewPracticeReviewResponse(BaseModel):
    """模拟练习点评响应"""
    status: str = "success"
    message: str = "success"
    score: int
    strengths: List[str]
    weaknesses: List[str]
    improved_answer: str
