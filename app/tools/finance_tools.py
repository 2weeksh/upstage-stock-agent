import yfinance as yf
import pandas as pd
import requests as standard_requests  # 네이버용
from curl_cffi import requests as curl_requests  # 야후용
import re
import urllib3

# 1. SSL 경고 끄기 및 세션 초기화 (전역 설정)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
chrome_session = curl_requests.Session(impersonate="chrome")

def get_financial_summary(ticker: str) -> str:
    """
    [통합 재무 데이터 수집기]
    - TickerManager를 통해 들어온 정제된 티커를 기반으로 데이터 수집
    """
    ticker = ticker.strip().upper()

    try:
        # 한국 주식 판별 (숫자 6자리 포함 여부)
        # TickerManager가 '005930.KS' 형태로 넘겨주므로 숫자 6개만 있으면 네이버로 보냅니다.
        if re.search(r'\d{6}', ticker):
            return _get_naver_finance(ticker)
        
        # 그 외(미국 주식, ETF 등)는 야후 파이낸스
        return _get_yahoo_with_curl(ticker)

    except Exception as e:
        return f"❌ {ticker} 분석 중 오류 발생: {str(e)}"

def _get_naver_finance(ticker: str):
    """[한국] 네이버 금융 크롤링"""
    try:
        # 티커에서 숫자 6자리만 추출
        code = re.sub(r'[^0-9]', '', ticker)
        url = f"https://finance.naver.com/item/main.naver?code={code}"
        
        # 네이버는 일반 requests로 충분합니다.
        response = standard_requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, verify=False)
        dfs = pd.read_html(response.text)
        
        # 재무 테이블 찾기
        fin_df = next((df for df in dfs if '매출액' in str(df) or '영업이익' in str(df)), None)
        
        if fin_df is None:
            return f"⚠️ [네이버] {code} 데이터를 찾을 수 없습니다."

        # 멀티인덱스 및 빈칸 정리하여 문자열로 반환
        report = fin_df.fillna('-').to_string()
        return f"[Naver Financial Report: {code}]\n{report}"
    except Exception as e:
        return f"❌ 네이버 수집 에러: {str(e)}"

def _get_yahoo_with_curl(ticker: str):
    """[미국/ETF] yfinance + curl_cffi 위장"""
    try:
        # TickerManager에서 넘어온 티커 그대로 사용 (TQQQ, AAPL 등)
        stock = yf.Ticker(ticker, session=chrome_session)
        info = stock.info
        
        if not info or len(info) < 5:
            return f"⚠️ [야후] {ticker} 데이터를 가져올 수 없습니다."

        # 필요한 핵심 지표만 가독성 있게 정리
        v = info.get
        return f"""
[Yahoo Finance Report: {ticker}]
1. Valuation:
   - Market Cap: {v('marketCap', 'N/A')} / PER: {v('trailingPE', 'N/A')} / PBR: {v('priceToBook', 'N/A')}
2. Financials:
   - Revenue: {v('totalRevenue', 'N/A')} / Net Income: {v('netIncomeToCommon', 'N/A')} / ROE: {v('returnOnEquity', 'N/A')}
3. Cash & Debt:
   - Free Cash Flow: {v('freeCashflow', 'N/A')} / Total Debt: {v('totalDebt', 'N/A')}
        """.strip()
    except Exception as e:
        return f"❌ 야후(yfinance) 에러: {str(e)}"


if __name__ == "__main__":
    # 테스트 실행
    print(get_financial_summary("035720.KS"))  # 카카오
    #print(get_financial_summary("000660.KS"))  # SK하이닉스
