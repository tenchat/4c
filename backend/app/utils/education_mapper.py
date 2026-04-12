"""
学历映射工具
将碎片化的学历字符串归一化为标准学历分类
"""

from typing import Dict, List, Tuple
from collections import Counter


# 标准学历分类
STANDARD_EDUCATION = [
    "博士",
    "硕士",
    "本科",
    "大专",
    "不限",
]

# 学历关键词映射表
EDUCATION_KEYWORDS: Dict[str, List[str]] = {
    "博士": [
        "博士", "博士学位", "博士研究生", "博士及以上",
        "全日制博士", "工程博士", "医学博士", "PhD",
        "本博", "硕博", "直博",
    ],
    "硕士": [
        "硕士", "硕士学位", "硕士研究生", "全日制研究生",
        "在职研究生", "非全日制研究生", "研究生及以上",
        "硕士及以上", "MBA", "EMBA", "MPA", "工程硕士",
        "专业硕士", "学术硕士", "港澳台硕士", "国外硕士",
        "双硕士", "本硕", "硕博",
    ],
    "本科": [
        "本科", "学士学位", "本科及以上", "学士",
        "一本", "二本", "三本", "重本", "普本",
        "本科985", "本科211", "985", "211",
        "全日制本科", "统招本科", "本科一批", "本科二批",
        "本科985/211", "一本211", "本科一批211",
    ],
    "大专": [
        "大专", "专科", "高职", "大专及以上",
        "全日制大专", "统招大专", "高专",
    ],
    "不限": [
        "不限", "学历不限", "初中及以上", "高中及以上",
        "中技", "中专", "职高", "其他",
    ],
}


def normalize_education(raw: str) -> str:
    """
    将原始学历字符串归一化为标准学历分类

    Args:
        raw: 原始学历字符串（如 "全日制研究生博士学位"）

    Returns:
        标准学历分类字符串
    """
    if not raw or raw.strip() == "":
        return "不限"

    raw_str = raw.strip()

    # 精确匹配优先
    for standard, variants in EDUCATION_KEYWORDS.items():
        if raw_str == standard:
            return standard

    # 遍历关键词，优先匹配更长的
    best_match = "不限"
    best_len = 0

    for standard, variants in EDUCATION_KEYWORDS.items():
        for variant in variants:
            if variant in raw_str or raw_str in variant:
                if len(variant) > best_len:
                    best_len = len(variant)
                    best_match = standard

    return best_match


def batch_normalize_education(raw_education_list: List[str]) -> Dict[str, str]:
    """
    批量归一化学历

    Args:
        raw_education_list: 原始学历列表

    Returns:
        {原始学历: 标准学历} 映射字典
    """
    mapping: Dict[str, str] = {}
    for raw in set(raw_education_list):
        mapping[raw] = normalize_education(raw)
    return mapping


def get_education_distribution(
    raw_education_list: List[str],
) -> List[Tuple[str, int]]:
    """
    获取归一化后的学历分布

    Args:
        raw_education_list: 原始学历列表

    Returns:
        [(标准学历, 数量)] 列表，按数量降序
    """
    mapping = batch_normalize_education(raw_education_list)
    counter = Counter(mapping.values())
    return counter.most_common()
