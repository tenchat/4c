from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date, time, datetime


class ActivityCreate(BaseModel):
    type: Literal["seminar", "job_fair"]
    title: str = Field(..., max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    activity_date: date
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    description: Optional[str] = None
    expected_num: Optional[int] = None


class ActivityUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    activity_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    description: Optional[str] = None
    status: Optional[int] = None
    actual_num: Optional[int] = None


class ActivityOut(BaseModel):
    activity_id: str
    company_id: str
    type: str
    title: str
    location: Optional[str]
    activity_date: date
    start_time: Optional[time]
    end_time: Optional[time]
    description: Optional[str]
    status: int
    expected_num: Optional[int]
    actual_num: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}