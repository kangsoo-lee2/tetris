#!/bin/bash
# Tetris 백엔드 서버 시작
# 실행: bash start.sh
# 접속: http://localhost:8765/index.html

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Tetris Backend ==="
pip install -r requirements.txt -q

echo "Starting FastAPI on :8000 ..."
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

sleep 1

echo "Starting static file server on :8765 ..."
python3 -m http.server 8765 &
STATIC_PID=$!

echo ""
echo "  Backend API : http://localhost:8000/docs"
echo "  Game        : http://localhost:8765/index.html"
echo ""
echo "Press Ctrl+C to stop both servers."

trap "kill $BACKEND_PID $STATIC_PID 2>/dev/null; exit" INT TERM
wait
