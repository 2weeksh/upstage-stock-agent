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
    
    chart_agent = ChartAgent(llm)
    news_agent = NewsAgent(llm)
    finance_agent = FinanceAgent(llm)
    moderator = ModeratorAgent(llm)
    judge = JudgeAgent(llm)

    print(f"\n{'='*20} 🤖 끝장 토론 시스템 (Reasoning Mode) {'='*20}")
    
    # 1. 데이터 수집
    company_name = extract_company_name(user_query)
    ticker = get_clean_ticker(company_name)
    print(f"✅ 대상: {company_name} ({ticker})")
    
    f_data = get_financial_summary(ticker)
    n_data = get_stock_news(ticker, company_name) 
    c_data = get_chart_indicators(ticker)

    agent_map = {
        "Chart": {"instance": chart_agent, "data": c_data, "name": "차트 분석가"},
        "News": {"instance": news_agent, "data": n_data, "name": "뉴스 분석가"},
        "Finance": {"instance": finance_agent, "data": f_data, "name": "재무 분석가"}
    }

    # ---------------------------------------------------------
    # [Step 1] 입론 (Opening Statements)
    # ---------------------------------------------------------
    print(f"\n🎤 [Step 1: 입론] 사회자가 각 전문가에게 초기 분석을 요청합니다.")
    current_debate_history = "[사회자]: 지금부터 토론을 시작합니다. 각 전문가는 입론을 해주세요.\n"

    for role_name in ["Chart", "News", "Finance"]:
        agent = agent_map[role_name]
        print(f"👉 {agent['name']} 입론 준비 중...")
        await asyncio.sleep(1)
        
        # 입론 생성
        stmt = agent["instance"].analyze(company_name, ticker, agent["data"])
        
        # [수정완료] 잘림 없이 전체 내용 출력 (\n으로 줄바꿈 추가)
        print(f"🗣️ {agent['name']} 입론:\n{stmt}\n") 
        
        current_debate_history += f"\n[{agent['name']} 입론]: {stmt}"
    
    debate_rules = moderator.get_debate_rules()
    print("✅ 모든 입론 완료.")

    # ---------------------------------------------------------
    # [Step 2] 상호 토론 (Cross Examination)
    # ---------------------------------------------------------
    turn_count = 1
    max_turns = 10 

    print(f"\n🔥 [Step 2: 상호 토론] 최대 {max_turns}회 진행")

    while turn_count <= max_turns:
        print("⏳ API 호출 대기 (3초)...")
        await asyncio.sleep(3) 

        print(f"\n🔄 [Turn {turn_count}/{max_turns}] 사회자 Reasoning...")
        
        try:
            mod_output = moderator.facilitate(company_name, current_debate_history)
        except Exception as e:
            print(f"⚠️ 사회자 에러: {e}")
            await asyncio.sleep(3)
            continue
        
        thought = re.search(r"THOUGHT:(.*?)(?=STATUS|NEXT_SPEAKER|$)", mod_output, re.DOTALL)
        status = re.search(r"STATUS:\s*\[?(TERMINATE|CONTINUE)\]?", mod_output)
        speaker = re.search(r"NEXT_SPEAKER:\s*\[?(\w+)\]?", mod_output)
        instruction = re.search(r"INSTRUCTION:\s*(.*)", mod_output, re.DOTALL)

        if thought:
            print(f"🤔 사회자 생각: {thought.group(1).strip()}")

        # 종료 조건
        if status and "TERMINATE" in status.group(1):
            print("\n🏁 사회자가 토론 종료를 선언했습니다.")
            break
        if turn_count == max_turns:
            print("\n⏰ 시간 관계상 토론을 종료합니다.")
            break

        if speaker and instruction:
            target_key_raw = speaker.group(1).strip()
            inst_text = instruction.group(1).strip()
            target_key = next((k for k in agent_map if k.lower() in target_key_raw.lower()), None)
            
            if target_key:
                target = agent_map[target_key]
                print(f"👉 지목: {target['name']}")
                print(f"📢 질문: {inst_text}")

                forced_context = (
                    f"{current_debate_history}\n\n"
                    f"--- [SYSTEM ALERT] ---\n"
                    f"규칙 준수 필수:\n{debate_rules}\n"
                    f"----------------------\n"
                    f"[사회자 지시]: {inst_text}"
                )
                
                await asyncio.sleep(1)
                try:
                    rebuttal = target["instance"].analyze(company_name, ticker, target["data"], debate_context=forced_context)
                    
                    # [수정] 답변 전체 출력
                    print(f"💬 {target['name']} 답변:\n{rebuttal}\n") 
                    
                    current_debate_history += f"\n\n[사회자]: {inst_text}\n[{target['name']}]: {rebuttal}"
                except Exception as e:
                    print(f"⚠️ 답변 실패: {e}")
            else:
                print(f"⚠️ 발언자 매핑 실패({target_key_raw}).")
        
        turn_count += 1

    # ---------------------------------------------------------
    # [Step 3] 사회자 요약 (Summarization)
    # ---------------------------------------------------------
    print(f"\n📝 [Step 3: 중간 정리] 사회자가 오늘의 논점을 정리합니다.")
    print("⏳ 요약 생성 중...")
    await asyncio.sleep(3)
    
    summary = moderator.summarize_debate(company_name, current_debate_history)
    print(f"\n[사회자 정리]:\n{summary}")
    
    current_debate_history += f"\n\n[사회자 정리]: {summary}"

    # ---------------------------------------------------------
    # [Step 4] 최후 변론 (Closing Arguments)
    # ---------------------------------------------------------
    print(f"\n🎤 [Step 4: 최후 변론] 각 전문가의 마지막 어필.")
    current_debate_history += "\n\n[사회자]: 정리가 끝났습니다. 이제 각 전문가는 '최후 변론'을 하세요."

    for role, agent_info in agent_map.items():
        print(f"⏳ {agent_info['name']} 최후 변론 중...")
        await asyncio.sleep(2)

        closing_context = f"""
        {current_debate_history}
        
        --- [SYSTEM INSTRUCTION] ---
        지금까지의 토론 흐름과 사회자의 정리를 참고하여, 
        당신의 최종 투자의견(매수/매도/보류)을 투자자들에게 설득력 있게 전달하는 '최후 변론'을 하십시오.
        """
        try:
            closing_statement = agent_info["instance"].analyze(
                company_name, ticker, agent_info["data"], debate_context=closing_context
            )
            
            # [수정] 최후 변론 전체 출력
            print(f"🗣️ {agent_info['name']} 최후 변론:\n{closing_statement}\n") 
            
            current_debate_history += f"\n[{agent_info['name']} 최후 변론]: {closing_statement}"
        except Exception as e:
            print(f"⚠️ 변론 실패: {e}")

    # ---------------------------------------------------------
    # [Step 5] 최종 판결 (Judge)
    # ---------------------------------------------------------
    print(f"\n{'='*20} ⚖️ Judge Agent 판결 {'='*20}")
    print("⏳ 최종 전략 수립 중 (5초 대기)...")
    await asyncio.sleep(5)

    try:
        final_decision = judge.adjudicate(company_name, current_debate_history)
        print("\n" + final_decision)
    except Exception as e:
        print(f"\n❌ 판결 생성 실패: {e}")

if __name__ == "__main__":
    user_input = input("종목 입력: ")
    if not user_input.strip(): user_input = "삼성전자"
    asyncio.run(run_multi_turn_debate(user_input))