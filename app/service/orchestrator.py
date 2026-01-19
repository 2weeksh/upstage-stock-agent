import os
import re
from app.utils.llm import get_solar_model
from app.repository.chroma_db import get_vector_db

# 우리가 만든 서비스들 소환
from app.service.dart_collector import DartCollector
from app.service.news_collector import NewsCollector
from app.service.stock_ingestor import StockIngestor
# 차트 수집기는 API를 통해 category: chart로 저장하는 클래스라고 가정합니다.
from app.service.chart_collector import ChartCollector 
from app.service.finance_collector import FinanceCollector 
from app.utils.ticker_utils import get_clean_ticker, ticker_manager

# 유저님의 에이전트들 소환
from app.agents.moderator_agent import ModeratorAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.news_agent import NewsAgent
from app.agents.chart_agent import ChartAgent
from app.agents.ticker_agent import extract_company_name

class StockDebateOrchestrator:
    def __init__(self):
        self.llm = get_solar_model()
        self.dart_collector = DartCollector()
        self.news_collector = NewsCollector()
        self.chart_collector = ChartCollector()
        self.finance_collector = FinanceCollector()
        self.moderator = ModeratorAgent(self.llm)

    def _extract_ticker(self, user_query):
        """
        [Step 1] 사용자 질문에서 분석 대상을 확정합니다.
        1. LLM 에이전트가 질문에서 '종목명'이나 '티커'를 유연하게 추출합니다.
        2. TickerManager가 실제 상장 리스트와 대조하여 표준 티커(.KS/.KQ 등)로 정제합니다.
        """
        print("🔍 티커 에이전트: 분석 대상을 식별하고 검증 중입니다...")

        try:
            # 1. LLM에게 종목명/티커 추출 시키기 (예: "삼전" -> "삼성전자" 또는 "005930")
            raw_input = extract_company_name(user_query)
            
            if raw_input == "NONE":
                print("⚠️ 질문에서 종목을 찾을 수 없습니다.")
                return None, None

            # 2. TickerManager를 통해 표준 티커로 변환 (예: "삼성전자" -> "005930.KS")
            clean_ticker = get_clean_ticker(raw_input)
            
            # 3. 매핑 데이터에서 정식 기업명 가져오기 (없으면 입력값 사용)
            # ticker_manager._ticker_map에서 해당 심볼의 정식 이름을 역추적합니다.
            info = ticker_manager._ticker_map.get(clean_ticker.split('.')[0])
            company_name = raw_input # 기본값
            
            if info:
                # 역매핑을 통해 정식 명칭 확인 (예: "삼성전자")
                for name, data in ticker_manager._ticker_map.items():
                    if data['symbol'] == info['symbol'] and name != data['symbol']:
                        company_name = name
                        break

            print(f"✅ 분석 대상 확정: {company_name} ({clean_ticker})")
            return company_name, clean_ticker

        except ValueError as ve:
            print(f"❌ 종목 매핑 오류: {ve}")
            return None, None
        except Exception as e:
            print(f"❌ 티커 추출 중 예상치 못한 오류: {e}")
            return None, None

    def _prepare_knowledge_base(self, name, ticker):
        """
        [Step 2 & 3] 실시간 데이터를 수집하여 카테고리별로 벡터 DB를 구축합니다.
        DART는 숫자만, yfinance는 전체 티커를 사용하도록 분리합니다.
        """
        print(f"📦 {name}({ticker}) 지식 베이스 구축 시작...")
        
        # DART 전용 티커 (005930.ks -> 005930)
        # .이 있으면 앞부분만 취하고, 없으면 그대로 사용
        pure_ticker = ticker.split('.')[0]


        vector_db = get_vector_db(pure_ticker) # DB 폴더명은 숫자만 쓰는 것이 깔끔합니다.
        ingestor = StockIngestor(vector_db)

        # 1. DART (category: common) - 한 번만 주입
        dart_text, dart_title = self.dart_collector.get_latest_report_text(pure_ticker, name)
        ingestor.ingest_dart_data(pure_ticker, name, dart_text, dart_title)

        # 2. 뉴스 데이터 수집 및 저장 (category: news)
        news_docs = self.news_collector.fetch_news(pure_ticker, name)
        ingestor.ingest_news_data(pure_ticker, name, news_docs)

        # 3. 차트 데이터 수집 및 저장 (category: chart)
        chart_docs = self.chart_collector.fetch_technical_data(ticker, name)
        ingestor.ingest_chart_data(pure_ticker, name, chart_docs)
        
        # 4. 핵심 재무 지표 (category: finance)
        finance_docs = self.finance_collector.fetch_financial_summary(ticker, name)
        ingestor.ingest_finance_data(pure_ticker, name, finance_docs)
        
        return vector_db

    def run_full_process(self, user_query):
        """[Final Step] 전체 프로세스 실행 (입력 -> DB -> 토론)"""
        
        # 1. 티커 추출
        company_name, ticker = self._extract_ticker(user_query)
        
        if not ticker:
            return {"error": "분석할 종목을 식별하지 못했습니다. 질문을 다시 확인해주세요."}

        # 2. 실시간 데이터 수집 및 DB 업데이트 (RAG 준비)
        db = self._prepare_knowledge_base(company_name, ticker)
        
        # 3. 전문가 에이전트 초기화 (생성된 DB 주입)
        finance_agent = FinanceAgent("재무 분석가", "Finance", db)
        news_agent = NewsAgent("뉴스 분석가", "News", db)
        chart_agent = ChartAgent("차트 분석가", "Chart", db)
        
        agents = {"Finance": finance_agent, "News": news_agent, "Chart": chart_agent}
        history = ""

        # 4. [입론] 모든 에이전트 기조 발언
        print("🎤 토론 시작: 전문가 입론 단계입니다.")
        for name, agent in agents.items():
            speech = agent.analyze(company_name, ticker) # debate_context 없이 호출 = 입론
            history += f"\n{speech}\n"

        # 5. [토론 루프] 사회자가 주도하는 반박 토론
        for i in range(3): # 최대 3회전
            decision = self.moderator.facilitate(company_name, history)
            
            # 사회자의 STATUS 판단
            if "[TERMINATE]" in decision:
                print("🏁 사회자: 결론이 도달하여 토론을 종료합니다.")
                break
            
            # 다음 발언자 및 지시사항 파싱
            next_speaker = self._parse_field(decision, "NEXT_SPEAKER")
            instruction = self._parse_field(decision, "INSTRUCTION")
            
            print(f"👉 {next_speaker} 발언 차례 (지시: {instruction[:30]}...)")
            
            # 지목된 에이전트가 반박 수행
            speech = agents[next_speaker].analyze(
                company_name, ticker, 
                debate_context=f"사회자 지시: {instruction}\n이전 기록: {history}"
            )
            history += f"\n{speech}\n"

        # 6. [최종 요약 및 결론]
        print("📊 토론 마무리 및 요약 생성 중...")
        summary = self.moderator.summarize_debate(company_name, history)
        
        return {
            "company": company_name,
            "ticker": ticker,
            "summary": summary,
            "full_history": history
        }

    def _parse_field(self, text, field):
        """
        사회자 답변에서 특정 필드 추출 시 대괄호나 특수문자를 제거하여 KeyError를 방지합니다
        """
        # 필드명 뒤에 오는 내용을 가져오되, 대괄호([, ])나 공백을 무시하고 핵심 단어만 추출
        pattern = f"{field}:\\s*\\[?(\\w+)\\]?" 
        match = re.search(pattern, text)
        
        if match:
            value = match.group(1).strip()
            # 혹시 'News' 뒤에 ']'가 붙어있을 경우를 대비해 한 번 더 정제
            return value.replace("[", "").replace("]", "").strip()
        return ""