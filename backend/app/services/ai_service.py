"""
AI 服务

整合 RAG 服务，提供智能问答和分析功能
"""

import logging
import re
from typing import Any

from app.services.rag import get_rag_service, RAGServiceError

logger = logging.getLogger(__name__)


def adjust_internship_score(internship_text: str, original_score: float) -> tuple[float, list[str]]:
    """
    根据实习经历内容调整评分（奖惩机制）

    Returns:
        (调整后评分, 调整原因列表)
    """
    if not internship_text or internship_text in ['暂无', '无', '没有']:
        return original_score * 0.8, ["实习经历缺失"]

    text = internship_text.lower()
    reasons: list[str] = []
    bonus = 0.0
    penalty = 0.0

    # ==================== 惩罚机制 ====================

    # 1. 实习时长过短惩罚
    short_patterns = [
        r'几天', r'几周', r'不足一月', r'不到一个月', r'小于1个月',
        r'小于1月', r'试', r'试用期'
    ]
    if any(re.search(p, text) for p in short_patterns):
        penalty += 0.15
        reasons.append("实习时长过短")

    # 2. 可疑/违法内容惩罚
    suspicious_patterns = [
        r'违法', r'犯规', r'欺诈', r'诈骗', r'传销', r'菠菜',
        r'赌博', r'吸毒', r'走私', r'洗钱', r'虚假', r'欺骗',
        r'谎言', r'编造', r'冒充', r'冒名'
    ]
    if any(re.search(p, text) for p in suspicious_patterns):
        penalty += 0.25
        reasons.append("实习经历描述存在异常")

    # 3. 内容过于简略惩罚
    if len(internship_text) < 20:
        penalty += 0.1
        reasons.append("实习描述过于简略")

    # ==================== 奖励机制 ====================

    # 1. 知名公司奖励
    company_patterns = [
        r'华为', r'腾讯', r'阿里', r'字节', r'百度', r'京东',
        r'美团', r'小米', r'滴滴', r'拼多多', r'网易', r'新浪',
        r'搜狐', r'盛大', r'携程', r'嘀嘀', r'抖音', r'快手',
        r'哔哩', r'bilibili', r'微众', r'商汤', r'旷视',
        r'字节跳动', r'tencent', r'alibaba', r'baidu', r'bytedance',
        r'微软', r'谷歌', r'google', r'microsoft', r'amazon', r'meta',
        r'ibm', r'oracle', r'intel', r'nvidia', r'apple', r'特斯拉',
        r'tesla', r'spacex'
    ]
    if any(re.search(p, text) for p in company_patterns):
        bonus += 0.15
        reasons.append("拥有知名企业实习经历")

    # 2. 职责关键词奖励
    responsibility_patterns = [
        r'负责', r'主导', r'独立开发', r'独立完成', r'参与',
        r'开发', r'设计', r'研究', r'优化', r'提升', r'改进',
        r'构建', r'实现', r'搭建', r'部署', r'维护', r'测试',
        r'code', r'review', r'debug', r'analyze', r'ml', r'ai',
        r'model', r'train', r'data', r'database', r'system', r'algorithm'
    ]
    responsibility_count = sum(1 for p in responsibility_patterns if re.search(p, text))
    if responsibility_count >= 3:
        bonus += 0.12
        reasons.append("职责描述清晰具体")
    elif responsibility_count >= 1:
        bonus += 0.06

    # 3. 成果关键词奖励
    achievement_patterns = [
        r'成果', r'业绩', r'奖项', r'论文', r'专利', r'提升',
        r'增长', r'提高', r'减少', r'优化', r'获奖', r'突破',
        r'贡献', r'解决', r'完成率', r'准确率', r'性能提升',
        r'排名', r'领先', r'top', r'best', r'excellent', r'achievement'
    ]
    achievement_count = sum(1 for p in achievement_patterns if re.search(p, text))
    if achievement_count >= 2:
        bonus += 0.1
        reasons.append("有具体成果产出")
    elif achievement_count >= 1:
        bonus += 0.05

    # 4. 实习时长合理奖励 (3个月以上)
    long_patterns = [
        r'一年', r'两年', r'6个月', r'6月', r'三个月',
        r'半年', r'一年以上', r'six months', r'one year'
    ]
    if any(re.search(p, text) for p in long_patterns):
        bonus += 0.08
        reasons.append("实习时长充足")

    # 计算最终评分
    adjusted = original_score - penalty + bonus
    # 限制在 [0, 1] 范围内
    adjusted = max(0.0, min(1.0, adjusted))

    return adjusted, reasons


