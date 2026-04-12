"""
薪资解析工具
统一不同格式的薪资字符串为标准数值（单位：元/月）
"""

import re
from typing import Optional, Tuple, List


def parse_salary(salary_str: str) -> Tuple[Optional[float], Optional[float]]:
    """
    解析薪资字符串，返回 (min_salary, max_salary) 单位：元/月

    支持格式：
    - "10-20万"           → (100000, 200000)
    - "10-20万/月"        → (100000, 200000)
    - "100万以上"         → (1000000, None)
    - "100万以下"         → (None, 1000000)
    - "20-50万"           → (200000, 500000)
    - "34-56"             → (34000, 56000)  (千元/月)
    - "面议"              → (None, None)
    - "3000-5000"         → (3000, 5000)
    - "8000"              → (8000, 8000)

    Args:
        salary_str: 薪资字符串

    Returns:
        (最小薪资, 最大薪资) 单位元/月，解析失败返回 (None, None)
    """
    if not salary_str or salary_str.strip() in ("", "面议", "薪资面议", "None", "none", "N/A"):
        return None, None

    salary_str = str(salary_str).strip()

    # 清理全角字符
    salary_str = salary_str.replace("＋", "+").replace("－", "-")

    # 处理 "XX万以上"
    m = re.match(r"^(\d+(?:\.\d+)?)\s*万以上?$", salary_str)
    if m:
        return float(m.group(1)) * 10000, None

    # 处理 "XX万以下"
    m = re.match(r"^(\d+(?:\.\d+)?)\s*万以下?$", salary_str)
    if m:
        return None, float(m.group(1)) * 10000

    # 处理 "XX-YY万" 或 "XX-YY万/月"
    m = re.match(r"^(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*万(?:月)?$", salary_str)
    if m:
        return float(m.group(1)) * 10000, float(m.group(2)) * 10000

    # 处理纯数字（如 "34-56" 或 "3000-5000"）
    # 如果数值小于1000，认为是千元单位
    m = re.match(r"^(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)$", salary_str)
    if m:
        min_val = float(m.group(1))
        max_val = float(m.group(2))
        # 小于1000的数值视为千元，即 34-56 → 34000-56000
        if min_val < 1000:
            return min_val * 1000, max_val * 1000
        return min_val, max_val

    # 处理单个数字 "3000" 或 "8000"
    m = re.match(r"^(\d+(?:\.\d+)?)$", salary_str)
    if m:
        val = float(m.group(1))
        if val < 1000:
            return val * 1000, val * 1000
        return val, val

    return None, None


def parse_salary_distribution(
    salary_ranges: List[str],
) -> List[Tuple[str, int]]:
    """
    将薪资字符串列表转换为分段分布统计

    分段标准：0-5k, 5k-10k, 10k-15k, 15k-20k, 20k-30k, 30k+

    Returns:
        [(分段名称, 数量)]
    """
    from collections import Counter

    BUCKETS = [
        (0, 5000, "0-5k"),
        (5000, 10000, "5k-10k"),
        (10000, 15000, "10k-15k"),
        (15000, 20000, "15k-20k"),
        (20000, 30000, "20k-30k"),
        (30000, float("inf"), "30k+"),
    ]

    counts = Counter()
    for salary_str in salary_ranges:
        min_sal, max_sal = parse_salary(salary_str)
        if min_sal is None and max_sal is None:
            continue

        # 落入对应分段
        for low, high, label in BUCKETS:
            if (min_sal or 0) <= high and (max_sal or float("inf")) >= low:
                counts[label] += 1
                break

    # 按分段顺序返回
    ordered = []
    for _, _, label in BUCKETS:
        if label in counts:
            ordered.append((label, counts[label]))
    return ordered


# 异常值过滤阈值（元/月）
SALARY_MIN = 1000    # 最低1千元
SALARY_MAX = 100000  # 最高10万元


def is_valid_salary(salary: float) -> bool:
    """判断薪资是否在合理范围内"""
    if salary is None:
        return False
    return SALARY_MIN <= salary <= SALARY_MAX
