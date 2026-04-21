"""
Employment Warning Engine
就业预警评分引擎 - 基于多维度计算学生就业预警级别
"""

import uuid
import json
from datetime import datetime
from typing import Optional, List, Tuple

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student import StudentProfile
from app.models.employment_warning import EmploymentWarning

# 预警类型映射
WARNING_TYPE_MAP = {
    "unemployed_long_term": "长期未就业",
    "profile_incomplete": "档案不完整",
    "salary_low": "薪资偏低",
    "no_internship": "无实习经验",
    "no_skills": "技能特长缺失",
}

# 严重程度排序（数字越大越严重）
WARNING_SEVERITY = {
    "no_skills": 1,
    "no_internship": 2,
    "profile_incomplete": 3,
    "salary_low": 4,
    "unemployed_long_term": 5,
}


def calculate_months_unemployed(graduation_year: int) -> int:
    """计算待就业时长（月）"""
    if graduation_year:
        now = datetime.now()
        grad_month = graduation_year * 12 + 6  # 假设6月毕业
        current_month = now.year * 12 + now.month
        return max(0, current_month - grad_month)
    return 0


def parse_skills(skills_field) -> List[str]:
    """解析skills字段，支持JSON数组或逗号分隔字符串"""
    if not skills_field:
        return []
    if isinstance(skills_field, list):
        return skills_field
    try:
        # 尝试JSON解析
        parsed = json.loads(skills_field)
        if isinstance(parsed, list):
            return [s for s in parsed if s]
        return []
    except (json.JSONDecodeError, TypeError):
        # 尝试逗号分隔
        if isinstance(skills_field, str):
            return [s.strip() for s in skills_field.split(",") if s.strip()]
        return []


def calculate_warning_type_and_level(student: StudentProfile) -> Tuple[Optional[str], int]:
    """
    计算预警类型和级别。
    每个学生只返回一个最严重的预警类型。

    Returns: (warning_type, level)
    - warning_type: 最严重的预警类型，或 None 表示无需预警
    - level: 1=红, 2=黄, 3=绿
    """
    # 已就业/升学/出国 -> 无预警
    if student.employment_status in [1, 2, 3]:
        return None, 0

    triggered_types: List[Tuple[str, int]] = []  # (type, severity_score)

    # 1. 待就业时长（severity=50）
    months_unemployed = calculate_months_unemployed(student.graduation_year or 0)
    if months_unemployed > 12:
        triggered_types.append(("unemployed_long_term", 50))

    # 2. 档案完整度（severity=30）
    profile_complete = getattr(student, "profile_complete", None) or 0
    if profile_complete < 50:
        triggered_types.append(("profile_incomplete", 30))

    # 3. 薪资匹配度（severity=25）
    cur_salary = getattr(student, "cur_salary", None)
    desire_salary_min = getattr(student, "desire_salary_min", None)
    if cur_salary and desire_salary_min and desire_salary_min > 0:
        if cur_salary < desire_salary_min * 0.6:
            triggered_types.append(("salary_low", 25))

    # 4. 实习经历（severity=10）
    internship = getattr(student, "internship", None) or ""
    internship = internship.strip()
    if not internship or internship in ("无", "暂无", "NULL", ""):
        triggered_types.append(("no_internship", 10))

    # 5. 技能特长（severity=5）
    skills = parse_skills(getattr(student, "skills", None))
    if not skills:
        triggered_types.append(("no_skills", 5))

    if not triggered_types:
        return None, 0

    # 按严重程度排序，取最严重的一个
    triggered_types.sort(key=lambda x: x[1], reverse=True)
    warning_type = triggered_types[0][0]

    # 计算级别
    # 红色: 待业 > 18个月
    # 黄色: 待业 12-18个月，或 profile_incomplete，或 salary_low
    # 绿色: no_internship 或 no_skills
    if warning_type == "unemployed_long_term" and months_unemployed > 18:
        level = 1
    elif warning_type in ("profile_incomplete", "salary_low"):
        level = 2
    else:
        level = 3

    return warning_type, level


