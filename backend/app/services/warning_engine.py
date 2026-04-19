"""
就业预警评分引擎
根据学生档案数据计算预警评分，生成预警记录
"""

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.student import StudentProfile
from app.models.employment_warning import EmploymentWarning
from app.models.account import Account
from datetime import datetime, date
from typing import Tuple, List, Dict, Optional
import uuid
import logging

logger = logging.getLogger(__name__)


class WarningEngine:
    """就业预警评分引擎"""

    # 预警类型常量
    TYPE_LONG_TERM_UNEMPLOYED = "long_term_unemployed"      # 长期未就业
    TYPE_SKILL_GAP = "skill_gap"                            # 技能差距
    TYPE_HIGH_EXPECTATION = "high_expectation"              # 期望过高
    TYPE_LOCATION_LIMIT = "location_limit"                   # 地域限制
    TYPE_EXPERIENCE_LACK = "experience_lack"                # 经验缺乏
    TYPE_PROFILE_INCOMPLETE = "profile_incomplete"          # 档案不完整

    # 预警级别
    LEVEL_RED = 1    # 红色预警
    LEVEL_YELLOW = 2  # 黄色预警
    LEVEL_GREEN = 3   # 绿色提醒

    # 评分阈值
    SCORE_RED_THRESHOLD = 60    # 红色预警阈值
    SCORE_YELLOW_THRESHOLD = 30  # 黄色预警阈值
    SCORE_GREEN_THRESHOLD = 10   # 绿色提醒阈值

    # 评分权重
    WEIGHTS = {
        "employment_status": 40,    # 待就业时长
        "profile_complete": 15,     # 简历完整度
        "skills": 10,              # 技能数量
        "internship": 10,          # 实习经历
        "salary_expectation": 10,  # 薪资期望
        "location": 10,            # 地域偏好
        "gpa": 5,                 # 学业表现
    }

    # 期望薪资市场参考 (月薪，单位：元)
    MARKET_SALARY_REF = {
        "本科": 8000,
        "硕士": 12000,
        "博士": 18000,
    }

    # 一线城市列表
    TIER_ONE_CITIES = ["北京", "上海", "广州", "深圳", "新一线城市"]

    def __init__(self, db: AsyncSession):
        self.db = db

    def calculate_score(self, student: StudentProfile) -> Tuple[int, List[str], Dict]:
        """
        计算单个学生的预警评分

        Returns:
            (总分, 预警类型列表, 各维度得分详情)
        """
        dimension_scores = {}
        warning_types = []

        # 1. 待就业时长评分
        score_employment = self._calc_employment_score(student)
        dimension_scores["employment_status"] = score_employment
        if score_employment >= self.WEIGHTS["employment_status"]:
            warning_types.append(self.TYPE_LONG_TERM_UNEMPLOYED)

        # 2. 简历完整度评分
        score_profile = self._calc_profile_score(student)
        dimension_scores["profile_complete"] = score_profile
        if score_profile >= self.WEIGHTS["profile_complete"]:
            warning_types.append(self.TYPE_PROFILE_INCOMPLETE)

        # 3. 技能数量评分
        score_skills = self._calc_skills_score(student)
        dimension_scores["skills"] = score_skills
        if score_skills >= self.WEIGHTS["skills"]:
            warning_types.append(self.TYPE_SKILL_GAP)

        # 4. 实习经历评分
        score_internship = self._calc_internship_score(student)
        dimension_scores["internship"] = score_internship
        if score_internship >= self.WEIGHTS["internship"]:
            warning_types.append(self.TYPE_EXPERIENCE_LACK)

        # 5. 薪资期望评分
        score_salary = self._calc_salary_score(student)
        dimension_scores["salary_expectation"] = score_salary
        if score_salary >= self.WEIGHTS["salary_expectation"]:
            warning_types.append(self.TYPE_HIGH_EXPECTATION)

        # 6. 地域偏好评分
        score_location = self._calc_location_score(student)
        dimension_scores["location"] = score_location
        if score_location >= self.WEIGHTS["location"]:
            warning_types.append(self.TYPE_LOCATION_LIMIT)

        # 7. GPA评分
        score_gpa = self._calc_gpa_score(student)
        dimension_scores["gpa"] = score_gpa

        # 计算总分
        total_score = sum(dimension_scores.values())

        return total_score, warning_types, dimension_scores

    def _calc_employment_score(self, student: StudentProfile) -> int:
        """
        计算待就业时长得分
        40分: 待就业状态且毕业>=3个月
        20分: 待就业状态且毕业<3个月
        0分: 已就业或其他状态
        """
        if student.employment_status != 0:
            return 0

        if not student.graduation_year:
            return self.WEIGHTS["employment_status"] // 2

        # 计算待就业月数
        grad_year = student.graduation_year
        current_year = date.today().year
        months_since_grad = (current_year - grad_year) * 12

        if months_since_grad >= 3:
            return self.WEIGHTS["employment_status"]
        elif months_since_grad >= 1:
            return self.WEIGHTS["employment_status"] // 2
        else:
            return 0

    def _calc_profile_score(self, student: StudentProfile) -> int:
        """
        计算简历完整度得分
        15分: 完整度 < 50%
        10分: 完整度 50-70%
        5分: 完整度 70-90%
        0分: 完整度 >= 90%
        """
        complete = student.profile_complete or 0

        if complete < 50:
            return self.WEIGHTS["profile_complete"]
        elif complete < 70:
            return self.WEIGHTS["profile_complete"] * 2 // 3
        elif complete < 90:
            return self.WEIGHTS["profile_complete"] // 3
        else:
            return 0

    def _calc_skills_score(self, student: StudentProfile) -> int:
        """
        计算技能数量得分
        10分: 无技能或仅有1项
        5分: 2-3项技能
        0分: 4项以上
        """
        skills = student.skills
        if not skills or len(skills) < 2:
            return self.WEIGHTS["skills"]
        elif len(skills) <= 3:
            return self.WEIGHTS["skills"] // 2
        else:
            return 0

    def _calc_internship_score(self, student: StudentProfile) -> int:
        """
        计算实习经历得分
        10分: 无实习经历
        0分: 有实习经历
        """
        internship = student.internship
        if not internship or internship.strip() == "":
            return self.WEIGHTS["internship"]
        return 0

    def _calc_salary_score(self, student: StudentProfile) -> int:
        """
        计算薪资期望得分
        10分: 期望薪资 > 市场参考价 50%
        5分: 期望薪资 > 市场参考价 20%
        0分: 期望合理
        """
        if not student.desire_salary_max or student.desire_salary_max <= 0:
            return self.WEIGHTS["salary_expectation"] // 2

        # 根据学历获取市场参考价
        degree_ref = {1: 8000, 2: 12000, 3: 18000}
        market_ref = degree_ref.get(student.degree, 8000)

        # 期望薪资与市场参考价比较
        ratio = student.desire_salary_max / market_ref if market_ref > 0 else 1

        if ratio > 1.5:
            return self.WEIGHTS["salary_expectation"]
        elif ratio > 1.2:
            return self.WEIGHTS["salary_expectation"] // 2
        else:
            return 0

    def _calc_location_score(self, student: StudentProfile) -> int:
        """
        计算地域偏好得分
        10分: 仅一线城市 + 非本地生源
        5分: 仅一线城市 + 本地生源
        0分: 地域选择多元化
        """
        desire_city = student.desire_city or ""
        province_origin = student.province_origin or ""

        # 检查是否只选择了一线城市
        is_tier_one_only = any(city in desire_city for city in self.TIER_ONE_CITIES)

        if is_tier_one_only:
            # 判断是否为本地生源 (假设省份相同即为本地)
            is_local = province_origin and province_origin in desire_city
            if not is_local:
                return self.WEIGHTS["location"]
            else:
                return self.WEIGHTS["location"] // 2
        return 0

    def _calc_gpa_score(self, student: StudentProfile) -> int:
        """
        计算GPA得分
        5分: GPA < 2.5 (5分制)
        3分: GPA 2.5-3.0 (5分制)
        0分: GPA >= 3.0
        """
        gpa = student.gpa
        if not gpa:
            return self.WEIGHTS["gpa"] // 2  # 无GPA记录给一半分数

        try:
            gpa_value = float(gpa)
            if gpa_value < 2.5:
                return self.WEIGHTS["gpa"]
            elif gpa_value < 3.0:
                return self.WEIGHTS["gpa"] // 2
            else:
                return 0
        except (ValueError, TypeError):
            return self.WEIGHTS["gpa"] // 2

    def get_warning_level(self, score: int) -> int:
        """根据评分确定预警级别"""
        if score >= self.SCORE_RED_THRESHOLD:
            return self.LEVEL_RED
        elif score >= self.SCORE_YELLOW_THRESHOLD:
            return self.LEVEL_YELLOW
        elif score >= self.SCORE_GREEN_THRESHOLD:
            return self.LEVEL_GREEN
        return 0  # 无预警

    async def generate_warnings_for_university(
        self,
        university_id: str,
        graduation_year: Optional[int] = None,
        dry_run: bool = False
    ) -> Dict:
        """
        为学校生成预警

        Args:
            university_id: 学校ID
            graduation_year: 毕业年份筛选，不传则包含所有年份
            dry_run: True则只计算不保存

        Returns:
            生成结果统计
        """
        # 构建查询条件
        conditions = [
            StudentProfile.university_id == university_id,
            StudentProfile.employment_status == 0,  # 只检查待就业学生
        ]
        if graduation_year:
            conditions.append(StudentProfile.graduation_year == graduation_year)

        # 查询所有待就业学生
        result = await self.db.execute(
            select(StudentProfile).where(and_(*conditions))
        )
        students = result.scalars().all()

        stats = {
            "total": len(students),
            "red": 0,
            "yellow": 0,
            "green": 0,
            "no_warning": 0,
            "generated": 0,
            "skipped": 0,
            "errors": 0,
        }

        warning_records = []

        for student in students:
            try:
                score, warning_types, dimension_scores = self.calculate_score(student)
                level = self.get_warning_level(score)

                if level == 0:
                    stats["no_warning"] += 1
                    continue

                # 构建预警记录
                warning_record = {
                    "student": student,
                    "score": score,
                    "level": level,
                    "warning_types": warning_types,
                    "dimension_scores": dimension_scores,
                }

                # 检查是否已存在未处理的同类预警
                existing = await self._check_existing_warning(
                    university_id, student.account_id, warning_types
                )

                if existing and not dry_run:
                    # 更新已有预警
                    existing.level = level
                    existing.ai_suggestion = self._generate_suggestion(
                        warning_types, dimension_scores, student
                    )
                    stats["skipped"] += 1
                elif not dry_run:
                    # 创建新预警
                    new_warning = EmploymentWarning(
                        warning_id=str(uuid.uuid4()),
                        account_id=student.account_id,
                        university_id=university_id,
                        warning_type=",".join(warning_types) if warning_types else "general",
                        level=level,
                        ai_suggestion=self._generate_suggestion(
                            warning_types, dimension_scores, student
                        ),
                        handled=False,
                    )
                    self.db.add(new_warning)
                    stats["generated"] += 1

                # 统计预警级别
                if level == self.LEVEL_RED:
                    stats["red"] += 1
                elif level == self.LEVEL_YELLOW:
                    stats["yellow"] += 1
                else:
                    stats["green"] += 1

                warning_records.append(warning_record)

            except Exception as e:
                logger.error(f"处理学生 {student.profile_id} 时出错: {e}")
                stats["errors"] += 1

        if not dry_run:
            self.db.commit()

        return {
            **stats,
            "warnings": warning_records,
            "dry_run": dry_run,
        }

    async def _check_existing_warning(
        self,
        university_id: str,
        account_id: str,
        warning_types: List[str]
    ) -> Optional[EmploymentWarning]:
        """检查是否已存在未处理的同类预警"""
        if not account_id:
            return None

        result = await self.db.execute(
            select(EmploymentWarning).where(
                and_(
                    EmploymentWarning.university_id == university_id,
                    EmploymentWarning.account_id == account_id,
                    EmploymentWarning.handled == False,
                )
            )
        )
        return result.scalar_one_or_none()

    def _generate_suggestion(
        self,
        warning_types: List[str],
        dimension_scores: dict,
        student: StudentProfile
    ) -> str:
        """生成AI辅导建议"""
        suggestions = []

        type_messages = {
            self.TYPE_LONG_TERM_UNEMPLOYED: "该学生已待就业较长时间，需要重点关注和个性化辅导。",
            self.TYPE_SKILL_GAP: "学生技能储备不足，建议补充相关技能培训或项目经验。",
            self.TYPE_HIGH_EXPECTATION: "学生期望薪资偏高，建议进行市场行情分析和职业规划辅导。",
            self.TYPE_LOCATION_LIMIT: "学生就业地域选择较局限，建议拓宽就业地域范围。",
            self.TYPE_EXPERIENCE_LACK: "学生缺乏实习经历，建议推荐实习机会增加竞争力。",
            self.TYPE_PROFILE_INCOMPLETE: "学生简历信息不完整，建议完善简历以提升曝光率。",
        }

        for wtype in warning_types:
            if wtype in type_messages:
                suggestions.append(type_messages[wtype])

        base_suggestion = " ".join(suggestions) if suggestions else "建议与学生进行一对一沟通，了解其求职意向和困难点。"

        # 添加个性化建议
        if dimension_scores.get("salary_expectation", 0) > 0:
            base_suggestion += f" 当前期望薪资较高，学校可推荐一些匹配度高的岗位资源。"

        if dimension_scores.get("employment_status", 0) > 0:
            base_suggestion += f" 建议安排职业辅导老师与学生进行一对一沟通。"

        return base_suggestion

    async def generate_single_student_warning(
        self,
        profile_id: str,
        university_id: str
    ) -> Optional[Dict]:
        """为单个学生生成预警"""
        result = self.db.execute(
            select(StudentProfile).where(StudentProfile.profile_id == profile_id)
        )
        student = result.scalar_one_or_none()

        if not student:
            return None

        score, warning_types, dimension_scores = self.calculate_score(student)
        level = self.get_warning_level(score)

        # 删除旧的同类预警
        if student.account_id:
            await self.db.execute(
                EmploymentWarning.__table__.delete().where(
                    and_(
                        EmploymentWarning.account_id == student.account_id,
                        EmploymentWarning.handled == False,
                    )
                )
            )

        if level > 0:
            warning = EmploymentWarning(
                warning_id=str(uuid.uuid4()),
                account_id=student.account_id,
                university_id=university_id,
                warning_type=",".join(warning_types) if warning_types else "general",
                level=level,
                ai_suggestion=self._generate_suggestion(warning_types, dimension_scores, student),
                handled=False,
            )
            self.db.add(warning)
            await self.db.commit()

            return {
                "warning_id": warning.warning_id,
                "score": score,
                "level": level,
                "warning_types": warning_types,
            }

        return None
