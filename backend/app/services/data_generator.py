"""
Data Generator Service - Generates synthetic student data based on college enrollment statistics
"""
import csv
import io
import random
import uuid
from datetime import datetime
from typing import Dict, List, Tuple

from sqlalchemy import select, func, and_, delete, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student import StudentProfile
from app.models.college_employment import CollegeEmployment
from app.models.account import Account
from app.core.config import get_settings


# ========== Skill Library ==========
SKILL_LIBRARY = {
    "technical": [
        "Python", "Java", "C++", "JavaScript", "TypeScript", "SQL", "MATLAB",
        "R", "SPSS", "Stata", "AWS", "Docker", "Kubernetes", "Git",
        "TensorFlow", "PyTorch", "Pandas", "NumPy", "Vue.js", "React",
        "Spring Boot", "Django", "Flask", "MySQL", "PostgreSQL", "MongoDB",
        "Redis", "Elasticsearch", "Hadoop", "Spark", "Flink"
    ],
    "business": [
        "项目管理", "数据分析", "市场分析", "财务分析", "人力资源管理",
        "商务谈判", "供应链管理", "质量管理", "风险管理", "战略规划"
    ],
    "soft": [
        "沟通能力", "团队协作", "问题解决", "时间管理", "领导力",
        "创新思维", "批判性思维", "适应能力", "学习能力", "执行力"
    ],
    "language": [
        "英语CET-6", "英语CET-4", "英语IELTS", "英语TOEFL",
        "日语N2", "日语N1", "德语", "法语", "韩语"
    ],
    "design": [
        "Photoshop", "Illustrator", "Sketch", "Figma", "AutoCAD",
        "UG NX", "SolidWorks", "3D Max", "Premiere", "After Effects"
    ],
    "other": [
        "驾驶执照", "教师资格证", "会计从业资格证", "证券从业资格证"
    ]
}

# ========== Province to Region Mapping ==========
PROVINCE_TO_REGION = {
    # East region (东部地区)
    "北京": "east", "天津": "east", "河北": "east", "辽宁": "east",
    "上海": "east", "江苏": "east", "浙江": "east", "福建": "east",
    "山东": "east", "广东": "east", "海南": "east",
    # Central region (中部地区)
    "山西": "central", "吉林": "central", "黑龙江": "central",
    "安徽": "central", "江西": "central", "河南": "central",
    "湖北": "central", "湖南": "central",
    # West-Chongqing (西部地区-重庆)
    "重庆": "west_chongqing",
    # West-Sichuan (西部地区-四川)
    "四川": "west_sichuan",
    # West-other (西部地区-其他省区)
    "西藏": "west_other", "青海": "west_other", "宁夏": "west_other",
    "新疆": "west_other", "甘肃": "west_other", "陕西": "west_other",
    "云南": "west_other", "贵州": "west_other", "内蒙古": "west_other",
    "广西": "west_other",
    # HMT (港澳台及其他)
    "香港": "hmt", "澳门": "hmt", "台湾": "hmt",
}

# Province distribution weights (based on national averages)
PROVINCE_WEIGHTS = {
    # East (35%)
    "广东": 8.9, "山东": 7.8, "河南": 7.0, "江苏": 5.8, "四川": 5.6,
    "河北": 5.2, "湖南": 4.8, "浙江": 4.2, "安徽": 4.0, "湖北": 3.9,
    "北京": 1.5, "上海": 1.6, "福建": 2.7, "辽宁": 3.1, "天津": 1.0,
    "海南": 0.7,
    # Central (25%)
    "陕西": 2.7, "云南": 3.0, "贵州": 2.5, "江西": 3.1, "山西": 2.4,
    "广西": 3.3, "甘肃": 1.9, "黑龙江": 2.5, "吉林": 2.0, "安徽": 3.5,
    "湖南": 4.5, "湖北": 4.2,
    # West-Chongqing (8%)
    "重庆": 2.3,
    # West-Sichuan (15%)
    "四川": 6.0,
    # West-other (12%)
    "西藏": 0.3, "青海": 0.4, "宁夏": 0.5, "新疆": 1.6, "甘肃": 1.8,
    "陕西": 2.8, "云南": 3.2, "贵州": 2.6, "内蒙古": 1.5, "广西": 3.0,
    # HMT (5%)
    "香港": 0.5, "澳门": 0.1, "台湾": 1.2,
}

