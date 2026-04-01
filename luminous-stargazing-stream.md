# AI 对话系统需求文档 - 完整版

> 项目：高校学生就业信息智能分析平台 - RAG 模块
> 版本：v2.0
> 端口：1145（独立运行）
> 更新日期：2026-04-01

---

## 一、项目概述

### 1.1 背景
为高校学生就业平台构建智能问答系统，基于 RAG（检索增强生成）技术，为学生、学校、企业三类角色提供智能对话服务。

### 1.2 核心需求
- 三端对话（学生/学校/企业）各有独立知识库
- 支持文档上传（txt/pdf/word）实时更新知识库
- RAG 检索 + 结构化数据注入
- 流式输出
- 多 LLM 适配器预留（当前 Tongyi）

### 1.3 设计原则
1. **模块化设计**：每层职责单一，便于维护和测试
2. **高扩展性**：数据库仓储模式，支持任意表/字段动态查询
3. **低耦合**：RAG 核心与 API 层分离，适配器模式支持多 LLM

---

## 二、系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (Vue 3 - 后续)                      │
│              新建统一 AI 对话页（带文件上传）                      │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTP / SSE
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              RAG Service (FastAPI) - 端口 1145                   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      API Layer                            │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │  /qa         │  │ /upload      │  │ /history     │  │   │
│  │  │  问答接口    │  │ 文档上传     │  │ 会话历史     │  │   │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │   │
│  └─────────┼─────────────────┼─────────────────┼────────────┘   │
│            │                 │                 │                  │
│            ▼                 ▼                 ▼                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    Service Layer                             │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │  │ QueryParser │  │ DocService  │  │HistoryService│        │ │
│  │  │ 意图解析    │  │ 文档处理    │  │ 会话历史    │        │ │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │ │
│  │         │                │                │               │ │
│  │         └────────────────┼────────────────┘               │ │
│  │                          ▼                                │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │              RAG Engine (Core)                       │ │ │
│  │  │  1. Structured Query (SQLite) → 结构化数据          │ │ │
│  │  │  2. Vector Search (ChromaDB) → 知识库检索           │ │ │
│  │  │  3. Context Assembly → 合并上下文                    │ │ │
│  │  │  4. Prompt Builder → 组装提示词                      │ │ │
│  │  │  5. LLM Generate → LLM 生成（流式）                 │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐              │
│         ▼                    ▼                    ▼               │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐        │
│  │  SQLite     │      │  ChromaDB  │      │  FileStore  │        │
│  │ (元数据)    │      │  (向量库)   │      │ (会话历史)  │        │
│  └─────────────┘      └─────────────┘      └─────────────┘        │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 RAG/ 目录结构（模块化设计）

```
RAG/
├── app.py                      # FastAPI 入口
├── config_data.py              # 配置（现有，保留）
│
├── db/                         # 数据库层（高扩展性）
│   ├── __init__.py
│   ├── connection.py           # SQLite 连接管理
│   ├── repositories/           # 仓储层
│   │   ├── __init__.py
│   │   ├── base_repository.py  # 通用仓储基类
│   │   └── knowledge_repo.py  # 知识库仓储
│   └── models/                  # SQLAlchemy 模型
│       ├── __init__.py
│       └── knowledge.py
│
├── schemas/                    # Pydantic 模型
│   ├── __init__.py
│   ├── request.py
│   └── response.py
│
├── services/                   # 业务服务层
│   ├── __init__.py
│   ├── llm/                    # LLM 抽象层
│   │   ├── __init__.py
│   │   ├── base.py            # 抽象基类
│   │   ├── tongyi_adapter.py  # 通义千问适配器
│   │   └── factory.py         # 工厂类
│   ├── rag/                    # RAG 核心
│   │   ├── __init__.py
│   │   ├── query_parser.py
│   │   ├── structured_query.py
│   │   ├── vector_search.py
│   │   ├── context_assembler.py
│   │   ├── prompt_builder.py
│   │   └── rag_engine.py
│   ├── document/
│   │   ├── __init__.py
│   │   ├── parser.py          # PDF/Word 解析
│   │   └── knowledge_sync.py  # 知识库同步
│   └── chat/
│       ├── __init__.py
│       └── history_service.py
│
├── api/                        # API 路由层
│   ├── __init__.py
│   ├── qa.py
│   ├── upload.py
│   └── history.py
│
├── chroma_db/                  # 向量数据库
├── chat_history/               # 会话历史
├── data/                       # 测试数据
└── requirements.txt
```

---

## 三、技术栈

| 组件 | 技术方案 | 用途 |
|------|----------|------|
| LLM | Qwen3-max (DashScope) | 对话生成 |
| Embedding | text-embedding-v4 | 文本向量化 |
| 向量数据库 | ChromaDB | 知识库向量存储 |
| 结构化数据 | SQLite | 元数据存储 |
| 对话框架 | LangChain | RAG 编排 |
| 后端框架 | FastAPI | API 服务 |
| 文档解析 | PyMuPDF + python-docx | PDF/Word 解析 |

---

## 四、Skills 分析

### 4.1 可用 Skills 总览

| Skill | 功能 | 与本项目关系 |
|-------|------|-------------|
| **planner** | 实现规划 | ⭐ 核心 - 用于规划整体实施 |
| **api-design** | API 设计 | ⭐ 核心 - 设计 REST API 规范 |
| **tdd-workflow** | TDD 工作流 | ⭐ 核心 - 测试驱动开发 |
| **iterative-retrieval** | 迭代检索 | ⭐ 核心 - RAG 检索模式 |
| **backend-patterns** | 后端模式 | ⭐ 核心 - 服务层设计 |
| **python-patterns** | Python 模式 | ⭐ 核心 - Python 代码规范 |
| **code-reviewer** | 代码审查 | ⭐ 核心 - 代码质量把控 |
| **python-reviewer** | Python 审查 | ⭐ 核心 - Python 专项审查 |
| **database-reviewer** | 数据库审查 | ⭐ 核心 - SQL 质量把控 |
| **build-error-resolver** | 构建错误解决 | 🟡 支持 - 问题排查 |

