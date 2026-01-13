@echo off
echo ==========================================
echo Stock Agent - 로컬 환경 시작
echo ==========================================
echo.

echo 1. 환경 변수 확인 중...
if not exist .env (
    echo [ERROR] .env 파일이 없습니다!
    echo .env.example을 복사하여 .env를 생성하세요.
    pause
    exit /b 1
)
echo [OK] .env 파일 확인 완료
echo.

echo 2. 의존성 설치 중...
where uv >nul 2>nul
if %errorlevel% equ 0 (
    echo [OK] uv 사용
    uv sync
) else (
    echo [WARN] uv가 없습니다. pip 사용
    pip install -e .
)
echo.

echo 3. 백엔드 서버 시작 중...
echo [INFO] http://localhost:8001 에서 서버를 시작합니다...
echo.
echo 종료하려면 Ctrl+C를 누르세요.
echo.
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