# ========== College to Major Mapping ==========
COLLEGE_MAJORS = {
    "马克思主义学院": ["思想政治教育", "马克思主义理论"],
    "建筑城规学院": ["建筑学", "城乡规划", "风景园林", "环境设计"],
    "环境与生态学院": ["环境工程", "环境科学", "生态学", "资源与环境经济学"],
    "化学化工学院": ["化学", "应用化学", "化学工程与工艺", "过程装备与控制工程"],
    "艺术学院": ["艺术设计", "视觉传达设计", "产品设计", "数字媒体艺术"],
    "管理科学与房地产学院": ["工程管理", "工程造价", "房地产开发与管理", "物业管理"],
    "航空航天学院": ["航空航天工程", "飞行器设计与工程", "飞行器动力工程", "无人驾驶航空器系统工程"],
    "材料科学与工程学院": ["材料科学与工程", "材料成型及控制工程", "无机非金属材料工程", "高分子材料与工程"],
    "经济与工商管理学院": ["经济学", "金融学", "国际经济与贸易", "工商管理", "会计学", "财务管理"],
    "公共管理学院": ["公共事业管理", "行政管理", "土地资源管理", "城市管理"],
    "微电子与通信工程学院": ["微电子科学与工程", "电子科学与技术", "通信工程", "电子信息工程"],
    "计算机学院": ["计算机科学与技术", "软件工程", "信息安全", "数据科学与大数据技术", "人工智能"],
    "土木工程学院": ["土木工程", "给排水科学与工程", "建筑环境与能源应用工程", "城市地下空间工程"],
    "大数据与软件学院": ["软件工程", "数据科学与大数据技术", "人工智能", "计算机科学与技术"],
    "生命科学学院": ["生物科学", "生物技术", "生物工程", "食品科学与工程"],
    "机械与运载工程学院": ["机械设计制造及其自动化", "机械工程", "车辆工程", "工业设计", "机器人工程"],
    "资源与安全学院": ["资源科学与工程", "安全工程", "应急技术与管理", "职业卫生工程"],
    "生物工程学院": ["生物工程", "生物制药", "食品科学与工程", "酿酒工程"],
    "新闻学院": ["新闻学", "广播电视学", "传播学", "广告学", "播音与主持艺术"],
    "光电工程学院": ["光电信息科学与工程", "测控技术与仪器", "电子科学与技术", "微电子科学与工程"],
    "自动化学院": ["自动化", "电气工程及其自动化", "智能科学与技术", "物联网工程"],
    "数学与统计学院": ["数学与应用数学", "信息与计算科学", "统计学", "应用统计学"],
    "物理学院": ["物理学", "应用物理学", "材料物理", "光电信息科学与工程"],
    "药学院": ["药学", "临床药学", "药物制剂", "中药学", "生物制药"],
    "能源与动力工程学院": ["能源与动力工程", "新能源科学与工程", "储能科学与工程", "核工程与核技术"],
    "电气工程学院": ["电气工程及其自动化", "智能电网信息工程", "电工理论与新技术", "电气工程"],
    "体育学院": ["体育教育", "社会体育指导与管理", "运动训练", "休闲体育"],
    "美视电影学院": ["广播电视编导", "戏剧影视导演", "表演", "影视摄影与制作", "戏剧影视美术设计"],
    "外国语学院": ["英语", "日语", "德语", "法语", "翻译", "商务英语"],
    "博雅学院&人文社会科学高等研究院": ["哲学", "历史学", "社会学", "人类学", "政治学"],
    "医学院": ["临床医学", "口腔医学", "预防医学", "基础医学", "医学检验技术", "护理学"],
    "国家卓越工程师学院": ["计算机科学与技术", "软件工程", "电子信息工程", "机械工程", "材料工程"],
}

