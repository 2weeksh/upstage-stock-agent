import asyncio
import re
import os
from dotenv import load_dotenv
from collections import Counter

# 사용자님의 기존 에이전트 및 유틸 임포트
from app.utils.llm import get_solar_model
from app.agents.ticker_agent import extract_company_name
from app.utils.ticker_utils import get_clean_ticker
from app.agents.chart_agent import ChartAgent
from app.agents.news_agent import NewsAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.moderator_agent import ModeratorAgent
from app.agents.judge_agent import JudgeAgent


# 우리가 만든 과거 데이터 툴들
from evaluate.post_finance_tool import get_historical_financial_summary
from evaluate.post_search_tool import get_historical_news
from evaluate.post_char_tool import get_historical_chart_indicators

load_dotenv()

async def run_multiple_evaluations(user_query: str, count: int = 10):
    all_scores = []
    all_labels = []
    
    print(f"\n📊 {user_query} 종목에 대해 {count}회 자동 테스트를 시작합니다.")
    print("="*60)

    for i in range(1, count + 1):
        print(f"\n🔄 [{i}/{count}] 번째 시뮬레이션 가동 중...")
        
        # 1. 시뮬레이션 실행
        decision = await evaluate_postdata(user_query)
        
        # --- [마지막 승부] 모든 케이스 대응 추출 로직 ---
        
        # 1. 텍스트 하단부만 타겟팅 (기준표 무시)
        # "등급 선정 근거" 이후의 텍스트만 봅니다.
        target_text = decision.split("등급 선정 근거")[-1] if "등급 선정 근거" in decision else decision

        # 2. 점수 추출 (점수 뒤의 별표나 공백을 무시하고 숫자만 낚아챔)
        # 패턴: '점수'라는 단어 뒤에 나오는 첫 번째 숫자(소수점 포함)를 찾음
        score_match = re.search(r"점수.*?\s*[:：]\s*(?:\*\*)?(\d+(?:\.\d+)?)", target_text)
        score = float(score_match.group(1)) if score_match else 0.0

        # 3. 등급 추출 (대괄호 유무 상관없이 추출)
        label_match = re.search(r"등급.*?\s*[:：]\s*(?:\*\*)?\[?([\w\s]+)\]?", target_text)
        label = label_match.group(1).strip() if label_match else "추출 실패"
        
        # 불필요한 별표나 공백 제거
        label = label.replace("*", "").strip()
        
        # 등급 이름에 포함된 불필요한 공백이나 특수문자 제거
        label = label.replace("[", "").replace("]", "").strip()
        
        all_scores.append(score)
        all_labels.append(label)
        
        print(f"✅ {i}회차 결과: {label} ({score}점)")
        # API 부하 방지
        await asyncio.sleep(1)

    # 3. 전체 통계 계산
    print("\n" + "="*60)
    print(f"📈 최종 통계 리포트 ({user_query})")
    print("-" * 60)
    
    if all_scores:
        avg_score = sum(all_scores) / len(all_scores)
        print(f"📍 평균 점수: {avg_score:.2f} / 10.0")
        print(f"📍 최고/최저: {max(all_scores):.1f} / {min(all_scores):.1f}")
    
    if all_labels:
        stats = Counter(all_labels)
        print(f"📍 등급 분포:")
        # 사용자님이 정의한 순서대로 출력
        for rank in ["강력 매수", "매수", "중립", "매도", "강력 매도"]:
            if rank in stats:
                num = stats[rank]
                print(f" - [{rank}]: {num}회 ({(num/count)*100:.1f}%)")
    
    print("="*60)

async def evaluate_postdata(user_query: str):
    # 0. 초기화
    llm = get_solar_model()
    chart_agent = ChartAgent(llm)
    news_agent = NewsAgent(llm)
    finance_agent = FinanceAgent(llm)
    moderator = ModeratorAgent(llm)
    judge = JudgeAgent(llm)

    # 1. 대상 및 시점 설정
    company_name = extract_company_name(user_query)
    ticker = get_clean_ticker(company_name)
    
    if ticker == "035720.KS": # 카카오
        chart_date = "2021-06-23" 
        target_date = "2021-06-24" 
    else: # SK 하이닉스
        chart_date = "2023-01-31" 
        target_date = "2023-02-01" 
    
    # [핵심] 타임머신 프롬프트
    time_machine_prompt = f"""
    [⚠️ 타임머신 가동 - 절대 준수 사항]
    1. 오늘은 {target_date}입니다.
    2. 모든 분석은 반드시 '현재 시제'로만 작성하십시오.
    3. 당신은 {target_date} 이후의 미래를 전혀 모릅니다.
    """

    # 2. 데이터 수집
    f_data = get_historical_financial_summary(ticker, target_date)
    n_data = get_historical_news(ticker, target_date)
    c_data = get_historical_chart_indicators(ticker, chart_date)

    agent_map = {
        "Chart": {"instance": chart_agent, "data": c_data, "name": "차트 분석가"},
        "News": {"instance": news_agent, "data": n_data, "name": "뉴스 분석가"},
        "Finance": {"instance": finance_agent, "data": f_data, "name": "재무 분석가"}
    }

    # [에러 방지] ModeratorAgent에 get_debate_rules가 없을 경우 대비
    try:
        debate_rules = moderator.get_debate_rules()
    except AttributeError:
        debate_rules = "상대방의 논리적 허점을 데이터 기반으로 비판하십시오."

    # [Step 1: 입론]
    current_debate_history = f"[사회자]: {target_date} 시점의 분석을 시작합니다.\n"
    for role_name in ["Chart", "News", "Finance"]:
        agent = agent_map[role_name]
        injected_data = f"{time_machine_prompt}\n\n데이터:\n{agent['data']}"
        stmt = agent["instance"].analyze(company_name, ticker, injected_data)
        current_debate_history += f"\n[{agent['name']} 입론]: {stmt}"
    
    # [Step 2: 상호 토론]
    turn_count = 1
    max_turns = 5 # 10번 테스트를 위해 토론 횟수는 짧게 조절
    while turn_count <= max_turns:
        moderator_context = f"{time_machine_prompt}\n\n역사:\n{current_debate_history}"
        mod_output = moderator.facilitate(company_name, moderator_context)
        
        status = re.search(r"STATUS:\s*\[?(TERMINATE|CONTINUE)\]?", mod_output)
        speaker = re.search(r"NEXT_SPEAKER:\s*\[?(\w+)\]?", mod_output)
        instruction = re.search(r"INSTRUCTION:\s*(.*)", mod_output, re.DOTALL)

        if status and "TERMINATE" in status.group(1): break
        if speaker and instruction:
            target_key = next((k for k in agent_map if k.lower() in speaker.group(1).lower()), None)
            if target_key:
                target = agent_map[target_key]
                forced_context = f"{time_machine_prompt}\n{debate_rules}\n{current_debate_history}\n지시: {instruction.group(1)}"
                rebuttal = target["instance"].analyze(company_name, ticker, target["data"], debate_context=forced_context)
                current_debate_history += f"\n\n[사회자 지시]: {instruction.group(1)}\n[{target['name']}]: {rebuttal}"
        turn_count += 1

    # [Step 3: 최종 판결]
    final_decision = judge.adjudicate(company_name, f"{time_machine_prompt}\n{current_debate_history}")
    print(final_decision)
    return final_decision

if __name__ == "__main__":
    user_input = input("분석 종목 (카카오/SK하이닉스): ")
    asyncio.run(run_multiple_evaluations(user_input, 10))