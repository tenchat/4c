# 企业活动管理 + 管理端统计看板 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add company activity management (seminars + job fairs), recruitment announcements, and admin dashboard enterprise statistics to an existing employment platform.

**Architecture:** FastAPI backend with SQLAlchemy async ORM and Alembic migrations. Vue.js + TypeScript frontend using useTable hooks. Redis caching for statistics. Company data strictly isolated by `company_id`.

**Tech Stack:** Python/FastAPI, SQLAlchemy 2.0 async, Alembic, Redis, Vue 3 + TypeScript, Element Plus

---

## File Structure

### Backend (f:/repos/employment-backend/)

**New files:**
- `app/models/company_activity.py` — CompanyActivity ORM model
- `app/models/company_announcement.py` — CompanyAnnouncement ORM model
- `app/schemas/company_activity.py` — Activity Pydantic schemas
- `app/schemas/company_announcement.py` — Announcement Pydantic schemas
- `app/services/activity_service.py` — Activity business logic
- `app/services/announcement_service.py` — Announcement business logic
- `app/services/stats_service.py` — Enterprise stats with Redis cache
- `alembic/versions/<hash>_add_company_activities_and_announcements.py` — Migration

**Modified files:**
- `app/models/__init__.py` — Export new models
- `app/models/company.py` — Add `activities` and `announcements` relationships
- `app/schemas/__init__.py` — Export new schemas
- `app/api/v1/company.py` — Append activity and announcement routes
- `app/api/v1/admin.py` — Append `/admin/enterprise-stats` route

### Frontend (f:/repos/art-design-pro/)

**New files:**
- `src/api/company_activity.ts` — Activity API functions
- `src/api/company_announcement.ts` — Announcement API functions
- `src/api/stats.ts` — Enterprise stats API
- `src/views/company/activities/index.vue` — Activities management page
- `src/views/company/announcements/index.vue` — Announcements management page

**Modified files:**
- `src/router/modules/employment.ts` — Register new company routes
- `src/views/admin/dashboard/index.vue` — Append enterprise stats cards

---

## Phase 1: Database Migration

---

### Task 1: Create Alembic Migration

**Files:**
- Create: `alembic/versions/<hash>_add_company_activities_and_announcements.py`

- [ ] **Step 1: Check current alembic heads**

Run: `cd f:/repos/employment-backend && alembic heads`
Output: Shows the current head revision (e.g., `20260330_add_job_description_indexes`)

- [ ] **Step 2: Generate migration**

Run: `cd f:/repos/employment-backend && alembic revision --autogenerate -m "add_company_activities_and_announcements"`
Expected: Generates new migration file in `alembic/versions/`

- [ ] **Step 3: Edit the generated migration to add proper table definitions**

Read the generated file first, then replace its contents with:

```python
"""add_company_activities_and_announcements

Revision ID: <generated_hash>
Revises: <parent_revision>
Create Date: 2026-03-30
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = '<generated_hash>'
down_revision = '<parent_revision>'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'company_activities',
        sa.Column('activity_id', sa.String(36), primary_key=True, server_default=sa.text('UUID()')),
        sa.Column('company_id', sa.String(36), sa.ForeignKey('companies.company_id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.Enum('seminar', 'job_fair', name='activity_type_enum', create_type=False), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('location', sa.String(200), nullable=True),
        sa.Column('activity_date', sa.Date, nullable=False),
        sa.Column('start_time', sa.Time, nullable=True),
        sa.Column('end_time', sa.Time, nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('status', sa.SmallInteger, nullable=False, server_default='1'),
        sa.Column('expected_num', sa.Integer, nullable=True),
        sa.Column('actual_num', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_company_activities_company_id', 'company_activities', ['company_id'])
    op.create_index('ix_company_activities_type', 'company_activities', ['type'])
    op.create_index('ix_company_activities_activity_date', 'company_activities', ['activity_date'])
    op.create_index('ix_company_activities_status', 'company_activities', ['status'])

    op.create_table(
        'company_announcements',
        sa.Column('announcement_id', sa.String(36), primary_key=True, server_default=sa.text('UUID()')),
        sa.Column('company_id', sa.String(36), sa.ForeignKey('companies.company_id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('target_major', sa.String(200), nullable=True),
        sa.Column('target_degree', sa.SmallInteger, nullable=True),
        sa.Column('headcount', sa.Integer, nullable=True),
        sa.Column('deadline', sa.Date, nullable=True),
        sa.Column('status', sa.SmallInteger, nullable=False, server_default='1'),
        sa.Column('published_at', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_company_announcements_company_id', 'company_announcements', ['company_id'])
    op.create_index('ix_company_announcements_status', 'company_announcements', ['status'])


def downgrade() -> None:
    op.drop_table('company_announcements')
    op.drop_table('company_activities')
    op.execute('DROP TYPE IF EXISTS activity_type_enum')
```

- [ ] **Step 4: Apply migration**

Run: `cd f:/repos/employment-backend && alembic upgrade head`
Expected: `Running upgrade  ... -> <new_revision>`

- [ ] **Step 5: Verify tables**

Run: `cd f:/repos/employment-backend && python -c "from app.models.company_activity import CompanyActivity; from app.models.company_announcement import CompanyAnnouncement; print('Models import OK')"`
Expected: `Models import OK`

---

## Phase 2: Backend Models

---

### Task 2: SQLAlchemy Models

**Files:**
- Create: `app/models/company_activity.py`
- Create: `app/models/company_announcement.py`
- Modify: `app/models/company.py`

- [ ] **Step 1: Write CompanyActivity model**

```python
# app/models/company_activity.py
import enum
from datetime import date, time
from sqlalchemy import Column, String, Text, Date, Time, Integer, SmallInteger, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class ActivityType(str, enum.Enum):
    seminar = "seminar"
    job_fair = "job_fair"


class ActivityStatus(int, enum.Enum):
    ongoing = 1       # 进行中/待举办
    ended = 2         # 已结束
    cancelled = 0     # 已取消


class CompanyActivity(Base, TimestampMixin):
    __tablename__ = "company_activities"

    activity_id = Column(String(36), primary_key=True)
    company_id = Column(String(36), ForeignKey("companies.company_id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(SQLEnum(ActivityType, name="activity_type_enum", create_type=False), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    location = Column(String(200), nullable=True)
    activity_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(SmallInteger, nullable=False, default=1, index=True)
    expected_num = Column(Integer, nullable=True)
    actual_num = Column(Integer, nullable=True)

    company = relationship("Company", back_populates="activities")
```

- [ ] **Step 2: Write CompanyAnnouncement model**

```python
# app/models/company_announcement.py
import enum
from sqlalchemy import Column, String, Text, Date, Integer, SmallInteger, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class AnnouncementStatus(int, enum.Enum):
    draft = 0        # 草稿
    published = 1    # 发布中
    expired = 2     # 已过期


class CompanyAnnouncement(Base, TimestampMixin):
    __tablename__ = "company_announcements"

    announcement_id = Column(String(36), primary_key=True)
    company_id = Column(String(36), ForeignKey("companies.company_id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    target_major = Column(String(200), nullable=True)
    target_degree = Column(SmallInteger, nullable=True)
    headcount = Column(Integer, nullable=True)
    deadline = Column(Date, nullable=True)
    status = Column(SmallInteger, nullable=False, default=1, index=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default="CURRENT_TIMESTAMP", nullable=False)
    updated_at = Column(DateTime, server_default="CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP", nullable=False)

    company = relationship("Company", back_populates="announcements")
```

