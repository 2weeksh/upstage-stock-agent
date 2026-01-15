@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo Stock Agent - 배포 전 체크리스트
echo ==========================================
echo.

set "ERRORS=0"
set "WARNINGS=0"

REM 1. 환경 파일 확인
echo [1/8] 환경 파일 확인 중...
if exist .env (
    echo [OK] .env 파일 존재
    findstr /C:"dummy_key_for_testing" .env >nul
    if !errorlevel! equ 0 (
        echo [WARN] .env에 더미 API 키가 있습니다. 실제 키로 변경하세요.
        set /a WARNINGS+=1
    )
) else (
    echo [ERROR] .env 파일이 없습니다!
    set /a ERRORS+=1
)
echo.

REM 2. Docker 확인
echo [2/8] Docker 확인 중...
docker --version >nul 2>&1
if !errorlevel! equ 0 (
    echo [OK] Docker 설치됨
    docker ps >nul 2>&1
    if !errorlevel! equ 0 (
        echo [OK] Docker 데몬 실행 중
    ) else (
        echo [ERROR] Docker 데몬이 실행되지 않았습니다!
        set /a ERRORS+=1
    )
) else (
    echo [ERROR] Docker가 설치되지 않았습니다!
    set /a ERRORS+=1
)
echo.

REM 3. 필수 디렉토리 확인
echo [3/8] 필수 디렉토리 확인 중...
set "DIRS=app infra\frontend infra\k8s\application"
for %%D in (%DIRS%) do (
    if exist "%%D" (
        echo [OK] %%D 존재
    ) else (
        echo [ERROR] %%D가 없습니다!
        set /a ERRORS+=1
    )
)
echo.

REM 4. 필수 파일 확인
echo [4/8] 필수 파일 확인 중...
set "FILES=main.py pyproject.toml Dockerfile docker-compose.yml"
for %%F in (%FILES%) do (
    if exist "%%F" (
        echo [OK] %%F 존재
    ) else (
        echo [ERROR] %%F가 없습니다!
        set /a ERRORS+=1
    )
)
echo.

REM 5. K8s 매니페스트 확인
echo [5/8] Kubernetes 매니페스트 확인 중...
set "K8S_FILES=01-namespace.yaml 02-configmap.yaml 03-chromadb.yaml 04-backend.yaml 05-frontend.yaml 06-ingress.yaml"
for %%F in (%K8S_FILES%) do (
    if exist "infra\k8s\application\%%F" (
        echo [OK] %%F 존재
    ) else (
        echo [ERROR] %%F가 없습니다!
        set /a ERRORS+=1
    )
)
echo.

REM 6. GitHub Actions 확인
echo [6/8] CI/CD 파이프라인 확인 중...
if exist ".github\workflows\deploy.yml" (
    echo [OK] GitHub Actions workflow 존재
) else (
    echo [WARN] GitHub Actions workflow가 없습니다.
    set /a WARNINGS+=1
)
echo.

REM 7. 이미지 경로 확인
echo [7/8] Docker 이미지 경로 확인 중...
findstr /C:"ghcr.io/2weeksh" "infra\k8s\application\04-backend.yaml" >nul
if !errorlevel! equ 0 (
    echo [WARN] 04-backend.yaml의 이미지 경로를 본인 GitHub 계정으로 변경하세요
    echo       현재: ghcr.io/2weeksh/...
    echo       변경: ghcr.io/YOUR_USERNAME/...
    set /a WARNINGS+=1
)
findstr /C:"ghcr.io/2weeksh" "infra\k8s\application\05-frontend.yaml" >nul
if !errorlevel! equ 0 (
    echo [WARN] 05-frontend.yaml의 이미지 경로를 본인 GitHub 계정으로 변경하세요
    set /a WARNINGS+=1
)
echo.

REM 8. Python 확인
echo [8/8] Python 환경 확인 중...
python --version >nul 2>&1
if !errorlevel! equ 0 (
    echo [OK] Python 설치됨
    for /f "tokens=*" %%V in ('python --version') do echo     %%V
) else (
    echo [ERROR] Python이 설치되지 않았습니다!
    set /a ERRORS+=1
)
echo.

REM 결과 출력
echo ==========================================
echo 체크 결과
echo ==========================================
echo.

if !ERRORS! equ 0 (
    if !WARNINGS! equ 0 (
        echo [SUCCESS] 모든 체크 통과! 배포 준비 완료
        echo.
        echo 다음 단계:
        echo   1. 로컬 테스트: start.bat
        echo   2. Docker 테스트: start_docker.bat
        echo   3. EC2 설정: SETUP_GUIDE.md 참고
    ) else (
        echo [WARNING] !WARNINGS!개의 경고가 있습니다.
        echo 경고를 확인하고 필요시 수정하세요.
    )
) else (
    echo [ERROR] !ERRORS!개의 오류가 발견되었습니다!
    echo 위 오류를 수정한 후 다시 실행하세요.
)

echo.
echo ==========================================
pause
