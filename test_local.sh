#!/bin/bash

echo "=========================================="
echo "Stock Agent - 로컬 테스트"
echo "=========================================="
echo ""

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Python 확인
echo "1. Python 환경 확인..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} Python 설치됨: $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python이 설치되어 있지 않습니다."
    exit 1
fi

# 2. pip 확인 및 설치
echo ""
echo "2. pip 확인 및 설치..."
if ! command -v pip3 &> /dev/null; then
    echo "pip3가 설치되어 있지 않습니다. 설치 중..."
    sudo apt-get update -qq
    sudo apt-get install -y python3-pip -qq
fi

if command -v pip3 &> /dev/null; then
    echo -e "${GREEN}✓${NC} pip3 설치됨"
else
    echo -e "${RED}✗${NC} pip3 설치 실패"
    exit 1
fi

# 3. 필요한 패키지 확인 및 설치
echo ""
echo "3. 필수 패키지 설치 중..."
echo "   (처음 실행 시 시간이 걸릴 수 있습니다...)"

# 패키지 설치
pip3 install fastapi uvicorn python-dotenv httpx --quiet --user 2>/dev/null

# 설치 확인
if python3 -c "import fastapi, uvicorn" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} 패키지 설치 완료"
else
    echo -e "${YELLOW}⚠${NC} 패키지 설치 중... (조금만 기다려주세요)"
    pip3 install fastapi uvicorn python-dotenv httpx --user
    echo -e "${GREEN}✓${NC} 패키지 설치 완료"
fi

# 4. 서버 시작
echo ""
echo "4. Mock API 서버 시작 중..."
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 > test_app.log 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > test_app.pid
echo -e "${GREEN}✓${NC} 서버 시작됨 (PID: $SERVER_PID)"

# 5. 서버 준비 대기
echo ""
echo "5. 서버 준비 대기 중..."
MAX_WAIT=30
WAIT_COUNT=0

while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✓${NC} 서버 준비 완료!"
        break
    fi
    echo -ne "\r   대기 중... ($WAIT_COUNT/$MAX_WAIT초)"
    sleep 1
    WAIT_COUNT=$((WAIT_COUNT + 1))
done

echo ""

if [ $WAIT_COUNT -eq $MAX_WAIT ]; then
    echo -e "${RED}✗${NC} 서버 시작 실패. 로그를 확인합니다..."
    echo ""
    echo "=== 에러 로그 ==="
    cat test_app.log
    echo "================="
    echo ""
    kill $SERVER_PID 2>/dev/null
    rm -f test_app.pid
    exit 1
fi

# 6. API 테스트
echo ""
echo "=========================================="
echo "API 엔드포인트 테스트"
echo "=========================================="

echo ""
echo "📍 테스트 1: Root 엔드포인트"
RESPONSE=$(curl -s http://localhost:8001/)
if echo "$RESPONSE" | grep -q "Stock Agent API"; then
    echo -e "${GREEN}✓${NC} Root 엔드포인트 정상"
    echo "   응답: $(echo $RESPONSE | head -c 60)..."
else
    echo -e "${RED}✗${NC} Root 엔드포인트 실패"
    echo "   응답: $RESPONSE"
fi

echo ""
echo "📍 테스트 2: Health Check"
RESPONSE=$(curl -s http://localhost:8001/health)
if echo "$RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓${NC} Health Check 정상"
    echo "   응답: $RESPONSE"
else
    echo -e "${RED}✗${NC} Health Check 실패"
    echo "   응답: $RESPONSE"
fi

echo ""
echo "📍 테스트 3: Agent Health"
RESPONSE=$(curl -s http://localhost:8001/agent/health)
if echo "$RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓${NC} Agent Health 정상"
    echo "   응답: $RESPONSE"
else
    echo -e "${RED}✗${NC} Agent Health 실패"
    echo "   응답: $RESPONSE"
fi

echo ""
echo "📍 테스트 4: Seed Status"
RESPONSE=$(curl -s http://localhost:8001/agent/seed-status)
if echo "$RESPONSE" | grep -q "completed"; then
    echo -e "${GREEN}✓${NC} Seed Status 정상"
    echo "   응답: $RESPONSE"
else
    echo -e "${RED}✗${NC} Seed Status 실패"
    echo "   응답: $RESPONSE"
fi

echo ""
echo "📍 테스트 5: Stats"
RESPONSE=$(curl -s http://localhost:8001/agent/stats)
if echo "$RESPONSE" | grep -q "stock_embeddings"; then
    echo -e "${GREEN}✓${NC} Stats 정상"
    echo "   응답: $RESPONSE"
else
    echo -e "${RED}✗${NC} Stats 실패"
    echo "   응답: $RESPONSE"
fi

echo ""
echo "📍 테스트 6: Chat API"
RESPONSE=$(curl -s -X POST http://localhost:8001/agent/chat \
    -H "Content-Type: application/json" \
    -d '{"query": "삼성전자 분석해줘"}')
if echo "$RESPONSE" | grep -q "answer"; then
    echo -e "${GREEN}✓${NC} Chat API 정상"
    echo "   응답: $(echo $RESPONSE | head -c 80)..."
else
    echo -e "${RED}✗${NC} Chat API 실패"
    echo "   응답: $RESPONSE"
fi

echo ""
echo "📍 테스트 7: Stock Analysis"
RESPONSE=$(curl -s http://localhost:8001/api/v1/analyze/005930)
if echo "$RESPONSE" | grep -q "005930"; then
    echo -e "${GREEN}✓${NC} Stock Analysis 정상"
    echo "   응답: $RESPONSE"
else
    echo -e "${RED}✗${NC} Stock Analysis 실패"
    echo "   응답: $RESPONSE"
fi

echo ""
echo "=========================================="
echo "브라우저 테스트"
echo "=========================================="
echo ""
echo "다음 URL을 브라우저에서 확인하세요:"
echo ""
echo -e "${YELLOW}📄 API 문서 (Swagger):${NC}"
echo "   http://localhost:8001/docs"
echo ""
echo -e "${YELLOW}📊 대체 API 문서 (ReDoc):${NC}"
echo "   http://localhost:8001/redoc"
echo ""
echo -e "${YELLOW}🔍 직접 테스트:${NC}"
echo "   curl http://localhost:8001/health"
echo ""
echo "서버는 계속 실행 중입니다."
echo -e "${YELLOW}종료하려면:${NC} sh test_stop.sh"
echo "=========================================="
