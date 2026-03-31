from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class AnnouncementCreate(BaseModel):
    title: str = Field(..., max_length=200)
    content: str
    target_major: Optional[str] = Field(None, max_length=200)
    target_degree: Optional[int] = None
    headcount: Optional[int] = None
    deadline: Optional[date] = None
    status: int = 1


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    target_major: Optional[str] = Field(None, max_length=200)
    target_degree: Optional[int] = None
    headcount: Optional[int] = None
    deadline: Optional[date] = None
    status: Optional[int] = None


class AnnouncementOut(BaseModel):
    announcement_id: str
    company_id: str
    title: str
    content: str
    target_major: Optional[str]
    target_degree: Optional[int]
    headcount: Optional[int]
    deadline: Optional[date]
    status: int
    published_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}