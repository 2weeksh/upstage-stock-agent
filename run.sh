#!/bin/bash

echo "=========================================="
echo "가상환경 설정 및 서버 실행"
echo "=========================================="
echo ""

# 1. python3-venv 설치 확인
echo "1. 가상환경 도구 확인 중..."
if ! dpkg -l | grep -q python3-venv; then
    echo "   python3-venv 설치 중..."
    sudo apt-get update -qq
    sudo apt-get install -y python3-venv python3-full -qq
fi
echo "   ✓ 가상환경 도구 준비 완료"

# 2. 가상환경 생성
echo ""
echo "2. 가상환경 생성 중..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "   ✓ 가상환경 생성 완료 (.venv/)"
else
    echo "   ✓ 기존 가상환경 사용 (.venv/)"
fi

# 3. 가상환경 활성화 (. 사용)
echo ""
echo "3. 가상환경 활성화..."
. .venv/bin/activate
echo "   ✓ 가상환경 활성화됨"

# 4. pip 업그레이드
echo ""
echo "4. pip 업그레이드 중..."
.venv/bin/pip install --upgrade pip -q
echo "   ✓ pip 업그레이드 완료"

# 5. 패키지 설치
echo ""
echo "5. 필수 패키지 설치 중..."
.venv/bin/pip install fastapi uvicorn python-dotenv httpx -q
echo "   ✓ 패키지 설치 완료"

# 6. 서버 실행
echo ""
echo "=========================================="
echo "✅ 서버 실행 준비 완료!"
echo "=========================================="
echo ""
echo "📍 서버 주소:"
echo "   - API: http://localhost:8001"
echo "   - 문서: http://localhost:8001/docs"
echo ""
echo "🚀 서버 시작 중..."
echo "   (종료: Ctrl+C)"
echo ""

# 가상환경의 uvicorn 사용
.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8001