def generate_ai_suggestion(warning_type: str, months_unemployed: int = 0) -> str:
    """根据预警类型生成AI辅导建议"""
    suggestions = {
        "unemployed_long_term": f"该学生待就业时间较长（{months_unemployed}个月），建议安排一对一职业辅导，了解其求职意向和困难点，同时推荐相关实习/就业岗位。",
        "profile_incomplete": "学生档案信息不完整，建议督促其完善简历、技能证书、实习经历等信息，提升简历完整度。",
        "salary_low": "当前薪资低于期望值，建议与学生沟通调整期望值或推荐符合预期的岗位，同时关注就业市场行情。",
        "no_internship": "学生缺乏实习经历，建议推荐实习岗位或项目实践机会，积累工作经验，提升就业竞争力。",
        "no_skills": "学生技能信息缺失，建议了解其实际技能情况，并推荐相关技能培训或证书考试。",
    }
    return suggestions.get(warning_type, "该学生需要关注，请根据实际情况提供适当辅导。")


class WarningEngine:
    """预警引擎"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_single_student_warning(
        self, profile_id: str, university_id: str
    ) -> Optional[dict]:
        """为单个学生生成预警"""
        result = await self.db.execute(
            select(StudentProfile).where(StudentProfile.profile_id == profile_id)
        )
        student = result.scalar_one_or_none()

        if not student:
            return None

        warning_type, level = calculate_warning_type_and_level(student)

        if level == 0:
            # 无需预警，但可能之前有记录，需要删除
            existing = await self.db.execute(
                select(EmploymentWarning).where(
                    and_(
                        EmploymentWarning.profile_id == profile_id,
                        EmploymentWarning.university_id == university_id,
                        EmploymentWarning.handled == False,
                    )
                )
            )
            existing_warning = existing.scalar_one_or_none()
            if existing_warning:
                await self.db.delete(existing_warning)
                await self.db.commit()
            return None

        months_unemployed = calculate_months_unemployed(student.graduation_year or 0)
        ai_suggestion = generate_ai_suggestion(warning_type, months_unemployed)

        # 查询是否已存在未处理的预警
        existing = await self.db.execute(
            select(EmploymentWarning).where(
                and_(
                    EmploymentWarning.profile_id == profile_id,
                    EmploymentWarning.university_id == university_id,
                    EmploymentWarning.handled == False,
                )
            )
        )
        existing_warning = existing.scalar_one_or_none()

        if existing_warning:
            # 更新已有预警
            existing_warning.warning_type = warning_type
            existing_warning.level = level
            existing_warning.ai_suggestion = ai_suggestion
            warning = existing_warning
        else:
            # 创建新预警
            warning = EmploymentWarning(
                warning_id=str(uuid.uuid4()),
                profile_id=profile_id,
                university_id=university_id,
                warning_type=warning_type,
                level=level,
                ai_suggestion=ai_suggestion,
                handled=False,
            )
            self.db.add(warning)

        await self.db.commit()
        await self.db.refresh(warning)

        return {
            "warning_id": warning.warning_id,
            "profile_id": warning.profile_id,
            "warning_type": warning.warning_type,
            "level": warning.level,
            "ai_suggestion": warning.ai_suggestion,
        }

    async def generate_warnings_for_university(
        self,
        university_id: str,
        graduation_year: Optional[int] = None,
        dry_run: bool = False,
    ) -> dict:
        """批量为该校学生生成预警"""
        conditions = [StudentProfile.university_id == university_id]
        if graduation_year:
            conditions.append(StudentProfile.graduation_year == graduation_year)

        result = await self.db.execute(
            select(StudentProfile.profile_id).where(and_(*conditions))
        )
        profile_ids = [row[0] for row in result.all()]

        total = len(profile_ids)
        red = yellow = green = no_warning = generated = skipped = 0

        for profile_id in profile_ids:
            try:
                warning_type, level = await self._get_warning_for_profile(profile_id)

                if level == 0:
                    no_warning += 1
                    continue

                if level == 1:
                    red += 1
                elif level == 2:
                    yellow += 1
                else:
                    green += 1

                if not dry_run:
                    await self.generate_single_student_warning(profile_id, university_id)
                    generated += 1
                else:
                    skipped += 1

            except Exception as e:
                skipped += 1

        return {
            "total": total,
            "red": red,
            "yellow": yellow,
            "green": green,
            "no_warning": no_warning,
            "generated": generated,
            "skipped": skipped,
            "errors": [],
        }

    async def _get_warning_for_profile(self, profile_id: str) -> Tuple[Optional[str], int]:
        """获取学生预警信息"""
        result = await self.db.execute(
            select(StudentProfile).where(StudentProfile.profile_id == profile_id)
        )
        student = result.scalar_one_or_none()
        if not student:
            return None, 0
        return calculate_warning_type_and_level(student)