# ========== Company Names for Employed Students ==========
COMPANY_PREFIXES = [
    "腾讯", "阿里巴巴", "百度", "字节跳动", "美团", "京东", "华为", "小米",
    "OPPO", "vivo", "网易", "搜狐", "新浪", "360", "拼多多", "快手", "哔哩哔哩",
    "比亚迪", "吉利", "长城汽车", "长安汽车", "上汽集团", "一汽集团",
    "中国建筑", "中国铁建", "中国中铁", "中国交建", "中国电建",
    "国家电网", "南方电网", "中国石油", "中国石化", "中国海油",
    "招商银行", "工商银行", "建设银行", "中国银行", "交通银行",
    "平安保险", "中国人寿", "太平洋保险", "新华保险",
    "华润集团", "保利集团", "绿地集团", "万科集团", "融创中国",
    "海康威视", "大华股份", "三一重工", "中联重科", "徐工集团",
    "宁德时代", "比亚迪半导体", "中芯国际", "华星光电", "京东方",
    "迈瑞医疗", "药明康德", "恒瑞医药", "复星医药", "上海医药",
    "顺丰速运", "中通快递", "圆通速递", "韵达快递", "德邦快递",
]

COMPANY_SUFFIXES = [
    "科技有限公司", "技术有限公司", "软件技术有限公司", "信息技术有限公司",
    "电子科技有限公司", "通信技术有限公司", "网络技术有限公司",
    "工程设计有限公司", "工程建设有限公司", "建设工程有限公司",
    "咨询有限公司", "管理咨询有限公司", "财务咨询有限公司",
    "投资集团有限公司", "资本投资有限公司", "资产管理有限公司",
    "实业有限公司", "实业有限公司", "贸易实业有限公司",
    "制药有限公司", "医药有限公司", "生物科技有限公司",
    "汽车有限公司", "汽车制造有限公司", "新能源汽车有限公司",
]

# ========== City Lists ==========
CITIES = [
    "北京", "上海", "广州", "深圳", "杭州", "南京", "苏州", "无锡", "常州", "南通",
    "宁波", "温州", "嘉兴", "湖州", "绍兴", "金华", "衢州", "舟山", "台州", "丽水",
    "合肥", "芜湖", "蚌埠", "淮南", "马鞍山", "淮北", "铜陵", "安庆", "黄山", "阜阳",
    "福州", "厦门", "泉州", "漳州", "莆田", "宁德", "三明", "南平", "龙岩",
    "南昌", "景德镇", "九江", "赣州", "吉安", "宜春", "抚州", "上饶", "鹰潭", "新余",
    "济南", "青岛", "烟台", "威海", "潍坊", "淄博", "临沂", "济宁", "泰安", "德州",
    "郑州", "洛阳", "开封", "平顶山", "安阳", "新乡", "焦作", "许昌", "漯河", "三门峡",
    "武汉", "宜昌", "襄阳", "荆州", "荆门", "黄冈", "孝感", "咸宁", "随州", "恩施",
    "长沙", "株洲", "湘潭", "衡阳", "邵阳", "岳阳", "常德", "张家界", "益阳", "郴州",
    "重庆", "成都", "绵阳", "德阳", "宜宾", "南充", "泸州", "达州", "乐山", "内江",
    "西安", "宝鸡", "咸阳", "铜川", "渭南", "延安", "榆林", "汉中", "安康", "商洛",
    "昆明", "曲靖", "玉溪", "保山", "昭通", "丽江", "普洱", "临沧", "楚雄", "红河",
]

INDUSTRIES = [
    "互联网", "计算机软件", "电子/半导体", "通信/网络设备",
    "房地产/建筑", "金融/银行", "保险", "汽车/交通设备",
    "机械/装备制造", "化工", "医药生物", "教育培训",
    "批发/零售", "电力/能源", "政府/公共事业", "文化/传媒",
    "航空航天", "环保", "新材料", "现代农业",
]