### 4.2 推荐的 Skills 调用策略

```
阶段1（基础框架）    → planner, api-design, python-patterns
阶段2（RAG核心）     → iterative-retrieval, python-reviewer
阶段3（文档处理）    → python-patterns, code-reviewer
阶段4（API层）       → api-design, backend-patterns, tdd-workflow
阶段5（代码审查）    → code-reviewer, python-reviewer, database-reviewer
```

---

## 五、技术路线（分阶段实施）

### Phase 1: 基础框架（1天）

**目标**：搭建项目骨架，配置数据库连接

**任务清单**：
- [ ] 创建 FastAPI 入口 `app.py`
- [ ] 配置 SQLite 连接 `db/connection.py`
- [ ] 创建通用仓储基类 `db/repositories/base_repository.py`
- [ ] 创建 Pydantic 模型 `schemas/`
- [ ] 配置 CORS

**Skill 调用**：
```
调用: /plan
调用: api-design (API 规范设计)
调用: python-patterns (代码结构)
```

---

### Phase 2: RAG 核心引擎（2天）

**目标**：实现 RAG 检索 + 生成逻辑

**任务清单**：
- [ ] 实现结构化数据查询 `services/rag/structured_query.py`
- [ ] 实现向量检索 `services/rag/vector_search.py`
- [ ] 实现上下文组装 `services/rag/context_assembler.py`
- [ ] 实现 Prompt 构建 `services/rag/prompt_builder.py`
- [ ] 实现 RAG 引擎 `services/rag/rag_engine.py`

**Skill 调用**：
```
调用: iterative-retrieval (检索模式参考)
调用: python-reviewer (代码审查)
调用: backend-patterns (服务层设计)
```

---

### Phase 3: LLM 适配器层（0.5天）

**目标**：实现 Tongyi 适配器，预留扩展

**任务清单**：
- [ ] 创建 LLM 抽象基类 `services/llm/base.py`
- [ ] 实现 Tongyi 适配器 `services/llm/tongyi_adapter.py`
- [ ] 创建工厂类 `services/llm/factory.py`

**Skill 调用**：
```
调用: python-patterns (适配器模式)
调用: python-reviewer
```

---

### Phase 4: 文档处理（1天）

**目标**：实现 PDF/Word 上传解析

**任务清单**：
- [ ] 实现文档解析器 `services/document/parser.py`
- [ ] 实现知识库同步 `services/document/knowledge_sync.py`
- [ ] 实现文件上传 API `api/upload.py`

**Skill 调用**：
```
调用: python-patterns (文件处理)
调用: code-reviewer (安全审查)
```

---

### Phase 5: API 路由层（0.5天）

**目标**：完成所有 API 接口

**任务清单**：
- [ ] 实现问答接口 `api/qa.py`
- [ ] 实现流式输出
- [ ] 实现会话历史 `api/history.py`

**Skill 调用**：
```
调用: api-design (API 规范)
调用: tdd-workflow (接口测试)
调用: backend-patterns (中间件模式)
```

---

### Phase 6: 代码审查与收尾（0.5天）

**目标**：全面审查，确保代码质量

**任务清单**：
- [ ] 全局代码审查
- [ ] 数据库查询优化
- [ ] API 文档生成
- [ ] 测试验证

**Skill 调用**：
```
调用: code-reviewer
调用: python-reviewer
调用: database-reviewer
```

---

## 六、各阶段详细 Prompt（Agent 分派指令）

### Phase 1: 基础框架

---

#### 📋 Phase 1.1: 创建 FastAPI 入口

**文件**：`RAG/app.py`

**Prompt**：
```
# 任务：创建 RAG 服务的 FastAPI 入口

## 项目背景
- 项目：高校学生就业信息平台 RAG 模块
- 运行端口：1145
- 位置：d:\Deep Learning\jisuanji\4c-1\RAG\

## 技术要求
1. 创建 FastAPI 应用，端口 1145
2. 配置 CORS，允许前端直连
3. 注册 API 路由 prefix="/api/v1/rag"
4. 添加健康检查端点 /health
5. 添加启动日志

## 参考文件
- 现有 backend 入口：backend/app/main.py（参考其 CORS 配置和异常处理）
- 现有 RAG 目录结构在 RAG/ 下

## 代码规范
- 使用 python-patterns skill 的最佳实践
- 类型注解必须完整
- 遵循项目已有的代码风格

## 输出要求
创建完整的 app.py 文件，包含：
- FastAPI 实例配置
- CORS 中间件配置
- 全局异常处理
- 路由注册
- 启动事件
```

**Skill 调用**：
```
/python-patterns - 参考 Python 代码规范
/api-design - 参考 API 设计规范
```

---

#### 📋 Phase 1.2: 数据库连接与仓储

**文件**：`RAG/db/connection.py`, `RAG/db/repositories/base_repository.py`

**Prompt**：
```
# 任务：创建数据库连接和通用仓储基类

## 项目背景
- SQLite 数据库位置：backend/schema.sqlite.sql（需复制到 RAG/db/ 使用）
- 数据库表：knowledge_documents 等

## 技术要求

### 1. 数据库连接 (db/connection.py)
```python
# 要求：
- 使用 SQLAlchemy async
- 支持 SQLite
- 提供 get_db() 依赖注入函数
- 配置外键约束
```

### 2. 通用仓储基类 (db/repositories/base_repository.py)
```python
# 要求：
- 泛型基类 BaseRepository[T]
- 必须方法：
  - get_by_id(id: str) -> dict | None
  - get_all(filters: dict = None, limit: int = 100, offset: int = 0) -> list[dict]
  - create(data: dict) -> dict
  - update(id: str, data: dict) -> dict
  - delete(id: str) -> bool
  - raw_query(sql: str, params: dict = None) -> list[dict]  # 原生 SQL 查询
