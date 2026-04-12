from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
from datetime import datetime
import uuid
from fastapi import HTTPException
from app.models.company_announcement import CompanyAnnouncement, AnnouncementStatus
from app.schemas.company_announcement import AnnouncementCreate, AnnouncementUpdate, AnnouncementOut


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
            # Use extract for SQLite compatibility, handle NULL published_at
            from sqlalchemy import extract
            conditions.append(
                and_(
                    CompanyAnnouncement.published_at.isnot(None),
                    extract('year', CompanyAnnouncement.published_at) == year
                )
            )

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
        announcement_id = str(uuid.uuid4())
        row = CompanyAnnouncement(
            announcement_id=announcement_id,
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