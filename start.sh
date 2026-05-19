#!/bin/bash
# Tetris 서버 시작 (Docker Compose)
# 실행: bash start.sh
# 접속: http://localhost:8765/index.html

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env 파일이 없어 .env.example에서 복사했습니다. 필요시 내용을 수정하세요."
fi

echo "=== Tetris (Docker Compose) ==="
docker compose up --build -d

echo ""
echo "  Game        : http://localhost:8765/index.html"
echo "  Backend API : http://localhost:8000/docs"
echo ""
echo "로그 확인: docker compose logs -f"
echo "종료:     docker compose down"