class DataGenerator:
    """Generate random student data based on college enrollment statistics"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()
        self.university_id = self.settings.DEFAULT_UNIVERSITY_ID or "UNI001"

    def _parse_csv_data(self, csv_content: bytes) -> Dict[str, Dict]:
        """Parse college enrollment CSV data"""
        decoded = csv_content.decode("utf-8-sig", errors="replace")
        reader = csv.DictReader(io.StringIO(decoded))

        college_data = {}
        for row in reader:
            college_name = row.get("院系名称", "").strip()
            if not college_name:
                continue

            year = int(row.get("年份", 0))
            if year not in college_data:
                college_data[year] = {}

            # Parse undergraduate (本科) numbers
            bachelor_grad = self._parse_number(row.get("本科生毕业_毕业人数", "0"))
            bachelor_employed = self._parse_number(row.get("本科生毕业_就业数", "0"))

            # Parse master (硕士) numbers
            master_grad = self._parse_number(row.get("硕士生毕业_毕业人数", "0"))
            master_employed = self._parse_number(row.get("硕士生毕业_就业数", "0"))

            # Parse PhD (博士) numbers
            doctoral_grad = self._parse_number(row.get("博士生毕业_毕业人数", "0"))
            doctoral_employed = self._parse_number(row.get("博士生毕业_就业数", "0"))

            college_data[year][college_name] = {
                "bachelor": {"grad": bachelor_grad, "employed": bachelor_employed},
                "master": {"grad": master_grad, "employed": master_employed},
                "doctoral": {"grad": doctoral_grad, "employed": doctoral_employed},
            }

        return college_data

    def _parse_number(self, value: str) -> int:
        """Parse number from string, handling '-' as 0"""
        if not value or value == "-" or value == " ":
            return 0
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return 0

    def _generate_student_no(self, graduation_year: int, sequence: int) -> str:
        """Generate student number: year + 4-digit sequence"""
        return f"{graduation_year}{sequence:04d}"

    def _generate_gpa(self) -> str:
        """Generate GPA using normal distribution (mean=2.8, std=0.5)"""
        gpa = random.gauss(2.8, 0.5)
        gpa = max(1.0, min(4.0, gpa))  # Clip to [1.0, 4.0]
        return f"{gpa:.2f}"

    def _generate_skills(self) -> List[str]:
        """Generate random skills (5-15 skills)"""
        num_skills = random.randint(5, 15)
        all_skills = []

        # Get 2-4 technical skills
        tech_skills = random.sample(SKILL_LIBRARY["technical"], min(4, len(SKILL_LIBRARY["technical"])))
        all_skills.extend(random.sample(tech_skills, min(3, len(tech_skills))))

        # Get 1-3 business skills
        biz_skills = random.sample(SKILL_LIBRARY["business"], min(3, len(SKILL_LIBRARY["business"])))
        all_skills.extend(random.sample(biz_skills, min(2, len(biz_skills))))

        # Get 1-3 soft skills
        soft_skills = random.sample(SKILL_LIBRARY["soft"], min(3, len(SKILL_LIBRARY["soft"])))
        all_skills.extend(random.sample(soft_skills, min(2, len(soft_skills))))

        # Get 1-2 language skills
        lang_skills = random.sample(SKILL_LIBRARY["language"], min(2, len(SKILL_LIBRARY["language"])))
        all_skills.extend(random.sample(lang_skills, min(1, len(lang_skills))))

        # Add 0-2 other skills
        other_skills = random.sample(SKILL_LIBRARY["other"], min(2, len(SKILL_LIBRARY["other"])))
        all_skills.extend(random.sample(other_skills, min(1, len(other_skills))))

        return random.sample(all_skills, min(num_skills, len(all_skills)))

    def _generate_province(self) -> str:
        """Generate province based on national average distribution"""
        provinces = list(PROVINCE_WEIGHTS.keys())
        weights = list(PROVINCE_WEIGHTS.values())
        return random.choices(provinces, weights=weights, k=1)[0]

    def _get_region(self, province: str) -> str:
        """Map province to region"""
        return PROVINCE_TO_REGION.get(province, "west_other")

    def _generate_internship(self, employment_rate: float) -> str:
        """Generate internship status (60% have internship)"""
        if random.random() < 0.6:
            cities = ["北京", "上海", "深圳", "广州", "杭州", "成都", "重庆", "武汉", "南京"]
            return f"有|{random.choice(cities)}"
        return "无"

    def _generate_employment_status(self, employed_rate: float) -> int:
        """Generate employment status based on employment rate"""
        r = random.random()
        if r < employed_rate:
            return 1  # Employed
        elif r < employed_rate + 0.03:
            return 2  # Further study
        elif r < employed_rate + 0.05:
            return 3  # Abroad
        else:
            return 0  # Unemployed

    def _generate_company_info(self, employment_status: int) -> Tuple[str, str, str, int]:
        """Generate company info for employed students"""
        if employment_status != 1:
            return "", "", "", 0

        company = random.choice(COMPANY_PREFIXES) + random.choice(COMPANY_SUFFIXES)
        city = random.choice(CITIES)
        industry = random.choice(INDUSTRIES)
        # Salary: 5000-25000 based on degree
        salary = random.randint(5000, 25000)

        return company, city, industry, salary

    def _generate_major(self, college: str) -> str:
        """Generate major based on college"""
        majors = COLLEGE_MAJORS.get(college, ["专业未定"])
        return random.choice(majors)

    async def generate_students(
        self,
        csv_content: bytes,
        year: int = 2026,
        clear_existing: bool = False
    ) -> Dict:
        """Generate student records from CSV data"""

        # Parse CSV
        college_data = self._parse_csv_data(csv_content)

        if year not in college_data:
            return {"success": False, "error": f"No data for year {year}"}

        # Clear existing student profiles for this year if requested
        if clear_existing:
            await self.db.execute(
                delete(StudentProfile).where(
                    and_(
                        StudentProfile.university_id == self.university_id,
                        StudentProfile.graduation_year == year
                    )
                )
            )
            await self.db.commit()

        # Generate students for each college
        generated = 0
        student_counts = {}  # {college: {degree: count}}

        for college_name, degree_data in college_data[year].items():
            student_counts[college_name] = {}

            for degree_level, counts in degree_data.items():
                grad_count = counts["grad"]
                employed_count = counts["employed"]

                if grad_count == 0:
                    continue

                # Calculate employment rate for this college/degree
                employment_rate = employed_count / grad_count if grad_count > 0 else 0.9

                # Map degree level to integer
                degree_map = {"bachelor": 1, "master": 2, "doctoral": 3}
                degree_int = degree_map.get(degree_level, 1)

                student_counts[college_name][degree_level] = grad_count

                # Generate students for this college/degree
                sequence = 1
                for i in range(grad_count):
                    student_no = self._generate_student_no(year, sequence)
                    province = self._generate_province()
                    employment_status = self._generate_employment_status(employment_rate)
                    cur_company, cur_city, cur_industry, cur_salary = self._generate_company_info(employment_status)

                    profile = StudentProfile(
                        profile_id=str(uuid.uuid4()),
                        account_id=None,
                        university_id=self.university_id,
                        student_no=student_no,
                        college=college_name,
                        major=self._generate_major(college_name),
                        degree=degree_int,
                        graduation_year=year,
                        province_origin=province,
                        gpa=self._generate_gpa(),
                        skills=self._generate_skills(),
                        internship=self._generate_internship(employment_rate),
                        employment_status=employment_status,
                        desire_city=random.choice(CITIES),
                        desire_industry=random.choice(INDUSTRIES),
                        desire_salary_min=random.randint(5000, 10000),
                        desire_salary_max=random.randint(10000, 30000),
                        cur_company=cur_company,
                        cur_city=cur_city,
                        cur_industry=cur_industry,
                        cur_salary=cur_salary if employment_status == 1 else 0,
                        resume_url=f"/uploads/resumes/{student_no}.pdf",
                        profile_complete=random.randint(60, 95),
                    )
                    self.db.add(profile)
                    generated += 1
                    sequence += 1

                    # Batch commit every 500 records
                    if generated % 500 == 0:
                        await self.db.commit()

        await self.db.commit()

        # Update college_employment and regional_flow
        await self._sync_college_employment(year)
        await self._sync_regional_flow(year)

        return {
            "success": True,
            "generated": generated,
            "student_counts": student_counts,
        }

    async def _sync_college_employment(self, year: int) -> None:
        """Sync college_employment table from student_profiles"""
        # Delete existing records for this year
        await self.db.execute(
            delete(CollegeEmployment).where(
                and_(
                    CollegeEmployment.university_id == self.university_id,
                    CollegeEmployment.graduation_year == year
                )
            )
        )
        await self.db.commit()

        # Aggregate from student_profiles
        result = await self.db.execute(
            select(
                StudentProfile.college,
                StudentProfile.degree,
                func.count(StudentProfile.profile_id).label("total"),
                func.sum(
                    case((StudentProfile.employment_status == 1, 1), else_=0)
                ).label("employed"),
                func.sum(
                    case((StudentProfile.employment_status == 2, 1), else_=0)
                ).label("further_study"),
                func.sum(
                    case((StudentProfile.employment_status == 3, 1), else_=0)
                ).label("overseas"),
            )
            .where(
                and_(
                    StudentProfile.university_id == self.university_id,
                    StudentProfile.graduation_year == year
                )
            )
            .group_by(StudentProfile.college, StudentProfile.degree)
        )

        degree_level_map = {1: "本科生", 2: "硕士生", 3: "博士生"}

        for row in result.all():
            college_name = row.college
            degree_level = degree_level_map.get(row.degree, "本科生")
            total = row.total or 0
            employed = row.employed or 0
            further_study = row.further_study or 0
            overseas = row.overseas or 0

            employment_rate = (employed / total * 100) if total > 0 else 0
            further_study_rate = (further_study / total * 100) if total > 0 else 0
            overseas_rate = (overseas / total * 100) if total > 0 else 0

            record = CollegeEmployment(
                record_id=str(uuid.uuid4()),
                university_id=self.university_id,
                college_name=college_name,
                graduation_year=year,
                degree_level=degree_level,
                graduation_type="毕业",
                graduate_nums=total,
                employed_nums=employed,
                contract_nums=int(employed * 0.6),  # Assume 60% signed contract
                total_graduate_school_nums=further_study + overseas,
                domestic_graduate_school_nums=further_study,
                overseas_graduate_school_nums=overseas,
                employment_rate=employment_rate,
                further_study_nums=further_study,
                further_study_rate=further_study_rate,
                overseas_nums=overseas,
                overseas_rate=overseas_rate,
                avg_salary=8000 + (row.degree * 2000 if row.degree else 2000),  # Estimate
            )
            self.db.add(record)

        await self.db.commit()

    async def _sync_regional_flow(self, year: int) -> None:
        """Sync regional_flow table from student_profiles"""
        # Import here to avoid circular import
        from app.models.regional_flow import RegionalFlow

        # Delete existing records for this year
        await self.db.execute(
            delete(RegionalFlow).where(
                and_(
                    RegionalFlow.university_id == self.university_id,
                    RegionalFlow.graduation_year == year
                )
            )
        )
        await self.db.commit()

        # Aggregate from student_profiles by province
        result = await self.db.execute(
            select(
                StudentProfile.province_origin,
                func.count(StudentProfile.profile_id).label("count"),
            )
            .where(
                and_(
                    StudentProfile.university_id == self.university_id,
                    StudentProfile.graduation_year == year,
                    StudentProfile.province_origin.isnot(None),
                )
            )
            .group_by(StudentProfile.province_origin)
        )

        # Initialize region counts
        regions = {
            "east": 0,
            "central": 0,
            "west_chongqing": 0,
            "west_sichuan": 0,
            "west_other": 0,
            "hmt": 0,
        }

        # Aggregate by region
        for row in result.all():
            province = row.province_origin
            count = row.count or 0
            region = self._get_region(province)
            regions[region] = regions.get(region, 0) + count

        total = sum(regions.values())

        record = RegionalFlow(
            record_id=str(uuid.uuid4()),
            university_id=self.university_id,
            degree_level="本科毕业生",
            graduation_year=year,
            east_nums=regions["east"],
            central_nums=regions["central"],
            west_chongqing_nums=regions["west_chongqing"],
            west_sichuan_nums=regions["west_sichuan"],
            west_other_nums=regions["west_other"],
            hmt_nums=regions["hmt"],
            total_nums=total,
        )
        self.db.add(record)

        # Also create record for graduate students (硕士+博士 combined)
        master_phd_record = RegionalFlow(
            record_id=str(uuid.uuid4()),
            university_id=self.university_id,
            degree_level="毕业研究生",
            graduation_year=year,
            east_nums=int(regions["east"] * 0.4),
            central_nums=int(regions["central"] * 0.4),
            west_chongqing_nums=int(regions["west_chongqing"] * 0.4),
            west_sichuan_nums=int(regions["west_sichuan"] * 0.4),
            west_other_nums=int(regions["west_other"] * 0.4),
            hmt_nums=int(regions["hmt"] * 0.4),
            total_nums=int(total * 0.4),
        )
        self.db.add(master_phd_record)

        await self.db.commit()


async def generate_data_from_csv(db: AsyncSession, csv_content: bytes, year: int = 2026) -> Dict:
    """Main entry point for data generation"""
    generator = DataGenerator(db)
    return await generator.generate_students(csv_content, year)
