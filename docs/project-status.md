# 大学生就业信息智能分析平台 - 项目进展报告

**日期**: 2026-04-04 | **版本**: v1.0 | **项目**: art-design-pro

---

## 一、已完成功能

### 1.1 基础架构

| 模块 | 状态 | 说明 |
|------|------|------|
| 前端框架 | 完成 | Vue 3 + Vite + Element Plus + ECharts + Pinia |
| 后端框架 | 完成 | FastAPI + SQLAlchemy + SQLite (employment.db) |
| 认证系统 | 完成 | JWT + Refresh Token + 登录限流 + 账号锁定 |
| 数据库 | 完成 | 24张表，涵盖用户、学生、企业、岗位、AI、日志等 |

### 1.2 前端页面

**学生端** (`/student/*`)：
- 个人首页/仪表盘 (`/student/dashboard`)
- 档案管理 (`/student/profile`) — 包含简历上传
- 岗位推荐列表 (`/student/jobs`)
- AI就业画像 (`/student/ai-profile`)
- AI简历优化 (`/student/ai-resume`)
- AI考研vs就业决策 (`/student/ai-decision`)

**学校端** (`/school/*`)：
- 就业概况仪表盘 (`/school/dashboard`)
- 学生管理 (`/school/students`)
- 就业预警 (`/school/warnings`)
- 数据大屏 (`/school/databoard`)

**管理端** (`/admin/*`)：
- 管理首页 (`/admin/dashboard`)
- 学院管理 (`/admin/colleges`)
- 企业管理 (`/admin/companies`)
- 信息审核 (`/admin/profile-review`)
- 数据大屏 (`/admin/databoard`)

**企业端** (`/company/*`)：
- 企业首页 (`/company/dashboard`)
- 企业信息 (`/company/profile`)
- 岗位管理 (`/company/jobs`)
- 发布岗位 (`/company/post-job`)
- 活动管理 (`/company/activities`)
- 招聘公告 (`/company/announcements`)
- 简历管理 (`/company/resumes`)

### 1.3 AI 服务 (Stub)

| 功能 | 状态 | 说明 |
|------|------|------|
| 就业画像 | Stub | 返回 mock 数据 |
| 岗位推荐 | Stub | 返回 mock 数据 |
| 技能路径 | Stub | 返回 mock 数据 |
| 就业预警 | Stub | 返回 mock 数据 |
| 简历分析 | Stub | 部分实现 |
| 考研vs就业 | Stub | 部分实现 |

### 1.4 RAG 服务

| 功能 | 状态 | 说明 |
|------|------|------|
| ChromaDB 向量库 | 基础 | 已初始化 |
| 聊天历史 | 基础 | JSON 文件存储 |
| 文件上传 | 基础 | 简历上传服务 |

---

## 二、未完成功能 (TODO)

### 2.1 后端 API 缺失 (P0 - 阻塞前后端联调)

根据 `docs/ARCHITECTURE.md` 第2.2节，以下 **16个后端接口缺失**：

| 优先级 | 接口 | 前端调用方 |
|--------|------|-----------|
| P0 | `POST /api/v1/students/import` | 学生管理 - 批量导入 |
| P0 | `GET /api/v1/students/export` | 学生管理 - 导出 |
| P0 | `GET /api/v1/jobs` | 岗位推荐列表 |
| P0 | `GET /api/v1/jobs/{id}` | 岗位详情 |
| P0 | `POST /api/v1/jobs` | 发布岗位 |
| P0 | `PUT /api/v1/jobs/{id}` | 编辑岗位 |
| P0 | `DELETE /api/v1/jobs/{id}` | 删除岗位 |
| P0 | `POST /api/v1/jobs/apply` | 投递岗位 |
| P0 | `GET /api/v1/jobs/my-applications` | 我的申请 |
| P0 | `GET /api/v1/dashboard/data` | 仪表盘数据 |
| P1 | `GET /api/v1/statistics/trend` | 趋势统计 |
| P1 | `GET /api/v1/statistics/industry-salary` | 行业薪资 |
| P1 | `GET /api/v1/dashboard/stats` | 统计摘要 |
| P1 | `GET /api/v1/dashboard/visit-trend` | 访问趋势 |
| P1 | `GET /api/v1/dashboard/region` | 地区分布 |
| P1 | `GET /api/v1/dashboard/realtime` | 实时数据 |

### 2.2 AI 服务真实对接 (P1)

| 功能 | 现状 | 待做 |
|------|------|------|
| MiniMax API | Stub/mock | 接入真实 API |
| 就业画像分析 | 返回假数据 | 接入真实 AI |
| 简历 ATS 评分 | 部分实现但不对接 | 接入 AI |
| 考研vs就业 | 部分实现但不对接 | 接入 AI |

### 2.3 数据导入 (P1)

`docs/import-plan.md` 定义了 Phase 1-5 数据导入流程，**目前尚未执行**：

