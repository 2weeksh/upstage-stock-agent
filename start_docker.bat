@echo off
echo ==========================================
echo Stock Agent - Docker 환경 시작
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

echo 2. Docker Compose 실행 중...
docker-compose up -d --build

if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose 실행 실패
    pause
    exit /b 1
)

echo.
echo 3. 컨테이너 상태 확인 중...
timeout /t 5 /nobreak > nul
docker-compose ps

echo.
echo ==========================================
echo [SUCCESS] 서비스가 시작되었습니다!
echo ==========================================
echo.
echo 접속 정보:
echo   - Backend API: http://localhost:8001
echo   - API 문서: http://localhost:8001/docs
echo   - Frontend: http://localhost:8002
echo   - ChromaDB: http://localhost:8000
echo.
echo 로그 확인: docker-compose logs -f
echo 종료: stop_docker.bat
echo ==========================================
pause
