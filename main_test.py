# main_test.py (완성본)
import os
from dotenv import load_dotenv
from app.agents.ticker_agent import extract_company_name
from app.utils.ticker_utils import get_clean_ticker
from app.agents.news_agent import NewsAgent
from app.agents.chart_agent import ChartAgent
from app.tools.chart_tools import get_chart_indicators
from app.tools.search_tools import get_stock_news  # 뉴스 수집 도구 임포트

load_dotenv()

def run_integrated_test(user_query: str):
    print(f"\n💬 유저 질문: '{user_query}'")
    print("-" * 50)

    try:
        # STEP 1: 종목명 추출 (LLM)
        refined_name = extract_company_name(user_query)
        if refined_name == "NONE":
            print("❌ 질문에서 종목명을 찾을 수 없습니다.")
            return
        print(f"✅ 추출된 종목: {refined_name}")

        # STEP 2: 티커 변환
        ticker = get_clean_ticker(refined_name)
        print(f"✅ 변환된 티커: {ticker}")

        # STEP 3: 차트 분석
        print("[3/4] 차트 데이터 수집 및 분석 중...")
        chart_data = get_chart_indicators(ticker)
        chart_analysis = ChartAgent().analyze(ticker, refined_name, chart_data)
        print("✅ 차트 분석 완료")

        # STEP 4: 뉴스 분석 (이 부분이 추가되었습니다)
        print("[4/4] 실시간 뉴스 수집 및 분석 중...")
        # 4-1. Tavily를 통해 실시간 뉴스 수집
        news_raw_data = get_stock_news(ticker, refined_name) 
        # 4-2. NewsAgent를 통한 감성 및 리스크 분석
        news_agent = NewsAgent()
        news_analysis = news_agent.analyze(ticker, refined_name, news_raw_data)
        print("✅ 뉴스 분석 완료")

        # 최종 통합 리포트 출력
        print("\n" + "="*60)
        print(f"🚀 {refined_name}({ticker}) 통합 분석 리포트")
        print("="*60)
        
        print("\n[📈 차트 분석가의 발언]")
        print(chart_analysis)
        
        print("\n" + "-"*60)
        
        print("\n[📰 뉴스 분석가의 발언]")
        print(news_analysis)
        
        print("="*60)
        print("\n💡 이제 이 두 의견을 사회자(Moderator)에게 전달하면 최종 결정이 내려집니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    query = input("분석할 종목을 입력하세요 (예: 삼전 분석해줘): ")
    run_integrated_test(query)