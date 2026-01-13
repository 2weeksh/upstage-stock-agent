# EC2에서 로컬 빌드로 배포하기
# (GitHub Container Registry 없이 바로 테스트)

cd ~/deploy/upstage-stock-agent-main

# 1. Backend 이미지 빌드
echo "Building backend image..."
docker build --target backend -t stock-agent-backend:latest .

# 2. Frontend 이미지 빌드  
echo "Building frontend image..."
docker build --target frontend -t stock-agent-frontend:latest .

# 3. K8s 매니페스트를 로컬 이미지로 수정
cd infra/k8s/application

# Backend 매니페스트 수정
cat > 04-backend-local.yaml << 'EOF'
# Deployment - Backend FastAPI 서버 (로컬 이미지)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: stock-agent
  labels:
    app: backend
spec:
  replicas: 1
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0
      maxSurge: 1
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: stock-agent-backend:latest
        imagePullPolicy: Never
        ports:
        - containerPort: 8001
          name: http
        env:
        - name: UPSTAGE_API_KEY
          valueFrom:
            secretKeyRef:
              name: app-secret
              key: UPSTAGE_API_KEY
              optional: true
        - name: SERPER_API_KEY
          valueFrom:
            secretKeyRef:
              name: app-secret
              key: SERPER_API_KEY
              optional: true
        envFrom:
        - configMapRef:
            name: app-config
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2

---
# Service - Backend 내부 접근
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: stock-agent
  labels:
    app: backend
spec:
  type: ClusterIP
  selector:
    app: backend
  ports:
  - port: 8001
    targetPort: 8001
    protocol: TCP
    name: http
EOF

# Frontend 매니페스트 수정
cat > 05-frontend-local.yaml << 'EOF'
# Deployment - Frontend Streamlit UI (로컬 이미지)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: stock-agent
  labels:
    app: frontend
spec:
  replicas: 1
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0
      maxSurge: 1
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: stock-agent-frontend:latest
        imagePullPolicy: Never
        ports:
        - containerPort: 8002
          name: http
        envFrom:
        - configMapRef:
            name: app-config
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"

---
# Service - Frontend 내부 접근
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: stock-agent
  labels:
    app: frontend
spec:
  type: ClusterIP
  selector:
    app: frontend
  ports:
  - port: 8002
    targetPort: 8002
    protocol: TCP
    name: http
EOF

echo "로컬 매니페스트 생성 완료!"
echo ""
echo "다음 명령어로 배포하세요:"
echo "kubectl apply -f 01-namespace.yaml"
echo "kubectl apply -f 02-configmap.yaml"
echo "kubectl apply -f 03-chromadb.yaml"
echo "kubectl apply -f 04-backend-local.yaml"
echo "kubectl apply -f 05-frontend-local.yaml"
echo "kubectl apply -f 06-ingress.yaml"
