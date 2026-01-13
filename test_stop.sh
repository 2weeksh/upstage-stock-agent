#!/bin/bash

echo "=========================================="
echo "테스트 서버 종료 중..."
echo "=========================================="

if [ -f test_app.pid ]; then
    PID=$(cat test_app.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "서버(PID: $PID) 종료 중..."
        kill $PID
        sleep 2
        if ps -p $PID > /dev/null 2>&1; then
            echo "강제 종료 중..."
            kill -9 $PID 2>/dev/null || true
        fi
        echo "✓ 서버 종료됨"
    else
        echo "서버가 실행 중이지 않습니다."
    fi
    rm -f test_app.pid
else
    echo "PID 파일이 없습니다."
fi

# 로그 파일 정리 (선택)
# rm -f test_app.log

echo ""
echo "=========================================="
echo "테스트 환경 정리 완료"
echo "=========================================="
