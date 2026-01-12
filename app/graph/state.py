from typing import TypedDict, List

class AgentState(TypedDict):
    # 공통 정보
    symbol: str
    company_name: str
    
    # 각 분석가 에이전트의 출력물 저장소
    chart_analysis: str
    finance_analysis: str
    news_analysis: str  # 주혁님이 작업한 뉴스 분석 결과가 여기 담깁니다.
    
    # 토론 및 의사결정 기록
    debate_history: List[str]
    final_decision: str