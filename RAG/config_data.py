"""
RAG 服务配置

所有敏感配置应通过环境变量设置
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 文件 MD5 缓存
md5_path = os.getenv("RAG_MD5_PATH", "./md5.text")

# Chroma 向量数据库
collection_name = os.getenv("CHROMA_COLLECTION_NAME", "rag")
persist_directory = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

# 文本分割器
chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "100"))
separators = ["\n\n", "\n", ".", "!", "?", "。", "!", "?", " ", ""]
max_split_char_num = int(os.getenv("MAX_SPLIT_CHAR_NUM", "1000"))   # 文本分割阈值

# 检索配置
similarity_threshold = int(os.getenv("SIMILARITY_THRESHOLD", "1"))   # 检索返回数量

# LLM 配置
embedding_model_name = os.getenv("EMBEDDING_MODEL", "text-embedding-v4")
chat_model_name = os.getenv("CHAT_MODEL", "qwen3-max")

# CORS 配置（生产环境应设置具体域名）
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")