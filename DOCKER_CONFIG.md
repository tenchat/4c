# Docker 配置文件

## 文件结构

```
cccc/
├── docker-compose.yml              # 主编排文件
├── Dockerfile.frontend             # 前端镜像
├── nginx.conf                      # Nginx 配置
├── .dockerignore                   # Docker 忽略文件
├── .env.docker                     # 环境变量模板
├── .env.production                 # 生产环境变量
├── DOCKER_README.md                # Docker 部署说明
├── backend/
│   ├── Dockerfile                  # 后端镜像
│   └── docker-compose.yml          # 后端独立编排（MySQL+Redis）
└── RAG/
    └── Dockerfile                  # RAG 服务镜像
```

---

## docker-compose.yml

```yaml
version: '3.8'

services:
  # ========== 前端服务 ==========
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: cccc_frontend
    ports:
      - '3006:3006'
    depends_on:
      - backend
    networks:
      - cccc_network
    restart: unless-stopped

  # ========== 后端服务 ==========
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: cccc_backend
    ports:
      - '5174:5174'
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///./employment.db
      - REDIS_URL=redis://redis:6379/0
      - DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY:-}
      - JWT_SECRET_KEY=resibacksecretkey
      - APP_ENV=production
    volumes:
      - ./backend/employment.db:/app/employment.db
      - ./backend/uploads:/app/uploads
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - cccc_network
    restart: unless-stopped

  # ========== RAG 服务 ==========
  rag:
    build:
      context: ./RAG
      dockerfile: Dockerfile
    container_name: cccc_rag
    ports:
      - '1145:1145'
    environment:
      - DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY:-}
      - CHROMA_PERSIST_DIR=/app/chroma_db
      - CHROMA_COLLECTION_NAME=rag
      - CORS_ORIGINS=http://localhost:3006,http://localhost:5173
    volumes:
      - rag_data:/app/chroma_db
    networks:
      - cccc_network
    restart: unless-stopped

  # ========== Redis 服务 ==========
  redis:
    image: redis:7-alpine
    container_name: cccc_redis
    ports:
      - '6379:6379'
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - cccc_network
    restart: unless-stopped
    healthcheck:
      test: ['CMD', 'redis-cli', 'ping']
      interval: 2s
      timeout: 1s
      retries: 10

networks:
  cccc_network:
    driver: bridge

volumes:
  backend_data:
  rag_data:
  redis_data:
```

---

## Dockerfile.frontend

```dockerfile
# 前端 Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

# 复制依赖文件
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile

# 复制源代码
COPY . .

# 构建生产版本
RUN pnpm vite build

# 生产镜像
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3006

CMD ["nginx", "-g", "daemon off;"]
```

---

## nginx.conf

```nginx
server {
    listen 3006;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # SPA 路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 代理到后端
    location /api/ {
        proxy_pass http://cccc_backend:5174;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # RAG API 代理
    location /rag/ {
        proxy_pass http://cccc_rag:1145;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml application/javascript;
}
```

---

## backend/Dockerfile

```dockerfile
# 后端 Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码
COPY . .

# 创建上传目录
RUN mkdir -p /app/uploads/resumes

# 暴露端口
EXPOSE 5174

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5174"]
```

---

## RAG/Dockerfile

```dockerfile
# RAG 服务 Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码
COPY . .

# 创建必要的目录
RUN mkdir -p /app/chroma_db /app/db /app/chat_history /app/data /app/uploads

# 暴露端口
EXPOSE 1145

# 启动命令
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "1145"]
```

---

## .dockerignore

```dockerignore
# Git
.git
.gitignore

# IDE
.vscode
.idea
*.md

# 依赖
node_modules
__pycache__
*.pyc
.venv
.pytest_cache

# 环境文件
.env
.env.*
!.env.docker

# 日志
*.log
npm-debug.log*

# 临时文件
.DS_Store
Thumbs.db
*.tmp

# 数据库 (容器内使用 volume 挂载)
*.db
!employment.db

# 构建产物
dist
build
*.egg-info

# 测试
.coverage
htmlcov
tests
backend/tests
```

---

## .env.docker

```env
# Docker 环境变量模板
# 复制此文件为 .env 并填入实际值

# 阿里云 DashScope API Key (必需)
# 用于 RAG 服务的 LLM 和 Embedding 功能
DASHSCOPE_API_KEY=your_dashscope_api_key_here
```

---

## .env.production

```env
# 【生产】环境变量

# 应用部署基础路径
VITE_BASE_URL = /

# API 代理地址（相对路径，由 Nginx 代理到后端）
VITE_API_BASE_URL =
VITE_API_PROXY_URL = http://cccc_backend:5174

# Delete console
VITE_DROP_CONSOLE = true
```

---

## backend/docker-compose.yml

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: employment_mysql
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: employment_db
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    command: --default-authentication-plugin=mysql_native_password

  redis:
    image: redis:7-alpine
    container_name: employment_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  mysql_data:
  redis_data:
```

---

## DOCKER_README.md

```markdown
# Docker 一键部署配置

## 快速开始

1. 克隆项目后，创建 `.env` 文件：
   ```bash
   cp .env.docker .env
   # 编辑 .env 填入 DASHSCOPE_API_KEY
   ```

2. 确保存在数据库文件：
   - Windows: `backend\employment.db`
   - Linux/Mac: `backend/employment.db`

3. 启动服务：
   ```bash
   docker compose up -d
   ```

4. 访问 http://localhost:3006

## 服务说明

| 服务 | 端口 | 说明 |
|------|------|------|
| frontend | 3006 | Vue 前端 + Nginx |
| backend | 5174 | FastAPI 后端 |
| rag | 1145 | RAG 服务 |
| redis | 6379 | Redis 缓存 |

## 注意事项

- 数据库文件通过 volume 挂载到容器内 `/app/employment.db`
- RAG 服务的 Chroma 数据持久化到 `rag_data` volume
- Redis 数据持久化到 `redis_data` volume
```
