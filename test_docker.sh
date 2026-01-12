#!/bin/bash

echo "=========================================="
echo "Stock Agent - Docker 테스트"
echo "=========================================="
echo ""

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. Docker 확인
echo "1. Docker 환경 확인..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✓${NC} Docker 설치됨: $DOCKER_VERSION"
else
    echo -e "${RED}✗${NC} Docker가 설치되어 있지 않습니다."
    exit 1
fi

if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗${NC} Docker 데몬이 실행되지 않았습니다."
    echo "   Docker Desktop을 실행하세요."
    exit 1
fi

# 2. 기존 컨테이너 정리
echo ""
echo "2. 기존 테스트 컨테이너 정리 중..."
docker rm -f test-stock-backend 2>/dev/null || true
echo -e "${GREEN}✓${NC} 정리 완료"

# 3. 이미지 빌드
echo ""
echo "3. Docker 이미지 빌드 중..."
echo "   (시간이 좀 걸릴 수 있습니다...)"
docker build --target backend -t test-stock-backend:latest . -q
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} 이미지 빌드 완료"
else
    echo -e "${RED}✗${NC} 이미지 빌드 실패"
    exit 1
fi

# 4. 컨테이너 실행
echo ""
echo "4. 컨테이너 시작 중..."
docker run -d \
    --name test-stock-backend \
    -p 8001:8001 \
    -e UPSTAGE_API_KEY=dummy_key \
    -e CHROMA_MODE=local \
    test-stock-backend:latest

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} 컨테이너 시작됨"
else
    echo -e "${RED}✗${NC} 컨테이너 시작 실패"
    exit 1
fi

# 5. 서버 준비 대기
echo ""
echo "5. 서버 준비 대기 중..."
MAX_WAIT=30
WAIT_COUNT=0

while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} 서버 준비 완료!"
        break
    fi
    echo -ne "\r   대기 중... ($WAIT_COUNT/$MAX_WAIT초)"
    sleep 1
    WAIT_COUNT=$((WAIT_COUNT + 1))
done

echo ""

if [ $WAIT_COUNT -eq $MAX_WAIT ]; then
    echo -e "${RED}✗${NC} 서버 시작 실패"
    echo ""
    echo "컨테이너 로그:"
    docker logs test-stock-backend
    docker rm -f test-stock-backend
    exit 1
fi

# 6. API 테스트
echo ""
echo "=========================================="
echo "API 엔드포인트 테스트"
echo "=========================================="

echo ""
echo "📍 테스트 1: Health Check"
RESPONSE=$(curl -s http://localhost:8001/health)
if echo "$RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓${NC} Health Check 정상"
else
    echo -e "${RED}✗${NC} Health Check 실패"
fi

echo ""
echo "📍 테스트 2: Agent Health"
RESPONSE=$(curl -s http://localhost:8001/agent/health)
if echo "$RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓${NC} Agent Health 정상"
else
    echo -e "${RED}✗${NC} Agent Health 실패"
fi

echo ""
echo "📍 테스트 3: Chat API"
RESPONSE=$(curl -s -X POST http://localhost:8001/agent/chat \
    -H "Content-Type: application/json" \
    -d '{"query": "테스트"}')
if echo "$RESPONSE" | grep -q "answer"; then
    echo -e "${GREEN}✓${NC} Chat API 정상"
else
    echo -e "${RED}✗${NC} Chat API 실패"
fi

# 7. 컨테이너 정보
echo ""
echo "=========================================="
echo "컨테이너 정보"
echo "=========================================="
echo ""
docker ps --filter "name=test-stock-backend" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "=========================================="
echo "테스트 완료!"
echo "=========================================="
echo ""
echo -e "${YELLOW}📄 API 문서:${NC} http://localhost:8001/docs"
echo ""
echo -e "${YELLOW}📋 컨테이너 로그:${NC} docker logs -f test-stock-backend"
echo -e "${YELLOW}🛑 종료:${NC} docker rm -f test-stock-backend"
echo ""
echo "=========================================="
