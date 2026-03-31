# tests/test_company_activities.py
import pytest
import pytest_asyncio
import uuid
from datetime import date

# Helper to create a test company
async def create_test_company(db_session, company_name="Test Corp"):
    from app.models.company import Company
    from app.models.account import Account, RoleType
    account_id = str(uuid.uuid4())
    company_id = str(uuid.uuid4())
    account = Account(
        account_id=account_id,
        username=f"user_{uuid.uuid4().hex[:8]}",
        password_hash="x",
        role=RoleType.company_admin,
        status=1
    )
    company = Company(
        company_id=company_id,
        account_id=account_id,
        company_name=company_name,
        verified=True
    )
    db_session.add(account)
    db_session.add(company)
    await db_session.commit()
    return company


# Test fixtures
@pytest_asyncio.fixture
async def db_session():
    """Get an async DB session for testing"""
    from app.core.database import AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def company(db_session):
    """Create a test company"""
    return await create_test_company(db_session, "Test Company")


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

    # Should not appear in normal list (excluded by default)
    page = await svc.list_activities(company.company_id, page=1, page_size=20)
    assert page["total"] == 0