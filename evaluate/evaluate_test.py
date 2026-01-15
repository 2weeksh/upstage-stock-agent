import asyncio
import re
import os
from dotenv import load_dotenv

# 사용자님의 기존 에이전트 및 유틸 임포트
from app.utils.llm import get_solar_model
from app.agents.ticker_agent import extract_company_name
from app.utils.ticker_utils import get_clean_ticker
from app.agents.chart_agent import ChartAgent
from app.agents.news_agent import NewsAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.moderator_agent import ModeratorAgent
from app.agents.judge_agent import JudgeAgent
from app.utils.file_utils import save_debate_log
from app.agents.report_agent import InsightReportAgent

# 우리가 만든 과거 데이터 툴들
from evaluate.post_finance_tool import get_historical_financial_summary
from evaluate.post_search_tool import get_historical_news
from evaluate.post_char_tool import get_historical_chart_indicators

load_dotenv()

async def evaluate_postdata(user_query: str):
    # 0. 초기화
    llm = get_solar_model()
    chart_agent = ChartAgent(llm)
    news_agent = NewsAgent(llm)
    finance_agent = FinanceAgent(llm)
    moderator = ModeratorAgent(llm)
    judge = JudgeAgent(llm)

    print(f"🚀 과거 데이터 기반 평가 시스템 가동")
    
    # 1. 대상 및 시점 설정
    company_name = extract_company_name(user_query)
    ticker = get_clean_ticker(company_name)
    
    if ticker == "035720.KS": # 카카오
        target_date = "2021-06-24" # 고점
    else: # SK 하이닉스
        target_date = "2023-02-01" # 저점
    
    print(f"✅ 대상: {company_name} ({ticker}) | 기준일: {target_date}")

    # [핵심] 타임머신 프롬프트 정의
    time_machine_prompt = f"""
    [⚠️ 타임머신 가동 - 절대 준수 사항]
    1. 오늘은 {target_date}입니다. (과거가 아닙니다. 바로 '오늘'입니다!)
    2. 모든 대화와 분석은 반드시 '현재 시제'로만 작성하십시오. 
        - (X) "2021년 6월 당시는~", "그때는~"
        - (O) "현재~", "지금 우리 시장은~", "오늘 기준으로~"
    3. 당신은 {target_date} 이후의 역사를 전혀 모릅니다. 
    4. '당시'나 '그때'라는 단어 대신 '지금', '현재'라는 단어를 사용하십시오.
    5. 미래 지식을 활용한 분석은 '치팅'으로 간주됩니다. 당시 시점에서 가장 합리적인 판단을 하십시오.
    """

    # 2. 데이터 수집 (과거 툴 호출)
    f_data = get_historical_financial_summary(ticker, target_date)
    n_data = get_historical_news(ticker, target_date)
    c_data = get_historical_chart_indicators(ticker, target_date)

    agent_map = {
        "Chart": {"instance": chart_agent, "data": c_data, "name": "차트 분석가"},
        "News": {"instance": news_agent, "data": n_data, "name": "뉴스 분석가"},
        "Finance": {"instance": finance_agent, "data": f_data, "name": "재무 분석가"}
    }

    # [Step 1: 입론] 
    print(f"\n[Step 1: 입론] 각 전문가의 초기 분석")
    current_debate_history = f"[사회자]: {target_date} 시점의 분석을 시작합니다. 각 전문가는 입론해주세요.\n"

    for role_name in ["Chart", "News", "Finance"]:
        agent = agent_map[role_name]
        
        # 에이전트 파일로 가기 싫을 때 사용하는 핵심 로직:
        # 데이터 앞에 지침을 '포장'해서 전달합니다.
        injected_data = f"{time_machine_prompt}\n\n분석 대상 데이터:\n{agent['data']}"
        
        # 매개변수는 그대로 'data' 자리에 injected_data를 넣습니다.
        stmt = agent["instance"].analyze(company_name, ticker, injected_data)
        
        print(f"{agent['name']} 입론 완료")
        current_debate_history += f"\n[{agent['name']} 입론]: {stmt}"
    
    debate_rules = moderator.get_debate_rules()

    # [Step 2: 상호 토론]
    turn_count = 1
    max_turns = 10 # 시연용으로 적절히 조절

    while turn_count <= max_turns:
        await asyncio.sleep(2)
        print(f"\n🔄 [Turn {turn_count}/{max_turns}] 사회자 중재 중...")
        
        moderator_context = f"{time_machine_prompt}\n\n현재까지의 토론 기록:\n{current_debate_history}"

        mod_output = moderator.facilitate(company_name, moderator_context)
        
        # 파싱 로직
        status = re.search(r"STATUS:\s*\[?(TERMINATE|CONTINUE)\]?", mod_output)
        speaker = re.search(r"NEXT_SPEAKER:\s*\[?(\w+)\]?", mod_output)
        instruction = re.search(r"INSTRUCTION:\s*(.*)", mod_output, re.DOTALL)

        if status and "TERMINATE" in status.group(1): break

        if speaker and instruction:
            target_key_raw = speaker.group(1).strip()
            inst_text = instruction.group(1).strip()
            target_key = next((k for k in agent_map if k.lower() in target_key_raw.lower()), None)
            
            if target_key:
                target = agent_map[target_key]
                print(f"📢 {target['name']}에게 지시: {inst_text}")

                # 상호 토론 컨텍스트에도 타임머신 주입
                forced_context = (
                    f"{time_machine_prompt}\n" # 맨 위에 추가
                    f"{debate_rules}\n"
                    f"{current_debate_history}\n\n"
                    f"--- [사회자 지시] ---\n"
                    f"{inst_text}"
                )
                
                rebuttal = target["instance"].analyze(company_name, ticker, target["data"], debate_context=forced_context)
                current_debate_history += f"\n\n[사회자]: {inst_text}\n[{target['name']}]: {rebuttal}"
        
        turn_count += 1

    # [Step 3: 최종 판결 및 리포트]
    print(f"\n⚖️ Judge Agent 최종 판결 중...")
    final_decision = judge.adjudicate(company_name, f"{time_machine_prompt}\n{current_debate_history}")
    print(final_decision)

    print("📊 인사이트 리포트 생성 중...")
    report_agent = InsightReportAgent(llm)
    insight_report = report_agent.generate_report(company_name, ticker, current_debate_history)
    save_debate_log(company_name, ticker, insight_report)
    print("✅ 모든 과정이 완료되었습니다.")

if __name__ == "__main__":
    user_input = input("분석 종목 (카카오/SK하이닉스): ")
    asyncio.run(evaluate_postdata(user_input))