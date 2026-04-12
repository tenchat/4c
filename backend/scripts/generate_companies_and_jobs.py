"""
批量生成企业账号、公司信息和岗位数据
行业覆盖：互联网/IT、金融、教育、制造业、房地产、医疗健康、政府/事业单位
"""
import sqlite3
import uuid
import random
import hashlib
import json
import sys
import os
from datetime import datetime, timedelta

# 添加 backend 路径以导入 bcrypt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DB_PATH = r"f:\repos\art-design-pro\backend\employment.db"


def get_password_hash(password: str) -> str:
    """使用 bcrypt 生成密码哈希"""
    return pwd_context.hash(password)


# 各行业数据 (使用英文 key)
INDUSTRIES = {
    "internet": {
        "companies": [
            "腾讯科技", "阿里巴巴", "字节跳动", "百度在线", "京东科技",
            "网易网络", "美团网络", "拼多多", "快手科技", "滴滴出行",
            "小米通讯", "华为技术", "OPPO移动通信", "vivo移动通信", "海尔家电",
            "格力电器", "海尔智家", "海信电器", "TCL科技", "创维数字",
            "联想集团", "华硕电脑", "戴尔中国", "惠普中国", "英特尔中国",
            "微软中国", "IBM中国", "甲骨文中国", "SAP中国", "思爱普中国",
            "中兴通讯", "烽火通信", "京东方", "华星光电", "维信诺",
            "三六零安全", "奇安信", "启明星辰", "深信服", "安恒信息",
            "晶盛机电", "中微公司", "北方华创", "长川科技", "华大九天",
            "芯原股份", "寒武纪", "地平线机器人", "商汤科技", "旷视科技",
            "云从科技", "依图科技", "第四范式", "竹间智能", "追一科技",
            "携程旅行", "去哪儿网", "同程旅行", "马蜂窝", "途牛旅游",
            "Keep", "咕咚运动", "悦跑圈", "Fiture", "华为健康",
            "平安好医生", "丁香园", "微医集团", "好大夫在线", "医联",
            "叮当快药", "阿里健康", "京东健康", "腾讯健康", "百度健康",
            "完美世界", "盛趣游戏", "网易游戏", "米哈游", "莉莉丝游戏",
            "鹰角网络", "叠纸游戏", "西山居", "游族网络", "三七互娱",
        ],
        "jobs": [
            "Java开发工程师", "Python开发工程师", "前端开发工程师", "后端开发工程师",
            "全栈工程师", "算法工程师", "AI工程师", "数据工程师",
            "架构师", "技术经理", "产品经理", "UI设计师", "UX设计师",
            "测试工程师", "运维工程师", "DBA", "网络安全工程师",
            "项目经理", "实施工程师", "技术支持工程师",
        ]
    },
    "finance": {
        "companies": [
            "中国工商银行", "中国建设银行", "中国农业银行", "中国银行", "交通银行",
            "招商银行", "浦发银行", "中信银行", "兴业银行", "民生银行",
            "华夏银行", "平安银行", "浙商银行", "恒丰银行", "广发银行",
            "中国人寿", "中国平安", "中国太保", "新华保险", "泰康保险",
            "中国人保", "中华联合保险", "阳光保险", "友邦保险", "太平保险",
            "中信证券", "国泰君安", "海通证券", "广发证券", "招商证券",
            "华泰证券", "申万宏源", "银河证券", "中信建投", "中金公司",
            "华夏基金", "易方达基金", "博时基金", "嘉实基金", "南方基金",
            "汇添富基金", "工银瑞信", "广发基金", "富国基金", "招商基金",
            "蚂蚁集团", "京东金融", "陆金所", "微众银行", "网商银行",
            "京东科技", "360数科", "携程金融", "小米金融", "网易金融",
        ],
        "jobs": [
            "投资顾问", "理财经理", "客户经理", "风控专员", "合规专员",
            "审计专员", "产品经理", "数据分析", "量化研究员", "交易员",
            "保险顾问", "核保专员", "理赔专员", "资产管理", "基金经理",
            "行业研究员", "投行经理", "保荐代表人", "并购顾问", "法务专员",
        ]
    },
    "education": {
        "companies": [
            "新东方教育", "好未来教育", "学而思教育", "猿辅导教育", "作业帮教育",
            "一起教育", "VIPKID", "51Talk", "流利说", "英语流利说",
            "高途教育", "跟谁学", "有道教育", "沪江教育", "新航道教育",
            "启德教育", "金吉列留学", "澳际教育", "新通留学", "留学中介",
            "中公教育", "华图教育", "粉笔教育", "导氮教育", "华晟教育",
            "华大教育", "学大教育", "精锐教育", "昂立教育", "卓越教育",
            "北京学而思", "上海学而思", "广州学而思", "深圳学而思", "杭州学而思",
            "清华大学出版社", "高等教育出版社", "人民教育出版社", "北京师范大学出版社", "华东师范大学出版社",
        ],
        "jobs": [
            "英语教师", "数学教师", "语文教师", "物理教师", "化学教师",
            "生物教师", "历史教师", "地理教师", "政治教师", "音乐教师",
            "美术教师", "体育教师", "编程教师", "课程顾问", "学习规划师",
            "班主任", "教学主管", "教研员", "产品经理", "运营专员",
        ]
    },
    "manufacturing": {
        "companies": [
            "中国石油", "中国石化", "中国建筑", "中国中铁", "中国铁建",
            "中国交建", "中国建筑", "中国电建", "中国能建", "中国化学",
            "宝武钢铁", "河钢集团", "沙钢集团", "鞍钢集团", "首钢集团",
            "上汽集团", "一汽集团", "东风汽车", "长安汽车", "北汽集团",
            "吉利汽车", "长城汽车", "比亚迪汽车", "蔚来汽车", "小鹏汽车",
            "理想汽车", "威马汽车", "哪吒汽车", "零跑汽车", "广汽集团",
            "中国中车", "中国商飞", "航天科工", "航天科技", "航空工业",
            "中国船舶", "中国重工", "振华重工", "三一重工", "中联重科",
            "徐工集团", "柳工集团", "临工集团", "山河智能", "北方股份",
            "海尔集团", "美的集团", "格力电器", "海信集团", "TCL集团",
        ],
        "jobs": [
            "机械工程师", "电气工程师", "工艺工程师", "质量工程师", "采购工程师",
            "生产管理", "设备工程师", "模具工程师", "工装工程师", "项目工程师",
            "研发工程师", "材料工程师", "化工工程师", "冶金工程师", "能源工程师",
            "汽车工程师", "发动机工程师", "底盘工程师", "车身工程师", "电气工程师",
        ]
    },
    "real_estate": {
        "companies": [
            "万科地产", "碧桂园", "恒大地产", "融创中国", "保利发展",
            "中海地产", "华润置地", "招商蛇口", "龙湖集团", "金地集团",
            "绿城中国", "中国金茂", "阳光城", "中南建设", "蓝光发展",
            "世茂集团", "华夏幸福", "荣盛发展", "新城控股", "旭辉控股",
            "正荣地产", "中梁控股", "祥生集团", "美的置业", "禹洲集团",
            "宝龙地产", "弘阳地产", "新力控股", "大唐地产", "海伦堡",
            "贝壳找房", "链家地产", "中原地产", "我爱我家", "Q房网",
            "自如寓", "蛋壳公寓", "万科物业", "碧桂园服务", "融创服务",
        ],
        "jobs": [
            "置业顾问", "房产经纪人", "销售经理", "策划专员", "渠道专员",
            "拓展经理", "招商经理", "运营经理", "物业经理", "客服专员",
            "工程造价", "预算工程师", "招投标专员", "资料员", "施工员",
            "安全员", "质量员", "材料员", "测量员", "试验员",
        ]
    },
    "healthcare": {
        "companies": [
            "恒瑞医药", "石药集团", "中国生物制药", "复星医药", "上海医药",
            "九州药业", "泰格医药", "药明康德", "药明生物", "康龙化成",
            "凯莱英", "博腾股份", "九洲药业", "博瑞医药", "华海药业",
            "迈瑞医疗", "联影医疗", "西门子医疗", "GE医疗", "飞利浦医疗",
            "新华医疗", "鱼跃医疗", "三诺医疗", "乐普医疗", "微创医疗",
            "威高集团", "蓝帆医疗", "英科医疗", "振德医疗", "稳健医疗",
            "阿里健康", "京东健康", "平安好医生", "丁香园", "微医集团",
            "华大基因", "金域医学", "迪安诊断", "艾迪康", "达安基因",
            "爱尔眼科", "通策医疗", "美年健康", "瑞尔齿科", "拜博口腔",
        ],
        "jobs": [
            "医药代表", "医疗器械销售", "医学经理", "临床监查员", "医学顾问",
            "学术推广", "产品经理", "市场专员", "商务经理", "政府事务",
            "研发工程师", "制剂工程师", "质量工程师", "生产工程师", "验证工程师",
            "执业药师", "药剂师", "检验师", "放射技师", "康复治疗师",
        ]
    },
    "government": {
        "companies": [
            "中国科学院", "中国社会科学院", "中国农业科学院", "中国医学科学院",
            "国家图书馆", "中国美术馆", "中国博物馆", "国家博物馆", "故宫博物院",
            "中国气象局", "国家地震局", "国家海洋局", "国家测绘局", "国家林业局",
            "中国航天科技", "中国航天科工", "中国航空工业", "中国兵器工业", "中国船舶重工",
            "国家电网", "南方电网", "中国华能", "中国华电", "大唐集团",
            "中国电信", "中国移动", "中国联通", "中国铁塔", "中国广电",
            "中科院计算所", "中科院物理所", "中科院化学所", "中科院生物所", "中科院数学所",
            "北京大学医院", "清华大学医院", "复旦大学附属医院", "上海交通大学医学院", "浙江大学医学院",
        ],
        "jobs": [
            "行政专员", "人事专员", "财务专员", "党务专员", "文秘",
            "档案管理员", "后勤管理", "资产管理", "统计员", "审计员",
            "政策研究员", "项目申报", "科技管理", "宣传教育", "纪检监察",
            "科研助理", "实验技术", "数据分析师", "网络管理员", "系统管理员",
        ]
    }
}

