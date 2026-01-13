@echo off
echo ==========================================
echo Stock Agent - Docker 환경 종료
echo ==========================================
echo.

echo 1. 컨테이너 종료 중...
docker-compose down

if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose 종료 실패
    pause
    exit /b 1
)

echo.
echo ==========================================
echo [SUCCESS] 모든 컨테이너가 종료되었습니다!
echo ==========================================
pause
