import json
import asyncio
import re
# langchain 메시지 관련 import 제거 (더 이상 안 씀)
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
        self.shared_llm = get_solar_model()
        self.chart_agent = ChartAgent(self.shared_llm)
        self.news_agent = NewsAgent(self.shared_llm)
        self.finance_agent = FinanceAgent(self.shared_llm)
        self.moderator_agent = ModeratorAgent(self.shared_llm)

    async def handle_user_task(self, user_input: str, max_turns: int = 3):
        try:
            # 헬퍼 함수
            def create_msg(speaker, msg_type, message, data=None):
                return json.dumps({
                    "type": msg_type,
                    "speaker": speaker,
                    "message": message,
                    "data": data
                }) + "\n"

            loop = asyncio.get_event_loop()

            # 1. [System] 시작
            yield create_msg("system", "status", f"시스템이 '{user_input}' 에서 종목을 식별하고 있습니다...")

            refined_name = extract_company_name(user_input)
            if refined_name == "NONE":
                yield create_msg("system", "error", "종목을 찾을 수 없습니다.")
                return

            ticker = get_clean_ticker(refined_name)

            # ------------------------------------------------------------------
            # [수정됨] 이름 변환 로직 제거 -> 고정 텍스트 사용
            # ------------------------------------------------------------------

            # 여기서 복잡하게 이름 만들지 말고, 그냥 '대상 종목'이라고 고정 멘트 날림
            yield create_msg("system", "status", "대상 종목의 3대 데이터 수집 및 초기 분석을 통합 진행합니다...")

            # 1) 데이터 수집
            # 검색 도구에는 refined_name(원래 추출한 이름)을 넘겨줌
            f_task = loop.run_in_executor(None, get_financial_summary, ticker)
            n_task = loop.run_in_executor(None, get_stock_news, ticker, refined_name)
            c_task = loop.run_in_executor(None, get_chart_indicators, ticker)

            f_data, n_data, c_data = await asyncio.gather(f_task, n_task, c_task)

            # 2) 에이전트 분석
            agent_map = {
                "Chart": {"instance": self.chart_agent, "data": c_data, "name": "차트 분석가", "code": "chart"},
                "News": {"instance": self.news_agent, "data": n_data, "name": "뉴스 분석가", "code": "news"},
                "Finance": {"instance": self.finance_agent, "data": f_data, "name": "재무 분석가", "code": "finance"}
            }

            async def run_analysis_task(tag, agent, *args):
                result = await loop.run_in_executor(None, agent.analyze, *args)
                return tag, result

            # 에이전트한테는 refined_name (추출된 이름) 그대로 전달
            tasks = [
                run_analysis_task("Chart", self.chart_agent, refined_name, ticker, c_data),
                run_analysis_task("News", self.news_agent, refined_name, ticker, n_data),
                run_analysis_task("Finance", self.finance_agent, refined_name, ticker, f_data)
            ]

            results = {}

            for completed_task in asyncio.as_completed(tasks):
                tag, result = await completed_task
                results[tag] = result

                if tag == "Chart":
                    yield create_msg("chart", "status", "기술적 지표 분석 완료. 추세를 확인했습니다.")
                elif tag == "News":
                    yield create_msg("news", "status", "시장 심리 및 뉴스 분석 완료. 트렌드를 파악했습니다.")
                elif tag == "Finance":
                    yield create_msg("finance", "status", "기업 가치 및 재무 건전성 평가를 마쳤습니다.")

            chart_init = results["Chart"]
            news_init = results["News"]
            finance_init = results["Finance"]

            full_history = f"[기조 발언]\n차트: {chart_init}\n\n뉴스: {news_init}\n\n재무: {finance_init}"
            current_history = full_history

            # ------------------------------------------------------------------
            # [단계 2] 전문가 토론
            # ------------------------------------------------------------------

            yield create_msg("system", "status", "모든 초기 분석 완료. 본격적인 전문가 토론을 시작합니다.")

            for turn in range(max_turns):
                yield create_msg("system", "status", f"토론 {turn + 1}라운드: 사회자가 발언자를 선정 중입니다...")

                # 여기도 refined_name 사용
                instruction = await loop.run_in_executor(None, self.moderator_agent.facilitate, refined_name,
                                                         current_history)

                match = re.search(r"\[NEXT\]:\s*(\w+)", instruction)
                if not match: break

                target_key = match.group(1)
                if target_key in agent_map:
                    target = agent_map[target_key]

                    yield create_msg(target['code'], "status", f"{target['name']}가 반박 의견을 제시합니다.")

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

            # ------------------------------------------------------------------
            # [단계 3] 최종 결과
            # ------------------------------------------------------------------

            yield create_msg("system", "status", "사회자가 최종 투자 리포트를 작성 중입니다...")

            final_conclusion = await loop.run_in_executor(None, self.moderator_agent.summarize, refined_name,
                                                          full_history)

            result_data = {
                # 제목도 깔끔하게 추출된 이름 그대로 사용
                "summary": f"{refined_name} 분석 리포트",
                "conclusion": final_conclusion,
                "discussion": full_history
            }

            yield create_msg("system", "result", "완료", data=result_data)

        except Exception as e:
            import traceback
            traceback.print_exc()
            yield create_msg("system", "error", str(e))