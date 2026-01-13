#!/bin/bash
set -e

echo "=========================================="
echo "Stock Agent - 로컬 환경 종료"
echo "=========================================="

echo ""
echo "프로세스 종료 중..."

# 백엔드 프로세스 종료
if [ -f app.pid ]; then
    PID=$(cat app.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "  - Backend(PID: $PID) 종료 중..."
        kill $PID
        sleep 2
        # 강제 종료가 필요한 경우
        if ps -p $PID > /dev/null 2>&1; then
            echo "    강제 종료 중..."
            kill -9 $PID 2>/dev/null || true
        fi
        echo "  ✓ Backend 종료됨"
    else
        echo "  - Backend 프로세스가 실행 중이지 않습니다."
    fi
    rm -f app.pid
else
    echo "  - Backend PID 파일이 없습니다."
fi

# 프론트엔드 프로세스 종료
if [ -f ui.pid ]; then
    PID=$(cat ui.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "  - Frontend(PID: $PID) 종료 중..."
        kill $PID
        sleep 2
        # 강제 종료가 필요한 경우
        if ps -p $PID > /dev/null 2>&1; then
            echo "    강제 종료 중..."
            kill -9 $PID 2>/dev/null || true
        fi
        echo "  ✓ Frontend 종료됨"
    else
        echo "  - Frontend 프로세스가 실행 중이지 않습니다."
    fi
    rm -f ui.pid
else
    echo "  - Frontend PID 파일이 없습니다."
fi

echo ""
echo "=========================================="
echo "✅ 모든 서비스가 종료되었습니다."
echo "=========================================="
