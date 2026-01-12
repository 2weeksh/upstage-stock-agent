# 🚀 배포 가이드

이 문서는 Stock Agent를 Kubernetes 환경에 배포하는 전체 과정을 설명합니다.

---

## 📋 목차

1. [사전 준비](#사전-준비)
2. [로컬 테스트](#로컬-테스트)
3. [Docker 이미지 빌드](#docker-이미지-빌드)
4. [Kubernetes 배포](#kubernetes-배포)
5. [CI/CD 설정](#cicd-설정)
6. [트러블슈팅](#트러블슈팅)

---

## 사전 준비

### 1. 필수 도구 설치

```bash
# Docker 설치 확인
docker --version

# kubectl 설치 확인
kubectl version --client

# uv 설치 (Python 패키지 관리자)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. API 키 발급

- **Upstage API**: https://console.upstage.ai/
- **Serper.dev** (Optional): https://serper.dev/

### 3. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집
vi .env
```

**.env 예시**:
```
UPSTAGE_API_KEY=your_actual_api_key_here
SERPER_API_KEY=your_serper_key_here
CHROMA_MODE=local
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_COLLECTION_NAME=stock_embeddings
```

---

## 로컬 테스트

### 1. 로컬 환경 실행

```bash
# 실행
sh start.sh

# 로그 확인
tail -f app.log
```

**테스트**:
- http://localhost:8001/docs - Swagger UI 확인
- http://localhost:8001/health - Health check

### 2. 종료

```bash
sh stop.sh
```

---

## Docker 이미지 빌드

### 1. Docker 환경 테스트

```bash
# Docker Compose로 실행
sh start_docker.sh

# 컨테이너 상태 확인
docker ps

# 로그 확인
docker-compose logs -f backend
```

### 2. 종료

```bash
sh stop_docker.sh
```

### 3. 수동 빌드 (필요시)

```bash
# Backend 이미지 빌드
docker build --target backend -t stock-agent-backend:latest .

# Frontend 이미지 빌드
docker build --target frontend -t stock-agent-frontend:latest .
```

---

## Kubernetes 배포

### 1. EC2 서버 준비

#### SSH 키 설정
```bash
# 로컬에서 EC2 접속
ssh -i /path/to/your-key.pem ubuntu@your-ec2-ip
```

#### 프로젝트 클론
```bash
# EC2 서버에서
mkdir -p ~/deploy
cd ~/deploy
git clone https://github.com/YOUR_USERNAME/upstage-stock-agent-main.git
cd upstage-stock-agent-main
```

### 2. Manifest 파일 수정

#### 04-backend.yaml, 05-frontend.yaml
```yaml
# 변경 전
image: ghcr.io/YOUR_GITHUB_USERNAME/stock-agent-backend:latest

# 변경 후 (실제 GitHub 계정명 입력)
image: ghcr.io/your-actual-username/stock-agent-backend:latest
```

#### 06-ingress.yaml
```yaml
# 변경 전
host: YOUR_DUCKDNS_DOMAIN.duckdns.org

# 변경 후 (실제 DuckDNS 도메인 입력)
host: mystock-agent.duckdns.org
```

### 3. Kubernetes Secret 생성

```bash
# EC2 서버에서
cd ~/deploy/upstage-stock-agent-main

# .env 파일 설정
cp .env.example .env
vi .env  # API 키 입력

# Secret 생성
kubectl create secret generic app-secret \
  --from-env-file=.env \
  -n stock-agent
```

### 4. 매니페스트 적용

```bash
cd infra/k8s/application

# Namespace 생성
kubectl apply -f 01-namespace.yaml

# 기본 네임스페이스 변경
kubectl config set-context --current --namespace=stock-agent

# 전체 리소스 적용
kubectl apply -f .
```

### 5. 배포 상태 확인

```bash
# Pod 상태 확인
kubectl get pods -w

# 서비스 확인
kubectl get svc

# Ingress 확인
kubectl get ingress

# 로그 확인
kubectl logs -f deployment/backend
```

---

## CI/CD 설정

### 1. GitHub Secrets 설정

Repository → Settings → Secrets and variables → Actions

**필수 Secrets**:
- `EC2_HOST`: EC2 서버 IP 주소
- `EC2_SSH_KEY`: EC2 SSH private key 전체 내용

#### EC2_SSH_KEY 설정 방법

```bash
# 로컬에서 pem 키 내용 복사
cat /path/to/your-key.pem

# GitHub에 붙여넣기 (-----BEGIN ... END----- 포함)
```

### 2. 자동 배포 트리거

```bash
# main 브랜치에 Push
git add .
git commit -m "Deploy to production"
git push origin main
```

### 3. Actions 확인

- GitHub Repository → Actions 탭
- 워크플로우 실행 상태 확인
- 실패 시 로그 확인

---

## 트러블슈팅

### 1. Pod가 Running 상태가 안됨

```bash
# Pod 상세 정보 확인
kubectl describe pod <pod-name>

# 로그 확인
kubectl logs <pod-name>

# 이벤트 확인
kubectl get events --sort-by='.lastTimestamp'
```

**일반적인 원인**:
- 이미지 Pull 실패 → GHCR 권한 확인
- Secret 누락 → `kubectl get secret -n stock-agent`
- 리소스 부족 → `kubectl top nodes`

### 2. Ingress 접속 안됨

```bash
# Ingress 상태 확인
kubectl describe ingress app-ingress

# Nginx Ingress Controller 확인
kubectl get pods -n ingress-nginx
```

**확인 사항**:
- DuckDNS 도메인 설정
- EC2 Security Group (80, 443 포트)
- Nginx Ingress Controller 설치 여부

### 3. ChromaDB 연결 실패

```bash
# ChromaDB Pod 확인
kubectl logs deployment/chromadb

# Service 확인
kubectl get svc chromadb

# 연결 테스트
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://chromadb:8000/api/v1/heartbeat
```

### 4. GitHub Actions 배포 실패

**SSH 연결 실패**:
- EC2_HOST가 올바른지 확인
- EC2_SSH_KEY가 정확한지 확인
- EC2 Security Group에 SSH(22) 허용되어 있는지 확인

**이미지 Push 실패**:
- Repository가 Public인지 확인
- GITHUB_TOKEN 권한 확인

### 5. 메모리 부족 에러

```bash
# 리소스 사용량 확인
kubectl top pods
kubectl top nodes

# 리소스 제한 조정 (04-backend.yaml)
resources:
  limits:
    memory: "1Gi"  # 늘림
```

---

## 유용한 명령어 모음

### Pod 관리
```bash
# Pod 목록
kubectl get pods

# Pod 재시작
kubectl rollout restart deployment/backend

# Pod 삭제 (자동 재생성됨)
kubectl delete pod <pod-name>
```

### 로그 확인
```bash
# 실시간 로그
kubectl logs -f deployment/backend

# 이전 컨테이너 로그
kubectl logs <pod-name> --previous

# 여러 Pod 로그 동시 확인
kubectl logs -l app=backend --tail=100
```

### 설정 변경
```bash
# ConfigMap 수정
kubectl edit configmap app-config

# Secret 수정
kubectl delete secret app-secret
kubectl create secret generic app-secret --from-env-file=.env -n stock-agent

# 변경 사항 적용
kubectl rollout restart deployment/backend
```

### 디버깅
```bash
# Pod 내부 접속
kubectl exec -it <pod-name> -- /bin/sh

# 임시 디버그 Pod 생성
kubectl run -it --rm debug --image=alpine --restart=Never -- sh
```

---

## 모니터링

### 1. 기본 모니터링

```bash
# 전체 리소스 상태
kubectl get all -n stock-agent

# Pod 상태 Watch
kubectl get pods -w

# 리소스 사용량
kubectl top pods
kubectl top nodes
```

### 2. 로그 수집

```bash
# 특정 기간 로그
kubectl logs deployment/backend --since=1h

# 에러 로그만 필터링
kubectl logs deployment/backend | grep ERROR
```

---

## 백업 및 복구

### 데이터 백업
```bash
# ChromaDB PVC 백업
kubectl get pvc chromadb-pvc -o yaml > backup-pvc.yaml

# ConfigMap 백업
kubectl get configmap app-config -o yaml > backup-configmap.yaml
```

### 복구
```bash
# 리소스 재적용
kubectl apply -f backup-pvc.yaml
kubectl apply -f backup-configmap.yaml
```

---

## 참고 자료

- [Kubernetes 공식 문서](https://kubernetes.io/docs/)
- [Docker 공식 문서](https://docs.docker.com/)
- [GitHub Actions 문서](https://docs.github.com/actions)
- [Nginx Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
