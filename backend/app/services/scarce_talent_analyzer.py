"""
紧缺人才RAG分析服务
对碎片化的行业数据进行归一化分析，生成词云和地图可视化数据
"""

import json
import logging
from collections import Counter
from typing import Any, List, Dict

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scarce_talent import get_scarce_talent_data
from app.services.rag.rag_service import get_rag_service, RAGServiceError
from app.utils.industry_normalizer import (
    STANDARD_INDUSTRIES,
    normalize_industry,
    extract_provincial_industry_keywords,
)
from app.utils.education_mapper import normalize_education

logger = logging.getLogger(__name__)


# RAG 分析提示词模板
SCARCE_TALENT_ANALYSIS_PROMPT = """
你是一个就业数据分析专家。请根据以下紧缺人才行业数据，进行归一化分析和解读。

【任务】
1. 分析以下行业的关键词，判断其属于哪个标准行业分类
2. 给出每个行业的紧缺程度分析
3. 识别新兴行业和传统行业的分布特点

【标准行业分类（共20类）】
{standard_industries}

【待分析的行业关键词（按省份分组）】
{provincial_industry_keywords}

【紧缺程度数据（level: 1-10，越高越紧缺）】
{shortage_level_data}

请以JSON格式返回：
{{
    "industry_mapping": {{"原始行业1": "标准行业A", "原始行业2": "标准行业B", ...}},
    "analysis": {{
        "新兴行业": ["行业列表，按紧缺程度排序"],
        "传统行业": ["行业列表"],
        "高紧缺省份": ["省份列表"],
        "关键洞察": "100字以内的关键发现"
    }},
    "word_cloud_data": [
        {{"word": "词1", "frequency": 100, "province": "北京"}},
        {{"word": "词2", "frequency": 80, "province": "上海"}},
        ...
    ]
}}
"""


