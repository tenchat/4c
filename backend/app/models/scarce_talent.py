"""
紧缺人才模型

注意：scarce_talent表在数据库中没有主键，
因此不作为ORM模型使用，改为在analyzer中直接使用原始SQL查询
"""
from typing import Optional, List, Dict
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def get_scarce_talent_data(
    db: AsyncSession,
    province: Optional[str] = None,
    shortage_level: Optional[int] = None,
    year: Optional[int] = None,
) -> List[Dict]:
    """
    直接使用原始SQL查询scarce_talent表，支持过滤

    Args:
        db: 数据库会话
        province: 按省份/区域筛选 (region_scarce 或 province_city 模糊匹配)
        shortage_level: 按紧缺程度筛选 (level字段)
        year: 按年份筛选

    Returns:
        [{"region_scarce": "...", "industry": "...", "job_title": "...", "level": ..., ...}, ...]
    """
    # 构建WHERE条件
    conditions = []
    params = {}

    if province:
        conditions.append("(region_scarce LIKE :province OR province_city LIKE :province)")
        params["province"] = f"%{province}%"
    if shortage_level:
        conditions.append("level = :level")
        params["level"] = shortage_level
    if year:
        conditions.append("year = :year")
        params["year"] = year

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    sql = text(f"""
        SELECT
            region_scarce,
            province_city,
            city_district,
            industry,
            job_title,
            level,
            education,
            major,
            salary,
            shortage_type,
            year
        FROM scarce_talent
        {where_clause}
    """)

    result = await db.execute(sql, params)
    rows = result.fetchall()
    return [
        {
            "region_scarce": row[0],
            "province_city": row[1],
            "city_district": row[2],
            "industry": row[3],
            "job_title": row[4],
            "level": row[5],
            "education": row[6],
            "major": row[7],
            "salary": row[8],
            "shortage_type": row[9],
            "year": row[10],
        }
        for row in rows
    ]
