import asyncio
import re
from app.utils.llm import get_solar_model
from app.agents.ticker_agent import extract_company_name
from app.utils.ticker_utils import get_clean_ticker
from app.agents.chart_agent import ChartAgent
from app.agents.news_agent import NewsAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.moderator_agent import ModeratorAgent
from app.agents.judge_agent import JudgeAgent
from app.tools.chart_tools import get_chart_indicators
from app.tools.finance_tools import get_financial_summary
from app.tools.search_tools import get_stock_news

async def run_multi_turn_debate(user_query: str):
    # 0. 초기화
    llm = get_solar_model()
    
    # 각 에이전트 인스턴스 생성
    chart_agent = ChartAgent(llm)
    news_agent = NewsAgent(llm)
    finance_agent = FinanceAgent(llm)
    moderator = ModeratorAgent(llm) # Reasoning Mode 적용됨
    judge = JudgeAgent(llm)

    print(f"\n{'='*20} 🤖 끝장 토론 시스템 (Reasoning Mode) {'='*20}")
    
    # 1. 데이터 수집
    company_name = extract_company_name(user_query)
    ticker = get_clean_ticker(company_name)
    print(f"✅ 대상: {company_name} ({ticker})")
    
    # 데이터 로드 (실제 툴 사용)
    f_data = get_financial_summary(ticker)
    n_data = get_stock_news(ticker, company_name) 
    c_data = get_chart_indicators(ticker)

    agent_map = {
        "Chart": {"instance": chart_agent, "data": c_data, "name": "차트 분석가"},
        "News": {"instance": news_agent, "data": n_data, "name": "뉴스 분석가"},
        "Finance": {"instance": finance_agent, "data": f_data, "name": "재무 분석가"}
    }

    # 2. 기조 발언 (Round 1)
    print("\n🎤 [Round 1] 기조 발언 시작")
    chart_init = chart_agent.analyze(company_name, ticker, c_data)
    news_init = news_agent.analyze(company_name, ticker, n_data)
    finance_init = finance_agent.analyze(company_name, ticker, f_data)

    # 사회자로부터 규칙 텍스트 가져오기
    debate_rules = moderator.get_debate_rules()
    
    current_debate_history = f"""
    [차트 분석가 초기 관점]: {chart_init}
    [뉴스 분석가 초기 관점]: {news_init}
    [재무 분석가 초기 관점]: {finance_init}
    """

    # 3. [Task 3] 무제한 토론 루프 (While Loop)
    turn_count = 1
    max_safety_turns = 15 

    print(f"\n🔥 의견 수렴 시까지 토론을 진행합니다 (최대 {max_safety_turns}회)")

    while turn_count <= max_safety_turns:
        # [Rate Limit 방지 1] 루프 시작 전 대기
        print("⏳ API 호출 간격 조절 중 (3초 대기)...")
        await asyncio.sleep(3) 

        print(f"\n🔄 [Turn {turn_count}] 사회자가 상황을 Reasoning 중...")
        
        # 사회자 추론 및 지시
        try:
            mod_output = moderator.facilitate(company_name, current_debate_history)
        except Exception as e:
            print(f"⚠️ 사회자 호출 중 에러 발생: {e}")
            print("⏳ 5초 후 재시도합니다...")
            await asyncio.sleep(5)
            continue
        
        # 파싱 로직
        thought = re.search(r"THOUGHT:(.*?)(?=STATUS|NEXT_SPEAKER|$)", mod_output, re.DOTALL)
        status = re.search(r"STATUS:\s*\[?(TERMINATE|CONTINUE)\]?", mod_output)
        speaker = re.search(r"NEXT_SPEAKER:\s*\[?(\w+)\]?", mod_output)
        instruction = re.search(r"INSTRUCTION:\s*(.*)", mod_output, re.DOTALL)

        if thought:
            print(f"🤔 사회자 생각: {thought.group(1).strip()}")

        # [종료 조건 검사]
        if status and "TERMINATE" in status.group(1):
            print("\n🏁 사회자가 토론 종료를 선언했습니다 (의견 수렴 완료).")
            break
        
        # [토론 진행]
        if speaker and instruction:
            target_key_raw = speaker.group(1).strip()
            inst_text = instruction.group(1).strip()
            
            # 매핑 키 보정
            target_key = next((k for k in agent_map if k.lower() in target_key_raw.lower()), None)
            
            if target_key:
                target = agent_map[target_key]
                print(f"👉 지목: {target['name']}")
                print(f"📢 질문: {inst_text}")

                # [Task 2] 규칙 강제 주입
                forced_context = (
                    f"{current_debate_history}\n\n"
                    f"--- [SYSTEM ALERT] ---\n"
                    f"지금부터는 다음 규칙을 어기면 안 됩니다.\n"
                    f"{debate_rules}\n"
                    f"----------------------\n"
                    f"[사회자 지시]: {inst_text}"
                )

                # [Rate Limit 방지 2] 에이전트 답변 전 대기
                await asyncio.sleep(1) 

                try:
                    rebuttal = target["instance"].analyze(
                        company_name, 
                        ticker, 
                        target["data"], 
                        debate_context=forced_context
                    )
                    print(f"💬 {target['name']} 답변 완료")
                    current_debate_history += f"\n\n[사회자]: {inst_text}\n[{target['name']}]: {rebuttal}"
                except Exception as e:
                    print(f"⚠️ 에이전트 답변 생성 실패: {e}")
                    await asyncio.sleep(3) # 실패 시 대기 후 다음 턴
            else:
                print(f"⚠️ 발언자 매핑 실패({target_key_raw}). 다음 턴 진행")
        else:
            print("⚠️ 사회자 응답 형식 오류. 재시도합니다.")
        
        turn_count += 1

    # 4. 최종 판결
    print(f"\n{'='*20} ⚖️ Judge Agent 판결 {'='*20}")
    print("⏳ 전체 토론 기록을 분석하여 최종 전략을 수립합니다...")
    
    # [Rate Limit 방지 3] 최종 판결 전 충분한 대기
    print("⏳ 최종 판결 생성 전 5초 대기...")
    await asyncio.sleep(5)

    try:
        final_decision = judge.adjudicate(company_name, current_debate_history)
        print("\n" + final_decision)
    except Exception as e:
        print(f"\n❌ 최종 판결 생성 중 에러 발생: {e}")
        print("잠시 후 다시 시도해보세요.")

if __name__ == "__main__":
    user_input = input("종목 입력 (예: 삼성전자): ")
    if not user_input.strip(): user_input = "삼성전자"
    asyncio.run(run_multi_turn_debate(user_input))