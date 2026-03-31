from app.schemas.common import ApiResponse, PageResult
from app.schemas.auth import LoginRequest, RegisterRequest, LoginResponse, TokenResponse, UserInfo
from app.schemas.student import StudentProfileResponse, StudentProfileUpdate, JobApplicationResponse
from app.schemas.school import SchoolDashboardResponse, WarningResponse
from app.schemas.admin import AdminDashboardResponse, CollegeEmploymentUpdate, ScarceTalentResponse
from app.schemas.company import JobCreate, JobResponse, CompanyDashboardResponse
from app.schemas.company_activity import ActivityCreate, ActivityUpdate, ActivityOut
from app.schemas.company_announcement import AnnouncementCreate, AnnouncementUpdate, AnnouncementOut
from app.schemas.ai import (
    EmploymentProfileRequest, EmploymentProfileResponse,
    ResumeAnalysisRequest, ResumeAnalysisResponse,
    DecisionRequest, DecisionResponse,
    WarningRequest, WarningResponse,
    QARequest, QAResponse
)

__all__ = [
    "ApiResponse",
    "PageResult",
    "LoginRequest",
    "RegisterRequest",
    "LoginResponse",
    "TokenResponse",
    "UserInfo",
    "StudentProfileResponse",
    "StudentProfileUpdate",
    "JobApplicationResponse",
    "SchoolDashboardResponse",
    "WarningResponse",
    "AdminDashboardResponse",
    "CollegeEmploymentUpdate",
    "ScarceTalentResponse",
    "JobCreate",
    "JobResponse",
    "CompanyDashboardResponse",
    "ActivityCreate",
    "ActivityUpdate",
    "ActivityOut",
    "AnnouncementCreate",
    "AnnouncementUpdate",
    "AnnouncementOut",
    "EmploymentProfileRequest",
    "EmploymentProfileResponse",
    "ResumeAnalysisRequest",
    "ResumeAnalysisResponse",
    "DecisionRequest",
    "DecisionResponse",
    "WarningRequest",
    "WarningResponse",
    "QARequest",
    "QAResponse",
]