# 城市数据
CITIES = [
    ("北京", "华北"), ("上海", "华东"), ("深圳", "华南"), ("广州", "华南"),
    ("杭州", "华东"), ("南京", "华东"), ("苏州", "华东"), ("无锡", "华东"),
    ("宁波", "华东"), ("温州", "华东"), ("嘉兴", "华东"), ("湖州", "华东"),
    ("成都", "西南"), ("重庆", "西南"), ("昆明", "西南"), ("贵阳", "西南"),
    ("西安", "西北"), ("兰州", "西北"), ("乌鲁木齐", "西北"), ("银川", "西北"),
    ("武汉", "华中"), ("长沙", "华中"), ("郑州", "华中"), ("合肥", "华中"),
    ("南昌", "华中"), ("济南", "华东"), ("青岛", "华东"), ("烟台", "华东"),
    ("天津", "华北"), ("石家庄", "华北"), ("太原", "华北"), ("呼和浩特", "华北"),
    ("大连", "东北"), ("沈阳", "东北"), ("长春", "东北"), ("哈尔滨", "东北"),
    ("福州", "华东"), ("厦门", "华东"), ("泉州", "华东"), ("珠海", "华南"),
    ("东莞", "华南"), ("佛山", "华南"), ("中山", "华南"), ("惠州", "华南"),
]

