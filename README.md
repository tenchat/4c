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
| 前端     | Vue 3 + Vite + Element Plus    | 5173 |
| 后端     | FastAPI + SQLAlchemy + Redis   | 5174 |
| RAG 服务 | FastAPI + LangChain + ChromaDB | 1145 |
| 数据库   | SQLite（默认）/ MySQL（可选）  | -    |
| 缓存     | Redis                          | 6379 |

## 三、一键部署（推荐）

### 环境要求

- Node.js 20+
- Python 3.10以上
- pnpm 8+

### Windows 用户

1. 下载/克隆项目到本地
2. 双击运行 `install.bat` 安装所有依赖
3. 编辑 `backend\.env` 和 `RAG\.env` 文件，填入必要的配置信息
4. 双击运行 `start.bat` 启动所有服务

### Mac/Linux 用户

1. 下载/克隆项目到本地
2. 打开终端，进入项目目录
3. 运行 `chmod +x install.sh start-all.sh stop-all.sh`
4. 运行 `./install.sh` 安装所有依赖
5. 编辑 `backend/.env` 和 `RAG/.env` 文件，填入必要的配置信息
6. 运行 `./start-all.sh` 启动所有服务

### 服务地址

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:5173 |
| 后端 | http://localhost:5174 |
| RAG | http://localhost:1145 |

### 停止服务

- Windows: `stop.bat`
- Linux/Mac: `./stop-all.sh`

## 四、手动部署

### 前端

```bash
pnpm install
pnpm build
```

### Python 虚拟环境（后端和RAG共用）

```bash
# 创建共享虚拟环境
python -m venv .venv

# 安装后端依赖
cd backend
../.venv/bin/pip install -r requirements.txt  # Linux/Mac
..\.venv\Scripts\pip install -r requirements.txt  # Windows
cd ..

# 安装RAG依赖
cd RAG
../.venv/bin/pip install -r requirements.txt  # Linux/Mac
..\.venv\Scripts\pip install -r requirements.txt  # Windows
cd ..
```

### 启动服务

```bash
# 前端（构建后的 dist 目录）
npx serve dist -l 5173

# 后端
cd backend
.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 5174

# RAG
cd RAG
.venv/bin/python app.py
```

## 五、配置文件说明

| 文件 | 说明 |
|------|------|
| `backend/.env` | 后端配置（数据库、Redis、API Key 等） |
| `RAG/.env` | RAG 服务配置（DashScope API Key 等） |
| `.env` | 前端配置（端口等） |

## 六、常见问题

### Q: 端口被占用？

Windows 下可用以下命令停止占用端口的进程：

```cmd
taskkill /F /IM node.exe
taskkill /F /IM python.exe
```

### Q: RAG 服务功能不可用？

确保 `RAG/.env` 文件中配置了有效的 `DASHSCOPE_API_KEY`（阿里云通义千问 API Key）。

### Q: 安装依赖失败？

- 确保 Node.js 20+ 已安装
- 确保 Python 3.10+ 已安装
