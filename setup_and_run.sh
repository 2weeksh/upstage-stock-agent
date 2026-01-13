#!/bin/bash

echo "=========================================="
echo "WSL 환경 설정 및 테스트"
echo "=========================================="
echo ""

# 1. pip 설치
echo "1. pip 설치 중..."
sudo apt-get update -qq
sudo apt-get install -y python3-pip -qq

echo ""
echo "2. Python 패키지 설치 중..."
pip3 install fastapi uvicorn python-dotenv httpx

echo ""
echo "3. 서버 실행 중..."
echo "   서버 주소: http://localhost:8001"
echo "   API 문서: http://localhost:8001/docs"
echo "   종료: Ctrl+C"
echo ""

# 서버 실행
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001
