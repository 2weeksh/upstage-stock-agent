# tests/test_multi_stock.py
from app.service.orchestrator import StockDebateOrchestrator
import os

def test_multi_stock_analysis():
    orchestrator = StockDebateOrchestrator()
    
    # 테스트할 종목 리스트
    test_queries = [
        "삼성전자 최근 주가 흐름과 재무 건전성 분석해줘",
        "한화오션 현재 밸류에이션과 수주 뉴스 위주로 분석해줘"
    ]
    
    for i, query in enumerate(test_queries):
        print(f"\n{'='*30} TEST {i+1} START {'='*30}")
        print(f"🚀 질문: {query}")
        
        # 1. 실행
        result = orchestrator.run_full_process(query)
        
        # 2. 결과 출력 (기록 먼저, 요약 나중에)
        if result:
            print("\n📜 [전체 토론 기록]")
            print(result.get('full_history', '기록 없음'))
            print("\n" + "="*50)
            print("📊 [최종 토론 요약]")
            print(result.get('summary', '요약 없음'))
        
        print(f"{'='*30} TEST {i+1} END {'='*30}\n")

if __name__ == "__main__":
    test_multi_stock_analysis()