- [ ] **Step 3: Update Company model**

Read `app/models/company.py` first, then add:

```python
from app.models.company_activity import CompanyActivity
from app.models.company_announcement import CompanyAnnouncement

# Inside Company class, add these two relationships:
activities = relationship(
    "CompanyActivity",
    back_populates="company",
    cascade="all, delete-orphan"
)
announcements = relationship(
    "CompanyAnnouncement",
    back_populates="company",
    cascade="all, delete-orphan"
)
```

- [ ] **Step 4: Update models __init__.py**

Read `app/models/__init__.py`, then add exports:

```python
from app.models.company_activity import CompanyActivity, ActivityType, ActivityStatus
from app.models.company_announcement import CompanyAnnouncement, AnnouncementStatus
```

- [ ] **Step 5: Verify models**

Run: `cd f:/repos/employment-backend && python -c "from app.models.company_activity import CompanyActivity; from app.models.company_announcement import CompanyAnnouncement; print('OK')"`
Expected: OK

- [ ] **Step 6: Commit**

```bash
cd f:/repos/employment-backend
git add app/models/company_activity.py app/models/company_announcement.py app/models/company.py app/models/__init__.py alembic/versions/<new_migration>.py
git commit -m "feat(backend): add CompanyActivity and CompanyAnnouncement models and migration"
```

---

## Phase 3: Pydantic Schemas

---

### Task 3: Activity Schemas

**Files:**
- Create: `app/schemas/company_activity.py`

- [ ] **Step 1: Write activity schemas**

```python
# app/schemas/company_activity.py
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
```

- [ ] **Step 2: Update schemas __init__.py**

Read `app/schemas/__init__.py` and add:

```python
from app.schemas.company_activity import ActivityCreate, ActivityUpdate, ActivityOut
```

- [ ] **Step 3: Commit**

```bash
cd f:/repos/employment-backend
git add app/schemas/company_activity.py app/schemas/__init__.py
git commit -m "feat(backend): add activity schemas"
```

---

### Task 4: Announcement Schemas

**Files:**
- Create: `app/schemas/company_announcement.py`

- [ ] **Step 1: Write announcement schemas**

```python
# app/schemas/company_announcement.py
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
```

- [ ] **Step 2: Update schemas __init__.py**

Read `app/schemas/__init__.py` and add:

```python
from app.schemas.company_announcement import AnnouncementCreate, AnnouncementUpdate, AnnouncementOut
```

- [ ] **Step 3: Commit**

```bash
cd f:/repos/employment-backend
git add app/schemas/company_announcement.py app/schemas/__init__.py
git commit -m "feat(backend): add announcement schemas"
```

---

## Phase 4: Service Layer (TDD)

---

### Task 5: Activity Service (TDD)

**Files:**
- Create: `app/services/activity_service.py`
- Create: `tests/test_company_activities.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_company_activities.py
import pytest
import uuid
from datetime import date

# Use the existing test DB setup from the project if available
# This test file should work with the existing async test infrastructure

@pytest.mark.asyncio
async def test_create_activity_returns_out_model(db_session, company):
    """创建活动返回正确的模型"""
    from app.services.activity_service import ActivityService
    from app.schemas.company_activity import ActivityCreate

    svc = ActivityService(db_session)
    result = await svc.create_activity(company.company_id, ActivityCreate(
        type="seminar",
        title="Test Seminar",
        activity_date=date(2026, 5, 1),
        location="Room 101"
    ))
    assert result.title == "Test Seminar"
    assert result.type == "seminar"


@pytest.mark.asyncio
async def test_list_activities_only_returns_own(db_session, company):
    """企业只能看到自己的活动"""
    from app.services.activity_service import ActivityService
    from app.schemas.company_activity import ActivityCreate

    svc = ActivityService(db_session)
    await svc.create_activity(company.company_id, ActivityCreate(
        type="seminar", title="My Seminar", activity_date=date(2026, 5, 1)
    ))

    # Create another company's activity
    other_company = await create_test_company(db_session, "Other Corp")
    await svc.create_activity(other_company.company_id, ActivityCreate(
        type="job_fair", title="Other Fair", activity_date=date(2026, 6, 1)
    ))

    page = await svc.list_activities(company.company_id, page=1, page_size=20)
    assert page["total"] == 1
    assert page["list"][0].title == "My Seminar"


@pytest.mark.asyncio
async def test_get_activity_404_for_other_company(db_session, company):
    """获取其他企业的活动返回404"""
    from app.services.activity_service import ActivityService
    from app.schemas.company_activity import ActivityCreate
    from fastapi import HTTPException

    svc = ActivityService(db_session)
    created = await svc.create_activity(company.company_id, ActivityCreate(
        type="seminar", title="My Seminar", activity_date=date(2026, 5, 1)
    ))

    other_company = await create_test_company(db_session, "Other Corp")

    with pytest.raises(HTTPException) as exc_info:
        await svc.get_activity(created.activity_id, other_company.company_id)
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_activity_is_soft_delete(db_session, company):
    """删除是软删除，status变为0"""
    from app.services.activity_service import ActivityService
    from app.schemas.company_activity import ActivityCreate

    svc = ActivityService(db_session)
    created = await svc.create_activity(company.company_id, ActivityCreate(
        type="seminar", title="My Seminar", activity_date=date(2026, 5, 1)
    ))

    await svc.delete_activity(created.activity_id, company.company_id)

    # Should not appear in normal list
    page = await svc.list_activities(company.company_id, page=1, page_size=20)
    assert page["total"] == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd f:/repos/employment-backend && pytest tests/test_company_activities.py -v --tb=short 2>&1 | head -50`
Expected: FAIL (service not implemented yet)

- [ ] **Step 3: Implement ActivityService (minimal)**

