"""
简历优化服务

基于学生画像和 LLM 的简历优化
"""

import logging
import os
import sqlite3
import json
import re
from typing import Any

from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
import config_data as config

logger = logging.getLogger(__name__)


DEGREE_MAP = {1: '本科', 2: '硕士', 3: '博士', 4: '大专'}


def _get_db_path() -> str:
    """获取数据库路径"""
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


def _get_job_by_keyword(keyword: str, top_k: int = 3) -> list[dict]:
    """根据关键词搜索相关岗位信息作为参考"""
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            jd.title,
            jd.keywords,
            jd.description,
            c.company_name
        FROM job_descriptions jd
        LEFT JOIN companies c ON jd.company_id = c.company_id
        WHERE jd.status = 1
        LIMIT 50
    """)
    all_jobs = cursor.fetchall()
    conn.close()

    # 简单关键词匹配
    matched = []
    keyword_lower = keyword.lower()
    for job in all_jobs:
        job_dict = dict(job)
        if (keyword_lower in job_dict.get('title', '').lower() or
            keyword_lower in job_dict.get('keywords', '').lower() or
            keyword_lower in job_dict.get('description', '').lower()):
            matched.append(job_dict)
        if len(matched) >= top_k:
            break

    # 如果没有精确匹配，返回前几条
    if not matched:
        matched = [dict(j) for j in all_jobs[:top_k]]

    return matched


def _build_optimize_prompt(profile: dict, target_job: str, resume_text: str, job_references: list[dict]) -> str:
    """构建简历优化 Prompt"""
    # 构建学生画像描述
    profile_desc = []
    if profile.get('major'):
        profile_desc.append(f"- 专业：{profile['major']}")
    if profile.get('college'):
        profile_desc.append(f"- 学院：{profile['college']}")
    if profile.get('degree'):
        profile_desc.append(f"- 学历：{DEGREE_MAP.get(profile['degree'], '本科')}")
    if profile.get('skills'):
        profile_desc.append(f"- 技能：{profile['skills']}")
    if profile.get('desire_city'):
        profile_desc.append(f"- 期望城市：{profile['desire_city']}")
    if profile.get('desire_industry'):
        profile_desc.append(f"- 期望行业：{profile['desire_industry']}")
    if profile.get('internship'):
        profile_desc.append(f"- 实习经历：{profile['internship']}")
    if profile.get('university_name'):
        profile_desc.append(f"- 毕业院校：{profile['university_name']}")

    # 构建岗位参考信息
    job_ref_text = ""
    if job_references:
        job_ref_text = "\n\n相关岗位参考信息：\n"
        for i, job in enumerate(job_references, 1):
            job_ref_text += f"{i}. {job.get('title', '')} @ {job.get('company_name', '')}\n"
            job_ref_text += f"   技能要求：{job.get('keywords', '未知')}\n"
            job_ref_text += f"   描述：{job.get('description', '')[:200]}...\n"

    prompt = f"""你是简历优化专家，擅长根据目标岗位要求优化简历内容。

## 学生画像
{chr(10).join(profile_desc) if profile_desc else "- 暂无完整画像信息"}

## 目标岗位
{target_job}
{job_ref_text}

## 原始简历
{resume_text}

## 输出要求
请分析以上简历与目标岗位的匹配度，并返回 JSON 格式的优化结果：

{{
    "optimized_resume": "优化后的完整简历文本（使用 Markdown 格式，标题用 ## ，各部分清晰分隔）",
    "suggestions": [
        {{
            "section": "所属章节（如：工作经历、技能描述、项目经验）",
            "original": "原文摘录",
            "suggested": "建议修改后的内容",
            "reason": "修改原因"
        }}
    ],
    "match_analysis": {{
        "score": 85,
        "strengths": ["优势1", "优势2"],
        "weaknesses": ["不足1", "不足2"]
    }}
}}

请确保：
1. optimized_resume 是完整可用的简历，包含基本信息、教育背景、技能列表、实习/项目经历等
2. suggestions 中的修改建议具体、可操作
3. match_analysis 客观分析简历与岗位的匹配度
4. 返回的 JSON 必须可以正常解析"""

    return prompt


def _parse_llm_response(llm_output: str) -> dict:
    """解析 LLM 输出为结构化数据"""
    try:
        # 尝试提取 JSON
        json_match = re.search(r'\{[\s\S]*\}', llm_output)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError as e:
        logger.warning(f"JSON 解析失败: {e}")

    # 如果解析失败，返回默认结构
    return {
        "optimized_resume": llm_output,
        "suggestions": [],
        "match_analysis": {"score": 0, "strengths": [], "weaknesses": []}
    }


async def optimize_resume(account_id: str, resume_text: str, target_job: str) -> dict[str, Any]:
    """
    优化简历

    Args:
        account_id: 学生账户ID
        resume_text: 原始简历文本
        target_job: 目标岗位

    Returns:
        优化结果
    """
    # 获取学生画像
    profile = _get_student_profile(account_id)
    if not profile:
        logger.warning(f"未找到学生画像: {account_id}")
        profile = {}

    logger.info(f"简历优化: account_id={account_id}, target_job={target_job}")

    # 获取相关岗位参考
    job_references = _get_job_by_keyword(target_job)

    # 构建 Prompt
    prompt = _build_optimize_prompt(profile, target_job, resume_text, job_references)

    # 调用 LLM
    from services.llm.factory import LLMFactory
    llm = LLMFactory.get_adapter("tongyi")

    messages = [{"role": "user", "content": prompt}]
    response = await llm.chat(messages)
    llm_output = response.strip() if response else ""

    logger.info(f"LLM 响应长度: {len(llm_output)} 字符")

    # 解析响应
    result = _parse_llm_response(llm_output)

    return result