# 公司规模
SIZES = ["50人以下", "50-100人", "100-200人", "200-500人", "500-1000人", "1000人以上"]

# 薪资范围 (单位：元/月)
SALARY_RANGES = [
    (4000, 8000), (6000, 10000), (8000, 15000), (10000, 20000),
    (15000, 25000), (20000, 35000), (25000, 40000), (30000, 50000),
]

# 学历要求
DEGREE_REQS = [1, 1, 1, 2, 2, 3]  # 1=本科, 2=硕士, 3=博士，权重分布


def generate_job_description(company_id: str, industry: str, city: str) -> dict:
    """生成单个岗位数据"""
    jobs = []
    for ind, data in INDUSTRIES.items():
        if ind == industry:
            jobs = data["jobs"]
            break

    if not jobs:
        jobs = ["销售代表", "市场专员", "行政助理", "客服专员", "运营专员"]

    min_salary, max_salary = random.choice(SALARY_RANGES)
    min_degree = random.choice(DEGREE_REQS)

    keywords_list = [
        ["Python", "Django", "Flask"],
        ["Java", "Spring", "MySQL"],
        ["JavaScript", "Vue", "React"],
        ["数据分析", "Python", "SQL"],
        ["机器学习", "深度学习", "TensorFlow"],
        ["项目管理", "沟通能力", "团队协作"],
        ["沟通能力", "客户服务", "Office"],
        ["CAD", "SolidWorks", "机械设计"],
    ]

    province = next((p for p, d in CITIES if p == city), "北京")

    return {
        "job_id": str(uuid.uuid4()),
        "company_id": company_id,
        "title": random.choice(jobs),
        "city": city,
        "province": province,
        "industry": industry,
        "min_salary": min_salary,
        "max_salary": max_salary,
        "min_degree": min_degree,
        "min_exp_years": random.randint(0, 5),
        "keywords": json.dumps(random.choice(keywords_list), ensure_ascii=False),
        "description": f"诚聘{industry}{random.choice(jobs)}，福利待遇优厚，工作环境好，职业发展空间大。",
        "status": 1,
        "published_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "expired_at": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S"),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def main():
    print("=" * 60)
    print("开始生成企业账号、公司信息和岗位数据...")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 统计现有数据
    cursor.execute("SELECT COUNT(*) FROM accounts WHERE role = 'company_admin'")
    existing = cursor.fetchone()[0]
    print(f"\n现有企业账号数量: {existing}")

    # 收集要插入的数据
    accounts = []
    companies = []
    jobs = []

    total_companies = 0

    # 按行业生成公司
    for industry, data in INDUSTRIES.items():
        company_names = data["companies"]

        for company_name in company_names:
            # 生成唯一用户名
            username = f"company_{uuid.uuid4().hex[:8]}"

            # 创建账号
            account_id = str(uuid.uuid4())
            password_hash = get_password_hash("123456")  # 默认密码 123456

            accounts.append((
                account_id,
                username,
                password_hash,
                company_name,
                None,  # email
                None,  # phone
                "company_admin",
                1,  # status = 1 (approved)
                0,  # login_attempts
                None,  # locked_until
                None,  # last_login
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ))

            # 创建公司
            city, _ = random.choice(CITIES)
            company_id = str(uuid.uuid4())
            size = random.choice(SIZES)

            companies.append((
                company_id,
                account_id,
                company_name,
                industry,
                city,
                size,
                f"{company_name}是一家专注于{industry}的知名企业",
                None,  # address
                None,  # email
                None,  # contact
                None,  # contact_phone
                1,  # verified
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ))

            # 为每个公司生成多个岗位
            num_jobs = random.randint(5, 15)
            for _ in range(num_jobs):
                job = generate_job_description(company_id, industry, city)
                jobs.append(tuple(job.values()))

            total_companies += 1

    # 批量插入账号
    print(f"\n正在插入 {len(accounts)} 个企业账号...")
    cursor.executemany("""
        INSERT INTO accounts (account_id, username, password_hash, real_name, email, phone,
                            role, status, login_attempts, locked_until, last_login, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, accounts)

    # 批量插入公司
    print(f"正在插入 {len(companies)} 个公司信息...")
    cursor.executemany("""
        INSERT INTO companies (company_id, account_id, company_name, industry, city, size,
                             description, address, email, contact, contact_phone, verified, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, companies)

    # 批量插入岗位
    print(f"正在插入 {len(jobs)} 个岗位信息...")
    cursor.executemany("""
        INSERT INTO job_descriptions (job_id, company_id, title, city, province, industry,
                                     min_salary, max_salary, min_degree, min_exp_years, keywords,
                                     description, status, published_at, expired_at, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, jobs)

    conn.commit()

    # 验证插入结果
    cursor.execute("SELECT COUNT(*) FROM accounts WHERE role = 'company_admin'")
    total_accounts = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM companies")
    total_companies_db = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM job_descriptions")
    total_jobs = cursor.fetchone()[0]

    print("\n" + "=" * 60)
    print("数据生成完成！")
    print("=" * 60)
    print(f"企业账号总数: {total_accounts} (新增: {total_accounts - existing})")
    print(f"公司总数: {total_companies_db}")
    print(f"岗位总数: {total_jobs}")

    # 按行业统计
    print("\n按行业统计:")
    cursor.execute("""
        SELECT industry, COUNT(*) as cnt
        FROM companies
        GROUP BY industry
        ORDER BY cnt DESC
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} 家公司")

    conn.close()
    print("\n默认密码: 123456")
    print("请使用账号登录后修改密码。")


if __name__ == "__main__":
    main()
