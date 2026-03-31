"""
MySQL to SQLite 数据迁移脚本
零停机迁移：将MySQL数据导出为SQLite文件

使用方法:
    python -m migrate_to_sqlite

迁移前请确保:
1. MySQL数据库正在运行
2. 已创建SQLite数据库文件
"""

import asyncio
import sqlite3
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import get_settings
from app.models import Base

settings = get_settings()

# MySQL连接
MYSQL_URL = settings.DATABASE_URL

# SQLite文件路径
SQLITE_PATH = "./employment.db"


def create_sqlite_table_sql(model_class):
    """根据SQLAlchemy模型生成SQLite建表SQL"""
    table_name = model_class.__tablename__
    columns = []
    for col in model_class.__table__.columns:
        col_type = str(col.type)
        col_name = col.name
        is_pk = col.primary_key
        is_nullable = col.nullable

        # SQLite类型映射
        if 'VARCHAR' in col_type or 'TEXT' in col_type:
            sqlite_type = "TEXT"
        elif 'INTEGER' in col_type or 'INT' in col_type:
            sqlite_type = "INTEGER"
        elif 'BOOLEAN' in col_type:
            sqlite_type = "INTEGER"
        elif 'DATETIME' in col_type or 'TIMESTAMP' in col_type:
            sqlite_type = "TEXT"
        elif 'FLOAT' in col_type or 'REAL' in col_type:
            sqlite_type = "REAL"
        elif 'JSON' in col_type:
            sqlite_type = "TEXT"
        else:
            sqlite_type = "TEXT"

        col_def = f'"{col_name}" {sqlite_type}'
        if is_pk:
            col_def += " PRIMARY KEY"
        if not is_nullable and not is_pk:
            col_def += " NOT NULL"

        columns.append(col_def)

    return f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"


async def export_table_data(session, sqlite_conn, table_name, model_class):
    """导出单个表的数据"""
    # 获取所有列名
    columns = [col.name for col in model_class.__table__.columns]
    column_names = ', '.join([f'"{c}"' for c in columns])
    placeholders = ', '.join(['?' for _ in columns])

    # 从MySQL读取数据
    result = await session.execute(text(f"SELECT * FROM {table_name}"))
    rows = result.fetchall()

    if not rows:
        print(f"  {table_name}: 无数据")
        return 0

    # 插入SQLite
    insert_sql = f'INSERT OR REPLACE INTO {table_name} ({column_names}) VALUES ({placeholders})'
    cursor = sqlite_conn.cursor()

    for row in rows:
        # 转换数据
        values = []
        for val in row:
            if val is None:
                values.append(None)
            elif isinstance(val, bytes):
                values.append(val.hex())
            elif hasattr(val, 'value'):  # Enum
                values.append(val.value)
            elif hasattr(val, 'isoformat'):  # datetime
                values.append(val.isoformat())
            elif isinstance(val, (int, float)):
                values.append(val)
            elif isinstance(val, str):
                values.append(val)
            else:
                # 其他类型(如Decimal)转为字符串
                values.append(str(val))
        cursor.execute(insert_sql, values)

    sqlite_conn.commit()
    print(f"  {table_name}: 导出 {len(rows)} 条记录")
    return len(rows)


async def migrate_to_sqlite():
    """执行数据迁移"""
    print("=" * 60)
    print("MySQL -> SQLite 数据迁移")
    print("=" * 60)

    # 创建SQLite连接
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    print(f"\n1. 连接SQLite: {SQLITE_PATH}")

    # 导入所有模型
    from app.models import (
        Account, RefreshToken, University, StudentProfile, Company,
        JobDescription, JobApplication, CollegeEmployment, ScarceTalent,
        EmploymentWarning, AIAnalysisRecord, KnowledgeDocument,
        SystemConfig, OperationLog
    )

    models = [
        Account, RefreshToken, University, StudentProfile, Company,
        JobDescription, JobApplication, CollegeEmployment, ScarceTalent,
        EmploymentWarning, AIAnalysisRecord, KnowledgeDocument,
        SystemConfig, OperationLog
    ]

    # 创建表
    print("\n2. 创建SQLite表结构...")
    for model in models:
        sql = create_sqlite_table_sql(model)
        sqlite_conn.execute(sql)
    sqlite_conn.commit()
    print("  表结构创建完成")

    # 创建MySQL异步引擎
    print("\n3. 连接MySQL数据库...")
    mysql_engine = create_async_engine(MYSQL_URL, echo=False)
    MySQLSession = async_sessionmaker(mysql_engine, expire_on_commit=False)

    print("\n4. 导出数据...")
    total = 0
    async with MySQLSession() as session:
        for model in models:
            table_name = model.__tablename__
            count = await export_table_data(session, sqlite_conn, table_name, model)
            total += count

    # 关闭连接
    sqlite_conn.close()
    await mysql_engine.dispose()

    print("\n" + "=" * 60)
    print(f"迁移完成! 共导出 {total} 条记录")
    print(f"SQLite文件: {SQLITE_PATH}")
    print("\n下一步:")
    print("  1. 修改 .env 中的 DATABASE_URL")
    print("  2. 重启后端服务")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(migrate_to_sqlite())
