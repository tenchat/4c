"""
行业归一化工具
将碎片化的行业关键词映射到标准行业分类
"""

from typing import Dict, List, Tuple
from collections import Counter


# 标准行业分类（10大类）
STANDARD_INDUSTRIES = [
    "人工智能",
    "金融",
    "制造业",
    "互联网",
    "医疗健康",
    "教育",
    "房地产",
    "交通运输",
    "能源",
    "政府/公共事业",
    "文化传媒",
    "电子信息",
    "化工",
    "建筑",
    "法律",
    "消费零售",
    "农林牧渔",
    "军工",
    "环保",
    "其他",
]

# 行业关键词映射表（覆盖常见的碎片化表述）
INDUSTRY_KEYWORDS: Dict[str, List[str]] = {
    "人工智能": [
        "人工智能", "AI", "智能制造", "智能硬件", "智能家居", "智能驾驶",
        "机器学习", "深度学习", "计算机视觉", "自然语言处理", "大数据",
        "云计算", "物联网", "区块链", "元宇宙", "虚拟现实", "AR", "VR",
        "算法", "芯片", "半导体", "集成电路",
    ],
    "互联网": [
        "互联网", "电子商务", "网络", "网游", "游戏", "社交", "视频",
        "直播", "短视频", "内容", "资讯", "广告", "营销", "SaaS", "PaaS",
        "IT", "软件", "信息服务", "网站", "APP", "移动互联网",
    ],
    "金融": [
        "金融", "银行", "证券", "保险", "投资", "基金", "信托", "资产管理",
        "期货", "外汇", "贵金属", "融资", "担保", "拍卖", "典当",
        "消费金融", "供应链金融", "金融科技", "FinTech", "支付", "清算",
    ],
    "制造业": [
        "制造", "制造业", "机械", "电子", "电气", "自动化", "装备制造",
        "汽车", "新能源汽车", "摩托车", "航空航天", "军工", "船舶",
        "轨道交通", "模具", "铸造", "焊接", "加工", "生产制造",
        "精密制造", "智能装备", "工业自动化", "工业机器人",
    ],
    "医疗健康": [
        "医疗", "医院", "医药", "生物", "制药", "器械", "设备",
        "健康管理", "养老", "康复", "美容", "整形", "保健",
        "医疗器械", "体外诊断", "基因", "疫苗", "中药", "西药",
        "医疗信息化", "互联网医疗", "远程医疗",
    ],
    "教育": [
        "教育", "培训", "学校", "院校", "高等教育", "职业教育",
        "K12", "中小学", "学前教育", "课外辅导", "家教",
        "在线教育", "教育科技", "教育信息化", "考试", "留学",
    ],
    "房地产": [
        "房地产", "房产", "物业", "建筑", "园林", "景观", "装潢",
        "装修", "家居", "建材", "厨卫", "地板", "门窗",
        "房地产开发", "物业管理", "房地产经纪", "建筑工程",
    ],
    "交通运输": [
        "交通", "运输", "物流", "仓储", "快递", "配送", "供应链",
        "航空", "机场", "铁路", "高铁", "地铁", "公交", "出租车",
        "航运", "港口", "码头", "道路", "桥梁", "隧道",
    ],
    "能源": [
        "能源", "电力", "电网", "石油", "天然气", "煤炭", "新能源",
        "太阳能", "光伏", "风电", "核电", "水电", "储能", "充电桩",
        "电网", "配电", "输配电", "电力设备", "电力工程",
    ],
    "政府/公共事业": [
        "政府", "机关", "事业单位", "公共事业", "公用事业", "市政",
        "城市", "乡镇", "街道", "社区", "非营利", "社会组织",
        "协会", "学会", "商会", "基金会",
    ],
    "文化传媒": [
        "文化", "传媒", "广告", "公关", "策划", "创意", "设计",
        "影视", "电影", "电视", "综艺", "音乐", "娱乐", "演出",
        "出版", "印刷", "发行", "动漫", "文创", "旅游", "酒店",
        "餐饮", "体育", "健身", "会展", "会议",
    ],
    "电子信息": [
        "电子", "通信", "电信", "运营商", "网络通信", "光通信",
        "微波", "射频", "天线", "PCB", "电子元器件", "电子材料",
        "电子设备", "仪器仪表", "传感器", "显示器", "触摸屏",
    ],
    "化工": [
        "化工", "化学", "石油化工", "精细化工", "新材料", "复合材料",
        "塑料", "橡胶", "纤维", "涂料", "油漆", "胶粘剂", "助剂",
        "石化", "煤化工", "盐化工", "林化工",
    ],
    "建筑": [
        "建筑", "建筑设计", "工程造价", "工程监理", "工程咨询",
        "勘察", "测绘", "岩土", "结构", "装饰", "幕墙", "钢结构",
        "土建", "给排水", "暖通", "电气", "消防", "智能化",
    ],
    "法律": [
        "法律", "律师", "法务", "律所", "公证", "鉴定", "仲裁",
        "法律咨询", "知识产权", "专利", "商标", "著作权",
    ],
    "消费零售": [
        "消费", "零售", "商贸", "批发", "分销", "代理", "加盟",
        "便利店", "超市", "商场", "购物中心", "百货", "专卖店",
        "母婴", "童装", "玩具", "家电", "数码", "手机", "电脑",
    ],
    "农林牧渔": [
        "农业", "林业", "牧业", "渔业", "畜牧", "养殖", "种植",
        "农产品", "农资企业", "农机", "种子", "化肥", "农药",
        "食品", "饮料", "烟酒", "粮油", "调味", "乳制品",
    ],
    "军工": [
        "军工", "国防", "航空航天", "兵器", "船舶", "核工业",
        "军用", "军品", "军贸", "军民融合", "航天", "航空", "航海",
    ],
    "环保": [
        "环保", "环境", "生态", "节能", "减排", "碳中和", "污水处理",
        "垃圾处理", "固废处理", "资源回收", "环境监测", "环境影响评价",
        "水处理", "大气治理", "土壤修复", "噪声治理",
    ],
    "其他": [],  # 未匹配到的归入其他
}


