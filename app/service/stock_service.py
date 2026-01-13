import asyncio
import re
import json
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
        # ... 기존 __init__ 유지 ...
        self.shared_llm = get_solar_model()
        self.chart_agent = ChartAgent(self.shared_llm)
        self.news_agent = NewsAgent(self.shared_llm)
        self.finance_agent = FinanceAgent(self.shared_llm)
        self.moderator_agent = ModeratorAgent(self.shared_llm)

    # ❗ 함수 정의 변경: return 대신 yield를 사용하므로 비동기 제너레이터가 됩니다.
    async def handle_user_task(self, user_input: str, max_turns: int = 3):
        try:
            # [상태 전송 1]
            yield json.dumps({"type": "status", "message": f"'{user_input}' 종목 식별 및 데이터 수집 중..."}) + "\n"

            # 1. 전처리 및 티커 변환
            refined_name = extract_company_name(user_input)
            if refined_name == "NONE":
                yield json.dumps({"type": "error", "message": "종목을 찾을 수 없습니다."}) + "\n"
                return

            ticker = get_clean_ticker(refined_name)

            # 2. 기초 데이터 수집
            f_data = get_financial_summary(ticker)
            n_data = get_stock_news(ticker, refined_name)
            c_data = get_chart_indicators(ticker)

            # [상태 전송 2]
            yield json.dumps({"type": "status", "message": "각 분야 전문가들이 기초 데이터를 분석 중입니다..."}) + "\n"

            agent_map = {
                "Chart": {"instance": self.chart_agent, "data": c_data, "name": "차트 분석가"},
                "News": {"instance": self.news_agent, "data": n_data, "name": "뉴스 분석가"},
                "Finance": {"instance": self.finance_agent, "data": f_data, "name": "재무 분석가"}
            }

            # 3. [Round 1] 기조 발언
            loop = asyncio.get_event_loop()
            chart_init_task = loop.run_in_executor(None, self.chart_agent.analyze, refined_name, ticker, c_data)
            news_init_task = loop.run_in_executor(None, self.news_agent.analyze, refined_name, ticker, n_data)
            finance_init_task = loop.run_in_executor(None, self.finance_agent.analyze, refined_name, ticker, f_data)

            chart_init, news_init, finance_init = await asyncio.gather(chart_init_task, news_init_task,
                                                                       finance_init_task)

            full_history = f"[기조 발언]\n차트: {chart_init}\n\n뉴스: {news_init}\n\n재무: {finance_init}"
            current_history = full_history

            # 4. [Round 2] 토론 루프
            for turn in range(max_turns):
                # [상태 전송 3] 루프 돌 때마다 상태 업데이트
                yield json.dumps({"type": "status", "message": f"토론 {turn + 1}라운드: 사회자가 발언자를 선정 중입니다..."}) + "\n"

                instruction = await loop.run_in_executor(None, self.moderator_agent.facilitate, refined_name,
                                                         current_history)

                match = re.search(r"\[NEXT\]:\s*(\w+)", instruction)
                if not match: break

                target_key = match.group(1)
                if target_key in agent_map:
                    target = agent_map[target_key]

                    # [상태 전송 4] 누가 말하고 있는지 전송
                    yield json.dumps(
                        {"type": "status", "message": f"토론 {turn + 1}라운드: {target['name']}가 반박 의견을 작성 중입니다..."}) + "\n"

                    rebuttal = await loop.run_in_executor(
                        None, target["instance"].analyze,
                        refined_name, ticker, target["data"],
                        current_history + "\n\n" + instruction
                    )

                    new_entry = f"\n\n[사회자 지시]: {instruction}\n[{target['name']} 반박]: {rebuttal}"
                    full_history += new_entry
                    current_history = full_history
                else:
                    break

            # 5. [Final] 최종 요약
            yield json.dumps({"type": "status", "message": "최종 투자 전략 보고서를 작성 중입니다..."}) + "\n"

            final_conclusion = await loop.run_in_executor(None, self.moderator_agent.summarize, refined_name,
                                                          full_history)

            result_data = {
                "summary": f"{refined_name}({ticker}) 분석 리포트",
                "conclusion": final_conclusion,
                "discussion": full_history
            }

            # [최종 결과 전송]
            yield json.dumps({"type": "result", "data": result_data}) + "\n"

        except Exception as e:
            yield json.dumps({"type": "error", "message": str(e)}) + "\n"