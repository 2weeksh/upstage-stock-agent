# EC2 배포 가이드 (단계별 실행)

## 📋 사전 준비물
- EC2 인스턴스 퍼블릭 IP: `YOUR_EC2_IP`
- SSH 키 파일: `your-key.pem`
- GitHub 계정명: `YOUR_GITHUB_USERNAME`

---

## Step 1: EC2 접속

### Windows에서 접속 (PowerShell 또는 Git Bash)
```bash
ssh -i "your-key.pem" ubuntu@YOUR_EC2_IP
```

### 권한 오류 시 (Windows)
```powershell
# PowerShell에서 실행
icacls "your-key.pem" /inheritance:r
icacls "your-key.pem" /grant:r "%USERNAME%:R"
```

---

## Step 2: EC2 초기 설정

접속 후 다음 명령어들을 순서대로 실행하세요:

```bash
# 1. 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 2. 필수 도구 설치
sudo apt install -y curl wget git vim

# 3. Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# 4. Docker 권한 적용 (재접속 필요)
exit
```

**재접속**:
```bash
ssh -i "your-key.pem" ubuntu@YOUR_EC2_IP
```

```bash
# 5. Docker 설치 확인
docker --version
docker ps
```

---

## Step 3: Kubernetes (k3s) 설치

```bash
# 1. k3s 설치 (경량 Kubernetes)
curl -sfL https://get.k3s.io | sh -

# 2. kubectl 권한 설정
sudo chmod 644 /etc/rancher/k3s/k3s.yaml
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown ubuntu:ubuntu ~/.kube/config

# 3. kubectl 설치 확인
kubectl version
kubectl get nodes
```

예상 출력:
```
NAME               STATUS   ROLES                  AGE   VERSION
ip-xxx-xxx-xxx-xxx   Ready    control-plane,master   1m    v1.28.x+k3s1
```

---

## Step 4: Nginx Ingress Controller 설치

```bash
# Nginx Ingress 설치
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# 설치 확인 (약 1-2분 소요)
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s

# Ingress 상태 확인
kubectl get svc -n ingress-nginx
```

---

## Step 5: 프로젝트 클론 및 설정

```bash
# 1. 프로젝트 디렉토리 생성
mkdir -p ~/deploy
cd ~/deploy

# 2. GitHub에서 프로젝트 클론
git clone https://github.com/YOUR_GITHUB_USERNAME/upstage-stock-agent-main.git
cd upstage-stock-agent-main

# 3. .env 파일 생성
cp .env.example .env

# 4. .env 파일 편집 (API 키 입력)
nano .env
```

**.env 파일 수정**:
```env
UPSTAGE_API_KEY=up_xxxxxxxxxxxxxxxxx  # 실제 키로 변경
SERPER_API_KEY=xxxxxxxxxxxxxxxxx      # 실제 키로 변경

CHROMA_MODE=server
CHROMA_HOST=chromadb
CHROMA_PORT=8000
CHROMA_COLLECTION_NAME=stock_embeddings

BACKEND_URL=http://backend:8001
```

저장: `Ctrl + O` → Enter → `Ctrl + X`

---

## Step 6: Kubernetes Secret 생성

```bash
# 1. namespace 먼저 생성
kubectl apply -f infra/k8s/application/01-namespace.yaml

# 2. .env 파일로부터 Secret 생성
kubectl create secret generic app-secret \
  --from-env-file=.env \
  -n stock-agent

# 3. Secret 생성 확인
kubectl get secret app-secret -n stock-agent
```

---

## Step 7: Kubernetes 리소스 배포

```bash
# 1. K8s 매니페스트 디렉토리로 이동
cd ~/deploy/upstage-stock-agent-main/infra/k8s/application

# 2. ConfigMap 적용
kubectl apply -f 02-configmap.yaml

# 3. ChromaDB 배포
kubectl apply -f 03-chromadb.yaml

# 4. ChromaDB 준비 대기 (약 30초)
kubectl wait --for=condition=ready pod -l app=chromadb -n stock-agent --timeout=60s

# 5. Backend 배포
kubectl apply -f 04-backend.yaml

# 6. Frontend 배포
kubectl apply -f 05-frontend.yaml

# 7. Ingress 배포
kubectl apply -f 06-ingress.yaml
```

