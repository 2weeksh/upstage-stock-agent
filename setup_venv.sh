#!/bin/bash

echo "=========================================="
echo "가상환경 초기 설정 (최초 1회만)"
echo "=========================================="
echo ""

# 1. python3-venv 설치
echo "1. 가상환경 도구 설치 중..."
sudo apt-get update
sudo apt-get install -y python3-venv python3-full
echo "   ✓ 설치 완료"

# 2. 가상환경 생성
echo ""
echo "2. 가상환경 생성 중..."
python3 -m venv .venv
echo "   ✓ 가상환경 생성 완료 (.venv/)"

# 3. 가상환경 활성화
echo ""
echo "3. 가상환경 활성화..."
source .venv/bin/activate
echo "   ✓ 가상환경 활성화됨"

# 4. pip 업그레이드
echo ""
echo "4. pip 업그레이드 중..."
pip install --upgrade pip
echo "   ✓ pip 업그레이드 완료"

# 5. 패키지 설치
echo ""
echo "5. 필수 패키지 설치 중..."
pip install fastapi uvicorn python-dotenv httpx
echo "   ✓ 패키지 설치 완료"

echo ""
echo "=========================================="
echo "✅ 설정 완료!"
echo "=========================================="
echo ""
echo "다음 명령어로 서버를 실행하세요:"
echo "   sh run.sh"
echo ""
echo "또는 수동으로:"
echo "   source .venv/bin/activate"
echo "   uvicorn main:app --host 0.0.0.0 --port 8001"
echo ""
