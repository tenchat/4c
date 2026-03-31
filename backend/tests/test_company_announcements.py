# tests/test_company_announcements.py
import pytest
import pytest_asyncio
import uuid

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