# app/service/stock_ingestor.py

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

class StockIngestor:
    def __init__(self, vector_db):
        """
        vector_db: 이미 초기화된 ChromaDB 등의 리트리버 객체
        """
        self.vector_db = vector_db
        # 텍스트를 적절한 크기(약 1000자)로 쪼개는 설정
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150, # 문맥 연결을 위해 앞뒤 150자 정도 겹치게 함
            length_function=len,
        )

    def is_category_ingested(self, category:str):
        """해당 카테고리의 데이터가 이미 컬렉션에 존재하는지 확인"""
        # 간단하게 데이터 개수가 0보다 큰지 확인합니다.
        res = self.vector_db.get(where={"category": category})
        return len(res['ids']) > 0

    def _clear_category(self, ticker, category):
        """특정 티커의 특정 카테고리 데이터만 삭제 (뉴스/차트/재무 갱신용)"""
        try:
            self.vector_db.delete(where={
                "$and": [
                    {"ticker": {"$eq": ticker}},
                    {"category": {"$eq": category}}
                ]
            })
        except Exception:
            pass

    def ingest_dart_data(self, ticker, company_name, text, report_title):
        """
        [지속성 데이터] DART 보고서는 'common' 카테고리로 저장하며,
        이미 존재하면 추가 수집하지 않고 보존합니다.
        """

        # 이미 DRAT 보고서가 있다면 건너뜁니다.
        if self.is_category_ingested(category="common"):
            print(f"⚠️ {company_name}({ticker}) DART 데이터가 이미 존재하여 수집을 건너뜁니다.")
            return


        print(f"📦 {company_name}({ticker}) 지식 베이스 구축 시작 (Upsert, 중복 제거)")

        # 1. 메타데이터와 함께 Document 객체 생성
        # 'category': 'common' 태그를 붙여 모든 에이전트가 공유하게 합니다.
        doc = Document(
            page_content=text,
            metadata={
                "ticker": ticker,
                "company": company_name,
                "source": "DART",
                "category": "common",
                "report_title": report_title
            }
        )

        # 2. 텍스트 분할 (Chunking)
        all_split_docs = self.text_splitter.split_documents([doc])

        # 중복 내용 제거 로직 (set 사용)
        seen_contents = set()
        unique_docs = []
        for d in all_split_docs:
            # 공백을 제거한 텍스트를 기준으로 중복 체크
            clean_content = d.page_content.strip()
            if d.page_content not in seen_contents:
                unique_docs.append(d)
                seen_contents.add(clean_content)

        print(f"✂️ 전체 {len(all_split_docs)}개 조각 중 중복 {len(all_split_docs) - len(unique_docs)}개 발견 및 제거")
        print(f"✨ 최종 {len(unique_docs)}개 조각 저장 예정")

        # 2. [핵심] 고유 ID 생성 
        # 예: 005930_DART_0, 005930_DART_1 ...
        # 이렇게 ID를 지정하면 다시 실행해도 같은 ID 위치에 덮어씌워집니다.
        ids = [f"{ticker}_DART_{i}" for i in range(len(unique_docs))]

        # 3. ID와 함께 DB 저장
        try:
            # Chroma는 ids 인자를 주면 자동으로 Upsert 모드로 동작합니다.
            self.vector_db.add_documents(unique_docs, ids=ids)
            print(f"✅ {len(unique_docs)}개의 조각이 고유 ID와 함께 저장되었습니다.")
        except Exception as e:
            print(f"❌ DB 저장 중 오류 발생: {e}")


    def ingest_news_data(self, ticker, company_name, news_docs):
        """[휘발성 데이터] 기존 뉴스를 삭제하고 최신 뉴스로 교체합니다."""
        if not news_docs:
            print(f"⚠️ {company_name}({ticker}) 뉴스 문서가 없습니다. 건너뜁니다.")
            return
        
        print(f"🧹 {company_name}({ticker})의 기존 뉴스 조각을 정리 중...")

        self._clear_category(ticker, "news")

        ids = [f"{ticker}_NEWS_{i}" for i in range(len(news_docs))]
        for doc in news_docs:
            doc.metadata.update({"category": "news", "ticker": ticker})


        try:
            # Chroma는 ids 인자를 주면 자동으로 Upsert 모드로 동작합니다.
            self.vector_db.add_documents(news_docs, ids=ids)
            print(f"✨ {company_name} 최신 뉴스 {len(news_docs)}건 갱신 완료.")
        except Exception as e:
            # 처음 데이터를 넣을 때는 삭제할 데이터가 없어 에러가 날 수 있으므로 예외 처리합니다.
            print(f"💡 기존 뉴스가 없거나 삭제 중 참고사항이 발생했습니다.: {e}")


    def ingest_chart_data(self, ticker, company_name, chart_docs):
        if not chart_docs: return

        self._clear_category(ticker, "chart")

        ids = [f"{ticker}_CHART_{i}" for i in range(len(chart_docs))]
        for doc in chart_docs:
            doc.metadata.update({"category": "chart", "ticker": ticker})

        try:
            # Chroma는 ids 인자를 주면 자동으로 Upsert 모드로 동작합니다.
            self.vector_db.add_documents(chart_docs, ids=ids)
            print(f"✨ {company_name} 최신 차트 {len(chart_docs)}건 갱신 완료.")
        except Exception as e:
            # 처음 데이터를 넣을 때는 삭제할 데이터가 없어 에러가 날 수 있으므로 예외 처리합니다.
            print(f"💡 기존 차트가 없거나 삭제 중 참고사항이 발생했습니다.: {e}")

    def ingest_finance_data(self, ticker, company_name, finance_docs):
        """
        [신규 - 휘발성 데이터] yfinance에서 가져온 핵심 재무 수치(PER, PBR 등)를 
        'finance' 카테고리에 저장합니다.
        """
        if not finance_docs: return
        
        self._clear_category(ticker, "finance")
        
        ids = [f"{ticker}_FINANCE_{i}" for i in range(len(finance_docs))]
        for doc in finance_docs:
            doc.metadata.update({"category": "finance", "ticker": ticker})
            
        try:
            # Chroma는 ids 인자를 주면 자동으로 Upsert 모드로 동작합니다.
            self.vector_db.add_documents(finance_docs, ids=ids)
            print(f"✨ {company_name} 최신 재무 데이터 {len(finance_docs)}건 갱신 완료.")
        except Exception as e:
            # 처음 데이터를 넣을 때는 삭제할 데이터가 없어 에러가 날 수 있으므로 예외 처리합니다.
            print(f"💡 재무 데이터가 없거나 삭제 중 참고사항이 발생했습니다.: {e}")
        