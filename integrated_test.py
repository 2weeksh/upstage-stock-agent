import asyncio
import re
from app.utils.llm import get_solar_model
from app.agents.ticker_agent import extract_company_name
from app.utils.ticker_utils import get_clean_ticker
from app.agents.chart_agent import ChartAgent
from app.agents.news_agent import NewsAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.moderator_agent import ModeratorAgent

# 주혁님의 실제 도구 함수들 임포트
from app.tools.finance_tools import get_financial_summary
from app.tools.search_tools import get_stock_news  # 함수명 수정 완료

async def run_multi_turn_debate(user_query: str, max_turns: int =3):
    # 0. 준비 단계: 모델 및 에이전트 초기화
    llm = get_solar_model()
    chart_agent = ChartAgent(llm)
    news_agent = NewsAgent(llm)
    finance_agent = FinanceAgent(llm)
    moderator = ModeratorAgent(llm)

    print(f"\n{'='*20} 🤖 주식 분석 토론 시스템 가동 {'='*20}")
    print(f"💬 사용자 입력: '{user_query}'")

    # 1단계: 종목명 추출 및 티커 매핑
    print("\n[1/5] 종목 정보 확인 중...")
    company_name = extract_company_name(user_query)
    ticker = get_clean_ticker(company_name)
    print(f"✅ 대상: {company_name} ({ticker})")

    # 2단계: 기초 데이터 수집 (주혁님의 툴 적용)
    print("\n[2/5] 토론을 위한 기초 데이터 수집 중...")
    
    # [수정] 주혁님의 get_stock_news 함수 파라미터에 맞춰 ticker와 company_name 전달
    f_data = get_financial_summary(ticker)
    n_data = get_stock_news(ticker, company_name) 
    c_data = "RSI: 85, 5일 이평선 골든크로스, 거래량 급증" # 차트 데이터 (추후 툴 연결 가능)

    # 에이전트 맵 구성
    agent_map = {
        "Chart": {"instance": chart_agent, "data": c_data, "name": "차트 분석가"},
        "News": {"instance": news_agent, "data": n_data, "name": "뉴스 분석가"},
        "Finance": {"instance": finance_agent, "data": f_data, "name": "재무 분석가"}
    }

    # 3단계: Round 1 - 에이전트별 기조 발언
    print("\n🎤 [Round 1] 에이전트별 초기 리포트 작성 중...")
    
    chart_init = chart_agent.analyze(company_name, ticker, c_data)
    news_init = news_agent.analyze(company_name, ticker, n_data)
    finance_init = finance_agent.analyze(company_name, ticker, f_data)

    initial_reports = f"""
    [차트 분석가]: {chart_init}
    [뉴스 분석가]: {news_init}
    [재무 분석가]: {finance_init}
    """
    current_debate_history = initial_reports # 토론의 '기억' 저장소

    print("✅ 모든 에이전트의 기조 발언 수집 완료")

    # ---------------------------------------------------------
    # 🚀 [핵심] Round 2: 재귀적 토론 루프 (Ping-Pong)
    # ---------------------------------------------------------
    print(f"\n💬 최대 {max_turns}회 대결 토론을 시작합니다.")

    for turn in range(max_turns):
        print(f"\n🔄 [토론 {turn + 1}/{max_turns}] 사회자가 발언권을 분배합니다...")
        
        # 1. 사회자가 현재까지의 모든 토론 기록을 읽고 다음 지시를 내립니다.
        instruction = moderator.facilitate(company_name, current_debate_history)
        print(f"📢 사회자: {instruction}")

        # 2. 사회자의 지시에서 [NEXT] 태그를 찾아 다음 발언자 확인
        match = re.search(r"\[NEXT\]:\s*(\w+)", instruction)
        
        if match:
            target_key = match.group(1)
            if target_key in agent_map:
                target = agent_map[target_key]
                print(f"👉 {target['name']}에게 반박권이 넘어갔습니다.")
                
                # 3. 지목된 에이전트가 '지금까지의 토론 전체'를 읽고 답변합니다.
                rebuttal = target["instance"].analyze(
                    company_name, 
                    ticker, 
                    target["data"], 
                    debate_context=current_debate_history + "\n\n" + instruction
                )
                print(f"💬 {target['name']} (재반박): {rebuttal}")

                # 4. 토론 기록 업데이트 (이게 있어야 다음 턴에 이 내용을 기억합니다!)
                current_debate_history += f"\n\n[사회자 지시]: {instruction}\n[{target['name']} 반박]: {rebuttal}"
            else:
                print("⚠️ 잘못된 지목입니다. 루프를 중단합니다.")
                break
        else:
            print("🏁 사회자가 토론을 종료했습니다. (더 이상의 쟁점 없음)")
            break

    # ---------------------------------------------------------
    # 5단계: 최종 판결 (모든 히스토리를 종합)
    # ---------------------------------------------------------
    print("\n⚖️ [Final] 모든 토론을 종합하여 최종 판결을 내립니다...")
    final_decision = moderator.summarize(company_name, current_debate_history)

    print("\n" + "="*60)
    print(f"🏆 {company_name} ({ticker}) 최종 전략 보고서")
    print(final_decision)

if __name__ == "__main__":
    # 1. 사용자로부터 분석할 종목명을 입력받습니다.
    user_input = input("분석하고 싶은 종목을 말씀하세요 (예: 삼성전자, AAPL): ")
    
    # 2. 만약 입력이 비어있다면 기본값으로 실행하거나 경고를 줍니다.
    if not user_input.strip():
        user_input = "애플" # 테스트용 기본값
    
    # 3. 비동기 함수인 run_multi_turn_debate를 실행합니다.
    try:
        asyncio.run(run_multi_turn_debate(user_input, max_turns=3))
    except KeyboardInterrupt:
        print("\n👋 사용자에 의해 분석이 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 실행 중 예외 발생: {e}")