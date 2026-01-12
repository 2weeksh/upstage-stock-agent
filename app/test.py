# main.py (최종 완성 시 예상 코드)

from utils.llm import get_solar_model
from agents.finance_agent import FinanceAgent
# from src.agents.news_agent import NewsAgent   (나중에 추가)
# from src.agents.chart_agent import ChartAgent (나중에 추가)

def main():
    # 1. 준비
    llm = get_solar_model()
    
    # 2. 선수 입장 (객체 생성)
    finance = FinanceAgent(llm)
    # news = NewsAgent(llm)
    # chart = ChartAgent(llm)

    # 3. 사용자 입력
    ticker = input("토론할 종목 코드를 입력하세요 (예: 005930.KS): ")
    print(f"\n--- 📢 {ticker} 종목 대토론회를 시작합니다 ---\n")

    # 4. 토론 진행 (단순 순차 실행 예시)
    
    # [1라운드] 각자 의견 발표
    print("\n[💰 재무 분석가의 의견]")
    fin_opinion = finance.analyze(ticker)
    print(fin_opinion)

    # print("\n[📰 뉴스 분석가의 의견]")
    # news_opinion = news.analyze(ticker)
    # print(news_opinion)

    # print("\n[📈 차트 분석가의 의견]")
    # chart_opinion = chart.analyze(ticker)
    # print(chart_opinion)

    # [2라운드] 종합 결론 (여기에 나중에 사회자 에이전트를 추가하거나 LangGraph 로직 적용)
    print("\n--- ✅ 토론 종료 ---")

if __name__ == "__main__":
    main()