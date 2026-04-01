# RAG 服务使用说明

## 快速开始

### 1. 安装依赖

```bash
cd RAG
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
python -m db.init_db
```

### 3. 启动服务

```bash
# 开发模式（自动重载）
uvicorn app:app --reload --port 1145

# 或直接运行
python app.py
```

### 4. 访问 API 文档

打开浏览器访问：http://localhost:1145/docs

## API 接口

### 问答接口

```bash
# 非流式问答
curl -X POST http://localhost:1145/api/v1/rag/qa \
  -H "Content-Type: application/json" \
  -d '{
    "question": "计算机专业的就业率怎么样？",
    "user_id": "test_user",
    "role_type": "student"
  }'

# 流式问答
curl -X POST http://localhost:1145/api/v1/rag/qa/stream \
  -H "Content-Type: application/json" \
  -d '{
    "question": "计算机专业好就业吗？",
    "user_id": "test_user",
    "role_type": "student"
  }'
```

### 知识库接口

```bash
# 上传文档
curl -X POST http://localhost:1145/api/v1/rag/knowledge/upload \
  -F "file=@./data/test.txt" \
  -F "title=测试文档" \
  -F "category=student"

# 获取知识库列表
curl http://localhost:1145/api/v1/rag/knowledge/list

# 删除文档
curl -X DELETE http://localhost:1145/api/v1/rag/knowledge/{doc_id}
```

### 健康检查

```bash
curl http://localhost:1145/health
```

## 目录结构

```
RAG/
├── app.py                      # FastAPI 入口
├── config_data.py              # 配置文件
├── requirements.txt             # 依赖
│
├── api/                        # API 路由
│   ├── qa.py                   # 问答接口
│   ├── upload.py               # 上传接口
│   └── history.py               # 历史接口
│
├── schemas/                     # Pydantic 模型
│   ├── request.py
│   └── response.py
│
├── db/                         # 数据库层
│   ├── connection.py           # 连接管理
│   ├── init_db.py             # 初始化脚本
│   ├── models/                 # SQLAlchemy 模型
│   └── repositories/           # 仓储层
│
├── services/                   # 业务服务层
│   ├── llm/                   # LLM 适配器
│   │   ├── base.py
│   │   ├── tongyi_adapter.py
│   │   └── factory.py
│   ├── rag/                   # RAG 核心
│   │   ├── structured_query.py
│   │   ├── vector_search.py
│   │   ├── context_assembler.py
│   │   ├── prompt_builder.py
│   │   └── rag_engine.py
│   ├── document/              # 文档处理
│   │   ├── parser.py
│   │   └── knowledge_sync.py
│   └── chat/                  # 会话管理
│       └── history_service.py
│
├── chroma_db/                  # ChromaDB 向量库
├── chat_history/              # 会话历史文件
└── data/                      # 测试数据
```

## 扩展指南

### 添加新的 LLM 适配器

1. 在 `services/llm/` 下创建新的适配器类，如 `deepseek_adapter.py`
2. 继承 `LLMAdapter` 基类
3. 实现 `chat()` 和 `stream()` 方法
4. 在 `factory.py` 中注册

```python
# services/llm/deepseek_adapter.py
from services.llm.base import LLMAdapter

class DeepSeekAdapter(LLMAdapter):
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        ...

    async def chat(self, messages, **kwargs) -> str:
        ...

    async def stream(self, messages, **kwargs):
        ...
```

### 添加新的知识库来源

在 `services/rag/structured_query.py` 中添加新的查询方法。