class ScarceTalentAnalyzer:
    """紧缺人才RAG分析器"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.rag_service = get_rag_service()

    async def get_raw_data(self) -> List[Dict]:
        """
        获取scarce_talent原始数据

        Returns:
            [{"region_scarce": "粤港澳大湾区", "industry": "互联网", "job_title": "算法工程师", "level": 9.0, ...}, ...]
        """
        return await get_scarce_talent_data(self.db)

    async def analyze_with_rag(self) -> Dict[str, Any]:
        """
        使用RAG对紧缺人才数据进行归一化分析

        Returns:
            {
                "industry_mapping": {"原始行业": "标准行业", ...},
                "analysis": {...},
                "word_cloud_data": [...]
            }
        """
        # Step 1: 获取原始数据
        raw_data = await self.get_raw_data()
        if not raw_data:
            return {
                "industry_mapping": {},
                "analysis": {
                    "新兴行业": [],
                    "传统行业": [],
                    "高紧缺省份": [],
                    "关键洞察": "暂无数据",
                },
                "word_cloud_data": [],
            }

        # Step 2: 按省份提取行业关键词
        provincial_keywords = extract_provincial_industry_keywords(raw_data)

        # Step 3: 提取紧缺程度数据
        shortage_by_province = {}
        for item in raw_data:
            region = item.get("region_scarce", "")
            level = item.get("level")
            if region and level:
                if region not in shortage_by_province:
                    shortage_by_province[region] = []
                shortage_by_province[region].append(float(level))

        # 计算每个省份的平均紧缺程度
        avg_shortage = {
            region: sum(levels) / len(levels)
            for region, levels in shortage_by_province.items()
        }
        top_provinces = sorted(avg_shortage.items(), key=lambda x: x[1], reverse=True)[:5]

        # Step 4: 构造RAG提示词
        prompt = SCARCE_TALENT_ANALYSIS_PROMPT.format(
            standard_industries=", ".join(STANDARD_INDUSTRIES),
            provincial_industry_keywords=json.dumps(provincial_keywords, ensure_ascii=False, indent=2),
            shortage_level_data=json.dumps(
                {region: round(avg, 2) for region, avg in top_provinces},
                ensure_ascii=False,
            ),
        )

        # Step 5: 调用RAG服务
        try:
            rag_result = await self.rag_service.qa(
                question=prompt,
                user_id="system",
                role_type="school",
            )
            answer_text = rag_result.get("answer", "")

            # 尝试从回答中解析JSON
            # RAG可能返回包含JSON的文本，需要提取
            return self._parse_rag_response(answer_text, raw_data)

        except RAGServiceError as e:
            logger.warning(f"RAG服务调用失败，使用本地归一化: {e}")
            return self._local_normalize(raw_data, provincial_keywords, top_provinces)
        except Exception as e:
            logger.error(f"RAG分析异常: {e}")
            return self._local_normalize(raw_data, provincial_keywords, top_provinces)

    def _parse_rag_response(self, answer_text: str, raw_data: list) -> dict:
        """
        解析RAG返回的文本，提取JSON结果
        如果RAG未返回有效JSON，使用本地归一化兜底
        """
        # 尝试在回答中找JSON块
        try:
            # 查找 ```json ... ``` 或 ``` ... ``` 包裹的JSON
            import re

            json_match = re.search(r"```(?:json)?\s*([\s\S]+?)```", answer_text)
            if json_match:
                json_str = json_match.group(1)
                parsed = json.loads(json_str)
                return parsed

            # 直接尝试解析整个回答为JSON
            parsed = json.loads(answer_text)
            return parsed

        except (json.JSONDecodeError, Exception):
            # 解析失败，使用本地归一化
            pass

        # 使用本地归一化兜底
        return self._local_normalize_from_text(raw_data)

    def _local_normalize(self, raw_data: list, provincial_keywords: dict, top_provinces: list) -> dict:
        """本地归一化（不调用RAG）"""
        # 行业映射
        industry_mapping = {}
        for item in raw_data:
            raw_industry = item.get("industry", "")
            if raw_industry:
                industry_mapping[raw_industry] = normalize_industry(raw_industry)

        # 词云数据
        job_counter = Counter()
        for item in raw_data:
            job = item.get("job_title", "")
            if job:
                job_counter[job] += 1

        word_cloud = [
            {"word": job, "frequency": count}
            for job, count in job_counter.most_common(100)
        ]

        # 分析结果
        normalized_industries = Counter(industry_mapping.values())
        emerging = [ind for ind, _ in normalized_industries.most_common(5)]
        traditional = [ind for ind in ["制造业", "房地产", "建筑", "农林牧渔"] if ind in normalized_industries]

        return {
            "industry_mapping": industry_mapping,
            "analysis": {
                "新兴行业": emerging,
                "传统行业": traditional,
                "高紧缺省份": [p[0] for p in top_provinces],
                "关键洞察": f"共有{len(raw_data)}条紧缺人才数据，覆盖{len(set(industry_mapping.values()))}个标准行业",
            },
            "word_cloud_data": word_cloud,
        }

    def _local_normalize_from_text(self, raw_data: list) -> dict:
        """从RAG文本响应中提取信息并本地归一化"""
        return self._local_normalize(raw_data, {}, [])

    async def get_industry_wordcloud(self) -> List[Dict]:
        """
        获取行业词云数据（用于前端展示）

        Returns:
            [{"word": "人工智能", "value": 5000}, ...]
        """
        raw_data = await self.get_raw_data()
        if not raw_data:
            return []

        # 归一化行业
        counter = Counter()
        for item in raw_data:
            raw_industry = item.get("industry", "")
            if raw_industry:
                normalized = normalize_industry(raw_industry)
                counter[normalized] += 1

        return [
            {"word": industry, "value": count}
            for industry, count in counter.most_common(50)
        ]

    async def get_province_industry_map(self) -> Dict[str, List]:
        """
        获取省份-行业映射（用于地图+词云联动）

        Returns:
            {
                "粤港澳大湾区": [{"word": "人工智能", "value": 500}, ...],
                "长三角": [...],
                ...
            }
        """
        raw_data = await self.get_raw_data()
        if not raw_data:
            return {}

        # 按省份分组
        province_industry: Dict[str, Counter] = {}
        for item in raw_data:
            region = item.get("region_scarce", "")
            industry = item.get("industry", "")
            if region and industry:
                normalized = normalize_industry(industry)
                if region not in province_industry:
                    province_industry[region] = Counter()
                province_industry[region][normalized] += 1

        return {
            region: [
                {"word": industry, "value": count}
                for industry, count in counter.most_common(10)
            ]
            for region, counter in province_industry.items()
        }

    async def get_scarce_talent_summary(self) -> Dict[str, Any]:
        """
        获取紧缺人才汇总数据（用于数字卡片）

        Returns:
            {
                "total_count": 20071,
                "region_count": 7,
                "industry_count": 20,
                "avg_level": 6.5,
                "top_regions": [...],
                "top_industries": [...],
            }
        """
        raw_data = await self.get_raw_data()
        if not raw_data:
            return {
                "total_count": 0,
                "region_count": 0,
                "industry_count": 0,
                "avg_level": 0,
                "top_regions": [],
                "top_industries": [],
            }

        total_count = len(raw_data)

        # 地区分布
        region_counter = Counter(item.get("region_scarce", "") for item in raw_data if item.get("region_scarce"))
        top_regions = [
            {"name": region, "value": count}
            for region, count in region_counter.most_common(10)
        ]

        # 行业分布（归一化后）
        normalized_industries = [normalize_industry(item.get("industry", "")) for item in raw_data if item.get("industry")]
        industry_counter = Counter(normalized_industries)
        top_industries = [
            {"name": industry, "value": count}
            for industry, count in industry_counter.most_common(10)
        ]

        # 平均紧缺程度
        levels = [item.get("level") for item in raw_data if item.get("level")]
        avg_level = sum(levels) / len(levels) if levels else 0

        return {
            "total_count": total_count,
            "region_count": len(region_counter),
            "industry_count": len(industry_counter),
            "avg_level": round(avg_level, 2),
            "top_regions": top_regions,
            "top_industries": top_industries,
        }
