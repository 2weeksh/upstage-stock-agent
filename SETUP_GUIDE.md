# EC2 배포 전 준비 체크리스트

## ✅ 완료된 사항

### 1. 로컬 개발 환경
- [x] FastAPI 백엔드 (main.py)
- [x] 프론트엔드 HTML/CSS/JS (infra/frontend/)
- [x] Health check 엔드포인트 (/health)
- [x] API 라우터 (app/api/)
- [x] 환경 변수 설정 (.env)

### 2. Docker 환경
- [x] Dockerfile (멀티 스테이지: backend, frontend)
- [x] docker-compose.yml (backend, frontend, chromadb)
- [x] Windows 실행 스크립트 (start_docker.bat, stop_docker.bat)

### 3. Kubernetes 매니페스트
- [x] 01-namespace.yaml (stock-agent namespace)
- [x] 02-configmap.yaml (환경 설정)
- [x] 03-chromadb.yaml (벡터 DB)
- [x] 04-backend.yaml (FastAPI deployment & service)
- [x] 05-frontend.yaml (Streamlit deployment & service)
- [x] 06-ingress.yaml (Nginx ingress)

### 4. CI/CD 파이프라인
- [x] GitHub Actions workflow (.github/workflows/deploy.yml)
- [x] 자동 빌드 & Docker 이미지 푸시
- [x] 자동 K8s 배포

---

## 📋 EC2 배포 전 해야 할 일

### Step 1: GitHub 설정

1. **Repository 확인**
   - Repository가 Public인지 확인 (Private면 GHCR 접근 설정 필요)
   - Settings → Actions → General → Workflow permissions → Read and write 체크

2. **GitHub Secrets 추가**
   ```
   Settings → Secrets and variables → Actions → New repository secret
   ```
   
   필요한 Secrets:
   - `EC2_HOST`: EC2 인스턴스 퍼블릭 IP (예: 13.124.xx.xx)
   - `EC2_SSH_KEY`: EC2 SSH private key 전체 내용 (-----BEGIN ... -----END 포함)

### Step 2: 로컬 Docker 테스트

```bash
# 1. Docker 이미지 빌드 테스트
start_docker.bat

# 2. 접속 확인
# - http://localhost:8001 (백엔드)
# - http://localhost:8001/docs (API 문서)
# - http://localhost:8001/health (헬스체크)
# - http://localhost:8002 (프론트엔드)
# - http://localhost:8000 (ChromaDB)

# 3. 종료
stop_docker.bat
```

### Step 3: 환경 변수 확인

`.env` 파일에서 실제 API 키로 변경:
```env
UPSTAGE_API_KEY=up_xxxxxxxxxxxxxxxxx  # 실제 Upstage API 키
SERPER_API_KEY=xxxxxxxxxxxxxxxxx      # 실제 Serper API 키 (선택)
```

### Step 4: Kubernetes 매니페스트 수정

#### 4-1. Backend 이미지 경로 확인
`infra/k8s/application/04-backend.yaml`:
```yaml
image: ghcr.io/YOUR_GITHUB_USERNAME/upstage-stock-agent-main-backend:latest
```
→ `YOUR_GITHUB_USERNAME`을 실제 GitHub 계정명으로 변경

#### 4-2. Frontend 이미지 경로 확인
`infra/k8s/application/05-frontend.yaml`:
```yaml
image: ghcr.io/YOUR_GITHUB_USERNAME/upstage-stock-agent-main-frontend:latest
```
→ `YOUR_GITHUB_USERNAME`을 실제 GitHub 계정명으로 변경

#### 4-3. Ingress 도메인 설정 (선택)
`infra/k8s/application/06-ingress.yaml`:
```yaml
# DuckDNS 도메인이 있는 경우
- host: mystock.duckdns.org
```
또는 IP로 직접 접속하려면 `host` 부분 제거

---

## 🚀 다음 단계 (EC2에서 할 일)

### 1. EC2 인스턴스 준비
- Ubuntu 22.04 LTS
- t3.medium 이상 권장 (메모리 4GB+)
- 보안 그룹: 80, 443, 22 포트 오픈

### 2. EC2에 필요한 도구 설치
```bash
# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Kubernetes (k3s) 설치
curl -sfL https://get.k3s.io | sh -

# kubectl 설정
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown ubuntu:ubuntu ~/.kube/config
```

### 3. 프로젝트 클론 & Secret 생성
```bash
# 프로젝트 클론
mkdir -p ~/deploy
cd ~/deploy
git clone https://github.com/YOUR_USERNAME/upstage-stock-agent-main.git
cd upstage-stock-agent-main

# .env 파일 생성 및 API 키 입력
cp .env.example .env
nano .env  # API 키 입력

# Kubernetes Secret 생성
kubectl create secret generic app-secret \
  --from-env-file=.env \
  -n stock-agent

# ConfigMap도 적용
cd infra/k8s/application
kubectl apply -f 01-namespace.yaml
kubectl apply -f 02-configmap.yaml
```

### 4. Nginx Ingress Controller 설치
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
```

### 5. 매니페스트 적용
```bash
cd ~/deploy/upstage-stock-agent-main/infra/k8s/application
kubectl apply -f .
```

### 6. 배포 확인
```bash
# Pod 상태 확인
kubectl get pods -n stock-agent

# Service 확인
kubectl get svc -n stock-agent

# Ingress 확인
kubectl get ingress -n stock-agent
```

---

## 📊 로컬 테스트 체크리스트

배포 전 로컬에서 다음을 확인하세요:

- [ ] `start.bat` 실행 → http://localhost:8001 접속 성공
- [ ] API 문서 확인 → http://localhost:8001/docs
- [ ] Health check → http://localhost:8001/health 응답 확인
- [ ] 시장 데이터 → http://localhost:8001/market-summary 데이터 확인
- [ ] 코스피 데이터 → http://localhost:8001/kospi-data 데이터 확인
- [ ] 채팅 API 테스트 → POST http://localhost:8001/api/v1/chat
- [ ] Docker 빌드 → `start_docker.bat` 실행 성공
- [ ] Docker 접속 → http://localhost:8001, 8002, 8000 모두 접속 가능

---

## 🔧 트러블슈팅

### Docker 빌드 실패
```bash
# Docker Desktop이 실행 중인지 확인
# WSL2 백엔드 사용 권장
```

### Health check 실패
```bash
# main.py에 /health 엔드포인트 추가 확인
# uvicorn 서버가 정상 실행되는지 확인
```

### API 키 오류
```bash
# .env 파일에서 더미 키를 실제 키로 변경
# 환경 변수가 제대로 로드되는지 확인
```

---

## 📝 참고사항

- **현재 상태**: 로컬 개발 완료, Docker 준비 완료, K8s 매니페스트 준비 완료
- **다음 단계**: EC2 인스턴스 설정 및 배포
- **배포 방식**: GitHub Actions를 통한 자동 CI/CD

모든 준비가 완료되면 EC2 설정으로 넘어가시면 됩니다!