```python
# app/services/activity_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional, Literal
from datetime import date
from fastapi import HTTPException
from app.models.company_activity import CompanyActivity, ActivityType, ActivityStatus
from app.schemas.company_activity import ActivityCreate, ActivityUpdate, ActivityOut
from app.schemas.common import PageResult


class ActivityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_activities(
        self,
        company_id: str,
        type: Optional[str] = None,
        year: Optional[int] = None,
        status: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        conditions = [CompanyActivity.company_id == company_id]
        # Exclude soft-deleted (status=0) by default in normal list
        if status is not None:
            conditions.append(CompanyActivity.status == status)
        else:
            conditions.append(CompanyActivity.status != ActivityStatus.cancelled.value)

        if type:
            conditions.append(CompanyActivity.type == type)
        if year:
            conditions.append(func.year(CompanyActivity.activity_date) == year)

        count_result = await self.db.execute(
            select(func.count()).select_from(CompanyActivity).where(and_(*conditions))
        )
        total = count_result.scalar() or 0

        query = (
            select(CompanyActivity)
            .where(and_(*conditions))
            .order_by(CompanyActivity.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = (await self.db.execute(query)).scalars().all()

        return {
            "list": [ActivityOut.model_validate(r) for r in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def get_activity(self, activity_id: str, company_id: str) -> ActivityOut:
        result = await self.db.execute(
            select(CompanyActivity).where(
                and_(
                    CompanyActivity.activity_id == activity_id,
                    CompanyActivity.company_id == company_id,
                )
            )
        )
        row = result.scalar_one_or_none()
        if not row:
            raise HTTPException(status_code=404, detail="Activity not found")
        return ActivityOut.model_validate(row)

    async def create_activity(self, company_id: str, data: ActivityCreate) -> ActivityOut:
        row = CompanyActivity(
            company_id=company_id,
            type=ActivityType(data.type),
            title=data.title,
            location=data.location,
            activity_date=data.activity_date,
            start_time=data.start_time,
            end_time=data.end_time,
            description=data.description,
            expected_num=data.expected_num,
        )
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return ActivityOut.model_validate(row)

    async def update_activity(
        self, activity_id: str, company_id: str, data: ActivityUpdate
    ) -> ActivityOut:
        row = await self._get_owned(activity_id, company_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(row, key, value)
        await self.db.commit()
        await self.db.refresh(row)
        return ActivityOut.model_validate(row)

    async def delete_activity(self, activity_id: str, company_id: str) -> None:
        row = await self._get_owned(activity_id, company_id)
        row.status = ActivityStatus.cancelled.value
        await self.db.commit()

    async def _get_owned(self, activity_id: str, company_id: str) -> CompanyActivity:
        result = await self.db.execute(
            select(CompanyActivity).where(
                and_(
                    CompanyActivity.activity_id == activity_id,
                    CompanyActivity.company_id == company_id,
                )
            )
        )
        row = result.scalar_one_or_none()
        if not row:
            raise HTTPException(status_code=404, detail="Activity not found")
        return row
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd f:/repos/employment-backend && pytest tests/test_company_activities.py -v --tb=short`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd f:/repos/employment-backend
git add app/services/activity_service.py tests/test_company_activities.py
git commit -m "feat(backend): add ActivityService with TDD"
```

---

### Task 6: Announcement Service (TDD)

**Files:**
- Create: `app/services/announcement_service.py`
- Create: `tests/test_company_announcements.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_company_announcements.py
import pytest
import uuid
from datetime import date, datetime

@pytest.mark.asyncio
async def test_create_announcement_with_status_1_sets_published_at(db_session, company):
    """发布状态(status=1)时自动设置published_at"""
    from app.services.announcement_service import AnnouncementService
    from app.schemas.company_announcement import AnnouncementCreate

    svc = AnnouncementService(db_session)
    result = await svc.create_announcement(company.company_id, AnnouncementCreate(
        title="Hiring Now", content="We are hiring software engineers", status=1
    ))
    assert result.published_at is not None


@pytest.mark.asyncio
async def test_create_announcement_with_status_0_no_published_at(db_session, company):
    """草稿状态(status=0)时不设置published_at"""
    from app.services.announcement_service import AnnouncementService
    from app.schemas.company_announcement import AnnouncementCreate

    svc = AnnouncementService(db_session)
    result = await svc.create_announcement(company.company_id, AnnouncementCreate(
        title="Draft", content="Work in progress", status=0
    ))
    assert result.published_at is None


@pytest.mark.asyncio
async def test_company_cannot_see_other_company_announcements(db_session, company):
    """企业不能看到其他企业的公告"""
    from app.services.announcement_service import AnnouncementService
    from app.schemas.company_announcement import AnnouncementCreate

    svc = AnnouncementService(db_session)
    await svc.create_announcement(company.company_id, AnnouncementCreate(
        title="My Announcement", content="Content", status=1
    ))

    other_company = await create_test_company(db_session, "Other Corp")
    await svc.create_announcement(other_company.company_id, AnnouncementCreate(
        title="Other", content="Other content", status=1
    ))

    page = await svc.list_announcements(company.company_id, page=1, page_size=20)
    assert page["total"] == 1
    assert page["list"][0].title == "My Announcement"


@pytest.mark.asyncio
async def test_delete_is_soft_delete(db_session, company):
    """删除是软删除"""
    from app.services.announcement_service import AnnouncementService
    from app.schemas.company_announcement import AnnouncementCreate

    svc = AnnouncementService(db_session)
    created = await svc.create_announcement(company.company_id, AnnouncementCreate(
        title="To Delete", content="Content", status=1
    ))

    await svc.delete_announcement(created.announcement_id, company.company_id)

    page = await svc.list_announcements(company.company_id, page=1, page_size=20)
    assert page["total"] == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd f:/repos/employment-backend && pytest tests/test_company_announcements.py -v --tb=short 2>&1 | head -50`
Expected: FAIL

- [ ] **Step 3: Implement AnnouncementService (minimal)**

```python
# app/services/announcement_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
from datetime import date, datetime
from fastapi import HTTPException
from app.models.company_announcement import CompanyAnnouncement, AnnouncementStatus
from app.schemas.company_announcement import AnnouncementCreate, AnnouncementUpdate, AnnouncementOut
from app.schemas.common import PageResult