---

## Step 8: 배포 상태 확인

```bash
# 1. Pod 상태 확인
kubectl get pods -n stock-agent

# 예상 출력:
# NAME                        READY   STATUS    RESTARTS   AGE
# chromadb-xxx                1/1     Running   0          2m
# backend-xxx                 1/1     Running   0          1m
# frontend-xxx                1/1     Running   0          1m

# 2. Service 확인
kubectl get svc -n stock-agent

# 3. Ingress 확인
kubectl get ingress -n stock-agent

# 4. Pod 로그 확인 (문제 발생 시)
kubectl logs -f deployment/backend -n stock-agent
kubectl logs -f deployment/frontend -n stock-agent
```

---

## Step 9: 접속 테스트

브라우저에서 다음 URL로 접속:

```
http://YOUR_EC2_IP/
```

**기대 결과**: 
- 프론트엔드 화면이 보임
- 시장 데이터가 로드됨

**API 테스트**:
```
http://YOUR_EC2_IP/agent/health
http://YOUR_EC2_IP/agent/market-summary
http://YOUR_EC2_IP/agent/docs
```

---

## 🔧 트러블슈팅

### Pod가 Running이 안 될 때
```bash
# Pod 상세 정보 확인
kubectl describe pod POD_NAME -n stock-agent

# 이벤트 확인
kubectl get events -n stock-agent --sort-by='.lastTimestamp'
```

### 이미지를 Pull 못할 때
```bash
# ImagePullBackOff 오류 시
# → GitHub Container Registry 권한 문제
# → 04-backend.yaml, 05-frontend.yaml의 이미지 경로 확인
```

현재는 GitHub에 이미지가 없으므로 **로컬에서 이미지를 빌드**해야 합니다:

```bash
# EC2에서 직접 빌드하는 방법

# 1. 프로젝트 디렉토리로 이동
cd ~/deploy/upstage-stock-agent-main

# 2. Backend 이미지 빌드
docker build --target backend -t stock-agent-backend:latest .

# 3. Frontend 이미지 빌드
docker build --target frontend -t stock-agent-frontend:latest .

# 4. k3s에 이미지 로드
sudo k3s ctr images import stock-agent-backend:latest
sudo k3s ctr images import stock-agent-frontend:latest

# 또는 docker save/load 사용
docker save stock-agent-backend:latest | sudo k3s ctr images import -
docker save stock-agent-frontend:latest | sudo k3s ctr images import -
```

그 다음 **04-backend.yaml, 05-frontend.yaml 수정**:
```yaml
# 변경 전
image: ghcr.io/2weeksh/upstage-stock-agent-main-backend:latest

# 변경 후
image: stock-agent-backend:latest
imagePullPolicy: Never  # 추가!
```

### Ingress가 작동 안 할 때
```bash
# Ingress Controller 상태 확인
kubectl get pods -n ingress-nginx

# LoadBalancer 외부 IP 확인
kubectl get svc -n ingress-nginx
```

### 포트가 열리지 않을 때
- AWS Console → EC2 → Security Groups
- Inbound Rules에 80, 443 포트 추가 확인

---

## 🎉 성공!

접속이 되면 성공입니다!

**다음 단계**:
1. GitHub Actions를 통한 자동 배포 설정
2. 실제 LLM 에이전트 구현
3. 도메인 연결 (선택)

---

## 📌 유용한 명령어 모음

```bash
# 전체 리소스 확인
kubectl get all -n stock-agent

# 특정 Pod 재시작
kubectl rollout restart deployment/backend -n stock-agent

# 전체 삭제 (재배포 시)
kubectl delete namespace stock-agent

# 로그 실시간 확인
kubectl logs -f deployment/backend -n stock-agent --tail=100

# Pod 내부 접속 (디버깅)
kubectl exec -it POD_NAME -n stock-agent -- /bin/bash
```
