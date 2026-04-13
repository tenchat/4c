# 大学生就业信息智能分析平台

> 以数据驱动就业决策，用 AI 赋能职业规划

![Version](https://img.shields.io/badge/version-1.0.0-blue) ![Node](https://img.shields.io/badge/node-%3E%3D20.19.0-green) ![Python](https://img.shields.io/badge/python-3.9+-green)

## 项目简介

本平台是**计算机设计大赛参赛项目**，旨在整合校内毕业生数据、社会招聘数据与国家宏观就业数据，构建面向高校的**就业全链路智能分析系统**，为学生、辅导员、就业办三类用户提供差异化服务。

### 核心价值

- **信息整合**：打破学生信息、岗位需求、宏观就业数据孤岛
- **数据驱动**：用数据支撑个性化就业指导
- **AI 赋能**：智能分析就业竞争力，提供精准职业建议

## 技术架构

```
┌─────────────────────────────────────────┐
│               前端层                     │
│  Vue 3 + Vite + Element Plus + ECharts  │
│  TailwindCSS + Pinia                    │
└────────────────┬────────────────────────┘
                 │ REST API
┌────────────────▼────────────────────────┐
│               后端层                     │
│  FastAPI (Python) + SQLAlchemy          │
│  Redis 缓存 + MySQL 数据库              │
└─────────────────────────────────────────┘
```

### 技术栈

| 层级       | 技术           | 说明                       |
| ---------- | -------------- | -------------------------- |
| 前端框架   | Vue 3 + Vite   | 现代化前端框架，组件化开发 |
| UI 组件    | Element Plus   | 企业级组件库               |
| 图表可视化 | ECharts 5      | 数据可视化                 |
| 状态管理   | Pinia          | Vue 状态管理               |
| CSS 框架   | TailwindCSS 4  | 原子化 CSS                 |
| 后端框架   | FastAPI        | 高性能 Python 异步框架     |
| 数据库     | MySQL + SQLite | 关系型数据存储             |
| 缓存       | Redis          | 会话和缓存                 |
| AI 服务    | MiniMax API    | 智能分析（规划中）         |

## 项目结构

```
cccc/
├── src/                    # Vue 前端源码
│   ├── api/               # API 请求封装
│   ├── assets/             # 静态资源
│   ├── components/         # Vue 组件
│   │   ├── business/      # 业务组件
│   │   └── core/          # 核心组件（图表、卡片、表单）
│   ├── router/             # 路由配置
│   ├── stores/             # Pinia 状态管理
│   ├── styles/             # 全局样式
│   ├── types/              # TypeScript 类型定义
│   ├── utils/              # 工具函数
│   └── views/              # 页面视图
│       ├── admin/          # 管理端页面
│       ├── company/        # 企业端页面
│       ├── home/           # 首页/登录注册
│       ├── school/         # 学校端页面
│       └── student/        # 学生端页面
├── backend/                # FastAPI 后端源码
│   ├── app/
│   │   ├── api/v1/        # API 路由
│   │   ├── core/          # 核心配置
│   │   ├── models/        # 数据库模型
│   │   ├── schemas/       # Pydantic 模型
│   │   ├── services/      # 业务逻辑
│   │   └── utils/         # 工具函数
│   ├── migrations/         # 数据库迁移
│   └── tests/              # 后端测试
├── RAG/                    # RAG 服务（AI 增强）
├── docs/                   # 项目文档
├── dataset/                # 数据集
└── scripts/               # 构建脚本
```

## 功能模块

### 学生端 (`/student/*`)

| 功能                | 说明                              |
| ------------------- | --------------------------------- |
| 个人首页            | 就业状态、AI 竞争力评分、推荐岗位 |
| 档案管理            | 个人信息、简历上传、求职意向      |
| 岗位推荐            | 多维度筛选、岗位详情、投递        |
| AI 就业画像         | 就业竞争力评分、雷达图分析        |
| AI 简历优化         | ATS 评分、关键词匹配、优化建议    |
| AI 考研 vs 就业决策 | 考研回报率分析、路径对比          |

### 学校端 (`/school/*`)

| 功能     | 说明                         |
| -------- | ---------------------------- |
| 就业概况 | 统计卡片、学院排名、预警列表 |
| 学生管理 | 分页筛选、批量导入、导出     |
| 就业预警 | 预警识别、批量辅导建议       |
| 数据大屏 | ECharts 可视化、全屏展示     |

### 管理端 (`/admin/*`)

| 功能       | 说明                         |
| ---------- | ---------------------------- |
| 管理首页   | 系统运营数据、关键指标       |
| 统计分析   | 多维度统计、可视化图表、导出 |
| 学院就业率 | 录入编辑、历年对比、横向对比 |
| 稀缺人才   | 各省稀缺岗位热力图           |
| 数据大屏   | 黑色科技风格数据展示         |

### 企业端 (`/company/*`)

| 功能     | 说明                         |
| -------- | ---------------------------- |
| 招聘概况 | 岗位统计、简历统计、效果趋势 |
| 岗位管理 | 岗位列表、状态筛选、编辑下架 |
| 发布岗位 | 职位信息填写、技能标签       |

## 快速开始

### 环境要求

- Node.js >= 20.19.0
- pnpm >= 8.8.0
- Python >= 3.9
- MySQL 8.0 (可选，默认使用 SQLite)
- Redis (可选)

### 前端安装

```bash
# 安装依赖
pnpm install

# 开发模式启动
pnpm dev

# 构建生产版本
pnpm build
```

### 后端安装

```bash
cd backend

# 激活 conda 环境
conda activate cccc

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python -m app.cli init-db
python -m app.cli create-roles

# 创建管理员账号
python -m app.cli admin --username admin --name "系统管理员"

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 访问地址

| 服务     | 地址                       |
| -------- | -------------------------- |
| 前端     | http://localhost:5173      |
| 后端 API | http://localhost:8000      |
| API 文档 | http://localhost:8000/docs |

### 默认账号

| 角色       | 用户名 | 密码      |
| ---------- | ------ | --------- |
| 系统管理员 | admin  | Admin123! |

## 开发指南

详细开发指南请参考 [docs/前端开发指南.md](docs/前端开发指南.md) 和 [docs/前后端对接说明.md](docs/前后端对接说明.md)。

### 主要规范

- **代码风格**：ESLint + Prettier + Stylelint
- **提交规范**：Commitizen + Conventional Commits
- **Git 钩子**：Husky + lint-staged
- **类型检查**：TypeScript 严格模式

### 可用脚本

```bash
pnpm dev          # 开发服务器
pnpm build        # 生产构建
pnpm serve        # 预览构建结果
pnpm lint         # 代码检查
pnpm fix          # 自动修复
pnpm commit       # 交互式提交
```

## 数据说明

项目使用以下公开数据集：

| 数据集             | 用途             |
| ------------------ | ---------------- |
| 招聘数据集 (天池)  | 岗位推荐算法训练 |
| 学校就业数据       | 就业率统计分析   |
| 大学生就业选择调查 | 就业去向分析     |

详细说明见 [docs/data-dictionary.md](docs/data-dictionary.md) 和 [docs/cleaning-rules.md](docs/cleaning-rules.md)。

## 文档索引

| 文档                                             | 说明                |
| ------------------------------------------------ | ------------------- |
| [docs/README.md](docs/README.md)                 | 完整使用指南        |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)     | 技术架构与 API 设计 |
| [docs/PROJECT_GUIDE.md](docs/PROJECT_GUIDE.md)   | 项目规划与答辩材料  |
| [docs/前端开发指南.md](docs/前端开发指南.md)     | 前端开发规范        |
| [docs/前后端对接说明.md](docs/前后端对接说明.md) | 前后端接口文档      |
| [docs/操作手册.md](docs/操作手册.md)             | 管理员操作手册      |

## License

MIT License