class AnnouncementService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_announcements(
        self,
        company_id: str,
        status: Optional[int] = None,
        year: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        conditions = [CompanyAnnouncement.company_id == company_id]
        if status is not None:
            conditions.append(CompanyAnnouncement.status == status)
        if year:
            conditions.append(func.year(CompanyAnnouncement.published_at) == year)

        count_result = await self.db.execute(
            select(func.count()).select_from(CompanyAnnouncement).where(and_(*conditions))
        )
        total = count_result.scalar() or 0

        query = (
            select(CompanyAnnouncement)
            .where(and_(*conditions))
            .order_by(CompanyAnnouncement.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = (await self.db.execute(query)).scalars().all()

        return {
            "list": [AnnouncementOut.model_validate(r) for r in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def get_announcement(self, announcement_id: str, company_id: str) -> AnnouncementOut:
        row = await self._get_owned(announcement_id, company_id)
        return AnnouncementOut.model_validate(row)

    async def create_announcement(
        self, company_id: str, data: AnnouncementCreate
    ) -> AnnouncementOut:
        published_at = datetime.utcnow() if data.status == 1 else None
        row = CompanyAnnouncement(
            company_id=company_id,
            title=data.title,
            content=data.content,
            target_major=data.target_major,
            target_degree=data.target_degree,
            headcount=data.headcount,
            deadline=data.deadline,
            status=data.status,
            published_at=published_at,
        )
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return AnnouncementOut.model_validate(row)

    async def update_announcement(
        self, announcement_id: str, company_id: str, data: AnnouncementUpdate
    ) -> AnnouncementOut:
        row = await self._get_owned(announcement_id, company_id)
        update_data = data.model_dump(exclude_unset=True)
        # If publishing (status=1) and not yet published, set published_at
        if update_data.get("status") == 1 and row.published_at is None:
            update_data["published_at"] = datetime.utcnow()
        for key, value in update_data.items():
            setattr(row, key, value)
        await self.db.commit()
        await self.db.refresh(row)
        return AnnouncementOut.model_validate(row)

    async def delete_announcement(self, announcement_id: str, company_id: str) -> None:
        row = await self._get_owned(announcement_id, company_id)
        row.status = AnnouncementStatus.draft.value
        await self.db.commit()

    async def _get_owned(self, announcement_id: str, company_id: str) -> CompanyAnnouncement:
        result = await self.db.execute(
            select(CompanyAnnouncement).where(
                and_(
                    CompanyAnnouncement.announcement_id == announcement_id,
                    CompanyAnnouncement.company_id == company_id,
                )
            )
        )
        row = result.scalar_one_or_none()
        if not row:
            raise HTTPException(status_code=404, detail="Announcement not found")
        return row
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd f:/repos/employment-backend && pytest tests/test_company_announcements.py -v --tb=short`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd f:/repos/employment-backend
git add app/services/announcement_service.py tests/test_company_announcements.py
git commit -m "feat(backend): add AnnouncementService with TDD"
```

---

### Task 7: Stats Service (TDD)

**Files:**
- Create: `app/services/stats_service.py`
- Create: `tests/test_admin_stats.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_admin_stats.py
import pytest
from unittest.mock import AsyncMock
import json

@pytest.mark.asyncio
async def test_stats_returns_all_seven_fields():
    """返回全部7个统计字段"""
    from app.services.stats_service import StatsService

    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None  # Cache miss

    # Mock all count queries to return 0
    async def mock_execute(q):
        m = AsyncMock()
        m.scalar.return_value = 0
        return m
    mock_db.execute = mock_execute

    svc = StatsService()
    result = await svc.get_enterprise_stats(mock_db, mock_redis, year=2026)

    assert "total_companies" in result
    assert "new_companies_this_year" in result
    assert "job_demand_this_year" in result
    assert "seminars_this_year" in result
    assert "job_fairs_this_year" in result
    assert "announcements_this_year" in result
    assert "positions_this_year" in result
    assert result["year"] == 2026


@pytest.mark.asyncio
async def test_stats_cache_hit_returns_cached():
    """缓存命中时直接返回，不查数据库"""
    from app.services.stats_service import StatsService

    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    cached = {"total_companies": 10, "year": 2026, "new_companies_this_year": 2,
              "job_demand_this_year": 5, "seminars_this_year": 3, "job_fairs_this_year": 2,
              "announcements_this_year": 8, "positions_this_year": 12}
    mock_redis.get.return_value = json.dumps(cached)

    svc = StatsService()
    result = await svc.get_enterprise_stats(mock_db, mock_redis, year=2026)

    assert result["total_companies"] == 10
    mock_db.execute.assert_not_called()


@pytest.mark.asyncio
async def test_stats_year_defaults_to_current():
    """year为None时默认当前年"""
    from app.services.stats_service import StatsService
    from datetime import datetime

    mock_db = AsyncMock()
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    async def mock_execute(q):
        m = AsyncMock()
        m.scalar.return_value = 0
        return m
    mock_db.execute = mock_execute

    svc = StatsService()
    result = await svc.get_enterprise_stats(mock_db, mock_redis, year=None)

    assert result["year"] == datetime.utcnow().year
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd f:/repos/employment-backend && pytest tests/test_admin_stats.py -v --tb=short 2>&1 | head -30`
Expected: FAIL

- [ ] **Step 3: Implement StatsService (minimal)**

```python
# app/services/stats_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, text
from typing import Optional
import json
from datetime import datetime

CACHE_KEY = "stats:enterprise:{year}"
CACHE_TTL = 1800  # 30 minutes


class StatsService:
    async def get_enterprise_stats(
        self,
        db: AsyncSession,
        redis_client,
        year: Optional[int] = None,
    ) -> dict:
        if year is None:
            year = datetime.utcnow().year

        cache_key = CACHE_KEY.format(year=year)

        # Try cache first
        try:
            cached = await redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception:
            pass  # Redis unavailable

        # Build queries - use text() for raw SQL to work across MySQL/SQLite
        async def count_q(table, *conditions):
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            q = text(f"SELECT COUNT(*) FROM {table} WHERE {where_clause}")
            result = await db.execute(q)
            return result.scalar() or 0

        # total_companies: verified=TRUE
        total_companies = await count_q("companies", "verified = 1")

        # new_companies_this_year: verified=TRUE AND YEAR(created_at)=year
        new_companies_this_year = await count_q(
            "companies",
            f"verified = 1 AND strftime('%Y', created_at) = '{year}'"
        ) if db.bind.dialect.name == "sqlite" else await count_q(
            "companies",
            f"verified = 1 AND YEAR(created_at) = {year}"
        )

        # job_demand_this_year: status!=2 AND YEAR(created_at)=year
        if db.bind.dialect.name == "sqlite":
            job_demand_this_year = await count_q(
                "job_descriptions",
                f"status != 2 AND strftime('%Y', created_at) = '{year}'"
            )
            seminars_this_year = await count_q(
                "company_activities",
                f"type = 'seminar' AND strftime('%Y', activity_date) = '{year}'"
            )
            job_fairs_this_year = await count_q(
                "company_activities",
                f"type = 'job_fair' AND strftime('%Y', activity_date) = '{year}'"
            )
            announcements_this_year = await count_q(
                "company_announcements",
                f"strftime('%Y', published_at) = '{year}'"
            )
            positions_this_year_q = text(
                f"SELECT COUNT(DISTINCT title) FROM job_descriptions WHERE strftime('%Y', created_at) = '{year}'"
            )
        else:
            job_demand_this_year = await count_q(
                "job_descriptions",
                f"status != 2 AND YEAR(created_at) = {year}"
            )
            seminars_this_year = await count_q(
                "company_activities",
                f"type = 'seminar' AND YEAR(activity_date) = {year}"
            )
            job_fairs_this_year = await count_q(
                "company_activities",
                f"type = 'job_fair' AND YEAR(activity_date) = {year}"
            )
            announcements_this_year = await count_q(
                "company_announcements",
                f"YEAR(published_at) = {year}"
            )
            positions_this_year_q = text(
                f"SELECT COUNT(DISTINCT title) FROM job_descriptions WHERE YEAR(created_at) = {year}"
            )

        result = {
            "total_companies": total_companies,
            "new_companies_this_year": new_companies_this_year,
            "job_demand_this_year": job_demand_this_year,
            "seminars_this_year": seminars_this_year,
            "job_fairs_this_year": job_fairs_this_year,
            "announcements_this_year": announcements_this_year,
            "positions_this_year": positions_this_year,
            "year": year,
        }

        # Cache result
        try:
            await redis_client.setex(cache_key, CACHE_TTL, json.dumps(result))
        except Exception:
            pass  # Redis unavailable

        return result
```

Wait - the `positions_this_year` variable is referenced before assignment. Let me fix:

```python
        if db.bind.dialect.name == "sqlite":
            # ... existing code ...
        else:
            # ... existing code ...

        positions_this_year = (await db.execute(positions_this_year_q)).scalar() or 0
```

Actually, the `positions_this_year_q` is only defined inside the if/else branches. Let me restructure the service to avoid this issue:

```python
        # ... queries above ...

        positions_this_year = (await db.execute(positions_this_year_q)).scalar() or 0

        result = { ... }
```

The positions_this_year_q is referenced but not yet defined at the point of use. Let me write the full service correctly:

```python
# app/services/stats_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, text
from typing import Optional
import json
from datetime import datetime

CACHE_KEY = "stats:enterprise:{year}"
CACHE_TTL = 1800  # 30 minutes


class StatsService:
    async def get_enterprise_stats(
        self,
        db: AsyncSession,
        redis_client,
        year: Optional[int] = None,
    ) -> dict:
        if year is None:
            year = datetime.utcnow().year

        cache_key = CACHE_KEY.format(year=year)

        try:
            cached = await redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception:
            pass

        dialect = db.bind.dialect.name
        is_sqlite = dialect == "sqlite"
        year_expr = f"strftime('%Y', created_at) = '{year}'" if is_sqlite else f"YEAR(created_at) = {year}"
        year_date_expr = f"strftime('%Y', activity_date) = '{year}'" if is_sqlite else f"YEAR(activity_date) = {year}"
        year_published_expr = f"strftime('%Y', published_at) = '{year}'" if is_sqlite else f"YEAR(published_at) = {year}"

        async def count_q(table: str, *conditions) -> int:
            where = " AND ".join(conditions) if conditions else "1=1"
            q = text(f"SELECT COUNT(*) FROM {table} WHERE {where}")
            result = await db.execute(q)
            return result.scalar() or 0

        total_companies = await count_q("companies", "verified = 1")
        new_companies_this_year = await count_q("companies", f"verified = 1 AND {year_expr}")
        job_demand_this_year = await count_q("job_descriptions", f"status != 2 AND {year_expr}")
        seminars_this_year = await count_q("company_activities", f"type = 'seminar' AND {year_date_expr}")
        job_fairs_this_year = await count_q("company_activities", f"type = 'job_fair' AND {year_date_expr}")
        announcements_this_year = await count_q("company_announcements", year_published_expr)

        positions_title_q = text(
            f"SELECT COUNT(DISTINCT title) FROM job_descriptions WHERE {year_expr}"
        )
        positions_this_year = (await db.execute(positions_title_q)).scalar() or 0

        result = {
            "total_companies": total_companies,
            "new_companies_this_year": new_companies_this_year,
            "job_demand_this_year": job_demand_this_year,
            "seminars_this_year": seminars_this_year,
            "job_fairs_this_year": job_fairs_this_year,
            "announcements_this_year": announcements_this_year,
            "positions_this_year": positions_this_year,
            "year": year,
        }

        try:
            await redis_client.setex(cache_key, CACHE_TTL, json.dumps(result))
        except Exception:
            pass

        return result
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd f:/repos/employment-backend && pytest tests/test_admin_stats.py -v --tb=short`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd f:/repos/employment-backend
git add app/services/stats_service.py tests/test_admin_stats.py
git commit -m "feat(backend): add StatsService with Redis cache"
```

---

## Phase 5: API Routes

---

### Task 8: Company Activity & Announcement Routes

**Files:**
- Modify: `app/api/v1/company.py`

- [ ] **Step 1: Read existing company.py**

Read `app/api/v1/company.py` fully to understand current structure.

- [ ] **Step 2: Add new routes**

Append to `app/api/v1/company.py`:

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.company import Company
from app.services.activity_service import ActivityService
from app.services.announcement_service import AnnouncementService
from app.schemas.company_activity import (
    ActivityCreate, ActivityUpdate, ActivityOut
)
from app.schemas.company_announcement import (
    AnnouncementCreate, AnnouncementUpdate, AnnouncementOut
)
from app.schemas.common import PageResult

# --- Activity routes ---

@router.get("/activities")
async def list_activities(
    type: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    status: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_id = await get_company_id(db, payload.get("sub"))
    svc = ActivityService(db)
    return await svc.list_activities(company_id, type=type, year=year, status=status, page=page, page_size=page_size)


@router.post("/activities", status_code=201)
async def create_activity(
    data: ActivityCreate,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_id = await get_company_id(db, payload.get("sub"))
    svc = ActivityService(db)
    return await svc.create_activity(company_id, data)


@router.get("/activities/{activity_id}", response_model=ActivityOut)
async def get_activity(
    activity_id: str,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_id = await get_company_id(db, payload.get("sub"))
    svc = ActivityService(db)
    return await svc.get_activity(activity_id, company_id)


@router.put("/activities/{activity_id}", response_model=ActivityOut)
async def update_activity(
    activity_id: str,
    data: ActivityUpdate,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_id = await get_company_id(db, payload.get("sub"))
    svc = ActivityService(db)
    return await svc.update_activity(activity_id, company_id, data)


@router.delete("/activities/{activity_id}", status_code=204)
async def delete_activity(
    activity_id: str,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_id = await get_company_id(db, payload.get("sub"))
    svc = ActivityService(db)
    await svc.delete_activity(activity_id, company_id)


# --- Announcement routes ---

@router.get("/announcements")
async def list_announcements(
    status: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_id = await get_company_id(db, payload.get("sub"))
    svc = AnnouncementService(db)
    return await svc.list_announcements(company_id, status=status, year=year, page=page, page_size=page_size)


@router.post("/announcements", status_code=201)
async def create_announcement(
    data: AnnouncementCreate,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_id = await get_company_id(db, payload.get("sub"))
    svc = AnnouncementService(db)
    return await svc.create_announcement(company_id, data)


@router.get("/announcements/{announcement_id}", response_model=AnnouncementOut)
async def get_announcement(
    announcement_id: str,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_id = await get_company_id(db, payload.get("sub"))
    svc = AnnouncementService(db)
    return await svc.get_announcement(announcement_id, company_id)


@router.put("/announcements/{announcement_id}", response_model=AnnouncementOut)
async def update_announcement(
    announcement_id: str,
    data: AnnouncementUpdate,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_id = await get_company_id(db, payload.get("sub"))
    svc = AnnouncementService(db)
    return await svc.update_announcement(announcement_id, company_id, data)


@router.delete("/announcements/{announcement_id}", status_code=204)
async def delete_announcement(
    announcement_id: str,
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    company_id = await get_company_id(db, payload.get("sub"))
    svc = AnnouncementService(db)
    await svc.delete_announcement(announcement_id, company_id)
```

- [ ] **Step 3: Verify routes compile**

Run: `cd f:/repos/employment-backend && python -c "from app.api.v1.company import router; print('OK')"`
Expected: OK

- [ ] **Step 4: Commit**

```bash
cd f:/repos/employment-backend
git add app/api/v1/company.py
git commit -m "feat(backend): add company activity and announcement routes"
```

---

### Task 9: Admin Enterprise Stats Route

**Files:**
- Modify: `app/api/v1/admin.py`

- [ ] **Step 1: Read existing admin.py**

Read `app/api/v1/admin.py` to understand the current dashboard route.

- [ ] **Step 2: Add enterprise-stats endpoint**

Append to `app/api/v1/admin.py`:

```python
from app.services.stats_service import StatsService
from app.core.redis_client import get_redis


@router.get("/enterprise-stats")
async def get_enterprise_stats(
    year: Optional[int] = Query(None),
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取企业相关聚合统计数据（管理端）"""
    svc = StatsService()
    redis = await get_redis()
    if redis is None:
        # Create a dummy redis-like object for when Redis is unavailable
        class DummyRedis:
            async def get(self, key):
                return None
            async def setex(self, key, ttl, value):
                pass
        redis = DummyRedis()
    return await svc.get_enterprise_stats(db, redis, year)
```

- [ ] **Step 3: Verify routes compile**

Run: `cd f:/repos/employment-backend && python -c "from app.api.v1.admin import router; print('OK')"`
Expected: OK

- [ ] **Step 4: Commit**

```bash
cd f:/repos/employment-backend
git add app/api/v1/admin.py
git commit -m "feat(backend): add admin enterprise-stats endpoint"
```

---

## Phase 6: Frontend

---

### Task 10: Frontend API Layer

**Files:**
- Create: `src/api/company_activity.ts`
- Create: `src/api/company_announcement.ts`
- Create: `src/api/stats.ts`

- [ ] **Step 1: Create company_activity.ts**

```typescript
// src/api/company_activity.ts
import http from '@/utils/http'

export interface Activity {
  activity_id: string
  company_id: string
  type: 'seminar' | 'job_fair'
  title: string
  location?: string
  activity_date: string
  start_time?: string
  end_time?: string
  description?: string
  status: number
  expected_num?: number
  actual_num?: number
  created_at: string
}

export interface ActivityCreate {
  type: 'seminar' | 'job_fair'
  title: string
  location?: string
  activity_date: string
  start_time?: string
  end_time?: string
  description?: string
  expected_num?: number
}

export interface ActivityQuery {
  type?: 'seminar' | 'job_fair'
  year?: number
  status?: number
  page?: number
  page_size?: number
}

export const getActivities = (params?: ActivityQuery) =>
  http.get<{ list: Activity[]; total: number; page: number; page_size: number }>(
    { url: '/company/activities', params }
  )

export const getActivity = (id: string) =>
  http.get<Activity>({ url: `/company/activities/${id}` })

export const createActivity = (data: ActivityCreate) =>
  http.post<Activity>({ url: '/company/activities', data })

export const updateActivity = (id: string, data: Partial<ActivityCreate>) =>
  http.put<Activity>({ url: `/company/activities/${id}`, data })

export const deleteActivity = (id: string) =>
  http.delete({ url: `/company/activities/${id}` })
```

- [ ] **Step 2: Create company_announcement.ts**

```typescript
// src/api/company_announcement.ts
import http from '@/utils/http'

export interface Announcement {
  announcement_id: string
  company_id: string
  title: string
  content: string
  target_major?: string
  target_degree?: number
  headcount?: number
  deadline?: string
  status: number
  published_at?: string
  created_at: string
}

export interface AnnouncementCreate {
  title: string
  content: string
  target_major?: string
  target_degree?: number
  headcount?: number
  deadline?: string
  status?: number
}

export interface AnnouncementQuery {
  status?: number
  year?: number
  page?: number
  page_size?: number
}

export const getAnnouncements = (params?: AnnouncementQuery) =>
  http.get<{ list: Announcement[]; total: number; page: number; page_size: number }>(
    { url: '/company/announcements', params }
  )

export const getAnnouncement = (id: string) =>
  http.get<Announcement>({ url: `/company/announcements/${id}` })

export const createAnnouncement = (data: AnnouncementCreate) =>
  http.post<Announcement>({ url: '/company/announcements', data })

export const updateAnnouncement = (id: string, data: Partial<AnnouncementCreate>) =>
  http.put<Announcement>({ url: `/company/announcements/${id}`, data })

export const deleteAnnouncement = (id: string) =>
  http.delete({ url: `/company/announcements/${id}` })
```

- [ ] **Step 3: Create stats.ts**

```typescript
// src/api/stats.ts
import http from '@/utils/http'

export interface EnterpriseStats {
  total_companies: number
  new_companies_this_year: number
  job_demand_this_year: number
  seminars_this_year: number
  job_fairs_this_year: number
  announcements_this_year: number
  positions_this_year: number
  year: number
}

export const getEnterpriseStats = (year?: number) =>
  http.get<EnterpriseStats>({ url: '/admin/enterprise-stats', params: { year } })
```

- [ ] **Step 4: Commit**

```bash
cd f:/repos/art-design-pro
git add src/api/company_activity.ts src/api/company_announcement.ts src/api/stats.ts
git commit -m "feat(frontend): add company activity, announcement and stats API"
```

---

### Task 11: Company Activities Page

**Files:**
- Create: `src/views/company/activities/index.vue`

- [ ] **Step 1: Create activities page**

```vue
<!-- src/views/company/activities/index.vue -->
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useTable } from '@/hooks/core/useTable'
import {
  getActivities,
  createActivity,
  updateActivity,
  deleteActivity,
  type Activity,
  type ActivityCreate
} from '@/api/company_activity'
import { ElMessage, ElMessageBox } from 'element-plus'

defineOptions({ name: 'CompanyActivities' })

const activeTab = ref<'seminar' | 'job_fair'>('seminar')
const dialogVisible = ref(false)
const dialogTitle = ref('新增活动')
const isEdit = ref(false)
const currentId = ref('')

const formData = ref<ActivityCreate>({
  type: 'seminar',
  title: '',
  activity_date: '',
  location: '',
  start_time: '',
  end_time: '',
  description: '',
  expected_num: undefined
})

const resetForm = () => {
  formData.value = {
    type: activeTab.value,
    title: '',
    activity_date: '',
    location: '',
    start_time: '',
    end_time: '',
    description: '',
    expected_num: undefined
  }
}

const {
  columns,
  data,
  loading,
  pagination,
  getData,
  handleSizeChange,
  handleCurrentChange
} = useTable({
  core: {
    apiFn: getActivities as any,
    apiParams: computed(() => ({
      type: activeTab.value,
      page: pagination.page,
      page_size: pagination.pageSize
    })),
    columnsFactory: () => [
      { type: 'index', width: 60, label: '序号' },
      { prop: 'title', label: '活动标题', minWidth: 150 },
      { prop: 'location', label: '地点', minWidth: 120 },
      { prop: 'activity_date', label: '活动日期', minWidth: 120 },
      { prop: 'start_time', label: '开始时间', minWidth: 100 },
      { prop: 'expected_num', label: '预计人数', minWidth: 100 },
      {
        prop: 'status', label: '状态', minWidth: 100,
        formatter: (row: Activity) => {
          const map: Record<number, string> = { 0: '已取消', 1: '进行中', 2: '已结束' }
          return map[row.status] ?? String(row.status)
        }
      },
      {
        label: '操作', width: 150,
        formatter: (row: Activity) => [
          { label: '编辑', key: 'edit', type: 'primary' },
          { label: '删除', key: 'delete', type: 'danger' }
        ]
      }
    ]
  }
})

const handleTabChange = () => {
  pagination.page = 1
  resetForm()
  getData()
}

const handleCommand = async ({ key, row }: { key: string; row: Activity }) => {
  if (key === 'edit') {
    isEdit.value = true
    currentId.value = row.activity_id
    dialogTitle.value = '编辑活动'
    formData.value = {
      type: row.type,
      title: row.title,
      activity_date: row.activity_date,
      location: row.location ?? '',
      start_time: row.start_time ?? '',
      end_time: row.end_time ?? '',
      description: row.description ?? '',
      expected_num: row.expected_num
    }
    dialogVisible.value = true
  } else if (key === 'delete') {
    await ElMessageBox.confirm('确定删除该活动吗？', '提示', { type: 'warning' })
    await deleteActivity(row.activity_id)
    ElMessage.success('删除成功')
    getData()
  }
}

const handleAdd = () => {
  isEdit.value = false
  currentId.value = ''
  dialogTitle.value = '新增活动'
  resetForm()
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formData.value.title) {
    ElMessage.warning('请填写活动标题')
    return
  }
  if (!formData.value.activity_date) {
    ElMessage.warning('请选择活动日期')
    return
  }
  try {
    if (isEdit.value) {
      await updateActivity(currentId.value, formData.value)
      ElMessage.success('更新成功')
    } else {
      await createActivity(formData.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    getData()
  } catch {
    // Error already shown by http interceptor
  }
}
</script>

<template>
  <div class="page-activities">
    <ElTabs v-model="activeTab" @tab-change="handleTabChange" style="margin-bottom: 16px">
      <ElTabPane label="宣讲会" name="seminar" />
      <ElTabPane label="招聘会" name="job_fair" />
    </ElTabs>

    <ElRow justify="end" style="margin-bottom: 12px">
      <ElButton type="primary" @click="handleAdd">新增活动</ElButton>
    </ElRow>

    <ElTable :data="data" :loading="loading" :columns="columns" @command="handleCommand">
      <template #empty>
        <ElEmpty description="暂无数据" />
      </template>
    </ElTable>

    <ElPagination
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.pageSize"
      :total="pagination.total"
      :page-sizes="[10, 20, 50]"
      layout="total, sizes, prev, pager, next"
      style="margin-top: 16px; justify-content: flex-end"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />

    <ElDialog v-model="dialogVisible" :title="dialogTitle" width="600px" destroy-on-close>
      <ElForm :model="formData" label-width="100px">
        <ElFormItem label="活动标题" required>
          <ElInput v-model="formData.title" placeholder="请输入活动标题" maxlength="200" show-word-limit />
        </ElFormItem>
        <ElFormItem label="活动类型">
          <ElTag>{{ activeTab === 'seminar' ? '宣讲会' : '招聘会' }}</ElTag>
        </ElFormItem>
        <ElFormItem label="活动地点">
          <ElInput v-model="formData.location" placeholder="线下填写地址，线上填写平台名称" />
        </ElFormItem>
        <ElFormItem label="活动日期" required>
          <ElDatePicker
            v-model="formData.activity_date"
            type="date"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </ElFormItem>
        <ElFormItem label="开始时间">
          <ElTimePicker v-model="formData.start_time" format="HH:mm" value-format="HH:mm" style="width: 100%" />
        </ElFormItem>
        <ElFormItem label="结束时间">
          <ElTimePicker v-model="formData.end_time" format="HH:mm" value-format="HH:mm" style="width: 100%" />
        </ElFormItem>
        <ElFormItem label="预计人数">
          <ElInputNumber v-model="formData.expected_num" :min="1" style="width: 100%" />
        </ElFormItem>
        <ElFormItem label="活动描述">
          <ElInput v-model="formData.description" type="textarea" :rows="3" placeholder="请输入活动描述..." />
        </ElFormItem>
      </ElForm>
      <template #footer>
        <ElButton @click="dialogVisible = false">取消</ElButton>
        <ElButton type="primary" @click="handleSubmit">确定</ElButton>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
.page-activities {
  padding: 20px;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
cd f:/repos/art-design-pro
git add src/views/company/activities/index.vue
git commit -m "feat(frontend): add company activities management page"
```

---

### Task 12: Company Announcements Page

**Files:**
- Create: `src/views/company/announcements/index.vue`

- [ ] **Step 1: Create announcements page**

```vue
<!-- src/views/company/announcements/index.vue -->
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useTable } from '@/hooks/core/useTable'
import {
  getAnnouncements,
  createAnnouncement,
  updateAnnouncement,
  deleteAnnouncement,
  type Announcement,
  type AnnouncementCreate
} from '@/api/company_announcement'
import { ElMessage, ElMessageBox } from 'element-plus'

defineOptions({ name: 'CompanyAnnouncements' })

const dialogVisible = ref(false)
const dialogTitle = ref('新增公告')
const isEdit = ref(false)
const currentId = ref('')

const DEGREE_MAP: Record<number, string> = { 0: '不限', 1: '高中/中专', 2: '大专', 3: '本科', 4: '硕士', 5: '博士' }

const formData = ref<AnnouncementCreate>({
  title: '',
  content: '',
  target_major: '',
  target_degree: undefined,
  headcount: undefined,
  deadline: '',
  status: 1
})

const resetForm = () => {
  formData.value = {
    title: '',
    content: '',
    target_major: '',
    target_degree: undefined,
    headcount: undefined,
    deadline: '',
    status: 1
  }
}

const {
  columns,
  data,
  loading,
  pagination,
  getData,
  handleSizeChange,
  handleCurrentChange
} = useTable({
  core: {
    apiFn: getAnnouncements as any,
    apiParams: computed(() => ({
      page: pagination.page,
      page_size: pagination.pageSize
    })),
    columnsFactory: () => [
      { type: 'index', width: 60, label: '序号' },
      { prop: 'title', label: '公告标题', minWidth: 180 },
      { prop: 'target_major', label: '目标专业', minWidth: 120 },
      {
        prop: 'headcount', label: '招聘人数', minWidth: 100,
        formatter: (row: Announcement) => row.headcount ?? '-'
      },
      { prop: 'deadline', label: '截止日期', minWidth: 120 },
      {
        prop: 'status', label: '状态', minWidth: 100,
        formatter: (row: Announcement) => {
          const map: Record<number, string> = { 0: '草稿', 1: '发布中', 2: '已过期' }
          return map[row.status] ?? String(row.status)
        }
      },
      { prop: 'published_at', label: '发布时间', minWidth: 160 },
      {
        label: '操作', width: 150,
        formatter: (row: Announcement) => [
          { label: '编辑', key: 'edit', type: 'primary' },
          { label: '删除', key: 'delete', type: 'danger' }
        ]
      }
    ]
  }
})

const handleCommand = async ({ key, row }: { key: string; row: Announcement }) => {
  if (key === 'edit') {
    isEdit.value = true
    currentId.value = row.announcement_id
    dialogTitle.value = '编辑公告'
    formData.value = {
      title: row.title,
      content: row.content,
      target_major: row.target_major ?? '',
      target_degree: row.target_degree,
      headcount: row.headcount,
      deadline: row.deadline ?? '',
      status: row.status
    }
    dialogVisible.value = true
  } else if (key === 'delete') {
    await ElMessageBox.confirm('确定删除该公告吗？', '提示', { type: 'warning' })
    await deleteAnnouncement(row.announcement_id)
    ElMessage.success('删除成功')
    getData()
  }
}

const handleAdd = () => {
  isEdit.value = false
  currentId.value = ''
  dialogTitle.value = '新增公告'
  resetForm()
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formData.value.title) {
    ElMessage.warning('请填写公告标题')
    return
  }
  if (!formData.value.content) {
    ElMessage.warning('请填写公告内容')
    return
  }
  try {
    if (isEdit.value) {
      await updateAnnouncement(currentId.value, formData.value)
      ElMessage.success('更新成功')
    } else {
      await createAnnouncement(formData.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    getData()
  } catch {
    // Error already shown by http interceptor
  }
}
</script>

<template>
  <div class="page-announcements">
    <ElRow justify="end" style="margin-bottom: 12px">
      <ElButton type="primary" @click="handleAdd">新增公告</ElButton>
    </ElRow>

    <ElTable :data="data" :loading="loading" :columns="columns" @command="handleCommand">
      <template #empty>
        <ElEmpty description="暂无数据" />
      </template>
    </ElTable>

    <ElPagination
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.pageSize"
      :total="pagination.total"
      :page-sizes="[10, 20, 50]"
      layout="total, sizes, prev, pager, next"
      style="margin-top: 16px; justify-content: flex-end"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />

    <ElDialog v-model="dialogVisible" :title="dialogTitle" width="600px" destroy-on-close>
      <ElForm :model="formData" label-width="100px">
        <ElFormItem label="公告标题" required>
          <ElInput v-model="formData.title" placeholder="请输入公告标题" maxlength="200" show-word-limit />
        </ElFormItem>
        <ElFormItem label="公告内容" required>
          <ElInput v-model="formData.content" type="textarea" :rows="4" placeholder="请输入公告内容..." />
        </ElFormItem>
        <ElFormItem label="目标专业">
          <ElInput v-model="formData.target_major" placeholder="多个专业用逗号分隔" />
        </ElFormItem>
        <ElFormItem label="目标学历">
          <ElSelect v-model="formData.target_degree" placeholder="请选择" style="width: 100%">
            <ElOption v-for="(label, value) in DEGREE_MAP" :key="value" :label="label" :value="Number(value)" />
          </ElSelect>
        </ElFormItem>
        <ElFormItem label="招聘人数">
          <ElInputNumber v-model="formData.headcount" :min="1" style="width: 100%" />
        </ElFormItem>
        <ElFormItem label="截止日期">
          <ElDatePicker v-model="formData.deadline" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </ElFormItem>
        <ElFormItem label="状态">
          <ElRadioGroup v-model="formData.status">
            <ElRadio :label="0">草稿</ElRadio>
            <ElRadio :label="1">发布</ElRadio>
          </ElRadioGroup>
        </ElFormItem>
      </ElForm>
      <template #footer>
        <ElButton @click="dialogVisible = false">取消</ElButton>
        <ElButton type="primary" @click="handleSubmit">确定</ElButton>
      </template>
    </ElDialog>
  </div>
</template>

<style scoped>
.page-announcements {
  padding: 20px;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
cd f:/repos/art-design-pro
git add src/views/company/announcements/index.vue
git commit -m "feat(frontend): add company announcements management page"
```

---

### Task 13: Router Registration

**Files:**
- Modify: `src/router/modules/employment.ts`

- [ ] **Step 1: Read existing employment.ts**

Read `src/router/modules/employment.ts`. Find the `companyRoutes.children` array and append:

```typescript
{
  path: 'activities',
  name: 'CompanyActivities',
  component: '/company/activities/index',
  meta: {
    title: '活动管理',
    icon: 'ri:calendar-event-line',
    keepAlive: true,
    roles: ['company_admin']
  }
},
{
  path: 'announcements',
  name: 'CompanyAnnouncements',
  component: '/company/announcements/index',
  meta: {
    title: '招聘公告',
    icon: 'ri:megaphone-line',
    keepAlive: true,
    roles: ['company_admin']
  }
}
```

- [ ] **Step 2: Commit**

```bash
cd f:/repos/art-design-pro
git add src/router/modules/employment.ts
git commit -m "feat(frontend): register company activities and announcements routes"
```

---

### Task 14: Admin Dashboard Enterprise Stats

**Files:**
- Modify: `src/views/admin/dashboard/index.vue`

- [ ] **Step 1: Read existing dashboard**

Read `src/views/admin/dashboard/index.vue` to understand current structure.

- [ ] **Step 2: Add enterprise stats cards**

After the existing stats cards section, append:

```vue
<!-- 企业招聘统计区块 -->
<ElRow :gutter="16" style="margin-top: 16px">
  <ElCol :span="24">
    <div class="section-title">本年度企业招聘活动</div>
  </ElCol>
  <ElCol :xs="12" :sm="8" :md="6" :lg="4" v-for="item in enterpriseStatsConfig" :key="item.key">
    <ArtStatsCard
      :title="item.label"
      :count="stats[item.key] ?? 0"
      :icon="item.icon"
      :icon-style="item.iconStyle"
      :description="String(stats.year ?? new Date().getFullYear())"
    />
  </ElCol>
</ElRow>
```

Add to script:

```typescript
import { getEnterpriseStats } from '@/api/stats'

const stats = ref<Record<string, number>>({})

const enterpriseStatsConfig = [
  { key: 'total_companies', label: '总单位数', icon: 'ri:building-line', iconStyle: 'bg-blue-100 text-blue-600' },
  { key: 'new_companies_this_year', label: '本年度单位数', icon: 'ri:building-4-line', iconStyle: 'bg-teal-100 text-teal-600' },
  { key: 'job_demand_this_year', label: '本年度岗位需求', icon: 'ri:briefcase-line', iconStyle: 'bg-purple-100 text-purple-600' },
  { key: 'seminars_this_year', label: '本年度宣讲会', icon: 'ri:presentation-line', iconStyle: 'bg-amber-100 text-amber-600' },
  { key: 'job_fairs_this_year', label: '本年度招聘会', icon: 'ri:team-line', iconStyle: 'bg-rose-100 text-rose-600' },
  { key: 'announcements_this_year', label: '本年度招聘公告', icon: 'ri:megaphone-line', iconStyle: 'bg-green-100 text-green-600' },
  { key: 'positions_this_year', label: '本年度职位数', icon: 'ri:file-list-3-line', iconStyle: 'bg-pink-100 text-pink-600' },
]

const loadEnterpriseStats = async () => {
  try {
    const data = await getEnterpriseStats()
    stats.value = data
  } catch (e) {
    console.error('Failed to load enterprise stats:', e)
  }
}

onMounted(() => {
  // ... existing onMounted calls ...
  loadEnterpriseStats()
})
```

- [ ] **Step 3: Commit**

```bash
cd f:/repos/art-design-pro
git add src/views/admin/dashboard/index.vue
git commit -m "feat(frontend): add enterprise stats to admin dashboard"
```

---

## Phase 7: Final Verification

---

### Task 15: Run All Tests

- [ ] **Step 1: Run backend new tests**

```bash
cd f:/repos/employment-backend
pytest tests/test_company_activities.py tests/test_company_announcements.py tests/test_admin_stats.py -v --tb=short
```

- [ ] **Step 2: Verify existing tests still pass**

```bash
cd f:/repos/employment-backend
pytest tests/ -v --tb=short 2>&1 | tail -20
```

- [ ] **Step 3: Verify frontend builds**

```bash
cd f:/repos/art-design-pro
npm run build 2>&1 | tail -30
```

---

## Spec Coverage Checklist

| Spec Requirement | Task |
|------------------|------|
| `company_activities` table | Task 1 |
| `company_announcements` table | Task 1 |
| CompanyActivity model | Task 2 |
| CompanyAnnouncement model | Task 2 |
| ActivityCreate/Update/Out schemas | Task 3 |
| AnnouncementCreate/Update/Out schemas | Task 4 |
| ActivityService CRUD + company_id isolation | Task 5 |
| AnnouncementService CRUD + published_at logic | Task 6 |
| StatsService with Redis cache (key with year) | Task 7 |
| Company activity routes | Task 8 |
| Company announcement routes | Task 8 |
| Admin `/admin/enterprise-stats` route | Task 9 |
| Frontend activity API | Task 10 |
| Frontend announcement API | Task 10 |
| Frontend stats API | Task 10 |
| Activities page with Tab + CRUD dialog | Task 11 |
| Announcements page with CRUD dialog | Task 12 |
| Router registration for company routes | Task 13 |
| Admin dashboard enterprise stats cards | Task 14 |

---

## Key Design Decisions

1. **SQLite vs MySQL**: `StatsService` uses dialect detection to generate correct SQL (`strftime('%Y', ...)` for SQLite, `YEAR(...)` for MySQL)

2. **Redis unavailability**: Redis operations are wrapped in try/except; if unavailable, stats are computed without caching

3. **Role names**: Routes use actual roles: `company_admin` and `system_admin` (not `R_COMPANY`/`R_ADMIN`)

4. **http utility behavior**: The http utility returns `res.data.data` from an ApiResponse. The frontend correctly uses try-catch (errors thrown by interceptor) rather than checking `res.code`

5. **company_id injection**: Uses existing `get_company_id(db, account_id)` helper — already implemented in `company.py`

6. **Soft delete**: Activities set `status=0` (cancelled); Announcements set `status=0` (draft) — both excluded from normal list queries

7. **ArtForm button conflict**: The post-job page has BOTH ArtForm's built-in submit/reset buttons AND external buttons — the external buttons are correct since the form uses custom submit handling via `@submit` event

**Plan complete.**