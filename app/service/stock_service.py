import asyncio
import re
from app.agents.ticker_agent import extract_company_name
from app.utils.ticker_utils import get_clean_ticker
from app.agents.chart_agent import ChartAgent
from app.agents.news_agent import NewsAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.moderator_agent import ModeratorAgent
from app.tools.chart_tools import get_chart_indicators
from app.tools.search_tools import get_stock_news
from app.tools.finance_tools import get_financial_summary
from app.utils.llm import get_solar_model


class StockService:
    def __init__(self):
        shared_llm = get_solar_model()
        # 에이전트들을 부품처럼 초기화
        self.chart_agent = ChartAgent(shared_llm)
        self.news_agent = NewsAgent(shared_llm)
        self.finance_agent = FinanceAgent(shared_llm)
        self.moderator_agent = ModeratorAgent(shared_llm)

    async def handle_user_task(self, user_input: str, max_turns: int = 3):
        try:
            # 1. 전처리 및 티커 변환
            refined_name = extract_company_name(user_input)
            if refined_name == "NONE":
                return {"summary": "인식 실패", "conclusion": "종목을 찾을 수 없습니다.", "discussion": ""}
            ticker = get_clean_ticker(refined_name)

            # 2. 기초 데이터 수집
            f_data = get_financial_summary(ticker)
            n_data = get_stock_news(ticker, refined_name)
            c_data = get_chart_indicators(ticker)

            # 에이전트 매핑 (테스트 코드의 agent_map 전략)
            agent_map = {
                "Chart": {"instance": self.chart_agent, "data": c_data, "name": "차트 분석가"},
                "News": {"instance": self.news_agent, "data": n_data, "name": "뉴스 분석가"},
                "Finance": {"instance": self.finance_agent, "data": f_data, "name": "재무 분석가"}
            }

            # 3. [Round 1] 기조 발언 (병렬 실행으로 속도 향상)
            loop = asyncio.get_event_loop()
            chart_init_task = loop.run_in_executor(None, self.chart_agent.analyze, refined_name, ticker, c_data)
            news_init_task = loop.run_in_executor(None, self.news_agent.analyze, refined_name, ticker, n_data)
            finance_init_task = loop.run_in_executor(None, self.finance_agent.analyze, refined_name, ticker, f_data)

            chart_init, news_init, finance_init = await asyncio.gather(chart_init_task, news_init_task,
                                                                       finance_init_task)

            # 토론 히스토리 시작
            full_history = f"[기조 발언]\n차트: {chart_init}\n\n뉴스: {news_init}\n\n재무: {finance_init}"
            current_history = full_history

            # 4. [Round 2] 재귀적 토론 루프 (Ping-Pong)
            for turn in range(max_turns):
                # 사회자의 발언권 분배
                instruction = await loop.run_in_executor(None, self.moderator_agent.facilitate, refined_name,
                                                         current_history)

                # [NEXT] 태그 추출
                match = re.search(r"\[NEXT\]:\s*(\w+)", instruction)
                if not match: break  # 사회자가 종료하면 루프 탈출

                target_key = match.group(1)
                if target_key in agent_map:
                    target = agent_map[target_key]
                    # 지목된 에이전트의 반박 (debate_context 전달)
                    rebuttal = await loop.run_in_executor(
                        None, target["instance"].analyze,
                        refined_name, ticker, target["data"],
                        current_history + "\n\n" + instruction
                    )

                    # 히스토리 업데이트
                    new_entry = f"\n\n[사회자 지시]: {instruction}\n[{target['name']} 반박]: {rebuttal}"
                    full_history += new_entry
                    current_history = full_history  # 다음 턴의 맥락으로 설정
                else:
                    break

            # 5. [Final] 최종 요약
            final_conclusion = await loop.run_in_executor(None, self.moderator_agent.summarize, refined_name,
                                                        full_history)

            return {
                "summary": f"{refined_name}({ticker}) 분석 리포트",
                "conclusion": final_conclusion,
                "discussion": full_history
            }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"summary": "분석 오류", "conclusion": f"오류 발생: {str(e)}", "discussion": ""}