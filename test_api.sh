#!/bin/bash

echo "=========================================="
echo "API 테스트"
echo "=========================================="
echo ""

# 색상
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 서버 확인
if ! curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${RED}✗${NC} 서버가 실행되지 않았습니다."
    echo ""
    echo "서버를 먼저 실행하세요:"
    echo "   sh run.sh"
    exit 1
fi

echo -e "${GREEN}✓${NC} 서버 실행 중"
echo ""

# 테스트 실행
echo "📍 테스트 1: Health Check"
curl -s http://localhost:8001/health | jq . 2>/dev/null || curl -s http://localhost:8001/health
echo ""

echo ""
echo "📍 테스트 2: Root Endpoint"
curl -s http://localhost:8001/ | jq . 2>/dev/null || curl -s http://localhost:8001/
echo ""

echo ""
echo "📍 테스트 3: Agent Health"
curl -s http://localhost:8001/agent/health | jq . 2>/dev/null || curl -s http://localhost:8001/agent/health
echo ""

echo ""
echo "📍 테스트 4: Seed Status"
curl -s http://localhost:8001/agent/seed-status | jq . 2>/dev/null || curl -s http://localhost:8001/agent/seed-status
echo ""

echo ""
echo "📍 테스트 5: Stats"
curl -s http://localhost:8001/agent/stats | jq . 2>/dev/null || curl -s http://localhost:8001/agent/stats
echo ""

echo ""
echo "📍 테스트 6: Chat API"
curl -s -X POST http://localhost:8001/agent/chat \
    -H "Content-Type: application/json" \
    -d '{"query": "삼성전자 분석해줘"}' | jq . 2>/dev/null || \
curl -s -X POST http://localhost:8001/agent/chat \
    -H "Content-Type: application/json" \
    -d '{"query": "삼성전자 분석해줘"}'
echo ""

echo ""
echo "📍 테스트 7: Stock Analysis"
curl -s http://localhost:8001/api/v1/analyze/005930 | jq . 2>/dev/null || curl -s http://localhost:8001/api/v1/analyze/005930
echo ""

echo ""
echo "=========================================="
echo "✅ 모든 테스트 완료"
echo "=========================================="
echo ""
echo "브라우저에서 확인:"
echo "   http://localhost:8001/docs"
echo ""
