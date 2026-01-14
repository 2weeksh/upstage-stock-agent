# 🧪 테스트 가이드

이 문서는 Stock Agent 인프라가 정상적으로 작동하는지 확인하는 방법을 설명합니다.

---

## 테스트 시나리오

### 1️⃣ 로컬 환경 테스트 (가장 빠름)

Python 환경에서 직접 Mock API를 실행합니다.

```bash
# Windows (Git Bash)
sh test_local.sh

# 또는 수동 실행
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

**테스트 항목**:
- ✅ Root 엔드포인트 (/)
- ✅ Health Check (/health)
- ✅ Agent Health (/agent/health)
- ✅ Seed Status (/agent/seed-status)
- ✅ Stats (/agent/stats)
- ✅ Chat API (/agent/chat)
- ✅ Stock Analysis (/api/v1/analyze/{symbol})

**브라우저 확인**:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

**종료**:
```bash
sh test_stop.sh
```

---

### 2️⃣ Docker 환경 테스트

Docker 이미지 빌드와 컨테이너 실행을 검증합니다.

```bash
# Windows (Git Bash)
sh test_docker.sh
```

**수행 작업**:
1. Docker 환경 확인
2. 이미지 빌드 (`docker build`)
3. 컨테이너 실행
4. API 엔드포인트 테스트
5. 컨테이너 상태 확인

**수동 실행**:
```bash
# 이미지 빌드
docker build --target backend -t stock-agent-backend:latest .

# 컨테이너 실행
docker run -d -p 8001:8001 \
  -e UPSTAGE_API_KEY=dummy \
  stock-agent-backend:latest

# 테스트
curl http://localhost:8001/health

# 종료
docker rm -f stock-agent-backend
```

---

### 3️⃣ Docker Compose 환경 테스트

전체 스택(ChromaDB + Backend + Frontend)을 함께 실행합니다.

```bash
# 실행
sh start_docker.sh

# 종료
sh stop_docker.sh
```

**접속 확인**:
- Backend: http://localhost:8001
- Frontend: http://localhost:8002 (구현 완료 시)
- ChromaDB: http://localhost:8000

**수동 테스트**:
```bash
# 컨테이너 상태 확인
docker ps

# 로그 확인
docker-compose logs -f backend

# Health check
curl http://localhost:8001/health
curl http://localhost:8000/api/v1/heartbeat
```

---

## 🔍 테스트 체크리스트

### 로컬 환경
- [ ] Python 3.11+ 설치되어 있음
- [ ] `.env` 파일 생성됨
- [ ] `test_local.sh` 실행 성공
- [ ] 7개 API 엔드포인트 모두 정상 응답
- [ ] Swagger UI 접속 가능

### Docker 환경
- [ ] Docker Desktop 실행 중
- [ ] `test_docker.sh` 실행 성공
- [ ] 이미지 빌드 성공
- [ ] 컨테이너 정상 실행
- [ ] API 테스트 통과

### Docker Compose
- [ ] `start_docker.sh` 실행 성공
- [ ] 3개 컨테이너 모두 Running 상태
- [ ] Backend Health check 성공
- [ ] ChromaDB Health check 성공

---

## 🐛 문제 해결

### 로컬 테스트 실패

**문제**: Python을 찾을 수 없음
```bash
# 해결: Python 설치 확인
python --version
python3 --version
```

**문제**: 포트 8001이 이미 사용 중
```bash
# 해결: 포트 사용 프로세스 확인 및 종료
# Windows
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# 또는 다른 포트 사용
python -m uvicorn main:app --port 8002
```

**문제**: 패키지 설치 실패
```bash
# 해결: pip 업그레이드
python -m pip install --upgrade pip
pip install fastapi uvicorn python-dotenv
```

---

### Docker 테스트 실패

**문제**: Docker 데몬이 실행되지 않음
```
해결: Docker Desktop을 실행하세요
```

**문제**: 이미지 빌드 실패
```bash
# 해결: 빌드 로그 확인
docker build --target backend -t test-stock-backend:latest . --no-cache

