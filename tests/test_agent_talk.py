# tests/test_agent_talk.py

from app.service.orchestrator import StockDebateOrchestrator

def start_investor_debate():
    # 1. 지휘소(Orchestrator) 초기화
    orchestrator = StockDebateOrchestrator()
    
    # 2. 질문 던지기
    user_query = "삼성전자 현재 주가가 14만원대인데, 재무 건전성과 최근 뉴스를 고려했을 때 추가 상승 여력이 있을까?"
    
    print(f"\n🚀 질문: {user_query}")
    print("="*50)
    
    # 3. 전체 프로세스 실행 (티커 추출 -> DB 확인/업데이트 -> 토론 시작)
    result = orchestrator.run_full_process(user_query)
    
    # 4. 결과 출력

    print("\n📜 [전체 토론 기록]")
    print(result['full_history'])

    print("\n📊 [최종 토론 요약]")
    print(result['summary'])

if __name__ == "__main__":
    start_investor_debate()