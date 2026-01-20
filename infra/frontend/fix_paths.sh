#!/bin/bash

# HTML 파일 내의 href 속성 수정
find . -name "*.html" -type f -exec sed -i \
  -e 's|href="../css/|href="/css/|g' \
  -e 's|href="css/|href="/css/|g' \
  -e 's|src="../img/|src="/img/|g' \
  -e 's|src="img/|src="/img/|g' \
  -e 's|src="../js/|src="/js/|g' \
  -e 's|src="js/|src="/js/|g' \
  -e 's|href="login.html"|href="/html/login.html"|g' \
  -e 's|href="signup.html"|href="/html/signup.html"|g' \
  -e 's|href="userInput.html"|href="/html/userInput.html"|g' \
  -e 's|href="analysis.html"|href="/html/analysis.html"|g' \
  -e 's|href="mypage.html"|href="/html/mypage.html"|g' \
  -e 's|href="history.html"|href="/html/history.html"|g' \
  -e 's|href="loading.html"|href="/html/loading.html"|g' \
  -e 's|href="start.html"|href="/"|g' \
  {} \;

# JS 파일 내의 경로 수정
find js/ -name "*.js" -type f -exec sed -i \
  -e "s|window.location.href = 'login.html'|window.location.href = '/html/login.html'|g" \
  -e "s|window.location.href = 'signup.html'|window.location.href = '/html/signup.html'|g" \
  -e "s|window.location.href = 'userInput.html'|window.location.href = '/html/userInput.html'|g" \
  -e "s|window.location.href = 'analysis.html'|window.location.href = '/html/analysis.html'|g" \
  -e "s|window.location.href = 'mypage.html'|window.location.href = '/html/mypage.html'|g" \
  -e "s|window.location.href = 'history.html'|window.location.href = '/html/history.html'|g" \
  -e "s|window.location.href = 'loading.html'|window.location.href = '/html/loading.html'|g" \
  -e "s|window.location.href = 'start.html'|window.location.href = '/'|g" \
  -e 's|window.location.href = "../html/|window.location.href = "/html/|g' \
  {} \;

# API 엔드포인트를 상대 경로로 변경
sed -i "s|const AUTH_API_BASE = .*;|const AUTH_API_BASE = '/api/auth';|g" js/auth.js

echo "경로 수정 완료!"
