import json
import asyncio
import re
import functools
import time
from app.agents.ticker_agent import extract_company_name
from app.utils.ticker_utils import get_clean_ticker

# [에이전트]
from app.agents.chart_agent import ChartAgent
from app.agents.news_agent import NewsAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.moderator_agent import ModeratorAgent
from app.agents.judge_agent import JudgeAgent
from app.agents.report_agent import InsightReportAgent

# [툴]
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
        self.judge_agent = JudgeAgent(self.shared_llm)
        self.report_agent = InsightReportAgent(self.shared_llm)

    # [헬퍼] 리스트 -> 텍스트 변환
    def _format_history_for_llm(self, history_list):
        text_log = ""
        for item in history_list:
            text_log += f"[{item['speaker']}]: {item['message']}\n\n"
        return text_log

    async def handle_user_task(self, user_input: str, max_turns: int = 10):
        try:
            # 1. 메시지 생성 헬퍼
            def create_msg(speaker, msg_type, message, data=None):
                return json.dumps({
                    "type": msg_type,
                    "speaker": speaker,
                    "message": message,
                    "data": data
                }) + "\n"

            loop = asyncio.get_event_loop()

            # [핵심] 재시도(Retry) 래퍼 함수
            async def run_with_retry(func, *args, **kwargs):
                # functools.partial로 함수와 인자를 포장
                wrapped_func = functools.partial(func, *args, **kwargs)

                max_retries = 5  # 재시도 횟수 증가
                for attempt in range(max_retries):
                    try:
                        # 실행
                        return await loop.run_in_executor(None, wrapped_func)
                    except Exception as e:
                        error_str = str(e)
                        # 429 (Too Many Requests) 에러 감지 시 대기 후 재시도
                        if "429" in error_str or "too_many_requests" in error_str:
                            if attempt < max_retries - 1:
                                wait_time = 5 * (attempt + 1)
                                print(
                                    f"⚠️ API 호출 제한(429) 감지. {wait_time}초 대기 후 재시도합니다... ({attempt + 1}/{max_retries})")
                                await asyncio.sleep(wait_time)
                                continue
                        raise e

            # ------------------------------------------------------------------
            # [Step 0] 데이터 수집
            # ------------------------------------------------------------------
            yield create_msg("system", "status", f"시스템이 '{user_input}' 에서 종목을 식별 중입니다...")

            refined_name = extract_company_name(user_input)
            if refined_name == "NONE":
                yield create_msg("system", "error", "종목을 찾을 수 없습니다.")
                return

            ticker = get_clean_ticker(refined_name)
            yield create_msg("system", "status", f"대상 종목: {refined_name} ({ticker})")
            yield create_msg("system", "status", "3대 데이터(재무, 뉴스, 차트)를 수집 중입니다...")

            f_task = loop.run_in_executor(None, get_financial_summary, ticker)
            n_task = loop.run_in_executor(None, get_stock_news, ticker, refined_name)
            c_task = loop.run_in_executor(None, get_chart_indicators, ticker)

            f_data, n_data, c_data = await asyncio.gather(f_task, n_task, c_task)

            agent_map = {
                "Chart": {"instance": self.chart_agent, "data": c_data, "name": "차트 분석가", "code": "chart"},
                "News": {"instance": self.news_agent, "data": n_data, "name": "뉴스 분석가", "code": "news"},
                "Finance": {"instance": self.finance_agent, "data": f_data, "name": "재무 분석가", "code": "finance"}
            }

            discussion_log = []

            # ------------------------------------------------------------------
            # [Step 1] 기조 발언 (Opening Statements)
            # ------------------------------------------------------------------

            opening_log = {
                "speaker": "사회자", "code": "moderator",
                "message": "지금부터 토론을 시작합니다. 각 전문가는 분석 결과를 발표해주세요.",
                "type": "opening"
            }
            discussion_log.append(opening_log)

            async def run_analyze_parallel(tag, agent_info, *args):
                res = await run_with_retry(agent_info["instance"].analyze, *args)
                return tag, res

            tasks = [
                run_analyze_parallel("Chart", agent_map["Chart"], refined_name, ticker, c_data),
                run_analyze_parallel("News", agent_map["News"], refined_name, ticker, n_data),
                run_analyze_parallel("Finance", agent_map["Finance"], refined_name, ticker, f_data)
            ]

            for completed_task in asyncio.as_completed(tasks):
                tag, stmt = await completed_task
                agent_info = agent_map[tag]

                # [알림] 에이전트 직접 알림
                if tag == "Chart":
                    yield create_msg("chart", "status", "기술적 지표 분석 완료. 추세를 확인했습니다.")
                elif tag == "News":
                    yield create_msg("news", "status", "시장 심리 및 뉴스 분석 완료. 트렌드를 파악했습니다.")
                elif tag == "Finance":
                    yield create_msg("finance", "status", "기업 가치 및 재무 건전성 평가를 마쳤습니다.")

                yield create_msg(agent_info["code"], "debate", stmt)

                # 로그 저장
                discussion_log.append({
                    "speaker": agent_info["name"],
                    "code": agent_info["code"],
                    "message": stmt,
                    "type": "opening"
                })

            await asyncio.sleep(2)

            # ------------------------------------------------------------------
            # [Step 2] 상호 토론 (Reasoning)
            # ------------------------------------------------------------------
            yield create_msg("system", "status", "분석 내용을 바탕으로 상호 토론을 시작합니다.")

            debate_rules = await loop.run_in_executor(None, self.moderator_agent.get_debate_rules)

            for turn in range(max_turns):
                yield create_msg("system", "status", f"상호 토론 {turn + 1}/{max_turns} 라운드...")

                current_context = self._format_history_for_llm(discussion_log)
                mod_output = await run_with_retry(
                    self.moderator_agent.facilitate, refined_name, current_context
                )

                status_match = re.search(r"STATUS:\s*\[?(TERMINATE|CONTINUE)\]?", mod_output)
                speaker_match = re.search(r"NEXT_SPEAKER:\s*\[?(\w+)\]?", mod_output)
                instruction_match = re.search(r"INSTRUCTION:\s*(.*)", mod_output, re.DOTALL)

                if status_match and "TERMINATE" in status_match.group(1):
                    yield create_msg("system", "status", "사회자가 토론 종료를 선언했습니다.")
                    break

                if speaker_match and instruction_match:
                    target_key_raw = speaker_match.group(1).strip()
                    inst_text = instruction_match.group(1).strip()

                    yield create_msg("moderator", "debate", inst_text)
                    discussion_log.append(
                        {"speaker": "사회자", "code": "moderator", "message": inst_text, "type": "instruction"})

                    target_key = next((k for k in agent_map if k.lower() in target_key_raw.lower()), None)

                    if target_key:
                        target = agent_map[target_key]

                        yield create_msg(target['code'], "status", f"{target['name']}가 반박 의견을 제시합니다.")

                        forced_context = (
                            f"{current_context}\n\n"
                            f"--- [SYSTEM ALERT] ---\n"
                            f"규칙 준수 필수:\n{debate_rules}\n"
                            f"----------------------\n"
                            f"[사회자 지시]: {inst_text}"
                        )

                        rebuttal = await run_with_retry(
                            target["instance"].analyze,
                            refined_name, ticker, target["data"],
                            debate_context=forced_context
                        )

                        yield create_msg(target["code"], "debate", rebuttal)
                        discussion_log.append({"speaker": target["name"], "code": target["code"], "message": rebuttal,
                                               "type": "rebuttal"})

                        await asyncio.sleep(2)

            # ------------------------------------------------------------------
            # [Step 3] 최후 변론 (Closing)
            # ------------------------------------------------------------------
            yield create_msg("system", "status", "최후 변론을 진행합니다.")

            closing_msg = {"speaker": "사회자", "code": "moderator", "message": "토론을 마치겠습니다. 최후 변론을 해주세요.",
                           "type": "closing"}
            discussion_log.append(closing_msg)

            current_context = self._format_history_for_llm(discussion_log)

            for role_name in ["Chart", "News", "Finance"]:
                agent = agent_map[role_name]
                yield create_msg("system", "status", f"{agent['name']} 최후 변론 중...")

                closing_context_prompt = f"""
                {current_context}
                --- [SYSTEM INSTRUCTION] ---
                지금까지의 토론 흐름을 참고하여, 
                당신의 최종 투자의견(매수/매도/보류)을 투자자들에게 설득력 있게 전달하는 '최후 변론'을 하십시오.
                """

                closing_stmt = await run_with_retry(
                    agent["instance"].analyze,
                    refined_name, ticker, agent["data"],
                    debate_context=closing_context_prompt
                )

                yield create_msg(agent["code"], "debate", closing_stmt)
                discussion_log.append(
                    {"speaker": agent["name"], "code": agent["code"], "message": closing_stmt, "type": "closing"})

                await asyncio.sleep(2)

            # ------------------------------------------------------------------
            # [Step 4, 5, 6] 요약/판결/리포트 (여기는 discussion_log에 안 넣음)
            # ------------------------------------------------------------------
            yield create_msg("system", "status", "사회자가 토론을 요약 중입니다...")
            final_context = self._format_history_for_llm(discussion_log)
            await run_with_retry(self.moderator_agent.summarize_debate, refined_name, final_context)

            yield create_msg("system", "status", "재판관(Judge)이 최종 판결을 내리고 있습니다...")
            final_decision = await run_with_retry(self.judge_agent.adjudicate, refined_name, final_context)

            yield create_msg("system", "status", "최종 리포트를 생성 중입니다...")
            insight_report = await run_with_retry(self.report_agent.generate_report, refined_name, ticker,
                                                  final_context)

            # ------------------------------------------------------------------
            # [Step 7] 결과 반환 (프론트엔드용 데이터 구조)
            # ------------------------------------------------------------------
            result_data = {
                "summary": insight_report,  # 리포트 (HTML/MD)
                "conclusion": final_decision,  # 판결문
                "discussion_log": discussion_log  # [중요] 버튼으로 돌려볼 대화 리스트
            }

            yield create_msg("system", "result", "완료", data=result_data)

        except Exception as e:
            import traceback
            traceback.print_exc()
            yield create_msg("system", "error", f"시스템 오류: {str(e)}")