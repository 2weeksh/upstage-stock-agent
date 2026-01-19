import json
import asyncio
import re
import functools
import traceback

# [유틸 및 매니저]
from app.agents.ticker_agent import extract_company_name
from app.utils.ticker_utils import get_clean_ticker
from app.utils.llm import get_solar_model

# [DB 및 인제스터]
from app.repository.chroma_db import get_vector_db
from app.service.stock_ingestor import StockIngestor

# [데이터 콜렉터]
from app.service.dart_collector import DartCollector
from app.service.news_collector import NewsCollector
from app.service.chart_collector import ChartCollector
from app.service.finance_collector import FinanceCollector

# [에이전트]
from app.agents.chart_agent import ChartAgent
from app.agents.news_agent import NewsAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.moderator_agent import ModeratorAgent
from app.agents.judge_agent import JudgeAgent
from app.agents.report_agent import InsightReportAgent

class StockService:
    def __init__(self):
        # 1. 공통 사용 LLM 초기화
        self.news_llm = get_solar_model(temperature=0.3)
        self.chart_llm = get_solar_model(temperature=0.1)
        self.finance_llm = get_solar_model(temperature=0.1)
        self.moderator_llm = get_solar_model(temperature=0.2)
        self.judge_llm = get_solar_model(temperature=0.1)
        self.report_llm = get_solar_model(temperature=0.2)

        # 2. 데이터 콜렉터 초기화
        self.dart_collector = DartCollector()
        self.news_collector = NewsCollector()
        self.chart_collector = ChartCollector()
        self.finance_collector = FinanceCollector()

        # 3. 상태와 무관한 공통 에이전트 초기화
        self.moderator_agent = ModeratorAgent(self.moderator_llm)
        self.judge_agent = JudgeAgent(self.judge_llm)
        self.report_agent = InsightReportAgent(self.report_llm)

    def _format_history_for_llm(self, history_list):
        text_log = ""
        for item in history_list:
            if item.get('message'):
                text_log += f"\n\n[{item['speaker']}]: {item['message']}"
        return text_log

    async def handle_user_task(self, user_input: str, max_turns: int = 10):
        try:
            # 메시지 생성 헬퍼 (프론트엔드 규격 유지)
            def create_msg(speaker, msg_type, message, data=None):
                return json.dumps({
                    "type": msg_type,
                    "speaker": speaker,
                    "message": message,
                    "data": data
                }) + "\n"

            loop = asyncio.get_event_loop()

            async def run_with_retry(func, *args, **kwargs):
                wrapped_func = functools.partial(func, *args, **kwargs)
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        return await loop.run_in_executor(None, wrapped_func)
                    except Exception as e:
                        if "429" in str(e) and attempt < max_retries - 1:
                            await asyncio.sleep(5 * (attempt + 1))
                            continue
                        raise e

            # ------------------------------------------------------------------
            # [Step 0] 종목 식별 및 DB 연결
            # ------------------------------------------------------------------
            yield create_msg("system", "status", "종목을 식별 중입니다...")
            refined_name = extract_company_name(user_input)
            if refined_name == "NONE":
                yield create_msg("system", "error", "종목을 찾을 수 없습니다.")
                return

            ticker = get_clean_ticker(refined_name)
            pure_ticker = ticker.split('.')[0] # 005930.KS -> 005930

            # 종목 전용 DB 및 인제스터 준비
            db = get_vector_db(pure_ticker)
            ingestor = StockIngestor(db)

            # ------------------------------------------------------------------
            # [Step 1] 데이터 수집 및 지식 베이스 주입
            # ------------------------------------------------------------------
            yield create_msg("system", "status", f"'{refined_name}'의 최신 데이터를 수집하여 지식 베이스를 갱신합니다.")

            # 병렬 데이터 수집
            d_task = loop.run_in_executor(None, self.dart_collector.get_latest_report_text, pure_ticker, refined_name)
            n_task = loop.run_in_executor(None, self.news_collector.fetch_news, pure_ticker, refined_name)
            c_task = loop.run_in_executor(None, self.chart_collector.fetch_technical_data, ticker, refined_name)
            f_task = loop.run_in_executor(None, self.finance_collector.fetch_financial_summary, ticker, refined_name)

            (dart_text, dart_title), n_docs, c_docs, f_docs = await asyncio.gather(d_task, n_task, c_task, f_task)

            # DB 주입 (DART는 보존, 나머지는 최신화)
            ingestor.ingest_dart_data(pure_ticker, refined_name, dart_text, dart_title)
            ingestor.ingest_news_data(pure_ticker, refined_name, n_docs)
            ingestor.ingest_chart_data(pure_ticker, refined_name, c_docs)
            ingestor.ingest_finance_data(pure_ticker, refined_name, f_docs)

            # ------------------------------------------------------------------
            # [Step 2] 에이전트 런타임 생성 (Retriever 주입)
            # ------------------------------------------------------------------
            # 이제 DB가 준비되었으므로 각 에이전트에게 db(retriever)를 전달하여 생성합니다.
            finance_agent = FinanceAgent("재무 분석가", "Finance", db)
            news_agent = NewsAgent("뉴스 분석가", "News", db)
            chart_agent = ChartAgent("차트 분석가", "Chart", db)

            agent_map = {
                "Finance": {"instance": finance_agent, "name": "재무 분석가", "code": "finance"},
                "News": {"instance": news_agent, "name": "뉴스 분석가", "code": "news"},
                "Chart": {"instance": chart_agent, "name": "차트 분석가", "code": "chart"}
            }

            discussion_log = []

            # ------------------------------------------------------------------
            # [Step 3] 전문가 기조 발언 (Opening)
            # ------------------------------------------------------------------
            yield create_msg("system", "status", "전문가들이 지식 베이스를 바탕으로 분석을 시작합니다.")

            async def run_agent_analyze(tag, agent_info):
                # 에이전트 내부에서 RAG 검색을 수행하므로 ticker 정보만 넘깁니다.
                res = await run_with_retry(agent_info["instance"].analyze, refined_name, pure_ticker, debug = True)
                return tag, res

            opening_tasks = [
                run_agent_analyze("Finance", agent_map["Finance"]),
                run_agent_analyze("News", agent_map["News"]),
                run_agent_analyze("Chart", agent_map["Chart"])
            ]

            for completed_task in asyncio.as_completed(opening_tasks):
                tag, stmt = await completed_task
                info = agent_map[tag]
                yield create_msg(info["code"], "debate", stmt)
                discussion_log.append({"speaker": info["name"], "code": info["code"], "message": stmt, "type": "opening"})

            # ------------------------------------------------------------------
            # [Step 4] 상호 토론 (Reasoning)
            # ------------------------------------------------------------------
            for turn in range(max_turns):
                yield create_msg("system", "status", f"상호 토론 진행 중 ({turn+1}/{max_turns})")

                current_context = self._format_history_for_llm(discussion_log)
                mod_output = await run_with_retry(self.moderator_agent.facilitate, refined_name, current_context)

                # 사회자 판단 파싱
                status_match = re.search(r"STATUS:\s*\[?(TERMINATE|CONTINUE)\]?", mod_output)
                speaker_match = re.search(r"NEXT_SPEAKER:\s*\[?(\w+)\]?", mod_output)
                instruction_match = re.search(r"INSTRUCTION:\s*(.*)", mod_output, re.DOTALL)

                if status_match and "TERMINATE" in status_match.group(1):
                    break

                if speaker_match and instruction_match:
                    target_key_raw = speaker_match.group(1).strip()
                    inst_text = instruction_match.group(1).strip()

                    yield create_msg("moderator", "debate", inst_text)
                    discussion_log.append({"speaker": "사회자", "code": "moderator", "message": inst_text, "type": "instruction"})

                    target_key = next((k for k in agent_map if k.lower() in target_key_raw.lower()), None)
                    if target_key:
                        target = agent_map[target_key]
                        rebuttal = await run_with_retry(
                            target["instance"].analyze, 
                            refined_name, pure_ticker, 
                            debate_context=f"[사회자 지시]: {inst_text}\n\n[이전 토론 맥락]: {current_context}"
                        )
                        yield create_msg(target["code"], "debate", rebuttal)
                        discussion_log.append({"speaker": target["name"], "code": target["code"], "message": rebuttal, "type": "rebuttal"})

            # ------------------------------------------------------------------
            # [Step 5] 요약 및 판결 (Finalize)
            # ------------------------------------------------------------------
            yield create_msg("system", "status", "토론을 요약하고 최종 리포트를 생성합니다.")
            
            final_context = self._format_history_for_llm(discussion_log)
            
            # 1. 사회자 요약
            summary = await run_with_retry(self.moderator_agent.summarize_debate, refined_name, final_context)
            yield create_msg("moderator", "debate", summary)
            
            # 2. 판사 최종 판결
            decision = await run_with_retry(self.judge_agent.adjudicate, refined_name, final_context)
            
            # 3. 리포트 생성
            report = await run_with_retry(self.report_agent.generate_report, refined_name, pure_ticker, final_context)

            # [최종 결과 전송]
            result_data = {
                "summary": report,
                "conclusion": decision,
                "discussion_log": discussion_log
            }
            yield create_msg("system", "result", "토론이 완료되었습니다.", data=result_data)

        except Exception as e:
            traceback.print_exc()
            yield create_msg("system", "error", f"분석 중 오류 발생: {str(e)}")