# 또는 상세 로그 확인
docker build --target backend -t test-stock-backend:latest . --progress=plain
```

**문제**: 컨테이너가 즉시 종료됨
```bash
# 해결: 로그 확인
docker logs test-stock-backend

# 일반적인 원인: main.py 경로 문제
# Dockerfile의 COPY 경로 확인
```

---

### Docker Compose 테스트 실패

**문제**: ChromaDB 컨테이너가 시작되지 않음
```bash
# 해결: 포트 확인
docker ps -a
docker logs stock-agent-chromadb

# 포트 8000 사용 중인지 확인
netstat -ano | findstr :8000
```

**문제**: Backend가 ChromaDB에 연결 못함
```bash
# 해결: 네트워크 확인
docker network ls
docker network inspect stock-agent-network

# DNS 확인 (컨테이너 내부에서)
docker exec -it stock-agent-backend ping chromadb
```

---

## 📊 성공 기준

### 로컬 테스트
```bash
✓ Root 엔드포인트 정상
✓ Health Check 정상
✓ Agent Health 정상
✓ Seed Status 정상
✓ Stats 정상
✓ Chat API 정상
✓ Stock Analysis 정상
```

### Docker 테스트
```bash
✓ Docker 설치됨
✓ 이미지 빌드 완료
✓ 컨테이너 시작됨
✓ 서버 준비 완료!
✓ Health Check 정상
✓ Agent Health 정상
✓ Chat API 정상
```

### Docker Compose 테스트
```bash
✓ 서비스 및 데이터 준비 완료! (총 1000 개의 문서)
✅ Docker 환경이 성공적으로 시작되었습니다!
```

---

## 📸 스크린샷 예시

### Swagger UI
![Swagger UI](docs/images/swagger-ui.png)
- 모든 API 엔드포인트 확인 가능
- 직접 테스트 실행 가능

### Health Check 응답
```json
{
  "status": "healthy",
  "service": "stock-agent-backend"
}
```

### Chat API 응답
```json
{
  "answer": "주식 분석 에이전트입니다. '삼성전자'에 대한 분석은 곧 제공될 예정입니다.",
  "user_query": "삼성전자",
  "process_status": "success"
}
```

---

## 🎯 다음 단계

모든 테스트가 통과하면:

1. ✅ **로컬 환경** → Git에 커밋
2. ✅ **Docker 환경** → 이미지 GHCR에 푸시
3. ✅ **Kubernetes** → EC2에 배포

테스트 실패 시:
1. 로그 확인
2. 문제 해결 섹션 참조
3. 필요시 Issue 생성

---

## 💡 유용한 명령어

### 로그 확인
```bash
# 로컬
tail -f test_app.log

# Docker
docker logs -f test-stock-backend
docker-compose logs -f backend

# Kubernetes (배포 후)
kubectl logs -f deployment/backend -n stock-agent
```

### 완전 초기화
```bash
# 로컬
rm -f test_app.pid test_app.log

# Docker
docker rm -f test-stock-backend
docker rmi test-stock-backend:latest

# Docker Compose
docker-compose down -v
docker system prune -a
```

---

## ✅ 최종 검증

모든 환경에서 다음 명령어가 성공해야 합니다:

```bash
# 로컬
curl http://localhost:8001/health
# 예상 결과: {"status":"healthy","service":"stock-agent-backend"}

# Docker
docker run --rm -p 8001:8001 stock-agent-backend:latest &
sleep 5
curl http://localhost:8001/health
# 예상 결과: {"status":"healthy","service":"stock-agent-backend"}

# Docker Compose
docker-compose up -d
sleep 10
curl http://localhost:8001/health
curl http://localhost:8000/api/v1/heartbeat
# 모두 200 OK 응답
```

성공하면 인프라 설정이 완료된 것입니다! 🎉
