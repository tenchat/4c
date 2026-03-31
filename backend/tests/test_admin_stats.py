# tests/test_admin_stats.py
import pytest
try:
    from unittest.mock import AsyncMock
except ImportError:
    from mock import AsyncMock
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
    mock_db.bind = AsyncMock()
    mock_db.bind.dialect = AsyncMock()
    mock_db.bind.dialect.name = "sqlite"

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
    # db.execute should NOT be called on cache hit
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
    mock_db.bind = AsyncMock()
    mock_db.bind.dialect = AsyncMock()
    mock_db.bind.dialect.name = "sqlite"

    svc = StatsService()
    result = await svc.get_enterprise_stats(mock_db, mock_redis, year=None)

    assert result["year"] == datetime.utcnow().year