'''
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
        self.news_llm = get_solar_model(temperature=0.3)
        self.chart_llm = get_solar_model(temperature=0.1)
        self.finance_llm = get_solar_model(temperature=0.1)
        self.moderator_llm = get_solar_model(temperature=0.2)
        self.judge_llm = get_solar_model(temperature=0.1)
        self.report_llm = get_solar_model(temperature=0.2)

        self.chart_agent = ChartAgent(self.chart_llm)
        self.news_agent = NewsAgent(self.news_llm)
        self.finance_agent = FinanceAgent(self.finance_llm)
        self.moderator_agent = ModeratorAgent(self.moderator_llm)
        self.judge_agent = JudgeAgent(self.judge_llm)
        self.report_agent = InsightReportAgent(self.report_llm)

    # [헬퍼] 리스트 -> 텍스트 변환
    def _format_history_for_llm(self, history_list):
        text_log = ""
        for item in history_list:
            text_log += f"\n\n[{item['speaker']}]: {item['message']}"
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
                                    f"⚠️ API 호출 제한(429) 감지. {wait_time}초 대기 후 재시도합니다. ({attempt + 1}/{max_retries})")
                                await asyncio.sleep(wait_time)
                                continue
                        raise e

            # ------------------------------------------------------------------
            # [Step 0] 데이터 수집
            # ------------------------------------------------------------------
            yield create_msg("system", "status", f"시스템이 '{user_input}' 에서 종목을 식별 중입니다.")

            refined_name = extract_company_name(user_input)
            if refined_name == "NONE":
                yield create_msg("system", "error", "종목을 찾을 수 없습니다.")
                return

            ticker = get_clean_ticker(refined_name)
            yield create_msg("system", "status", f"대상 종목: {refined_name} ({ticker})")
            yield create_msg("system", "status", "3대 데이터(재무, 뉴스, 차트)를 수집 중입니다.")

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


            for turn in range(max_turns):
                turn_count = turn + 1
                yield create_msg("system", "status", f"상호 토론 {turn_count}/{max_turns} 라운드")

                # [추가 부분] 7라운드 이상 시 사회자의 Temperature를 낮춰 수렴 유도
                if turn_count >= 7:
                    self.moderator_agent.llm = self.moderator_llm.bind(temperature=0.1)

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
                yield create_msg("system", "status", f"{agent['name']} 최후 변론 중")

                closing_context_prompt = f"""
                {current_context}
                --- [SYSTEM INSTRUCTION] ---
                지금까지의 토론 흐름을 참고하여, '최후 변론'을 하십시오.
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


            yield create_msg("system", "status", "사회자가 토론을 요약 중입니다.")
            current_context = self._format_history_for_llm(discussion_log)
            summary_text = await run_with_retry(self.moderator_agent.summarize_debate, refined_name, current_context)
            yield create_msg("moderator", "debate", summary_text)
            discussion_log.append({
                "speaker": "사회자",
                "code": "moderator",
                "message": summary_text,
                "type": "summary"
            })
            final_context = self._format_history_for_llm(discussion_log)

            # ------------------------------------------------------------------
            # [Step 5, 6] 요약/판결/리포트 (여기는 discussion_log에 안 넣음)
            # ------------------------------------------------------------------

            yield create_msg("system", "status", "전략가가 최종 판결을 내리고 있습니다.")
            # final_context에는 이제 사회자의 요약까지 포함되어 있습니다.
            final_decision = await run_with_retry(self.judge_agent.adjudicate, refined_name, final_context)

            yield create_msg("system", "status", "최종 리포트를 생성 중입니다.")
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
'''