# app/services/stats_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
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
            pass  # Redis unavailable

        return result