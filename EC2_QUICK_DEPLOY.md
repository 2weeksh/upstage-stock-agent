# 🚀 EC2 빠른 배포 (5분 완성)

GitHub Actions 없이 EC2에서 직접 빌드하여 바로 배포하는 방법입니다.

---

## 전제 조건
- ✅ EC2 인스턴스 생성됨 (Ubuntu 22.04)
- ✅ 보안 그룹에 22, 80, 443 포트 오픈
- ✅ SSH 키로 접속 가능

---

## 1단계: EC2 접속 및 환경 설정 (2분)

```bash
# EC2 접속
ssh -i "your-key.pem" ubuntu@YOUR_EC2_IP

# 자동 설치 스크립트 실행
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/upstage-stock-agent-main/main/scripts/ec2-setup.sh | bash

# 재접속 (Docker 권한 적용)
exit
ssh -i "your-key.pem" ubuntu@YOUR_EC2_IP
```

위 스크립트가 없다면 수동으로:

```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# k3s 설치
curl -sfL https://get.k3s.io | sh -
sudo chmod 644 /etc/rancher/k3s/k3s.yaml
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown ubuntu:ubuntu ~/.kube/config

# Nginx Ingress 설치
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# 재접속
exit
ssh -i "your-key.pem" ubuntu@YOUR_EC2_IP
```

---

## 2단계: 프로젝트 설정 (1분)

```bash
# 프로젝트 클론
mkdir -p ~/deploy && cd ~/deploy
git clone https://github.com/YOUR_USERNAME/upstage-stock-agent-main.git
cd upstage-stock-agent-main

# .env 설정
cp .env.example .env
nano .env
```

**`.env` 파일에서 API 키 변경**:
```env
UPSTAGE_API_KEY=up_your_actual_key_here
SERPER_API_KEY=your_actual_key_here
```
저장: `Ctrl+O` → Enter → `Ctrl+X`

---

## 3단계: 이미지 빌드 및 배포 (2분)

```bash
# 자동 빌드 & 배포 스크립트 실행
chmod +x ec2-local-build.sh
./ec2-local-build.sh

# Secret 생성
kubectl create namespace stock-agent
kubectl create secret generic app-secret --from-env-file=.env -n stock-agent

# 배포 실행
cd infra/k8s/application
kubectl apply -f 01-namespace.yaml
kubectl apply -f 02-configmap.yaml
kubectl apply -f 03-chromadb.yaml

# ChromaDB 준비 대기
sleep 30

kubectl apply -f 04-backend-local.yaml
kubectl apply -f 05-frontend-local.yaml
kubectl apply -f 06-ingress.yaml
```

---

## 4단계: 확인 (30초)

```bash
# Pod 상태 확인
kubectl get pods -n stock-agent

# 모든 Pod가 Running이 될 때까지 대기 (약 1분)
watch kubectl get pods -n stock-agent
# Ctrl+C로 종료

# 브라우저에서 접속
echo "http://$(curl -s ifconfig.me)"
```

---

## ✅ 완료!

브라우저에서 다음 URL로 접속하세요:
- **메인 페이지**: http://YOUR_EC2_IP/
- **API 문서**: http://YOUR_EC2_IP/agent/docs
- **Health Check**: http://YOUR_EC2_IP/agent/health

---

## 🔧 문제 해결

### Pod가 Running이 안 될 때
```bash
kubectl describe pod -n stock-agent
kubectl logs -f deployment/backend -n stock-agent
```

### 이미지 빌드 실패 시
```bash
# Docker 빌드 확인
cd ~/deploy/upstage-stock-agent-main
docker build --target backend -t stock-agent-backend:latest .
docker images | grep stock-agent
```

### Ingress 접속 안 될 때
```bash
# Ingress Controller 확인
kubectl get pods -n ingress-nginx
kubectl get svc -n ingress-nginx

# AWS 보안 그룹 확인
# - 80, 443 포트가 0.0.0.0/0에 열려있는지 확인
```

---

## 🎯 다음 단계

배포가 성공하면:
1. ✅ 인프라 작동 확인 완료
2. ✅ 이제 에이전트 개발 시작
3. ✅ GitHub Actions로 자동 배포 설정

---

## 📌 유용한 명령어

```bash
# 실시간 로그 확인
kubectl logs -f deployment/backend -n stock-agent --tail=50

# Pod 재시작
kubectl rollout restart deployment/backend -n stock-agent

# 전체 삭제 후 재배포
kubectl delete namespace stock-agent
# 그 다음 3단계부터 다시 실행

# EC2 외부 IP 확인
curl ifconfig.me
```
