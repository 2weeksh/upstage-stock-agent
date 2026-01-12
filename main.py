from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(
    title="Stock Agent API (Mock)",
    description="주식 분석 에이전트 API - 인프라 테스트용 Mock 버전",
    version="0.1.0"
)

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Stock Agent API",
        "status": "running",
        "version": "0.1.0-mock"
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "service": "stock-agent-backend"
    }

@app.get("/agent/health")
async def agent_health():
    """에이전트 헬스 체크"""
    return {
        "status": "healthy",
        "agent": "ready"
    }

@app.get("/agent/seed-status")
async def seed_status():
    """시딩 상태 확인 (Mock)"""
    return {
        "status": "completed",
        "current": 1000,
        "total": 1000,
        "message": "Mock data ready"
    }

@app.get("/agent/stats")
async def get_stats():
    """지식 베이스 통계 (Mock)"""
    return {
        "name": "stock_embeddings",
        "count": 1000,
        "metadata": {"type": "mock"}
    }

@app.post("/agent/chat")
async def chat(request: dict):
    """채팅 엔드포인트 (Mock)"""
    query = request.get("query", "")
    return {
        "answer": f"주식 분석 에이전트입니다. '{query}'에 대한 분석은 곧 제공될 예정입니다.",
        "user_query": query,
        "process_status": "success"
    }

@app.post("/agent/chat/stream")
async def chat_stream(request: dict):
    """스트리밍 채팅 엔드포인트 (Mock)"""
    from fastapi.responses import StreamingResponse
    import json
    
    async def generate():
        yield f"data: {json.dumps({'type': 'log', 'log': '분석 시작...'})}\n\n"
        yield f"data: {json.dumps({'type': 'token', 'answer': '주식 분석 에이전트입니다. '})}\n\n"
        yield f"data: {json.dumps({'type': 'token', 'answer': '에이전트 구현이 완료되면 '})}\n\n"
        yield f"data: {json.dumps({'type': 'token', 'answer': '실제 분석을 제공합니다.'})}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.get("/api/v1/analyze/{symbol}")
async def analyze_stock(symbol: str):
    """주식 분석 엔드포인트 (Mock)"""
    return {
        "symbol": symbol,
        "message": f"{symbol} 종목 분석은 곧 제공될 예정입니다.",
        "status": "mock"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
