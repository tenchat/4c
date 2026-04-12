"""
省份名称规范化工具
将前端地图返回的省份名称（如"北京市"）转换为数据库存储的格式（如"北京"）
"""

from typing import Dict

# 特殊省份/直辖市名称映射
SPECIAL_MAPPINGS: Dict[str, str] = {
    "北京": "北京",
    "天津市": "天津",
    "上海市": "上海",
    "重庆市": "重庆",
    "内蒙古": "内蒙古",
    "广西": "广西",
    "西藏": "西藏",
    "宁夏": "宁夏",
    "新疆": "新疆",
    "香港": "香港",
    "澳门": "澳门",
    "台湾": "台湾",
}

# 需要移除的后缀
SUFFIXES_TO_REMOVE = ["市", "省", "自治区", "特别行政区", "壮族自治区", "回族自治区", "维吾尔自治区"]


def normalize_province_name(name: str) -> str:
    """
    将省份名称规范化，移除"市""省"等后缀

    Args:
        name: 原始省份名称（如"北京市"、"上海市"、"内蒙古自治区"）

    Returns:
        规范化后的省份名称（如"北京"、"上海"、"内蒙古"）
    """
    if not name:
        return name

    # 直接映射检查
    if name in SPECIAL_MAPPINGS:
        return SPECIAL_MAPPINGS[name]

    # 移除后缀
    result = name
    for suffix in SUFFIXES_TO_REMOVE:
        if result.endswith(suffix):
            result = result[: -len(suffix)]
            break

    return result


def batch_normalize_province_names(names: list[str]) -> list[str]:
    """批量规范化省份名称"""
    return [normalize_province_name(n) for n in names]
