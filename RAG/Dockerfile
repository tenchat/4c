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