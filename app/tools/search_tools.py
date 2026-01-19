import os
import re
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
#from langchain_tavily import TavilySearchResults

load_dotenv()  # .env 파일에서 환경 변수 로드

def get_stock_news(ticker: str, company_name: str):
    """
    Tavily API를 사용하여 특정 종목의 실시간 금융 뉴스를 수집합니다.
    
    Required Environment Variables:
        TAVILY_API_KEY: Tavily API 키 (https://tavily.com/ 에서 발급)
    """
    # Tavily API 키 확인
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        return "⚠️ TAVILY_API_KEY가 설정되지 않았습니다. .env 파일에 API 키를 추가해주세요."
    
    # 최신 뉴스 10건을 검색하도록 설정합니다.
    search = TavilySearchResults(k=10, api_key=tavily_api_key)
    
    # 검색 쿼리: 종목 코드와 기업명을 섞어 정확한 결과를 유도합니다.
    query = f"{company_name} ({ticker}) 주식 시장 최신 뉴스 및 투자 판단 정보"
    
    try:
        results = search.run(query)
        clean_news = []

        for i, res in enumerate(results, 1):
            title = res.get('title', '제목 없음').strip()
            content = res.get('content', '').strip()

            # 1. 불필요한 연속 공백 및 줄바꿈 정리 (Regex 사용)
            content = re.sub(r'\s+', ' ', content)
            
            # 2. 뉴스 내용이 너무 길면 LLM이 읽기 좋게 적절히 자름 (약 300자)
            # 불필요한 UI 잡음 제거 (예시: 특정 단어가 포함된 문장 삭제)
            noise_words = [
                # 언어 선택 메뉴 (단어 단위가 아닌 전체 문구로 지정)
                "English (USA)", "English (UK)", "English (India)", "English (Canada)",
                "Deutsch", "Español", "Français", "Italiano", "Português", "Русский", "日本語",
            
                # 사이트 공통 광고/유도 문구
                "새해 세일", "55% 할인", "앱에서 열기", "잠금 해제", "회원가입", "로그인",
                "리스크 고지", "실시간 티커", "지표 더 보기", "인베스팅프로"
            ]
            for word in noise_words:
                content = content.replace(word, "")

            # 2. 뉴스 내용 길이를 800자로 상향 (중요 분석 누락 방지)
            if len(content) > 1000:
                content = content[:1000] + "..."

            # 3. 깔끔한 포맷으로 저장
            news_item = f"[{i}] 제목: {title}\n   내용: {content}"
            clean_news.append(news_item)

        # 뉴스 사이를 구분자로 연결
        formatted_news = "\n\n".join(clean_news)
        
        return f"### {company_name}({ticker}) 관련 최신 뉴스 분석 보고 ###\n\n{formatted_news}"

    except Exception as e:
        return f"뉴스 검색 중 오류 발생: {str(e)}"

if __name__ == "__main__":
    # 테스트 실행
    print(get_stock_news("035720.KS", "카카오"))  # 카카오 뉴스 검색 예시
    # print(get_stock_news("000660.KS", "SK하이닉스"))  # SK하이닉스 뉴스 검색 예시