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
        if profile['desire_salary_min'] == 0 and profile['desire_salary_max'] == 0:
            parts.append("期望薪资: 面议")
        else:
            parts.append(f"期望薪资: {profile['desire_salary_min']}~{profile['desire_salary_max']}元/月")

    return '，'.join(parts) if parts else '求职'


def _calculate_match_score(job: dict, profile: dict, distance: float = 0.0) -> dict:
    """
    计算岗位与学生的综合匹配度 (0-1)

    权重分配（改进版）:
    - 向量相似度 (语义匹配): 10%  （降低权重，向量匹配不确定性强）
    - 城市匹配: 25%
    - 行业匹配: 25%
    - 薪资匹配: 20%
    - 学历匹配: 12%
    - 技能关键词匹配: 8%

    Returns:
        {
            'total': float,  # 综合匹配度 (0-1)
            'breakdown': {
                'vector': float,
                'city': float,
                'industry': float,
                'salary': float,
                'degree': float,
                'skills': float,
            }
        }
    """
    weights = {
        'vector': 0.10,
        'city': 0.25,
        'industry': 0.25,
        'salary': 0.20,
        'degree': 0.12,
        'skills': 0.08,
    }

    scores = {}

    # 1. 向量相似度转换 (distance 越小越好，转换为 0-1 相似度)
    # DashScope embedding distance 约在 0-2 之间，使用更合理的转换
    if distance > 0:
        # 使用 sigmoid 类平滑转换: 1 - sigmoid(distance - 0.5)
        # distance < 0.5 时接近 1.0, distance = 1 时约 0.38
        vector_sim = max(0.2, 1.0 - distance / (1.0 + distance))
    else:
        vector_sim = 0.75  # 默认较高相似度
    scores['vector'] = vector_sim

    # 2. 城市匹配 (精确=1.0, 同省=0.7, 部分匹配=0.5, 无期望=0.6)
    city_score = 0.5
    profile_city = profile.get('desire_city', '')
    job_city = job.get('city', '')

    if profile_city and job_city:
        if profile_city == job_city:
            city_score = 1.0
        elif profile_city in job_city or job_city in profile_city:
            city_score = 0.75
        # 检查是否同省（简化判断：城市名包含相同字符超过2个）
        elif len(set(profile_city) & set(job_city)) >= 2:
            city_score = 0.6
    elif profile_city and not job_city:
        city_score = 0.5  # 岗位未标注城市
    elif not profile_city:
        city_score = 0.7  # 学生无偏好，给较高分
    scores['city'] = city_score

    # 3. 行业匹配 (精确=1.0, 相关行业=0.7, 无期望=0.6)
    industry_score = 0.5
    profile_industry = profile.get('desire_industry', '')
    job_industry = job.get('industry', '')

    # 相关行业映射（简化版）
    related_industries = {
        '互联网': ['计算机', '软件', 'IT', '通信', '电子'],
        '计算机': ['互联网', '软件', 'IT', '电子'],
        '金融': ['银行', '证券', '保险', '投资'],
        '制造': ['机械', '电子', '汽车', '化工'],
        '教育': ['培训', '咨询'],
        '医疗': ['制药', '生物', '健康'],
    }

    if profile_industry and job_industry:
        if profile_industry == job_industry:
            industry_score = 1.0
        elif profile_industry in job_industry or job_industry in profile_industry:
            industry_score = 0.8
        else:
            # 检查相关行业
            related = related_industries.get(profile_industry, [])
            if job_industry in related or any(r in job_industry for r in related):
                industry_score = 0.65
    elif profile_industry and not job_industry:
        industry_score = 0.4
    elif not profile_industry:
        industry_score = 0.65  # 学生无偏好
    scores['industry'] = industry_score

    # 4. 薪资匹配 (更合理的计算方式)
    salary_score = 0.6  # 默认
    stu_min = profile.get('desire_salary_min') or 0
    stu_max = profile.get('desire_salary_max') or 0
    job_min = job.get('min_salary') or 0
    job_max = job.get('max_salary') or 0

    # 处理面议
    if stu_min == 0 and stu_max == 0:
        salary_score = 0.8  # 学生不挑薪资
    elif job_min == 0 and job_max == 0:
        salary_score = 0.75  # 岗位面议
    elif stu_max > 0 and stu_min > 0:
        # 检查是否有重叠区间
        if job_max >= stu_min and job_min <= stu_max:
            overlap_min = max(job_min, stu_min)
            overlap_max = min(job_max, stu_max)
            if overlap_max >= overlap_min:
                overlap_len = overlap_max - overlap_min
                stu_range = stu_max - stu_min
                job_range = job_max - job_min if job_max > job_min else 1

                # 重叠程度
                if stu_range > 0:
                    overlap_ratio = overlap_len / stu_range
                else:
                    overlap_ratio = 1.0 if overlap_len > 0 else 0.5

                # 岗位薪资区间与学生期望的重叠程度
                salary_score = 0.5 + 0.4 * min(1.0, overlap_ratio)

                # 如果岗位薪资完全在期望内，给额外加分
                if job_min >= stu_min and job_max <= stu_max:
                    salary_score = min(1.0, salary_score + 0.1)
        else:
            # 无重叠，但差距不大时给部分分
            if job_max < stu_min:
                gap = (stu_min - job_max) / stu_min if stu_min > 0 else 0
                salary_score = max(0.25, 0.5 - gap * 0.2)
            else:
                salary_score = 0.4
    scores['salary'] = salary_score

    # 5. 学历匹配 (更合理的计算)
    degree_map = {1: 1, 2: 2, 3: 3, 4: 4}  # 本科=1, 硕士=2, 博士=3, 大专=4
    stu_degree = degree_map.get(profile.get('degree', 1), 1)
    job_degree = degree_map.get(job.get('min_degree', 1), 1)

    if stu_degree >= job_degree:
        # 学生学历高于或等于要求
        if stu_degree == job_degree:
            scores['degree'] = 1.0
        else:
            # 高于要求也挺好，但给满分
            scores['degree'] = 0.95
    else:
        # 学生学历低于要求，但差一级时给部分分
        diff = job_degree - stu_degree
        scores['degree'] = max(0.0, 0.5 - diff * 0.2)

    # 6. 技能关键词匹配 (改进的 Jaccard)
    stu_skills = set(s.strip().lower() for s in (profile.get('skills') or '').split(',') if s.strip())
    job_keywords = set(s.strip().lower() for s in (job.get('keywords') or '').split(',') if s.strip())

    if stu_skills and job_keywords:
        intersection = stu_skills & job_keywords
        union = stu_skills | job_keywords
        if union:
            # 基础 Jaccard
            base_score = len(intersection) / len(union) if union else 0
            # 如果有匹配，增加基础分
            if intersection:
                # 匹配数量加成
                match_bonus = min(0.2, len(intersection) * 0.05)
                skills_score = min(1.0, base_score + match_bonus)
            else:
                skills_score = base_score
    elif not job_keywords:
        skills_score = 0.7  # 岗位无技能要求，容易匹配
    else:
        skills_score = 0.4  # 学生无技能，岗位有要求
    scores['skills'] = skills_score

    # 计算加权总分
    total_score = sum(scores[key] * weights[key] for key in weights)
    total_score = min(1.0, max(0.0, total_score))

    return {
        'total': total_score,
        'breakdown': {key: round(scores[key], 2) for key in scores}
    }


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
    for doc, distance_score in docs:
        job_id = doc.metadata.get('job_id')
        job = _get_job_by_id(job_id)

        if not job:
            continue

        # 计算综合匹配分 (distance_score 传入用于向量相似度计算)
        score_result = _calculate_match_score(job, profile, distance_score)
        match_score = score_result['total']
        score_breakdown = score_result['breakdown']

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
            'match_score': round(match_score, 2),
            'distance_score': round(distance_score, 4),
            # 细分分数（用于雷达图）
            'city_score': round(score_breakdown['city'] * 100),
            'industry_score': round(score_breakdown['industry'] * 100),
            'salary_score': round(score_breakdown['salary'] * 100),
            'degree_score': round(score_breakdown['degree'] * 100),
            'skills_score': round(score_breakdown['skills'] * 100),
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
- 期望薪资：{"面议" if (not profile.get('desire_salary_min') or profile.get('desire_salary_min') == 0) and (not profile.get('desire_salary_max') or profile.get('desire_salary_max') == 0) else f"{profile.get('desire_salary_min', 0) if profile.get('desire_salary_min') else '未知'}~{profile.get('desire_salary_max', 0) if profile.get('desire_salary_max') else '未知'}元/月"}
- 技能：{profile.get('skills', '未知')}

推荐岗位：
- 职位：{job.get('title')}
- 公司：{job.get('company_name')}
- 城市：{job.get('city')} | {job.get('province')}
- 行业：{job.get('industry')}
- 薪资：{"面议" if (not job.get('min_salary') or job.get('min_salary') == 0) and (not job.get('max_salary') or job.get('max_salary') == 0) else f"{job.get('min_salary') or 0}~{job.get('max_salary') or 0}元/月"}
- 技能要求：{job.get('keywords', '未知')}
- 技能要求：{job.get('keywords', '未知')}

请生成一段简洁的推荐理由（100字以内），说明为什么这个岗位适合该学生。"""

    messages = [{"role": "user", "content": prompt}]
    reason = await llm_adapter.chat(messages)
    return reason.strip()
