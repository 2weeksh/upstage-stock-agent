# app/service/news_collector.py

import os
import re
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.documents import Document

class NewsCollector:
    def __init__(self):
        load_dotenv()
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        # 검색 도구 설정 (최신 뉴스 10건)
        self.search = TavilySearchResults(k=10)

    def _clean_content(self, content):
        """유저님이 만드신 노이즈 제거 로직"""
        # 1. 불필요한 연속 공백 및 줄바꿈 정리
        content = re.sub(r'\s+', ' ', content)
        
        # 2. 사이트 잡음 제거
        noise_words = [
            "English (USA)", "English (UK)", "Deutsch", "Español", "Français", 
            "새해 세일", "55% 할인", "앱에서 열기", "잠금 해제", "회원가입", "로그인", "본문으로 바로가기",
            "리스크 고지", "실시간 티커", "지표 더 보기", "인베스팅프로", "메인 메뉴로 바로가기"
        ]
        for word in noise_words:
            content = content.replace(word, "")
            
        return content.strip()

    def fetch_news(self, ticker: str, company_name: str):
        """뉴스 수집 후 Document 객체 리스트로 반환"""
        if not self.tavily_api_key:
            print("⚠️ TAVILY_API_KEY가 없습니다.")
            return []

        query = f"{company_name} ({ticker}) 주식 시장 최신 뉴스 및 투자 판단 정보"
        
        try:
            results = self.search.run(query)
            docs = []

            for i, res in enumerate(results):
                title = res.get('title', '제목 없음').strip()
                content = self._clean_content(res.get('content', ''))
                url = res.get('url', '')

                # DB 저장용 Document 객체 생성
                doc = Document(
                    page_content=f"뉴스 제목: {title}\n내용: {content}",
                    metadata={
                        "ticker": ticker,
                        "company": company_name,
                        "source": "TAVILY_NEWS",
                        "category": "news", # 에이전트 필터링용 태그
                        "url": url
                    }
                )
                docs.append(doc)
            
            return docs

        except Exception as e:
            print(f"뉴스 검색 중 오류 발생: {e}")
            return []