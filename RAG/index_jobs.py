"""
岗位向量化索引脚本

将 job_descriptions 表中的岗位信息索引到 ChromaDB
运行方式: python -m RAG.index_jobs
"""

import sys
import os

# 确保项目根目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import config_data as config


DEGREE_MAP = {1: '本科', 2: '硕士', 3: '博士', 4: '大专'}


def format_job_text(row: dict) -> str:
    """将岗位行格式化为检索文本"""
    degree_text = DEGREE_MAP.get(row.get('min_degree') or 1, '本科')
    keywords = row.get('keywords') or ''

    text = f"""岗位: {row.get('title', '未知职位')}
公司: {row.get('company_name', '未知公司')}
城市: {row.get('city', '未知')} | 省份: {row.get('province', '未知')}
行业: {row.get('industry', '未知')}
薪资范围: {row.get('min_salary') or 0}~{row.get('max_salary') or 0}元/月
学历要求: {degree_text}
经验要求: {row.get('min_exp_years', 0)}年
技能关键词: {keywords}
职位描述: {row.get('description', '暂无描述')}"""

    return text


def get_jobs_from_db(db_path: str) -> list[dict]:
    """从 SQLite 数据库获取岗位数据"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            jd.job_id,
            jd.title,
            jd.city,
            jd.province,
            jd.industry,
            jd.min_salary,
            jd.max_salary,
            jd.min_degree,
            jd.min_exp_years,
            jd.keywords,
            jd.description,
            c.company_name
        FROM job_descriptions jd
        LEFT JOIN companies c ON jd.company_id = c.company_id
        WHERE jd.status = 1
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def index_jobs():
    """执行岗位索引"""
    # 数据库路径
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'backend',
        'employment.db'
    )

    print(f"从数据库加载岗位数据: {db_path}")
    jobs = get_jobs_from_db(db_path)
    print(f"加载到 {len(jobs)} 条岗位数据")

    if not jobs:
        print("没有找到可索引的岗位数据")
        return

    # 准备文档
    texts = []
    metadatas = []
    ids = []

    for job in jobs:
        text = format_job_text(job)
        texts.append(text)
        metadatas.append({
            'job_id': job['job_id'],
            'title': job['title'],
            'company_name': job['company_name'],
            'city': job['city'],
            'province': job['province'],
            'industry': job['industry'],
            'min_salary': job['min_salary'],
            'max_salary': job['max_salary'],
        })
        ids.append(f"job_{job['job_id']}")

    # 初始化 embedding 和向量库
    embedding = DashScopeEmbeddings(model=config.embedding_model_name)
    vector_store = Chroma(
        collection_name=config.collection_name,
        embedding_function=embedding,
        persist_directory=config.persist_directory,
    )

    # 添加文档
    documents = [
        Document(page_content=text, metadata=meta)
        for text, meta in zip(texts, metadatas)
    ]
    vector_store.add_documents(documents, ids=ids)

    print(f"成功索引 {len(jobs)} 条岗位到 ChromaDB")
    print(f"Collection: {config.collection_name}")
    print(f"Persist dir: {config.persist_directory}")


if __name__ == '__main__':
    index_jobs()
