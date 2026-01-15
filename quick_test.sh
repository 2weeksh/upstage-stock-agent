#!/bin/bash

echo "=========================================="
echo "간단 테스트 - 패키지 설치 및 서버 실행"
echo "=========================================="
echo ""

# 1. 필수 패키지 설치
echo "1. Python 패키지 설치 중..."
python3 -m pip install --user fastapi uvicorn python-dotenv httpx

echo ""
echo "2. 서버 실행 중..."
echo "   (Ctrl+C로 종료)"
echo ""

# 서버 실행
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001
