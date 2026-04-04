"""
岗位推荐服务

基于学生画像和向量检索的个性化岗位推荐
"""

import logging
import sqlite3
import os
from functools import lru_cache
from typing import Any

from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
import config_data as config

logger = logging.getLogger(__name__)


DEGREE_MAP = {1: '本科', 2: '硕士', 3: '博士', 4: '大专'}


@lru_cache(maxsize=1)
def _get_vector_store() -> Chroma:
    """获取向量存储（单例）"""
    embedding = DashScopeEmbeddings(model=config.embedding_model_name)
    return Chroma(
        collection_name=config.collection_name,
        embedding_function=embedding,
        persist_directory=config.persist_directory,
    )


def _get_db_path() -> str:
    """获取数据库路径"""
    # 从 RAG/services/rag/job_recommend.py 向上4层到达项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    return os.path.join(project_root, 'backend', 'employment.db')


def _get_student_profile(account_id: str) -> dict | None:
    """从数据库获取学生画像"""
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            sp.student_no,
            sp.major,
            sp.college,
            sp.degree,
            sp.employment_status,
            sp.cur_salary,
            sp.cur_industry,
            sp.cur_city,
            sp.desire_city,
            sp.desire_industry,
            sp.desire_salary_min,
            sp.desire_salary_max,
            sp.skills,
            sp.internship,
            u.name as university_name
        FROM student_profiles sp
        LEFT JOIN universities u ON sp.university_id = u.university_id
        WHERE sp.account_id = ?
        LIMIT 1
    """, (account_id,))

    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def _get_job_by_id(job_id: str) -> dict | None:
    """根据 job_id 获取岗位详情"""
    db_path = _get_db_path()
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
        WHERE jd.job_id = ?
    """, (job_id,))

    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def _build_student_query(profile: dict) -> str:
    """构建学生检索 Query"""
    parts = []

    if profile.get('desire_industry'):
        parts.append(f"期望行业: {profile['desire_industry']}")
    if profile.get('desire_city'):
        parts.append(f"期望城市: {profile['desire_city']}")
    if profile.get('major'):
        parts.append(f"专业: {profile['major']}")
    if profile.get('skills'):
        parts.append(f"技能: {profile['skills']}")
    if profile.get('degree'):
        parts.append(f"学历: {DEGREE_MAP.get(profile['degree'], '本科')}")
    if profile.get('desire_salary_min') and profile.get('desire_salary_max'):
        parts.append(f"期望薪资: {profile['desire_salary_min']}~{profile['desire_salary_max']}元/月")

    return '，'.join(parts) if parts else '求职'


def _calculate_match_score(job: dict, profile: dict) -> float:
    """计算岗位与学生的匹配度"""
    score = 0.5  # 基础分

    # 城市匹配
    if profile.get('desire_city') and job.get('city'):
        if profile['desire_city'] in job['city'] or job['city'] in profile['desire_city']:
            score += 0.2

    # 行业匹配
    if profile.get('desire_industry') and job.get('industry'):
        if profile['desire_industry'] == job['industry']:
            score += 0.2

    # 薪资匹配
    if profile.get('desire_salary_min') and job.get('min_salary'):
        if job['min_salary'] >= profile['desire_salary_min']:
            score += 0.1

    return min(score, 1.0)


async def recommend_jobs(account_id: str, top_k: int = 5) -> list[dict[str, Any]]:
    """
    为学生推荐岗位

    Args:
        account_id: 学生账户ID
        top_k: 返回推荐数量

    Returns:
        推荐结果列表
    """
    # 获取学生画像
    profile = _get_student_profile(account_id)
    if not profile:
        logger.warning(f"未找到学生画像: {account_id}")
        return []

    logger.info(f"为学生推荐岗位: {profile.get('major')}, {profile.get('desire_city')}")

    # 构建检索 Query
    query = _build_student_query(profile)
    logger.info(f"检索 Query: {query}")

    # 向量检索
    vector_store = _get_vector_store()
    docs = vector_store.similarity_search_with_score(query, k=top_k)

    recommendations = []
    for doc, similarity_score in docs:
        job_id = doc.metadata.get('job_id')
        job = _get_job_by_id(job_id)

        if not job:
            continue

        # 计算匹配分
        match_score = _calculate_match_score(job, profile)
        # 综合考虑向量相似度和规则匹配
        final_score = (similarity_score / 10 + match_score) / 2

        recommendations.append({
            'job_id': job_id,
            'title': job.get('title'),
            'company_name': job.get('company_name'),
            'city': job.get('city'),
            'province': job.get('province'),
            'industry': job.get('industry'),
            'min_salary': job.get('min_salary'),
            'max_salary': job.get('max_salary'),
            'keywords': job.get('keywords'),
            'description': job.get('description'),
            'match_score': round(final_score, 2),
            'vector_score': round(similarity_score, 4),
        })

    # 按匹配度排序
    recommendations.sort(key=lambda x: x['match_score'], reverse=True)

    logger.info(f"生成 {len(recommendations)} 条推荐")
    return recommendations


async def generate_recommend_reason(profile: dict, job: dict, llm_adapter) -> str:
    """
    使用 LLM 生成个性化推荐理由

    Args:
        profile: 学生画像
        job: 岗位信息
        llm_adapter: LLM 适配器

    Returns:
        推荐理由文本
    """
    # 构建 prompt
    prompt = f"""你是就业指导专家。请根据以下信息，为学生生成个性化的岗位推荐理由。

学生画像：
- 专业：{profile.get('major', '未知')}
- 学历：{DEGREE_MAP.get(profile.get('degree', 1), '本科')}
- 期望城市：{profile.get('desire_city', '未知')}
- 期望行业：{profile.get('desire_industry', '未知')}
- 期望薪资：{profile.get('desire_salary_min', 0) if profile.get('desire_salary_min') else '未知'}~{profile.get('desire_salary_max', 0) if profile.get('desire_salary_max') else '未知'}元/月
- 技能：{profile.get('skills', '未知')}

推荐岗位：
- 职位：{job.get('title')}
- 公司：{job.get('company_name')}
- 城市：{job.get('city')} | {job.get('province')}
- 行业：{job.get('industry')}
- 薪资：{job.get('min_salary') or 0}~{job.get('max_salary') or 0}元/月
- 技能要求：{job.get('keywords', '未知')}

请生成一段简洁的推荐理由（100字以内），说明为什么这个岗位适合该学生。"""

    messages = [{"role": "user", "content": prompt}]
    reason = await llm_adapter.chat(messages)
    return reason.strip()
