#!/bin/bash
set -e

export PATH="$HOME/.local/bin:$PATH"

echo "=========================================="
echo "Stock Agent - 로컬 환경 시작"
echo "=========================================="

echo ""
echo "1. 기존 프로세스 종료 중..."

# 백엔드 프로세스 종료
if [ -f app.pid ]; then
    PID=$(cat app.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "  - Backend(PID: $PID) 종료 중..."
        kill $PID 2>/dev/null || true
        sleep 2
    fi
    rm -f app.pid
fi

# 프론트엔드 프로세스 종료
if [ -f ui.pid ]; then
    PID=$(cat ui.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "  - Frontend(PID: $PID) 종료 중..."
        kill $PID 2>/dev/null || true
        sleep 2
    fi
    rm -f ui.pid
fi

echo ""
echo "2. 환경 변수 확인 중..."
if [ ! -f .env ]; then
    echo "  ⚠️  .env 파일이 없습니다. .env.example을 복사하여 .env를 생성하세요."
    echo "     cp .env.example .env"
    exit 1
fi

echo "  ✓ .env 파일 확인 완료"

echo ""
echo "3. 의존성 설치 중..."
if command -v uv &> /dev/null; then
    uv sync
else
    echo "  ⚠️  uv가 설치되어 있지 않습니다. pip를 사용합니다."
    pip install -r requirements.txt 2>/dev/null || echo "  - requirements.txt 없음, 건너뜀"
fi

echo ""
echo "4. 백엔드 서버(FastAPI) 시작 중..."
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8001 > app.log 2>&1 &
echo $! > app.pid
echo "  ✓ Backend 시작됨 (PID: $(cat app.pid))"

echo ""
echo "5. 서비스 준비 상태 확인 중..."
MAX_WAIT=30
WAIT_COUNT=0

while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo "  ✓ 백엔드 서비스 준비 완료!"
        break
    fi
    echo -ne "\r  - 백엔드 응답 대기 중... ($WAIT_COUNT/$MAX_WAIT초)"
    sleep 1
    WAIT_COUNT=$((WAIT_COUNT + 1))
done

echo ""

if [ $WAIT_COUNT -eq $MAX_WAIT ]; then
    echo "  ⚠️  백엔드 서비스가 시작되지 않았습니다. app.log를 확인하세요."
    exit 1
fi

echo ""
echo "6. 프론트엔드 서버(Streamlit) 시작 중..."
if [ -d "infra/frontend" ] && [ -f "infra/frontend/ui.py" ]; then
    export BACKEND_URL="http://localhost:8001"
    nohup python -m streamlit run infra/frontend/ui.py --server.port 8002 > ui.log 2>&1 &
    echo $! > ui.pid
    echo "  ✓ Frontend 시작됨 (PID: $(cat ui.pid))"
else
    echo "  ⚠️  프론트엔드 파일이 없습니다. 백엔드만 실행합니다."
fi

echo ""
echo "=========================================="
echo "✅ 서비스가 성공적으로 시작되었습니다!"
echo "=========================================="
echo ""
echo "📌 접속 정보:"
echo "  - 백엔드 API: http://localhost:8001"
echo "  - API 문서: http://localhost:8001/docs"
if [ -f ui.pid ]; then
    echo "  - 프론트엔드: http://localhost:8002"
fi
echo ""
echo "📋 로그 확인:"
echo "  - Backend: tail -f app.log"
if [ -f ui.pid ]; then
    echo "  - Frontend: tail -f ui.log"
fi
echo ""
echo "🛑 종료: sh stop.sh"
echo "=========================================="
