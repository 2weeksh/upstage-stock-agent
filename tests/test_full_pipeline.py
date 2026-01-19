# tests/test_full_pipeline.py

from app.service.dart_collector import DartCollector
from app.service.news_collector import NewsCollector
from app.service.stock_ingestor import StockIngestor
# 유저님이 구현해두신 벡터 DB 로드 함수를 가져오세요
from app.repository.chroma_db import get_vector_db 

def run_full_ingest():
    ticker = "005930"
    name = "삼성전자"
    
    # DB 연결
    vector_db = get_vector_db(ticker)
    ingestor = StockIngestor(vector_db)

    # 1. DART 데이터 (공통 지식)
    collector = DartCollector()
    dart_text, dart_title = collector.get_latest_report_text(ticker, name)
    ingestor.ingest_dart_data(ticker, name, dart_text, dart_title)

    # 2. 실시간 뉴스 데이터 (현재 소식)
    news_collector = NewsCollector()
    news_docs = news_collector.fetch_news(ticker, name)
    ingestor.ingest_news_data(ticker, name, news_docs)

if __name__ == "__main__":
    run_full_ingest()