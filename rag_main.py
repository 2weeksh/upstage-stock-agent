import os
from dotenv import load_dotenv

# 1. 에이전트 및 서비스 모듈 임포트
from app.repository.retriever import StockRetriever
from app.agents.finance_agent import FinanceAgent
from app.agents.news_agent import NewsAgent
from app.agents.chart_agent import ChartAgent
from app.agents.moderator_agent import ModeratorAgent
from app.service.debate_manager import DebateManager

from app.service.ticker_resolver import resolve_target_ticker
from app.service.orchestrator import prepare_knowledge_base

from langchain_upstage import ChatUpstage



def main():
    # .env 파일에서 UPSTAGE_API_KEY 로드
    load_dotenv()
    
    if not os.getenv("UPSTAGE_API_KEY"):
        print("❌ 에러: UPSTAGE_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
        return

    user_query = input("어떤 종목을 분석해 드릴까요? : ") # 예: "삼전 분석해줘"
    
    # 1. 티커 식별 (유저님 코드 기반)
    ticker = resolve_target_ticker(user_query)
    
    # 2. 데이터가 없으면 실시간 수집, 있으면 로드 (DART, 뉴스 등)
    # 이 과정에서 메타데이터(common, finance, news 등)가 달린 채로 저장됩니다.
    retriever = prepare_knowledge_base(ticker)


    # 2. 공통 자원 초기화 (Retriever & LLM)
    print("🛠️ 시스템 초기화 중...")
    retriever = StockRetriever(db_path="chroma_db/")
    
    # 토론의 논리력을 위해 업스테이지의 최상위 모델 Solar-Pro 사용
    llm = ChatUpstage(model="solar-pro2")

    # 3. 각 분야 전문가 에이전트 생성
    # 유저님이 작성하신 프롬프트가 이식된 클래스들입니다.
    finance_agent = FinanceAgent(name="재무 분석가", role="Finance", retriever=retriever)
    news_agent = NewsAgent(name="뉴스 분석가", role="News", retriever=retriever)
    chart_agent = ChartAgent(name="차트 분석가", role="Chart", retriever=retriever)
    
    # 4. 사회자 에이전트 생성
    moderator_agent = ModeratorAgent(llm=llm)

    # 5. 전문가 그룹 딕셔너리 구성
    agents = {
        "Finance": finance_agent,
        "News": news_agent,
        "Chart": chart_agent
    }

    # 6. 토론 매니저(오케스트레이터) 생성
    company_name = "삼성전자"
    ticker = "005930"
    
    manager = DebateManager(
        company_name=company_name,
        ticker=ticker,
        moderator=moderator_agent,
        agents=agents
    )

    # 7. 끝장 토론 시작! (최대 토론 턴수는 상황에 맞게 조절 가능)
    print(f"✨ {company_name} RAG 기반 AI 에이전트 토론 시스템 가동\n" + "="*50)
    manager.start_debate(max_turns=3)

if __name__ == "__main__":
    main()