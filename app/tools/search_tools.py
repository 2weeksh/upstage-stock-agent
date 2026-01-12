import os
from langchain_community.tools.tavily_search import TavilySearchResults

def get_stock_news(ticker: str, company_name: str):
    """
    Tavily API를 사용하여 특정 종목의 실시간 금융 뉴스를 수집합니다.
    """
    # 최신 뉴스 5건을 검색하도록 설정합니다.
    search = TavilySearchResults(k=5) 
    
    # 검색 쿼리: 종목 코드와 기업명을 섞어 정확한 결과를 유도합니다.
    query = f"{company_name} ({ticker}) 주식 시장 최신 뉴스 및 투자 리스크 분석"
    
    try:
        results = search.run(query)
        news_context = ""
        for res in results:
            news_context += f"\n제목: {res.get('title', '제목 없음')}\n내용: {res.get('content', '')}\n"
    
        return news_context

    except Exception as e:
        return f"뉴스 검색 중 오류가 발생했습니다: {str(e)}"