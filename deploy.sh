#!/bin/bash
set -e

echo "🚀 StockWars 최신 코드 배포 시작"
echo "================================"

# 1. 프론트엔드 경로 수정
echo "📝 프론트엔드 경로 수정 중..."
cd ~/upstage-stock-agent/infra/frontend

rm -f index.html
cp html/start.html index.html

# 절대 경로 수정
sed -i 's|href="../css/|href="/css/|g' index.html html/*.html
sed -i 's|href="css/|href="/css/|g' index.html html/*.html
sed -i 's|src="../img/|src="/img/|g' index.html html/*.html
sed -i 's|src="img/|src="/img/|g' index.html html/*.html
sed -i 's|src="../js/|src="/js/|g' index.html html/*.html
sed -i 's|src="js/|src="/js/|g' index.html html/*.html

sed -i 's|href="start.html"|href="/"|g' html/*.html index.html
sed -i 's|href="login.html"|href="/html/login.html"|g' html/*.html index.html
sed -i 's|href="signup.html"|href="/html/signup.html"|g' html/*.html index.html
sed -i 's|href="userInput.html"|href="/html/userInput.html"|g' html/*.html index.html
sed -i 's|href="analysis.html"|href="/html/analysis.html"|g' html/*.html index.html
sed -i 's|href="mypage.html"|href="/html/mypage.html"|g' html/*.html index.html
sed -i 's|href="history.html"|href="/html/history.html"|g' html/*.html index.html

sed -i "s|window.location.href = 'userInput.html'|window.location.href = '/html/userInput.html'|g" html/start.html index.html
sed -i "s|window.location.href = 'login.html'|window.location.href = '/html/login.html'|g" html/start.html index.html html/mypage.html

sed -i "s|'http://127.0.0.1:8000/kospi-data'|'/kospi-data'|g" js/analysis.js
sed -i "s|'http://127.0.0.1:8000/market-summary'|'/market-summary'|g" js/analysis.js

sed -i 's|window.location.href = "../loading.html"|window.location.href = "/html/loading.html"|g' js/script.js

sed -i 's|href="mypage.html"|href="/html/mypage.html"|g' js/auth.js
sed -i 's|href="login.html"|href="/html/login.html"|g' js/auth.js
sed -i 's|href="signup.html"|href="/html/signup.html"|g' js/auth.js

echo "✅ 프론트엔드 경로 수정 완료"

# 2. Backend Dockerfile
echo "📝 Backend Dockerfile 생성 중..."
cd ~/upstage-stock-agent
cat > Dockerfile << 'DOCKERFILE'
FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir \
    fastapi uvicorn python-dotenv yfinance \
    langchain langchain-upstage langchain-community \
    tavily-python pandas sqlalchemy passlib \
    python-jose python-multipart bcrypt \
    finance-datareader chromadb argon2-cffi
COPY . .
EXPOSE 8001
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
DOCKERFILE

# 3. Frontend Dockerfile
echo "📝 Frontend Dockerfile 생성 중..."
cd infra/frontend
cat > Dockerfile << 'DOCKERFILE'
FROM nginx:alpine
RUN rm -rf /usr/share/nginx/html/*
COPY index.html /usr/share/nginx/html/
COPY html/ /usr/share/nginx/html/html/
COPY css/ /usr/share/nginx/html/css/
COPY js/ /usr/share/nginx/html/js/
COPY img/ /usr/share/nginx/html/img/
RUN echo 'server { listen 8002; server_name localhost; root /usr/share/nginx/html; index index.html; location / { try_files \$uri \$uri/ /index.html; } }' > /etc/nginx/conf.d/default.conf
EXPOSE 8002
CMD ["nginx", "-g", "daemon off;"]
DOCKERFILE

# 4. 빌드 및 배포
echo "🔨 Backend 빌드 중..."
cd ~/upstage-stock-agent
sudo docker build -t stock-agent-backend:latest .

echo "🔨 Frontend 빌드 중..."
cd infra/frontend
sudo docker build -t stock-agent-frontend:latest .

echo "📦 이미지 import 중..."
sudo docker save stock-agent-backend:latest -o /tmp/stock-agent-backend.tar
sudo k3s ctr images import /tmp/stock-agent-backend.tar

sudo docker save stock-agent-frontend:latest -o /tmp/stock-agent-frontend.tar
sudo k3s ctr images import /tmp/stock-agent-frontend.tar

echo "🚀 배포 중..."
sudo kubectl rollout restart deployment/backend -n stock-agent
sudo kubectl delete pod -n stock-agent -l app=frontend

echo "⏳ 대기 중..."
sleep 20

echo ""
echo "================================"
echo "✅ 최신 코드 배포 완료!"
echo "================================"
sudo kubectl get pods -n stock-agent
echo ""
echo "🌐 http://stockwars.duckdns.org:30080/"