- 使用 text() 执行原生 SQL
- 所有方法需要 async/await
```

### 3. 知识库仓储 (db/repositories/knowledge_repo.py)
```python
# 要求：
- 继承 BaseRepository
- 表名：knowledge_documents
- 额外方法：
  - get_by_category(category: str) -> list[dict]
  - search_by_title(keyword: str) -> list[dict]
```

## 数据库表结构（knowledge_documents）
```sql
CREATE TABLE knowledge_documents (
    doc_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    doc_type TEXT,
    category TEXT DEFAULT 'shared',  -- student/school/company/shared
    vector_ids TEXT,                  -- ChromaDB IDs，逗号分隔
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

## 代码规范
- 遵循 python-patterns
- 完整的类型注解
- EAFP 风格（try/except 优于 if/else）
- 文档字符串必须

## 输出要求
创建完整的三个文件，包含完整代码和文档字符串
```

**Skill 调用**：
```
/python-patterns - 泛型、async/await、context manager
/python-reviewer - 代码审查
/database-reviewer - SQL 查询审查（需要时）
```

---

#### 📋 Phase 1.3: Pydantic 模型

**文件**：`RAG/schemas/request.py`, `RAG/schemas/response.py`

**Prompt**：
```
# 任务：创建 Pydantic 请求/响应模型

## 项目背景
- FastAPI 服务，端口 1145
- API prefix: /api/v1/rag

## 模型设计要求

### 请求模型 (schemas/request.py)

```python
# 1. QA 请求
class QARequest(BaseModel):
    question: str                    # 用户问题
    user_id: str                    # 用户ID
    role_type: str                  # student/school/company
    session_id: str | None = None   # 可选会话ID

# 2. 流式 QA 请求（同 QARequest）

# 3. 上传请求
class UploadRequest(BaseModel):
    title: str                       # 文档标题
    category: str = "shared"         # student/school/company/shared

# 4. 会话历史请求
class HistoryRequest(BaseModel):
    session_id: str | None = None
    user_id: str | None = None
```

### 响应模型 (schemas/response.py)

```python
# 1. 基础响应
class BaseResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Any | None = None

# 2. QA 响应
class SourceItem(BaseModel):
    type: str                        # structured/document
    table: str | None = None        # 来源表名
    doc_id: str | None = None       # 文档ID
    content: str                     # 内容片段

class QAResponse(BaseModel):
    answer: str                      # 回答
    sources: list[SourceItem]        # 来源列表
    session_id: str                  # 会话ID

# 3. 上传响应
class UploadResponse(BaseModel):
    doc_id: str                       # 文档ID
    chunks: int                       # 分块数量

# 4. 知识库项
class KnowledgeItem(BaseModel):
    doc_id: str
    title: str
    category: str
    created_at: str

# 5. 消息项
class MessageItem(BaseModel):
    type: str          # user/assistant
    content: str
    created_at: str
```

## 代码规范
- 使用 Pydantic v2 (BaseModel)
- 所有字段必须有类型注解
- 使用 | 而非 Optional[]
- 响应模型包含 code, message, data 包装

## 输出要求
创建完整的 schemas/ 目录结构，包含 __init__.py 和两个模型文件
```

**Skill 调用**：
```
/api-design - 响应格式规范
/python-patterns - Pydantic 模型
```

---

### Phase 2: RAG 核心引擎

---

#### 📋 Phase 2.1: 结构化数据查询

**文件**：`RAG/services/rag/structured_query.py`

**Prompt**：
```
# 任务：实现结构化数据查询服务

## 项目背景
- 数据库：SQLite（backend/schema.sqlite.sql）
- 作用：RAG 检索时查询结构化数据（就业率、薪资等），注入到 prompt

## 核心表结构（只读查询）

### college_employment（学院就业表）
```sql
university_id, college, major, year, total_students,
employed_students, employment_rate, avg_salary
```

### scarce_talents（稀缺人才表）
```sql
province, job_type, industry, demand_count, avg_salary, year
```

### student_profiles（学生档案表）
```sql
account_id, student_name, major, college, degree,
employment_status, annual_salary, industry, job_title, city
```

### job_descriptions（职位描述表）
```sql
job_id, company_id, job_title, job_type, salary_min, salary_max,
location, description, requirements, benefits, status
```

## 实现要求

```python
class StructuredQueryService:
    """查询结构化数据，用于注入 RAG prompt"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_employment_by_major(self, major: str) -> dict:
        """查询某专业的就业率数据"""
        # SQL: SELECT college, major, year, employment_rate, avg_salary
        # FROM college_employment
        # WHERE major LIKE ?
        # ORDER BY year DESC LIMIT 5

    async def get_talent_demand_by_province(self, province: str) -> dict:
        """查询某省份的人才需求"""

    async def get_student_profile(self, account_id: str) -> dict:
        """获取学生画像（个性化建议用）"""

    async def get_jobs_by_industry(self, industry: str, limit: int = 10) -> dict:
        """查询某行业的职位"""

    async def query_any_table(
        self,
        table: str,
        fields: list[str] | None = None,
        conditions: dict | None = None,
        limit: int = 100
    ) -> list[dict]:
        """通用动态查询 - 支持任意表/字段查询"""
        # 动态构建 SELECT 语句
        # 防止 SQL 注入（字段白名单）
```

## 关键设计点
1. **动态查询**：支持任意表/字段组合查询，体现"高扩展性"
2. **SQL 注入防护**：字段名白名单验证
3. **结果格式化**：返回 dict/list，便于组装到 prompt

## 代码规范
- async/await 全程
- 完整类型注解
- 文档字符串
- 使用 raw_query() 复用 base_repository

## 输出要求
创建完整的 structured_query.py，包含：
- StructuredQueryService 类
- 所有查询方法
- 动态查询方法
- 完整的错误处理
```

**Skill 调用**：
```
/python-patterns - async/await, SQL 处理
/python-reviewer - 代码审查
/database-reviewer - SQL 注入防护审查
```

---

#### 📋 Phase 2.2: 向量检索服务

**文件**：`RAG/services/rag/vector_search.py`

**Prompt**：
```
# 任务：实现向量检索服务

## 项目背景
- 向量数据库：ChromaDB
- Embedding 模型：DashScope text-embedding-v4
- 位置：RAG/chroma_db/

## 现有代码参考
- RAG/vector_stores.py（现有 ChromaDB 封装）
- RAG/config_data.py（配置）

## 实现要求

```python
class VectorSearchService:
    """向量检索服务"""

    def __init__(self):
        # 初始化 ChromaDB
        # 初始化 Embedding 函数
        self.collection_name = config.collection_name
        self.persist_directory = config.persist_directory

    def get_retriever(self, k: int = 5):
        """返回 LangChain retriever"""
        # 使用 as_retriever(search_kwargs={"k": k})

    async def search(
        self,
        query: str,
        role_type: str | None = None,  # student/school/company
        k: int = 5
    ) -> list[dict]:
        """
        向量相似度搜索
        返回格式：
        [{
            "content": "文档片段",
            "metadata": {"source": "xxx", "create_time": "..."},
            "score": 0.95
        }]
        """
        # 1. 生成 query 的 embedding
        # 2. 在 ChromaDB 中检索 top-k
        # 3. 格式化返回（包含 score）

    async def add_documents(
        self,
        texts: list[str],
        metadatas: list[dict],
        ids: list[str] | None = None
    ) -> list[str]:
        """批量添加文档到向量库"""
        # 使用 chroma.add_texts()

    async def delete_by_ids(self, ids: list[str]) -> bool:
        """根据 ID 删除向量"""
```

## 关键设计点
1. **LangChain 集成**：复用 vector_stores.py 的 LangChain 封装
2. **过滤支持**：按 role_type 过滤（未来扩展）
3. **MMR 检索**：后续可加 MMR（Maximal Marginal Relevance）去重

## ChromaDB 配置（参考 config_data.py）
```python
collection_name = "rag"
persist_directory = "./chroma_db"
embedding_model_name = "text-embedding-v4"
similarity_threshold = 1  # 检索数量
```

## 代码规范
- async 方法（ChromaDB 操作默认 sync，可在线程池中运行）
- LangChain Chroma 的 as_retriever() 返回的是 sync 对象
- 完整类型注解

## 输出要求
创建完整的 vector_search.py
```

**Skill 调用**：
```
/python-patterns - async/await, LangChain 集成
/python-reviewer
/iterative-retrieval - 检索模式参考
```

---

#### 📋 Phase 2.3: 上下文组装与 Prompt 构建

**文件**：`RAG/services/rag/context_assembler.py`, `RAG/services/rag/prompt_builder.py`

**Prompt**：
```
# 任务：实现上下文组装和 Prompt 构建

## 上下文组装 (context_assembler.py)

```python
class ContextAssembler:
    """组装 RAG 上下文"""

    def __init__(self):
        pass

    def assemble(
        self,
        structured_data: dict,
        documents: list[dict],
        role_type: str
    ) -> str:
        """
        组装完整的上下文字符串

        格式：
        【结构化数据】
        {structured_context}

        【知识库内容】
        {knowledge_context}

        返回组装后的字符串
        """

    def format_structured_context(self, data: dict) -> str:
        """格式化结构化数据"""
        if not data:
            return "暂无结构化数据"

        lines = []
        for key, value in data.items():
            lines.append(f"【{key}】")
            if isinstance(value, list):
                for item in value:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"  {value}")
        return "\n".join(lines)

    def format_knowledge_context(self, docs: list[dict]) -> str:
        """格式化知识库文档"""
        if not docs:
            return "暂无相关知识库内容"

        lines = []
        for i, doc in enumerate(docs, 1):
            lines.append(f"【文档{i}】")
            lines.append(f"内容：{doc['content']}")
            if doc.get('metadata'):
                lines.append(f"来源：{doc['metadata'].get('source', '未知')}")
            lines.append("")
        return "\n".join(lines)
```

## Prompt 构建 (prompt_builder.py)

```python
# Prompt 模板定义
STUDENT_QA_TEMPLATE = """你是大学生就业助手。请根据以下参考资料回答学生的问题。

【结构化数据】
{structured_context}

【知识库内容】
{knowledge_context}

【历史记录】
{history}

学生问题：{question}

回答要求：
1. 基于提供的参考资料回答，不要编造信息
2. 如果有具体数据（如就业率），请引用
3. 结合学生个人情况给出个性化建议
4. 回答要专业、友好、有帮助
"""

SCHOOL_QA_TEMPLATE = """你是高校就业指导工作助手。请根据以下参考资料回答问题。

【结构化数据】
{structured_context}

【知识库内容】
{knowledge_context}

【历史记录】
{history}

问题：{question}

回答要求：
1. 回答要专业、规范
2. 涉及数据统计时说明统计口径
3. 预警相关问题请结合平台数据
"""

COMPANY_QA_TEMPLATE = """你是企业招聘助手。请根据以下参考资料回答问题。

【结构化数据】
{structured_context}

【知识库内容】
{knowledge_context}

【历史记录】
{history}

问题：{question}

回答要求：
1. 提供专业的招聘建议
2. 涉及劳动法相关内容要准确
3. 帮助企业更好地发布职位和筛选人才
"""

class PromptBuilder:
    """Prompt 构建器"""

    TEMPLATES = {
        "student": STUDENT_QA_TEMPLATE,
        "school": SCHOOL_QA_TEMPLATE,
        "company": COMPANY_QA_TEMPLATE,
    }

    def build(
        self,
        role_type: str,
        question: str,
        structured_context: str,
        knowledge_context: str,
        history: str = ""
    ) -> list[dict]:
        """
        构建完整的消息列表（用于 LLM）

        返回格式：
        [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."}
        ]
        """
        template = self.TEMPLATES.get(role_type, STUDENT_QA_TEMPLATE)

        content = template.format(
            structured_context=structured_context,
            knowledge_context=knowledge_context,
            history=history,
            question=question
        )

        return [
            {"role": "user", "content": question}
        ]
```

## 关键设计点
1. **角色区分**：三个不同的 Prompt 模板
2. **上下文格式**：清晰区分结构化数据 vs 知识库内容
3. **历史记录**：支持会话上下文

## 代码规范
- 模板字符串格式化
- 类型注解
- 文档字符串

## 输出要求
创建完整的两个文件
```

**Skill 调用**：
```
/python-patterns - 模板字符串
/python-reviewer
```

---

#### 📋 Phase 2.4: RAG 引擎编排

**文件**：`RAG/services/rag/rag_engine.py`

**Prompt**：
```
# 任务：实现 RAG 引擎（核心编排）

## 项目背景
- 整合 structured_query + vector_search + context_assembler + prompt_builder + llm
- 支持流式输出

## 依赖服务
```python
from services.rag.structured_query import StructuredQueryService
from services.rag.vector_search import VectorSearchService
from services.rag.context_assembler import ContextAssembler
from services.rag.prompt_builder import PromptBuilder
from services.llm.factory import LLMFactory
```

## 实现要求

```python
class QueryParser:
    """解析用户查询，提取实体"""

    def parse(self, question: str) -> dict:
        """
        解析查询，提取实体

        返回：
        {
            "intent": "employment_stats" | "job_recommend" | "policy" | "general",
            "entities": {
                "major": "计算机" | None,
                "province": "北京" | None,
                "industry": "互联网" | None,
            }
        }
        """
        # 简单的关键词匹配
        # 后续可升级为 LLM 解析


class RAGEngine:
    """RAG 引擎 - 核心编排"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.query_parser = QueryParser()
        self.structured_query = StructuredQueryService(db)
        self.vector_search = VectorSearchService()
        self.context_assembler = ContextAssembler()
        self.prompt_builder = PromptBuilder()
        self.llm = LLMFactory.get_adapter("tongyi")

    async def ask(
        self,
        question: str,
        user_id: str,
        role_type: str,
        session_id: str | None = None
    ) -> dict:
        """
        非流式问答

        返回：
        {
            "answer": "...",
            "sources": [...],
            "session_id": "..."
        }
        """
        # Step 1: 解析查询
        parsed = self.query_parser.parse(question)

        # Step 2: 查询结构化数据
        structured_data = {}
        entities = parsed.get("entities", {})

        if entities.get("major"):
            structured_data["就业数据"] = await self.structured_query.get_employment_by_major(
                entities["major"]
            )
        if entities.get("province"):
            structured_data["人才需求"] = await self.structured_query.get_talent_demand_by_province(
                entities["province"]
            )
        if user_id and role_type == "student":
            structured_data["学生画像"] = await self.structured_query.get_student_profile(user_id)

        # Step 3: 向量检索
        docs = await self.vector_search.search(
            query=question,
            role_type=role_type,
            k=5
        )

        # Step 4: 组装上下文
        structured_context = self.context_assembler.format_structured_context(structured_data)
        knowledge_context = self.context_assembler.format_knowledge_context(docs)

        # Step 5: 获取历史（简化，暂用空字符串）
        history = ""

        # Step 6: 构建 Prompt
        messages = self.prompt_builder.build(
            role_type=role_type,
            question=question,
            structured_context=structured_context,
            knowledge_context=knowledge_context,
            history=history
        )

        # Step 7: LLM 生成
        answer = self.llm.chat(messages)

        return {
            "answer": answer,
            "sources": docs,
            "session_id": session_id or generate_session_id()
        }

    async def ask_stream(
        self,
        question: str,
        user_id: str,
        role_type: str,
        session_id: str | None = None
    ):
        """
        流式问答 - 使用 async generator

        Yields:
            dict: {"content": "字", "done": false}
            dict: {"content": "符", "done": false}
            ...
            dict: {"content": "完整回答", "done": true}
        """
        # 类似 ask() 但最后用 yield 返回
        # self.llm.stream(messages) 返回 async generator
        async for chunk in self.llm.stream(messages):
            yield {"content": chunk, "done": False}
        yield {"content": "", "done": True}
```

## 关键设计点
1. **分层解耦**：各服务独立，通过 RAGEngine 编排
2. **流式输出**：async generator 模式
3. **实体提取**：QueryParser 预留扩展

## 代码规范
- async/await 全程
- 完整类型注解
- 文档字符串

## 输出要求
创建完整的 rag_engine.py，包含 QueryParser 和 RAGEngine
```

**Skill 调用**：
```
/python-patterns - async generator
/python-reviewer
/backend-patterns - 服务编排模式
```

---

### Phase 3: LLM 适配器

---

#### 📋 Phase 3.1: LLM 适配器实现

**文件**：`RAG/services/llm/base.py`, `RAG/services/llm/tongyi_adapter.py`, `RAG/services/llm/factory.py`

**Prompt**：
```
# 任务：实现 LLM 适配器层

## 设计模式：适配器模式

```
                    ┌─────────────────┐
                    │   LLMFactory    │
                    │   (工厂类)      │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
      ┌────────────┐ ┌────────────┐ ┌────────────┐
      │  Tongyi   │ │  DeepSeek │ │  MiniMax   │
      │  Adapter   │ │   Adapter  │ │   Adapter  │
      └─────┬──────┘ └────────────┘ └────────────┘
            │
            ▼
      ┌────────────┐
      │  Base      │
      │  Adapter   │
      │ (ABC)      │
      └────────────┘
```

## 1. 抽象基类 (base.py)

```python
from abc import ABC, abstractmethod
from typing import AsyncGenerator

class LLMAdapter(ABC):
    """LLM 适配器抽象基类"""

    @abstractmethod
    async def chat(self, messages: list[dict], **kwargs) -> str:
        """
        同步聊天
        messages: [{"role": "user", "content": "..."}]
        返回: 完整回答字符串
        """
        pass

    @abstractmethod
    async def stream(self, messages: list[dict], **kwargs) -> AsyncGenerator[str, None]:
        """
        流式聊天
        Yields: 逐字返回
        """
        pass
```

## 2. Tongyi 适配器 (tongyi_adapter.py)

```python
from langchain_community.chat_models import ChatTongyi
from services.llm.base import LLMAdapter
import config_data as config

class TongyiAdapter(LLMAdapter):
    """通义千问适配器"""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.chat_model_name
        self.chat_model = ChatTongyi(model=self.model_name)

    async def chat(self, messages: list[dict], **kwargs) -> str:
        # LangChain 的 ChatTongyi.invoke() 是 sync 的
        # 需要在线程池中运行
        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.chat_model.invoke(messages)
        )
        return response.content

    async def stream(self, messages: list[dict], **kwargs) -> AsyncGenerator[str, None]:
        # ChatTongyi.astream() 是 async 的
        async for chunk in self.chat_model.astream(messages):
            yield chunk.content
```

## 3. 工厂类 (factory.py)

```python
from services.llm.base import LLMAdapter
from services.llm.tongyi_adapter import TongyiAdapter
# 后续扩展
# from services.llm.deepseek_adapter import DeepSeekAdapter

class LLMFactory:
    """LLM 适配器工厂"""

    _adapters = {
        "tongyi": TongyiAdapter,
        # "deepseek": DeepSeekAdapter,  # 后续添加
        # "minimax": MiniMaxAdapter,
    }

    @classmethod
    def get_adapter(cls, provider: str = "tongyi", **kwargs) -> LLMAdapter:
        """获取指定 provider 的适配器"""
        adapter_class = cls._adapters.get(provider.lower())
        if not adapter_class:
            raise ValueError(f"Unknown LLM provider: {provider}. Available: {list(cls._adapters.keys())}")
        return adapter_class(**kwargs)

    @classmethod
    def register_adapter(cls, name: str, adapter_class: type[LLMAdapter]):
        """注册新的适配器（后续扩展用）"""
        cls._adapters[name.lower()] = adapter_class
```

## 关键设计点
1. **适配器模式**：新 LLM 只需新增适配器类
2. **工厂模式**：统一入口，配置化
3. **async 支持**：chat 用线程池，stream 直接 async

## 代码规范
- ABC 抽象类
- async/await
- 类型注解

## 输出要求
创建完整的三个文件
```

**Skill 调用**：
```
/python-patterns - 适配器模式、ABC 类
/python-reviewer
```

---

### Phase 4: 文档处理

---

#### 📋 Phase 4.1: 文档解析器

**文件**：`RAG/services/document/parser.py`

**Prompt**：
```
# 任务：实现文档解析器（PDF/Word）

## 支持格式
- .pdf → PyMuPDF (fitz)
- .docx → python-docx
- .txt → 直接读取

## 实现要求

```python
from pathlib import Path
from typing import Literal

class DocumentParser:
    """文档解析器 - 提取纯文本"""

    SUPPORTED_FORMATS = {".pdf", ".docx", ".doc", ".txt"}

    def parse(self, file_path: str) -> str:
        """
        解析文档，返回纯文本

        Args:
            file_path: 文件路径

        Returns:
            提取的文本内容

        Raises:
            ValueError: 不支持的格式
            FileNotFoundError: 文件不存在
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        ext = path.suffix.lower()
        if ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"不支持的格式: {ext}. 支持: {self.SUPPORTED_FORMATS}")

        if ext == ".pdf":
            return self._parse_pdf(path)
        elif ext in {".docx", ".doc"}:
            return self._parse_docx(path)
        else:
            return self._parse_txt(path)

    def _parse_pdf(self, path: Path) -> str:
        """解析 PDF，提取文字（忽略图片）"""
        import fitz  # PyMuPDF
        text_parts = []

        with fitz.open(path) as doc:
            for page_num, page in enumerate(doc):
                text = page.get_text()
                if text.strip():
                    text_parts.append(f"[第{page_num + 1}页]\n{text}")

        return "\n".join(text_parts)

    def _parse_docx(self, path: Path) -> str:
        """解析 Word 文档"""
        from docx import Document

        doc = Document(path)
        paragraphs = []

        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text)

        return "\n".join(paragraphs)

    def _parse_txt(self, path: Path) -> str:
        """解析纯文本"""
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def validate_file(self, file_path: str) -> tuple[bool, str]:
        """
        验证文件

        Returns:
            (是否有效, 错误信息)
        """
        path = Path(file_path)

        if not path.exists():
            return False, "文件不存在"

        ext = path.suffix.lower()
        if ext not in self.SUPPORTED_FORMATS:
            return False, f"不支持的格式: {ext}"

        # 检查文件大小（限制 10MB）
        if path.stat().st_size > 10 * 1024 * 1024:
            return False, "文件超过 10MB 限制"

        return True, ""
```

## 关键设计点
1. **格式支持**：pdf/docx/txt
2. **错误处理**：详细错误信息
3. **文件验证**：大小限制、格式检查
4. **分页标记**：PDF 加页码便于定位引用

## 依赖安装
```
pip install pymupdf python-docx
```

## 代码规范
- pathlib.Path 处理文件路径
- 异常处理
- 文档字符串

## 输出要求
创建完整的 parser.py
```

**Skill 调用**：
```
/python-patterns - 文件处理、异常处理
/code-reviewer - 安全审查（文件路径遍历）
```

---

#### 📋 Phase 4.2: 知识库同步

**文件**：`RAG/services/document/knowledge_sync.py`

**Prompt**：
```
# 任务：实现知识库同步服务

## 职责
- 将上传文档同时写入 SQLite（metadata）和 ChromaDB（vectors）
- 保证数据一致性

## 依赖
```python
from services.document.parser import DocumentParser
from db.repositories.knowledge_repo import KnowledgeRepository
from services.rag.vector_search import VectorSearchService
from db.connection import get_db
import uuid
from datetime import datetime
```

## 实现要求

```python
class KnowledgeSyncService:
    """知识库同步服务 - SQLite + ChromaDB 双写"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.parser = DocumentParser()
        self.knowledge_repo = KnowledgeRepository(db)
        self.vector_search = VectorSearchService()

    async def add_document(
        self,
        file_path: str,
        title: str,
        category: str = "shared",
        operator: str = "system"
    ) -> dict:
        """
        添加文档到知识库

        流程：
        1. 解析文档 → 文本
        2. 文本分块
        3. 同步写入 SQLite (metadata)
        4. 同步写入 ChromaDB (vectors)
        5. 更新 SQLite 的 vector_ids

        Returns:
            {
                "doc_id": "xxx",
                "chunks": 5,
                "message": "success"
            }
        """
        # Step 1: 解析文档
        content = self.parser.parse(file_path)

        # Step 2: 文本分块（复用现有的 text splitter）
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        import config_data as config

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=config.separators
        )

        if len(content) > config.max_spplit_char_num:
            chunks = splitter.split_text(content)
        else:
            chunks = [content]

        # Step 3: 生成 doc_id
        doc_id = str(uuid.uuid4())

        # Step 4: 写入 SQLite (metadata)
        doc_data = {
            "doc_id": doc_id,
            "title": title,
            "content": content[:1000],  # 只存前1000字符作为预览
            "doc_type": Path(file_path).suffix,
            "category": category,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        await self.knowledge_repo.create(doc_data)

        # Step 5: 写入 ChromaDB (vectors)
        metadatas = [{
            "source": title,
            "doc_id": doc_id,
            "chunk_index": i,
            "operator": operator,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        } for i in range(len(chunks))]

        # 生成固定的 ID 列表
        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]

        await self.vector_search.add_documents(chunks, metadatas, ids)

        # Step 6: 更新 SQLite 的 vector_ids
        vector_ids = ",".join(ids)
        await self.knowledge_repo.update(doc_id, {"vector_ids": vector_ids})

        return {
            "doc_id": doc_id,
            "chunks": len(chunks),
            "message": "success"
        }

    async def delete_document(self, doc_id: str) -> bool:
        """
        删除文档（SQLite + ChromaDB 同步删除）

        Returns:
            是否成功
        """
        # Step 1: 获取 vector_ids
        doc = await self.knowledge_repo.get_by_id(doc_id)
        if not doc:
            return False

        # Step 2: 删除 ChromaDB vectors
        if doc.get("vector_ids"):
            ids = doc["vector_ids"].split(",")
            await self.vector_search.delete_by_ids(ids)

        # Step 3: 删除 SQLite record
        await self.knowledge_repo.delete(doc_id)

        return True
```

## 关键设计点
1. **双写一致性**：SQLite + ChromaDB 同时写入
2. **分块存储**：ChromaDB 存分块，SQLite 存 vector_ids 关联
3. **软删除考虑**：可后续加 is_deleted 字段支持软删除

## 代码规范
- async/await
- 事务处理
- 完整类型注解

## 输出要求
创建完整的 knowledge_sync.py
```

**Skill 调用**：
```
/python-patterns - async 服务设计
/python-reviewer
/code-reviewer - 数据一致性审查
```

---

### Phase 5: API 路由层

---

#### 📋 Phase 5.1: 问答 API

**文件**：`RAG/api/qa.py`

**Prompt**：
```
# 任务：实现问答 API

## API 设计

### POST /api/v1/rag/qa
非流式问答

### POST /api/v1/rag/qa/stream
流式问答（SSE）

## 实现要求

```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.request import QARequest
from schemas.response import BaseResponse, QAResponse, SourceItem
from services.rag.rag_engine import RAGEngine
from db.connection import get_db
import json

router = APIRouter(prefix="/rag", tags=["RAG"])

# 依赖注入
async def get_rag_engine(db: AsyncSession = Depends(get_db)) -> RAGEngine:
    return RAGEngine(db)

@router.post("/qa")
async def qa(
    req: QARequest,
    engine: RAGEngine = Depends(get_rag_engine)
) -> BaseResponse:
    """
    智能问答（非流式）
    """
    try:
        result = await engine.ask(
            question=req.question,
            user_id=req.user_id,
            role_type=req.role_type,
            session_id=req.session_id
        )

        # 转换 sources 格式
        sources = []
        for doc in result.get("sources", []):
            sources.append(SourceItem(
                type="document",
                content=doc.get("content", ""),
                metadata=doc.get("metadata", {})
            ))

        return BaseResponse(
            code=200,
            message="success",
            data={
                "answer": result["answer"],
                "sources": [s.model_dump() for s in sources],
                "session_id": result["session_id"]
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/qa/stream")
async def qa_stream(
    req: QARequest,
    engine: RAGEngine = Depends(get_rag_engine)
):
    """
    智能问答（流式输出）

    返回 SSE 格式：
    data: {"content": "字", "done": false}
    data: {"content": "符", "done": false}
    ...
    data: {"content": "", "done": true}
    """
    async def generate():
        try:
            async for chunk in engine.ask_stream(
                question=req.question,
                user_id=req.user_id,
                role_type=req.role_type,
                session_id=req.session_id
            ):
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        except Exception as e:
            error = {"content": f"Error: {str(e)}", "done": True}
            yield f"data: {json.dumps(error, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
```

## SSE 前端消费示例
```javascript
const eventSource = new EventSource('/api/v1/rag/qa/stream', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({question: '...', user_id: '...', role_type: '...'})
});

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.done) {
        eventSource.close();
    } else {
        // 追加到聊天框
        appendText(data.content);
    }
};
```

## 错误处理
- 400: 参数错误
- 500: 服务端错误

## 输出要求
创建完整的 qa.py
```

**Skill 调用**：
```
/api-design - SSE 流式响应规范
/backend-patterns - 中间件模式
/tdd-workflow - 接口测试
```

---

#### 📋 Phase 5.2: 上传与历史 API

**文件**：`RAG/api/upload.py`, `RAG/api/history.py`

**Prompt**：
```
# 任务：实现上传和历史 API

## 上传 API (upload.py)

```python
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import tempfile
import os
from pathlib import Path

from schemas.response import BaseResponse, UploadResponse
from services.document.knowledge_sync import KnowledgeSyncService
from db.connection import get_db

router = APIRouter(prefix="/rag/knowledge", tags=["Knowledge"])

@router.post("/upload")
async def upload_knowledge(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form("shared"),
    db: AsyncSession = Depends(get_db)
) -> BaseResponse:
    """
    上传知识文档

    支持格式：.txt, .pdf, .docx
    """
    # 1. 验证文件类型
    allowed_types = {"text/plain", "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
    if file.content_type not in allowed_types:
        # 也支持根据扩展名判断
        ext = Path(file.filename).suffix.lower()
        if ext not in {".txt", ".pdf", ".docx", ".doc"}:
            raise HTTPException(status_code=400, detail=f"不支持的文件格式: {ext}")

    # 2. 保存到临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # 3. 同步到知识库
        sync_service = KnowledgeSyncService(db)
        result = await sync_service.add_document(
            file_path=tmp_path,
            title=title,
            category=category
        )

        return BaseResponse(
            code=200,
            message="上传成功",
            data=UploadResponse(
                doc_id=result["doc_id"],
                chunks=result["chunks"]
            ).model_dump()
        )

    finally:
        # 4. 清理临时文件
        os.unlink(tmp_path)

@router.get("/list")
async def list_knowledge(
    category: str | None = None,
    page: int = 1,
    page_size: int = 10,
    db: AsyncSession = Depends(get_db)
) -> BaseResponse:
    """获取知识库列表"""

@router.delete("/{doc_id}")
async def delete_knowledge(
    doc_id: str,
    db: AsyncSession = Depends(get_db)
) -> BaseResponse:
    """删除知识文档"""
```

## 历史 API (history.py)

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.request import HistoryRequest
from schemas.response import BaseResponse, MessageItem
from db.connection import get_db

router = APIRouter(prefix="/rag/chat", tags=["Chat"])

@router.get("/history")
async def get_history(
    session_id: str | None = None,
    user_id: str | None = None,
    db: AsyncSession = Depends(get_db)
) -> BaseResponse:
    """获取会话历史"""

@router.delete("/history")
async def delete_history(
    session_id: str,
    db: AsyncSession = Depends(get_db)
) -> BaseResponse:
    """清空会话历史"""
```

## 输出要求
创建完整的 upload.py 和 history.py
```

**Skill 调用**：
```
/api-design - REST API 规范
/backend-patterns - 文件上传处理
/code-reviewer - 文件上传安全
/tdd-workflow - 接口测试
```

---

### Phase 6: 代码审查

---

#### 📋 Phase 6: 最终代码审查

**Prompt**：
```
# 任务：RAG 模块全面代码审查

## 项目信息
- 项目：高校学生就业信息平台 RAG 模块
- 位置：d:\Deep Learning\jisuanji\4c-1\RAG\

## 审查范围
对以下所有代码进行审查：

1. **db/** - 数据库层
   - connection.py
   - repositories/base_repository.py
   - repositories/knowledge_repo.py

2. **services/** - 业务服务层
   - llm/base.py, tongyi_adapter.py, factory.py
   - rag/rag_engine.py, structured_query.py, vector_search.py
   - rag/context_assembler.py, prompt_builder.py
   - document/parser.py, knowledge_sync.py
   - chat/history_service.py

3. **api/** - API 路由层
   - qa.py, upload.py, history.py

4. **schemas/** - 数据模型
   - request.py, response.py

5. **app.py** - 入口

## 审查标准

### 1. Security（最高优先级）
- [ ] 无硬编码密钥/密码
- [ ] 无 SQL 注入风险
- [ ] 文件上传安全（路径遍历检查）
- [ ] 输入验证完整

### 2. Code Quality
- [ ] 类型注解完整
- [ ] 文档字符串完整
- [ ] 错误处理完善
- [ ] 无重复代码
- [ ] 遵循 python-patterns

### 3. Architecture
- [ ] 分层清晰
- [ ] 依赖注入正确
- [ ] 适配器模式正确实现

### 4. Performance
- [ ] 异步操作正确使用
- [ ] 无阻塞操作
- [ ] 数据库连接正确管理

## 输出格式

```markdown
## 审查报告

### CRITICAL
（必须修复的问题）

### HIGH
（建议修复的问题）

### MEDIUM
（可以优化的问题）

### LOW
（代码风格问题）

### 总结
- CRITICAL: X
- HIGH: X
- MEDIUM: X
- LOW: X

Verdict: APPROVE / WARNING / BLOCK
```

## 执行指令

请使用以下 skills 进行全面审查：
1. /code-reviewer - 整体代码审查
2. /python-reviewer - Python 专项审查
3. /database-reviewer - SQL 查询审查
```

---

## 七、验证方案

### 7.1 启动服务
```bash
cd RAG
pip install -r requirements.txt
uvicorn app:app --reload --port 1145
```

### 7.2 测试接口

**健康检查**
```bash
curl http://localhost:1145/health
```

**测试问答**
```bash
curl -X POST http://localhost:1145/api/v1/rag/qa \
  -H "Content-Type: application/json" \
  -d '{"question": "计算机专业的就业率怎么样？", "user_id": "test", "role_type": "student"}'
```

**测试上传**
```bash
curl -X POST http://localhost:1145/api/v1/rag/knowledge/upload \
  -F "file=@./data/test.txt" \
  -F "title=测试文档" \
  -F "category=student"
```

---

## 八、风险与注意事项

| 风险 | 等级 | 缓解措施 |
|------|------|----------|
| ChromaDB 并发写入锁 | 🟡 中 | 加线程锁 |
| PDF 解析超时 | 🟡 中 | 加超时限制 |
| 流式输出断连 | 🟡 中 | 前端重连机制 |
| RAG 服务独立运行 | 🟡 中 | 1145 端口 CORS 配置 |