| 数据源 | 预估量 | 状态 |
|--------|--------|------|
| table1_user.csv | ~4,500 行 | 未执行 |
| table2_jd_part*.csv | ~540,000 行 | 未执行 |
| table3_action.csv | ~700,000 行 | 未执行 |
| 大学生就业选择*.csv | ~20,000 行 | 未执行 |
| 学校数据/*.xlsx | 8 个文件 | 未执行 |

### 2.4 数据结构不一致 (P2)

根据 `docs/ARCHITECTURE.md` 第2.3-2.4节：

| 问题 | 描述 |
|------|------|
| `POST /api/v1/ai/analyze-resume` | 前端传 `resume_url`，后端期望 `resume_text` |
| `POST /api/v1/ai/compare-options` | 前端调用但后端不存在 |
| `WarningRequest` schema | 前后端字段不匹配 |
| `JobDescription.status` | 前端用 `number`，后端用 `string` |
| `employment_status` | 前端用 `profile_id`，后端模型字段不同 |

### 2.5 RAG/聊天功能 (P2)

| 功能 | 现状 | 待做 |
|------|------|------|
| AI 聊天对话 | 基础实现 | 与学生档案/岗位联动 |
| RAG 检索 | ChromaDB 初始化 | 与 AI 服务整合 |
| 简历文本提取 | 新增 `text_extractor.py` | 与简历上传流程整合 |

---

## 三、TODO 清单 (按优先级)

### P0 - 阻塞性问题

- [ ] **实现完整 Jobs API** (`backend/app/api/v1/job.py`) — 6个接口
- [ ] **实现 Dashboard API** (`backend/app/api/v1/dashboard.py`) — 6个接口
- [ ] **修复 AI 端点 schema 不匹配** (`analyze-resume`, `compare-options`)
- [ ] **修复 Student Schema 不一致** (`employment_status` 字段映射)

### P1 - 核心功能

- [ ] **接入 MiniMax AI API** — 替换所有 stub/mock
- [ ] **执行数据导入** — 按 `import-plan.md` Phase 1-5 执行
- [ ] **实现学生批量导入/导出** (`students/import`, `students/export`)
- [ ] **企业端简历管理** — 简历查看/筛选功能
- [ ] **数据大屏真实数据** — 替换 mock 数据为真实查询

### P2 - 完善功能

- [ ] **公司端"收到的简历"列表** — 查看投递到本企业的简历
- [ ] **聊天历史与 RAG 联动** — 简历上下文感知
- [ ] **就业预警真实生成** — 基于真实数据触发预警
- [ ] **招聘公告功能完善** — 企业发布公告
- [ ] **考研vs就业真实分析** — 接入 AI 决策

### P3 - 创新功能 (计划中，未启动)

- [ ] **专业-市场契合度追踪器**
- [ ] **同校历届就业数据纵向对比**
- [ ] **校友就业轨迹匿名展示**
- [ ] **企业来校招聘热度分析**
- [ ] **政策解读摘要卡片**

---

## 四、里程碑对照

| 阶段 (plan.md) | 计划时间 | 实际状态 |
|---------------|----------|---------|
| 第一阶段: 数据库设计与基础框架 | 2026-03-25~03-29 | 完成 |
| 第一阶段: 学生信息管理模块 | 2026-03-27~04-02 | 完成 |
| 第一阶段: 基础可视化组件 | 2026-03-31~04-04 | 完成 |
| 第二阶段: 公开数据集导入与清洗 | 2026-04-03~04-05 | 未执行 |
| 第二阶段: 岗位需求分析模块 | 2026-04-04~04-07 | 部分 (Jobs API 缺失) |
| 第二阶段: 宏观就业数据面板 | 2026-04-06~04-08 | 部分 (Dashboard API 缺失) |
| 第三阶段: 大模型 API 接入 | 2026-04-07~04-08 | 未执行 (stub) |
| 第三阶段: 就业竞争力画像 | 2026-04-08~04-09 | 未执行 (stub) |
| 第三阶段: 技能提升路径推荐 | 2026-04-09~04-10 | 未执行 (stub) |
| 第三阶段: 就业困难预警系统 | 2026-04-09~04-10 | 未执行 (stub) |
| 第四阶段: 创新功能 | 2026-04-09~04-10 | 未启动 |
| 第五阶段: 测试与打磨 | 2026-04-09~04-10 | 未开始 |

---

## 五、当前阻塞项

**最关键的阻塞是 P0 的 Jobs API 和 Dashboard API 缺失**——这导致：
1. 学生无法搜索/申请岗位
2. 企业无法发布/管理岗位
3. 所有仪表盘只能显示 mock 数据
4. 数据大屏无法展示真实统计

**建议优先顺序**：
1. 完成 `job.py` 和 `dashboard.py` 的完整实现
2. 修复前后端 schema 不匹配问题
3. 接入 MiniMax AI API 替换 stub
4. 执行数据导入流程
5. 推进创新功能

---

*文档版本：v1.0 | 创建日期：2026-04-04*
