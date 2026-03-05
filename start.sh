#!/bin/bash
cd "$(dirname "$0")"

# 启动后端
source .venv/bin/activate 2>/dev/null || python3 -m venv .venv && source .venv/bin/activate
.venv/bin/python3 -m pip install -q -r backend/requirements.txt
.venv/bin/python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 启动前端
cd frontend && npm install && npm run dev &
FRONTEND_PID=$!

echo "=== 3Body X 已启动 ==="
echo "前端: http://localhost:5173"
echo "API:  http://127.0.0.1:8000/docs"
echo "按 Ctrl+C 停止"
wait