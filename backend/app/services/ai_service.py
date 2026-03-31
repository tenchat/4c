# TODO: AI - 暂不实现具体逻辑，返回 stub 数据


class AIService:
    def __init__(self, db=None):
        self.db = db

    async def generate_profile(self, data: dict) -> dict:
        return {
            "status": "not_implemented",
            "message": "AI 分析功能开发中",
            "score": 75,
            "professional_match": 0.82,
            "skill_match": 0.68,
            "location_demand": 0.90,
            "salary_expectation": 12000,
            "strengths": ["专业基础扎实", "项目经验丰富"],
            "weaknesses": ["缺乏大厂经验", "英语成绩一般"],
            "suggestions": ["建议加强算法能力", "可考虑提升学历"]
        }

    async def analyze_resume(self, resume_text: str, target_job: str) -> dict:
        return {
            "status": "not_implemented",
            "ats_score": 72,
            "matched_keywords": ["Python", "数据分析", "机器学习"],
            "missing_keywords": ["大规模数据处理", "分布式系统"],
            "suggestions": ["突出项目规模", "增加技术深度描述"]
        }

    async def graduate_vs_job(self, target_city: str, expected_salary: int, study_months: int) -> dict:
        return {
            "status": "not_implemented",
            "employment_path": {
                "expected_salary": expected_salary,
                "timeline": "6个月",
                "stability": 0.75
            },
            "study_path": {
                "expected_salary_after": expected_salary * 1.5,
                "timeline": f"{study_months}个月",
                "stability": 0.85
            },
            "recommendation": "建议先就业积累经验"
        }

    async def generate_warning(self, account_ids: list) -> dict:
        return {
            "status": "not_implemented",
            "generated": len(account_ids),
            "warnings": []
        }