class AIService:
    """AI 服务 - 代理调用 RAG 服务"""

    def __init__(self, db=None):
        self.db = db

    async def generate_profile(self, data: dict) -> dict:
        """
        生成就业画像分析

        Args:
            data: 包含 user_id, role_type 等信息

        Returns:
            画像分析结果（结构化数据）
        """
        try:
            rag_service = get_rag_service()

            # 检查 RAG 服务是否可用
            if not await rag_service.health_check():
                return {
                    "status": "service_unavailable",
                    "message": "RAG 服务暂不可用",
                    "score": 0,
                    "professional_match": 0,
                    "skill_match": 0,
                    "location_demand": 0,
                    "salary_expectation": 0,
                    "strengths": [],
                    "weaknesses": [],
                    "suggestions": ["服务暂时不可用，请稍后再试"]
                }

            major = data.get('major', '未知')
            target_city = data.get('target_city') or data.get('targetCity') or data.get('city') or '未填写'
            gpa = data.get('gpa')
            skills = ", ".join(data.get('skills', []) or []) or '未填写'
            internship = data.get('internship') or '暂无'

            # 请求结构化数据
            question = f"""你是就业分析专家。请分析以下求职者的就业竞争力并给出建议。

【求职者背景】
- 专业：{major}
- 目标城市：{target_city}
- GPA：{gpa if gpa else '未填写'}
- 技能：{skills}
- 实习经历：{internship}

请返回JSON格式的分析结果，包含：
- overallScore: 综合评分(0-100)
- professional_match: 专业匹配度(0-1)
- skill_match: 技能匹配度(0-1)
- city_demand: 城市就业需求度(0-1)
- internship_score: 实习经验评分(0-1)
- education_background: 学历背景评分(0-1)
- strengths: 优势列表（3-5条）
- weaknesses: 劣势列表（3-5条）
- suggestions: 建议列表（5条）

JSON格式：
{{"overallScore": 75, "professional_match": 0.85, "skill_match": 0.70, "city_demand": 0.65, "internship_score": 0.50, "education_background": 0.90, "strengths": ["优势1", "优势2", "优势3"], "weaknesses": ["劣势1", "劣势2"], "suggestions": ["建议1", "建议2", "建议3"]}}"""

            result = await rag_service.qa(
                question=question,
                user_id=data.get("user_id", "anonymous"),
                role_type=data.get("role_type", "student"),
            )

            answer = result.get("answer", "")

            # 尝试从回答中提取 JSON
            import re
            json_match = re.search(r'\{.*\}', answer, re.DOTALL)
            if json_match:
                import json
                try:
                    parsed = json.loads(json_match.group())

                    # 过滤掉包含"目标城市"的劣势条目（用户已填写，不再提示）
                    if 'weaknesses' in parsed and isinstance(parsed['weaknesses'], list):
                        parsed['weaknesses'] = [
                            w for w in parsed['weaknesses']
                            if '目标城市' not in str(w)
                        ]

                    # 应用实习经历奖惩机制
                    original_internship_score = parsed.get('internship_score', 0.5)
                    adjusted_score, adjustment_reasons = adjust_internship_score(
                        internship, original_internship_score
                    )
                    parsed['internship_score'] = adjusted_score

                    # 根据奖惩调整整体评分
                    if adjustment_reasons:
                        adjustment_note = " | 实习评分调整: " + ", ".join(adjustment_reasons)
                        if 'weaknesses' in parsed and isinstance(parsed['weaknesses'], list):
                            for reason in adjustment_reasons:
                                if '过短' in reason or '异常' in reason or '简略' in reason:
                                    parsed['weaknesses'].insert(0, f"实习经历存在问题: {reason}")
                                    break

                    return {
                        "status": "success",
                        "message": "分析完成",
                        **parsed,
                        "session_id": result.get("session_id", ""),
                    }
                except json.JSONDecodeError:
                    pass

            # 如果无法解析JSON，返回原始回答和默认结构
            # 应用实习经历奖惩机制
            default_internship_score = 0.60
            adjusted_default_score, _ = adjust_internship_score(internship, default_internship_score)

            return {
                "status": "success",
                "message": "分析完成",
                "overallScore": 75,
                "professional_match": 0.80,
                "skill_match": 0.70,
                "city_demand": 0.65,
                "internship_score": adjusted_default_score,
                "education_background": 0.85,
                "strengths": ["数据分析能力较强", "学习能力强"],
                "weaknesses": ["需要更多项目经验"],
                "suggestions": ["建议积累实习经验", "提升技术深度"],
                "answer": answer,
                "session_id": result.get("session_id", ""),
            }
        except RAGServiceError as e:
            logger.error(f"RAG 服务错误: {e.message}")
            return {
                "status": "error",
                "message": e.message,
                "score": 0,
                "professional_match": 0,
                "skill_match": 0,
                "location_demand": 0,
                "salary_expectation": 0,
                "strengths": [],
                "weaknesses": [],
                "suggestions": [f"服务错误: {e.message}"]
            }
        except Exception as e:
            logger.error(f"generate_profile 异常: {e}")
            return {
                "status": "error",
                "message": str(e),
                "score": 0,
                "suggestions": ["发生未知错误"]
            }

    async def analyze_resume(self, resume_text: str, target_job: str) -> dict:
        """
        简历分析

        Args:
            resume_text: 简历文本
            target_job: 目标职位

        Returns:
            ATS 分析结果
        """
        try:
            rag_service = get_rag_service()

            if not await rag_service.health_check():
                return {
                    "status": "service_unavailable",
                    "message": "RAG 服务暂不可用",
                    "ats_score": 0,
                    "matched_keywords": [],
                    "missing_keywords": [],
                    "suggestions": ["服务暂时不可用，请稍后再试"]
                }

            question = f"分析我的简历与{target_job}职位的匹配度，给出关键词匹配建议"
            result = await rag_service.qa(
                question=question,
                user_id="resume_analysis",
                role_type="student",
            )

            return {
                "status": "success",
                "message": "分析完成",
                "answer": result.get("answer", ""),
                "sources": result.get("sources", []),
                "session_id": result.get("session_id", ""),
            }
        except RAGServiceError as e:
            logger.error(f"RAG 服务错误: {e}")
            return {
                "status": "error",
                "message": e.message,
                "ats_score": 0,
                "matched_keywords": [],
                "missing_keywords": [],
                "suggestions": [f"服务错误: {e.message}"]
            }
        except Exception as e:
            logger.error(f"analyze_resume 异常: {e}")
            return {
                "status": "error",
                "message": str(e),
                "ats_score": 0,
                "suggestions": ["发生未知错误"]
            }

    async def graduate_vs_job(
        self,
        target_city: str,
        expected_salary: int,
        study_months: int
    ) -> dict:
        """
        考研 vs 就业决策分析

        Args:
            target_city: 目标城市
            expected_salary: 期望薪资
            study_months: 考研准备时间（月）

        Returns:
            决策分析结果
        """
        try:
            rag_service = get_rag_service()

            if not await rag_service.health_check():
                return {
                    "status": "service_unavailable",
                    "message": "RAG 服务暂不可用",
                    "employment_path": {},
                    "study_path": {},
                    "recommendation": "服务暂时不可用"
                }

            question = (
                f"我期望在{target_city}工作，期望薪资{expected_salary}元，"
                f"考研需要准备{study_months}个月，请分析考研和就业的利弊"
            )
            result = await rag_service.qa(
                question=question,
                user_id="decision_analysis",
                role_type="student",
            )

            return {
                "status": "success",
                "message": "分析完成",
                "answer": result.get("answer", ""),
                "sources": result.get("sources", []),
                "session_id": result.get("session_id", ""),
            }
        except RAGServiceError as e:
            logger.error(f"RAG 服务错误: {e}")
            return {
                "status": "error",
                "message": e.message,
                "recommendation": f"服务错误: {e.message}"
            }
        except Exception as e:
            logger.error(f"graduate_vs_job 异常: {e}")
            return {
                "status": "error",
                "message": str(e),
                "recommendation": "发生未知错误"
            }

    async def generate_warning(self, account_ids: list) -> dict:
        """
        生成就业预警

        Args:
            account_ids: 学生账号ID列表

        Returns:
            预警结果
        """
        try:
            rag_service = get_rag_service()

            if not await rag_service.health_check():
                return {
                    "status": "service_unavailable",
                    "message": "RAG 服务暂不可用",
                    "generated": 0,
                    "warnings": []
                }

            question = (
                f"请分析以下学生的就业风险：{', '.join(account_ids[:5])}。"
                f"给出就业预警和建议"
            )
            result = await rag_service.qa(
                question=question,
                user_id="warning_analysis",
                role_type="school",
            )

            return {
                "status": "success",
                "message": "预警生成完成",
                "answer": result.get("answer", ""),
                "sources": result.get("sources", []),
                "session_id": result.get("session_id", ""),
            }
        except RAGServiceError as e:
            logger.error(f"RAG 服务错误: {e}")
            return {
                "status": "error",
                "message": e.message,
                "generated": 0,
                "warnings": []
            }
        except Exception as e:
            logger.error(f"generate_warning 异常: {e}")
            return {
                "status": "error",
                "message": str(e),
                "generated": 0,
                "warnings": []
            }

    async def qa(
        self,
        question: str,
        user_id: str,
        role_type: str = "student",
        session_id: str | None = None
    ) -> dict:
        """
        通用问答

        Args:
            question: 问题
            user_id: 用户ID
            role_type: 角色类型
            session_id: 会话ID

        Returns:
            问答结果
        """
        try:
            rag_service = get_rag_service()
            result = await rag_service.qa(
                question=question,
                user_id=user_id,
                role_type=role_type,
                session_id=session_id,
            )
            return {
                "status": "success",
                "message": "问答完成",
                "answer": result.get("answer", ""),
                "sources": result.get("sources", []),
                "session_id": result.get("session_id", ""),
            }
        except RAGServiceError as e:
            logger.error(f"RAG 服务错误: {e}")
            return {
                "status": "error",
                "message": e.message,
                "answer": f"抱歉，RAG 服务暂时不可用：{e.message}",
                "sources": [],
                "session_id": ""
            }
        except Exception as e:
            logger.error(f"qa 异常: {e}")
            return {
                "status": "error",
                "message": str(e),
                "answer": "抱歉，发生未知错误",
                "sources": [],
                "session_id": ""
            }

    async def optimize_resume(
        self,
        account_id: str,
        resume_text: str,
        target_job: str
    ) -> dict:
        """
        AI 简历优化

        Args:
            account_id: 学生账户ID
            resume_text: 简历文本
            target_job: 目标岗位

        Returns:
            优化结果
        """
        try:
            rag_service = get_rag_service()
            result = await rag_service.optimize_resume(
                account_id=account_id,
                resume_text=resume_text,
                target_job=target_job,
            )
            return {
                "status": "success",
                "message": "简历优化完成",
                "data": result,
            }
        except RAGServiceError as e:
            logger.error(f"RAG 服务错误: {e}")
            return {
                "status": "error",
                "message": e.message,
                "data": None
            }
        except Exception as e:
            logger.error(f"optimize_resume 异常: {e}")
            return {
                "status": "error",
                "message": str(e),
                "data": None
            }

    async def interview_prep(self, data: dict) -> dict:
        """
        面试准备助手

        Args:
            data: 面试准备请求数据
                - job_title: 目标岗位
                - industry: 目标行业
                - city: 目标城市
                - major: 专业
                - skills: 技能列表
                - internship: 实习经历
                - degree: 学历
                - salary_min/max: 期望薪资
                - interview_type: 面试类型 (technical/hr/stress/group)
                - interview_round: 面试轮次 (first/second/final)
                - company_type: 公司类型 (large/medium/small/foreign/state)
                - action: 操作类型

        Returns:
            面试准备结果
        """
        try:
            rag_service = get_rag_service()

            if not await rag_service.health_check():
                return {
                    "status": "service_unavailable",
                    "message": "RAG 服务暂不可用"
                }

            action = data.get("action", "generate_questions")
            job_title = data.get("job_title", "")
            industry = data.get("industry", "")
            city = data.get("city", "")
            major = data.get("major", "")
            skills = ", ".join(data.get("skills", []) or [])
            internship = data.get("internship", "暂无")
            degree_text = {1: "本科", 2: "硕士", 3: "博士"}.get(data.get("degree", 1), "本科")
            salary_range = f"{data.get('salary_min', 0)}-{data.get('salary_max', 0)}元/月" if data.get("salary_min") or data.get("salary_max") else "面议"

            interview_type_map = {
                "technical": "技术面试",
                "hr": "HR面试",
                "stress": "压力面试",
                "group": "群面"
            }
            interview_round_map = {
                "first": "初试",
                "second": "复试",
                "final": "终面"
            }
            company_type_map = {
                "large": "大型企业/上市公司",
                "medium": "中小型企业",
                "small": "创业公司",
                "foreign": "外资/外企",
                "state": "国企/央企"
            }

            interview_type = interview_type_map.get(data.get("interview_type", "technical"), "技术面试")
            interview_round = interview_round_map.get(data.get("interview_round", "first"), "初试")
            company_type = company_type_map.get(data.get("company_type", "medium"), "中小型企业")

            # 根据 action 生成不同的 prompt
            if action == "generate_questions":
                # 根据面试类型构建差异化的问题重点
                type_focus = {
                    "technical": """【技术深度】
- 考察专业技能的掌握程度和实际应用能力
- 包含场景题/算法题/设计题
- 重点考察问题分析和解决能力
- 涉及技术选型、架构思维""",
                    "hr": """【HR综合】
- 考察职业素养、沟通表达、自我认知
- 职业规划、稳定性、价值观匹配
- 团队协作、抗压能力、成长潜力
- 薪资期望、离职原因等软性因素""",
                    "stress": """【压力面试】
- 连续质疑、否定、挑刺
- 考察心理素质、应变能力、情绪控制
- 考察在压力下的问题解决能力
- 故意制造紧张氛围测试反应""",
                    "group": """【群面/无领导小组】
- 考察团队协作、领导力、逻辑思维
- 观点输出、推动讨论、达成共识
- 角色分工、时间把控、说服技巧
- 团队贡献度和个人亮点展现"""
                }

                # 根据面试轮次构建深度层次
                round_depth = {
                    "first": """【初试特点】
- 侧重基础能力和岗位匹配度
- 验证简历信息的真实性
- 初步考察综合素质
- 筛选是否符合基本要求""",
                    "second": """【复试特点】
- 深入考察专业能力和项目经验
- 考察深度思考和独到见解
- 验证初试表现的一致性
- 进一步评估与团队的匹配度""",
                    "final": """【终面特点】
- 高层/总监级别的最终把关
- 考察文化认同、职业价值观
- 验证综合实力和潜力
- 确认候选人的稳定性和诚意"""
                }

                # 根据公司类型构建差异化背景
                company_focus = {
                    "large": """【大厂特点】
- 流程规范、层级分明
- 竞争激烈、淘汰率高
- 重视品牌、技术栈、学历背景
- 职业路径清晰、晋升体系成熟
- 薪资福利体系完善""",
                    "medium": """【中小厂特点】
- 扁平管理、决策快速
- 一专多能、成长机会多
- 重视实际产出和综合能力
- 技术栈可能更灵活
- 发展空间和不确定性并存""",
                    "foreign": """【外企特点】
- 英语能力是加分项
- 工作文化开放、平等
- 重视流程合规、边界清晰
- 沟通直接、反馈及时
- 薪资结构透明、福利多样""",
                    "state": """【国企特点】
- 稳定优先、重视合规
- 层级观念、论资排辈
- 福利体系完善、隐性福利多
- 裙带关系、编制问题
- 发展路径相对固定"""
                }

                question = f"""你是资深面试官。请为求职者准备针对性强、有深度的{interview_type}（{interview_round}）。

{type_focus.get(data.get("interview_type", "technical"), type_focus["technical"])}

{round_depth.get(data.get("interview_round", "first"), round_depth["first"])}

{company_focus.get(data.get("company_type", "medium"), company_focus["medium"])}

【求职者背景】
- 目标岗位：{job_title}
- 目标行业：{industry or '不限'}
- 专业：{major or '未填写'}
- 技能：{skills or '未填写'}
- 实习经历：{internship}
- 学历：{degree_text}
- 期望薪资：{salary_range}

【问题生成要求】
1. 生成5道高频且有针对性的{interview_type}问题
2. 问题难度和风格应匹配当前{interview_round}
3. 结合{company_type}的公司特点设计情境
4. 每道问题包含：问题文本、优秀回答范例（150-200字）、回答要点（3-5条）、注意事项

请用JSON格式返回：
{{"questions": [{{"question": "...", "answer_example": "...", "key_points": ["..."], "notes": "..."}}]}}"""

            elif action == "self_intro":
                question = f"""请为求职者生成一段简洁有力的自我介绍（用于面试开场）。

【个人背景】（来自档案）
- 应聘岗位：{job_title}
- 专业：{major or '未填写'}
- 学历：{degree_text}
- 技能：{skills or '未填写'}
- 实习经历：{internship}

【自我介绍要求】
1. 控制在2分钟口述时长（约300-400字）
2. 结构清晰：我是谁 → 我会什么 → 我做过什么 → 为什么投这个岗位
3. 突出与{job_title}岗位最相关的优势和经历
4. 用具体数据或成果量化能力（如："主导开发XX系统，用户量达XX"）
5. 结尾表达对岗位的热情和诚意

直接返回自我介绍文本，不需要JSON格式。"""

            elif action == "questions_to_ask":
                question = f"""求职者准备参加{job_title}岗位的面试，需要在面试结尾环节向面试官提问。

【求职者背景】
- 专业：{major or '未填写'}
- 技能：{skills or '未填写'}
- 实习经历：{internship}

请生成10个有质量的问题，覆盖以下维度：
1. 岗位核心工作内容和挑战
2. 团队氛围、协作方式
3. 成长空间、培训机制
4. 业务发展方向
5. 入职准备建议

【提问原则】
- 问题要具体、有深度，避免太宽泛
- 体现对岗位的真实兴趣和思考
- 不要问太功利的问题（如"加班多不多"）

用JSON格式返回：
{{"questions_to_ask": ["问题1", "问题2", ...]}}"""

            elif action == "salary_negotiation":
                question = f"""请为求职者提供薪资谈判的实用指导。

【背景】（来自档案）
- 应聘岗位：{job_title}
- 期望薪资：{salary_range}
- 目标城市：{city or '未填写'}
- 学历：{degree_text}

【指导内容】
1. 谈薪前的准备工作（市场调研、自身优势梳理）
2. 谈薪话术模板（3-5句）
3. 注意事项（5条）
4. 被问期望薪资时的最佳回答
5. 如何评估offer的合理性

【原则】
- 不要虚构经历或夸大能力
- 语气自信但不傲慢
- 综合评估总包而非只看月薪

用JSON格式返回：
{{"salary_tips": {{"1_谈薪前的准备工作": ["..."], "2_谈薪话术模板": ["..."], "3_注意事项": ["..."], "4_最佳回答": "...", "5_评估offer": ["..."]}}}}"""

            elif action == "follow_up_email":
                question = f"""请为求职者生成一封面试后跟进邮件。

【背景】
- 应聘岗位：{job_title}
- 面试时间：面试结束后当天发送

【邮件要求】
1. 主题简洁明确
2. 内容控制在200字以内
3. 表达感谢（提及具体面试官姓名或面试亮点）
4. 强调对岗位的兴趣和匹配度
5. 礼貌询问后续流程
6. 附上联系方式表示随时可沟通

【风格】
- 专业、简洁、真诚
- 不要过度恭维或表现焦虑

直接返回邮件模板，包含主题和正文。"""

            elif action == "dressing_advice":
                question = f"""请为求职者提供面试着装建议。

背景：
- 应聘岗位：{job_title}
- 公司类型：{company_type}

着装建议应该包括：
1. 整体风格建议
2. 男/女分开建议
3. 禁忌/雷区
4. 配饰/妆容建议
5. 不同公司类型的差异化建议

用JSON格式返回：
{{"dressing_tips": "..."}}"""

            else:
                return {
                    "status": "error",
                    "message": f"未知的 action: {action}"
                }

            result = await rag_service.qa(
                question=question,
                user_id=data.get("user_id", "interview_prep"),
                role_type="student",
            )

            return {
                "status": "success",
                "message": "生成完成",
                "answer": result.get("answer", ""),
                "sources": result.get("sources", []),
                "session_id": result.get("session_id", "")
            }

        except RAGServiceError as e:
            logger.error(f"RAG 服务错误: {e}")
            return {
                "status": "error",
                "message": e.message
            }
        except Exception as e:
            logger.error(f"interview_prep 异常: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def interview_practice_review(self, data: dict) -> dict:
        """
        模拟练习点评

        Args:
            data: 包含 question, user_answer, job_title

        Returns:
            点评结果
        """
        try:
            rag_service = get_rag_service()

            if not await rag_service.health_check():
                return {
                    "status": "service_unavailable",
                    "message": "RAG 服务暂不可用",
                    "score": 0,
                    "strengths": [],
                    "weaknesses": [],
                    "improved_answer": ""
                }

            question = data.get("question", "")
            user_answer = data.get("user_answer", "")
            job_title = data.get("job_title", "")

            prompt = f"""你是一位资深面试官。请点评以下面试回答。

面试问题：{question}
应聘岗位：{job_title}

求职者回答：
{user_answer}

请从以下维度进行点评：
1. 回答的亮点（2-3条）
2. 存在的问题（2-3条）
3. 改进建议
4. 给出一个更好的回答范例（150-200字）

评估标准：
- 逻辑清晰度
- 内容完整性
- 与岗位的匹配度
- 表达的自信度

用JSON格式返回：
{{"score": 75, "strengths": ["亮点1", "亮点2"], "weaknesses": ["问题1", "问题2"], "improved_answer": "改进后的回答..."}}"""

            result = await rag_service.qa(
                question=prompt,
                user_id="interview_practice",
                role_type="student",
            )

            return {
                "status": "success",
                "message": "点评完成",
                "answer": result.get("answer", ""),
                "sources": result.get("sources", []),
                "session_id": result.get("session_id", "")
            }

        except RAGServiceError as e:
            logger.error(f"RAG 服务错误: {e}")
            return {
                "status": "error",
                "message": e.message,
                "score": 0,
                "strengths": [],
                "weaknesses": [],
                "improved_answer": ""
            }
        except Exception as e:
            logger.error(f"interview_practice_review 异常: {e}")
            return {
                "status": "error",
                "message": str(e),
                "score": 0,
                "strengths": [],
                "weaknesses": [],
                "improved_answer": ""
            }
