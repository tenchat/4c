# app/services/activity_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional
import uuid
from fastapi import HTTPException
from app.models.company_activity import CompanyActivity, ActivityType, ActivityStatus
from app.schemas.company_activity import ActivityCreate, ActivityUpdate, ActivityOut


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
        # Exclude soft-deleted (status=0) by default
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
        row = await self._get_owned(activity_id, company_id)
        return ActivityOut.model_validate(row)

    async def create_activity(self, company_id: str, data: ActivityCreate) -> ActivityOut:
        row = CompanyActivity(
            activity_id=str(uuid.uuid4()),
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