def normalize_industry(raw_industry: str) -> str:
    """
    将原始行业字符串归一化为标准行业分类

    Args:
        raw_industry: 原始行业字符串（如 "互联网/电子商务"）

    Returns:
        标准行业分类字符串
    """
    if not raw_industry or raw_industry.strip() == "":
        return "其他"

    raw = raw_industry.strip()

    # 精确匹配优先
    for standard, keywords in INDUSTRY_KEYWORDS.items():
        if raw == standard:
            return standard

    # 包含匹配
    for standard, keywords in INDUSTRY_KEYWORDS.items():
        if standard == "其他":
            continue
        for keyword in keywords:
            if keyword in raw or raw in keyword:
                return standard

    # 遍历所有关键词
    for standard, keywords in INDUSTRY_KEYWORDS.items():
        if standard == "其他":
            continue
        for keyword in keywords:
            if keyword in raw:
                return standard

    return "其他"


def batch_normalize_industries(raw_industries: List[str]) -> Dict[str, str]:
    """
    批量归一化行业

    Args:
        raw_industries: 原始行业列表

    Returns:
        {原始行业: 标准行业} 映射字典
    """
    mapping: Dict[str, str] = {}
    for raw in set(raw_industries):
        mapping[raw] = normalize_industry(raw)
    return mapping


def get_industry_distribution(
    raw_industries: List[str],
) -> List[Tuple[str, int]]:
    """
    获取归一化后的行业分布

    Args:
        raw_industries: 原始行业列表

    Returns:
        [(标准行业, 数量)] 列表，按数量降序
    """
    mapping = batch_normalize_industries(raw_industries)
    counter = Counter(mapping.values())
    return counter.most_common()


def extract_provincial_industry_keywords(
    data: List[dict],
) -> Dict[str, List[str]]:
    """
    按省份提取行业关键词（用于RAG分析）

    Args:
        data: [{"province": "北京", "industry": "互联网"}, ...]

    Returns:
        {省份: [不重复行业列表]}
    """
    from collections import defaultdict

    result: Dict[str, List[str]] = defaultdict(set)
    for item in data:
        province = item.get("province", "")
        industry = item.get("industry", "")
        if province and industry:
            result[province].add(industry)

    return {k: list(v) for k, v in result.items()}
