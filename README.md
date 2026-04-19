# 大学生就业信息智能分析平台

## 一、项目简介

本项目是一个面向大学生就业信息管理的智能分析平台，包含以下功能：

- 学生简历管理与分析
- 岗位推荐与匹配
- 院校就业数据统计
- AI 智能问答（RAG）

## 二、技术架构

| 模块     | 技术栈                         | 端口 |
| -------- | ------------------------------ | ---- |
| 前端     | Vue 3 + Vite + Element Plus    | 3006 |
| 后端     | FastAPI + SQLAlchemy + Redis   | 5174 |
| RAG 服务 | FastAPI + LangChain + ChromaDB | 1145 |
| 数据库   | SQLite（默认）/ MySQL（可选）  | -    |
| 缓存     | Redis                          | 6379 |

## 三、Docker 一键部署

### 1. 配置环境变量

```bash
cp .env.docker .env
```

编辑 `.env` 文件，填入你的阿里云 DashScope API Key：

```
DASHSCOPE_API_KEY=your_actual_api_key_here
```

## 四、本地开发

### 前端

```bash
pnpm install
pnpm dev
```

### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 5174
```

### RAG 服务

```bash
cd RAG
pip install -r requirements.txt
uvicorn app:app --reload --port 1145
```

## 五、常见问题

### Q: 端口被占用？

修改启动命令中的 `--port` 参数。

### Q: RAG 服务功能不可用？

确保 `.env` 文件中配置了有效的 `DASHSCOPE_API_KEY`（阿里云通义千问 API Key）。
