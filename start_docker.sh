#!/bin/bash
set -e

echo "=========================================="
echo "Stock Agent - Docker 환경 시작"
echo "=========================================="

echo ""
echo "1. Docker 이미지 빌드 중..."

# Backend 이미지 빌드
echo "  - Backend 이미지 빌드 중..."
docker build --target backend -t stock-agent-backend:latest . --quiet && echo "    ✓ Backend 빌드 완료" || {
    echo "    ✗ Backend 빌드 실패"
    exit 1
}

# Frontend 이미지 빌드
echo "  - Frontend 이미지 빌드 중..."
docker build --target frontend -t stock-agent-frontend:latest . --quiet && echo "    ✓ Frontend 빌드 완료" || {
    echo "    ✗ Frontend 빌드 실패"
    exit 1
}

echo ""
echo "2. 환경 변수 확인 중..."
if [ ! -f .env ]; then
    echo "  ⚠️  .env 파일이 없습니다. .env.example을 복사하여 .env를 생성하세요."
    echo "     cp .env.example .env"
    exit 1
fi
echo "  ✓ .env 파일 확인 완료"

echo ""
echo "3. Docker Compose 실행 중..."
docker-compose up -d

echo ""
echo "4. 서비스 준비 상태 확인 중..."
MAX_WAIT=60
WAIT_COUNT=0

while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    # 컨테이너 상태 확인
    if ! docker ps | grep -q stock-agent-backend; then
        echo -ne "\r  - 컨테이너 시작 대기 중... ($WAIT_COUNT/$MAX_WAIT초)"
        sleep 1
        WAIT_COUNT=$((WAIT_COUNT + 1))
        continue
    fi

    # Health check
    HEALTH_JSON=$(curl -s http://localhost:8001/health 2>/dev/null || echo '{"status":"waiting"}')
    HEALTH_STATUS=$(echo $HEALTH_JSON | grep -o '"status":"[^"]*"' | cut -d'"' -f4 || echo "waiting")
    
    if [ "$HEALTH_STATUS" = "healthy" ]; then
        echo ""
        echo "  ✓ 서비스 준비 완료!"
        break
    fi
    
    echo -ne "\r  - 서비스 준비 대기 중... ($WAIT_COUNT/$MAX_WAIT초)"
    sleep 1
    WAIT_COUNT=$((WAIT_COUNT + 1))
done

echo ""

if [ $WAIT_COUNT -eq $MAX_WAIT ]; then
    echo "  ⚠️  서비스가 정상적으로 시작되지 않았습니다."
    echo "     로그 확인: docker-compose logs"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ Docker 환경이 성공적으로 시작되었습니다!"
echo "=========================================="
echo ""
echo "📌 접속 정보:"
echo "  - 백엔드 API: http://localhost:8001"
echo "  - API 문서: http://localhost:8001/docs"
echo "  - 프론트엔드: http://localhost:8002"
echo "  - ChromaDB: http://localhost:8000"
echo ""
echo "📋 상태 확인:"
echo "  - 컨테이너 목록: docker ps"
echo "  - 로그 확인: docker-compose logs -f"
echo "  - 특정 서비스 로그: docker-compose logs -f backend"
echo ""
echo "🛑 종료: sh stop_docker.sh"
echo "=========================================="
