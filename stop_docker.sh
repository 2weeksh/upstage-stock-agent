#!/bin/bash
set -e

echo "=========================================="
echo "Stock Agent - Docker 환경 종료"
echo "=========================================="

echo ""
echo "Docker Compose 종료 중..."

# Docker Compose 서비스 중지 및 제거
docker-compose down

echo ""
echo "컨테이너 정리 확인..."
if docker ps -a | grep -q stock-agent; then
    echo "  - 남은 컨테이너 제거 중..."
    docker ps -a | grep stock-agent | awk '{print $1}' | xargs docker rm -f 2>/dev/null || true
fi

echo ""
echo "=========================================="
echo "✅ Docker 환경이 종료되었습니다."
echo "=========================================="
echo ""
echo "📋 참고:"
echo "  - 데이터 볼륨은 유지됩니다 (chroma_data/)"
echo "  - 완전 삭제: docker-compose down -v"
echo "  - 이미지 삭제: docker rmi stock-agent-backend:latest stock-agent-frontend:latest"
echo "=========================================="
