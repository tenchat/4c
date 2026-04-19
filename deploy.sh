#!/usr/bin/env bash
set -euo pipefail

if [ ! -f .env ]; then
  if [ -f .env.docker ]; then
    cp .env.docker .env
    echo "[INFO] 首次部署已创建 .env，请先填写 DASHSCOPE_API_KEY 和 JWT_SECRET_KEY 后重试。"
    exit 1
  fi
fi

jwt_line="$(grep -E '^JWT_SECRET_KEY=' .env || true)"
if [ -z "$jwt_line" ] || [ "$jwt_line" = "JWT_SECRET_KEY=" ] || [ "$jwt_line" = "JWT_SECRET_KEY=change-me-in-production" ]; then
  echo "[ERROR] JWT_SECRET_KEY 未配置或仍为占位值，请先修改 .env。"
  exit 1
fi

docker compose up -d --build

echo "[OK] 部署成功"
echo "Frontend: http://localhost:3006"
echo "Backend:  http://localhost:5174/docs"
echo "RAG:      http://localhost:1145/docs"
